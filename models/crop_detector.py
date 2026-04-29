import cv2
import numpy as np
import os
from typing import List, Dict, Any

class CropDetector:
    def __init__(self, model_path: str = None):
        self.model = None
        self.class_names = ['crop', 'tea', 'tobacco', 'mulberry', 'lettuce', 'spinach', 'celery']
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.45
        self._load_model(model_path)

    def _load_model(self, model_path: str):
        try:
            from ultralytics import YOLO
            
            model_dir = os.path.join(os.path.dirname(__file__), '../models')
            os.makedirs(model_dir, exist_ok=True)
            
            os.environ['ULTRALYTICS_DIR'] = model_dir
            
            if model_path and os.path.exists(model_path):
                self.model = YOLO(model_path)
                print(f"已加载YOLO模型: {model_path}")
            else:
                self.model = YOLO('yolov8n.pt')
                print("使用YOLOv8n预训练模型")
            self.model_type = 'yolo'
        except ImportError:
            print("未安装ultralytics，使用OpenCV默认检测方法")
            self.model_type = 'default'
        except Exception as e:
            print(f"模型加载失败，使用默认检测方法: {e}")
            self.model_type = 'default'

    def detect_crops(self, image: np.ndarray) -> List[Dict[str, Any]]:
        if self.model_type == 'yolo' and self.model is not None:
            return self._yolo_detection(image)
        else:
            return self._default_detection(image)

    def _default_detection(self, image: np.ndarray) -> List[Dict[str, Any]]:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 30, 30])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        min_area = 400
        max_area = 50000
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 20 and h > 20:
                    confidence = min(0.95, 0.55 + (area / 10000))
                    detections.append({
                        'bbox': [x, y, x + w, y + h],
                        'confidence': confidence,
                        'class_name': 'crop',
                        'class_id': 0
                    })
        
        return self._apply_nms(detections)

    def _apply_nms(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(detections) == 0:
            return detections
        
        boxes = np.array([det['bbox'] for det in detections])
        confidences = np.array([det['confidence'] for det in detections])
        
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = confidences.argsort()[::-1]
        
        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            
            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            
            inter = w * h
            ovr = inter / (areas[i] + areas[order[1:]] - inter)
            
            inds = np.where(ovr <= self.nms_threshold)[0]
            order = order[inds + 1]
        
        return [detections[i] for i in keep]

    def _yolo_detection(self, image: np.ndarray) -> List[Dict[str, Any]]:
        results = self.model(image, conf=self.confidence_threshold, iou=self.nms_threshold)
        
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.class_names[class_id] if class_id < len(self.class_names) else 'crop'
                
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': confidence,
                    'class_name': class_name,
                    'class_id': class_id
                })
        
        return detections

    def count_crops(self, image: np.ndarray) -> tuple:
        detections = self.detect_crops(image)
        return len(detections), detections

    def draw_detections(self, image: np.ndarray, detections: List[Dict[str, Any]], 
                        color: tuple = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        result = image.copy()
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            cv2.rectangle(result, (x1, y1), (x2, y2), color, thickness)
            
            label = f"{det['class_name']}: {det['confidence']:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            label_y = max(y1, label_size[1])
            
            cv2.rectangle(result, (x1, label_y - label_size[1]), 
                        (x1 + label_size[0], label_y), color, cv2.FILLED)
            cv2.putText(result, label, (x1, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return result