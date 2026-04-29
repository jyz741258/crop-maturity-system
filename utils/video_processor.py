import cv2
import numpy as np
import os
from typing import List, Dict, Any
from models.crop_detector import CropDetector
from models.feature_extractor import FeatureExtractor
from data.maturity_standards import get_maturity_stage
import time

class VideoProcessor:
    def __init__(self, crop_type: str = 'tea'):
        self.crop_detector = CropDetector()
        self.feature_extractor = FeatureExtractor()
        self.crop_type = crop_type
        self.frame_interval = 1
        self.output_fps = 10

    def process_video(self, input_path: str, output_path: str = None) -> Dict[str, Any]:
        if not os.path.exists(input_path):
            return {'error': '视频文件不存在'}
        
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return {'error': '无法打开视频文件'}
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        if output_path is None:
            output_path = input_path.replace('.mp4', '_processed.mp4')
        
        out = cv2.VideoWriter(output_path, fourcc, self.output_fps, (width, height))
        
        frame_count = 0
        processed_frames = 0
        all_detections = []
        frame_stats = []
        
        start_time = time.time()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % self.frame_interval == 0:
                frame_results = self._process_frame(frame, frame_count)
                frame_stats.append(frame_results)
                
                if frame_results['detections']:
                    all_detections.extend(frame_results['detections'])
                
                out.write(frame_results['marked_image'])
                processed_frames += 1
            
            frame_count += 1
            
            if frame_count % 30 == 0:
                print(f"处理进度: {frame_count}/{total_frames}")
        
        cap.release()
        out.release()
        
        processing_time = time.time() - start_time
        
        summary_stats = self._compute_summary_stats(frame_stats)
        
        return {
            'success': True,
            'input_path': input_path,
            'output_path': output_path,
            'total_frames': total_frames,
            'processed_frames': processed_frames,
            'processing_time': round(processing_time, 2),
            'fps': fps,
            'output_fps': self.output_fps,
            'frame_stats': frame_stats,
            'summary_stats': summary_stats,
            'total_detections': len(all_detections)
        }

    def _process_frame(self, frame: np.ndarray, frame_index: int) -> Dict[str, Any]:
        detections = self.crop_detector.detect_crops(frame)
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            crop_roi = frame[y1:y2, x1:x2]
            
            if crop_roi.size > 0:
                features = self.feature_extractor.extract_all_features(crop_roi)
                green_ratio = features.get('green_ratio', 0.5)
                maturity_result = get_maturity_stage(self.crop_type, green_ratio)
                
                det['green_ratio'] = green_ratio
                det['maturity'] = maturity_result['stage']
                det['quality_score'] = maturity_result['quality_score']
                det['frame_index'] = frame_index
        
        from utils.visualizer import ImageVisualizer
        visualizer = ImageVisualizer()
        
        counts_by_maturity = {}
        for det in detections:
            maturity = det.get('maturity', '未知')
            counts_by_maturity[maturity] = counts_by_maturity.get(maturity, 0) + 1
        
        marked_image = visualizer.draw_maturity_boxes(frame, detections)
        
        return {
            'frame_index': frame_index,
            'detections': detections,
            'counts_by_maturity': counts_by_maturity,
            'marked_image': marked_image,
            'total_count': len(detections)
        }

    def _compute_summary_stats(self, frame_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not frame_stats:
            return {}
        
        total_crops = 0
        counts_by_maturity = {}
        avg_detections_per_frame = 0
        
        for stats in frame_stats:
            total_crops += stats.get('total_count', 0)
            for maturity, count in stats.get('counts_by_maturity', {}).items():
                counts_by_maturity[maturity] = counts_by_maturity.get(maturity, 0) + count
        
        avg_detections_per_frame = total_crops / len(frame_stats) if frame_stats else 0
        
        return {
            'total_crops_detected': total_crops,
            'average_detections_per_frame': round(avg_detections_per_frame, 2),
            'counts_by_maturity': counts_by_maturity,
            'frames_processed': len(frame_stats)
        }

    def extract_key_frames(self, input_path: str, num_frames: int = 10) -> List[np.ndarray]:
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return []
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        key_frames = []
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                key_frames.append(frame)
        
        cap.release()
        return key_frames

    def analyze_video_summary(self, input_path: str, sample_interval: int = 5) -> Dict[str, Any]:
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return {'error': '无法打开视频文件'}
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        sample_indices = np.arange(0, total_frames, sample_interval)
        all_detections = []
        
        for idx in sample_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            
            detections = self.crop_detector.detect_crops(frame)
            
            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                crop_roi = frame[y1:y2, x1:x2]
                
                if crop_roi.size > 0:
                    features = self.feature_extractor.extract_all_features(crop_roi)
                    green_ratio = features.get('green_ratio', 0.5)
                    maturity_result = get_maturity_stage(self.crop_type, green_ratio)
                    
                    det['green_ratio'] = green_ratio
                    det['maturity'] = maturity_result['stage']
                    det['quality_score'] = maturity_result['quality_score']
                    det['frame_index'] = idx
            
            all_detections.extend(detections)
        
        cap.release()
        
        counts_by_maturity = {}
        for det in all_detections:
            maturity = det.get('maturity', '未知')
            counts_by_maturity[maturity] = counts_by_maturity.get(maturity, 0) + 1
        
        avg_confidence = np.mean([det.get('confidence', 0) for det in all_detections]) if all_detections else 0
        avg_green_ratio = np.mean([det.get('green_ratio', 0) for det in all_detections]) if all_detections else 0
        
        return {
            'success': True,
            'total_samples': len(sample_indices),
            'total_detections': len(all_detections),
            'counts_by_maturity': counts_by_maturity,
            'average_confidence': round(avg_confidence, 2),
            'average_green_ratio': round(avg_green_ratio, 4),
            'video_width': width,
            'video_height': height,
            'total_frames': total_frames
        }