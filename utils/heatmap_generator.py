import cv2
import numpy as np
from typing import List, Dict, Any
from data.maturity_standards import get_maturity_stage

class HeatmapGenerator:
    def __init__(self):
        self.maturity_colors = {
            '幼嫩期': (243, 156, 18),
            '成熟期': (39, 174, 96),
            '过熟期': (230, 126, 34),
            '衰老期': (149, 165, 166),
            '未知': (128, 128, 128)
        }

    def generate_heatmap(self, image: np.ndarray, detections: List[Dict[str, Any]], grid_size: int = 20) -> np.ndarray:
        height, width = image.shape[:2]
        grid_height = height // grid_size
        grid_width = width // grid_size
        
        heatmap = np.zeros((grid_height, grid_width, 3), dtype=np.float32)
        count_map = np.zeros((grid_height, grid_width), dtype=np.int32)
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            maturity = det.get('maturity', '未知')
            color = self.maturity_colors.get(maturity, self.maturity_colors['未知'])
            
            grid_x1 = max(0, min(grid_width - 1, x1 // grid_size))
            grid_y1 = max(0, min(grid_height - 1, y1 // grid_size))
            grid_x2 = max(0, min(grid_width - 1, x2 // grid_size))
            grid_y2 = max(0, min(grid_height - 1, y2 // grid_size))
            
            for gy in range(grid_y1, grid_y2 + 1):
                for gx in range(grid_x1, grid_x2 + 1):
                    heatmap[gy, gx] += np.array(color)
                    count_map[gy, gx] += 1
        
        for gy in range(grid_height):
            for gx in range(grid_width):
                if count_map[gy, gx] > 0:
                    heatmap[gy, gx] /= count_map[gy, gx]
        
        heatmap = heatmap.astype(np.uint8)
        
        heatmap = cv2.resize(heatmap, (width, height), interpolation=cv2.INTER_CUBIC)
        
        return heatmap

    def overlay_heatmap(self, image: np.ndarray, heatmap: np.ndarray, alpha: float = 0.4) -> np.ndarray:
        result = cv2.addWeighted(image, 1 - alpha, heatmap, alpha, 0)
        return result

    def generate_maturity_heatmap(self, image: np.ndarray, detections: List[Dict[str, Any]], grid_size: int = 20) -> np.ndarray:
        heatmap = self.generate_heatmap(image, detections, grid_size)
        overlay = self.overlay_heatmap(image, heatmap)
        return overlay

    def generate_analysis_report(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        height, width = image.shape[:2]
        
        total_count = len(detections)
        counts_by_maturity = {}
        for det in detections:
            maturity = det.get('maturity', '未知')
            counts_by_maturity[maturity] = counts_by_maturity.get(maturity, 0) + 1
        
        avg_confidence = np.mean([det.get('confidence', 0) for det in detections]) if detections else 0
        avg_green_ratio = np.mean([det.get('green_ratio', 0) for det in detections]) if detections else 0
        
        grid_size = min(max(width, height) // 20, 50)
        heatmap = self.generate_heatmap(image, detections, grid_size)
        
        regions = self._analyze_regions(image, detections, grid_size)
        
        return {
            'total_count': total_count,
            'counts_by_maturity': counts_by_maturity,
            'average_confidence': round(float(avg_confidence), 2),
            'average_green_ratio': round(float(avg_green_ratio), 4),
            'image_dimensions': {'width': width, 'height': height},
            'grid_size': grid_size,
            'regions': regions,
            'heatmap_shape': heatmap.shape
        }

    def _analyze_regions(self, image: np.ndarray, detections: List[Dict[str, Any]], grid_size: int) -> List[Dict[str, Any]]:
        height, width = image.shape[:2]
        grid_height = height // grid_size
        grid_width = width // grid_size
        
        regions = []
        
        for gy in range(grid_height):
            for gx in range(grid_width):
                region_detections = []
                for det in detections:
                    x1, y1, x2, y2 = det['bbox']
                    det_center_x = (x1 + x2) // 2
                    det_center_y = (y1 + y2) // 2
                    
                    if (gx * grid_size <= det_center_x < (gx + 1) * grid_size and
                        gy * grid_size <= det_center_y < (gy + 1) * grid_size):
                        region_detections.append(det)
                
                if region_detections:
                    region_counts = {}
                    for det in region_detections:
                        maturity = det.get('maturity', '未知')
                        region_counts[maturity] = region_counts.get(maturity, 0) + 1
                    
                    avg_green_ratio = np.mean([d.get('green_ratio', 0) for d in region_detections])
                    
                    regions.append({
                        'grid_x': gx,
                        'grid_y': gy,
                        'x1': gx * grid_size,
                        'y1': gy * grid_size,
                        'x2': (gx + 1) * grid_size,
                        'y2': (gy + 1) * grid_size,
                        'detection_count': len(region_detections),
                        'counts_by_maturity': region_counts,
                        'average_green_ratio': round(float(avg_green_ratio), 4),
                        'dominant_maturity': max(region_counts, key=region_counts.get) if region_counts else '未知'
                    })
        
        return regions

    def draw_region_grid(self, image: np.ndarray, grid_size: int = 50) -> np.ndarray:
        result = image.copy()
        height, width = result.shape[:2]
        
        for x in range(0, width, grid_size):
            cv2.line(result, (x, 0), (x, height), (200, 200, 200), 1)
        for y in range(0, height, grid_size):
            cv2.line(result, (0, y), (width, y), (200, 200, 200), 1)
        
        return result

    def draw_region_labels(self, image: np.ndarray, regions: List[Dict[str, Any]]) -> np.ndarray:
        result = image.copy()
        
        for region in regions:
            center_x = (region['x1'] + region['x2']) // 2
            center_y = (region['y1'] + region['y2']) // 2
            
            count = region['detection_count']
            dominant = region['dominant_maturity']
            
            label = f"{count}"
            cv2.putText(result, label, (center_x - 10, center_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return result