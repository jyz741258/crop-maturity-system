import cv2
import numpy as np
from typing import List, Dict, Any
from collections import defaultdict

class HeatmapGenerator:
    def __init__(self):
        self.maturity_colors = {
            '幼嫩期': (245, 158, 11),
            '成熟期': (34, 197, 94),
            '过熟期': (234, 88, 12),
            '衰老期': (100, 116, 139),
            '未知': (128, 128, 128)
        }
        
        self.maturity_labels = {
            '幼嫩期': 'Young',
            '成熟期': 'Mature',
            '过熟期': 'Overripe',
            '衰老期': 'Senile'
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
            confidence = det.get('confidence', 1.0)
            color = np.array(self.maturity_colors.get(maturity, self.maturity_colors['未知'])) * confidence
            
            grid_x1 = max(0, min(grid_width - 1, x1 // grid_size))
            grid_y1 = max(0, min(grid_height - 1, y1 // grid_size))
            grid_x2 = max(0, min(grid_width - 1, x2 // grid_size))
            grid_y2 = max(0, min(grid_height - 1, y2 // grid_size))
            
            for gy in range(grid_y1, grid_y2 + 1):
                for gx in range(grid_x1, grid_x2 + 1):
                    heatmap[gy, gx] += color
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

    def draw_maturity_labels(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        result = image.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 2
        
        color_map = {
            '幼嫩期': (245, 158, 11),
            '成熟期': (34, 197, 94),
            '过熟期': (234, 88, 12),
            '衰老期': (100, 116, 139)
        }
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            maturity = det.get('maturity', '未知')
            confidence = det.get('confidence', 0)
            
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            color = color_map.get(maturity, (128, 128, 128))
            
            cv2.rectangle(result, (x1, y1), (x2, y2), color, 2)
            
            label = f"{maturity} {confidence:.1f}"
            label_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
            label_x = max(0, min(x1, result.shape[1] - label_size[0] - 5))
            label_y = max(label_size[1] + 5, y1 - 5)
            
            cv2.rectangle(result, (label_x - 2, label_y - label_size[1] - 3), 
                        (label_x + label_size[0] + 2, label_y + 2), color, -1)
            cv2.putText(result, label, (label_x, label_y), font, font_scale, (255, 255, 255), thickness)
        
        return result

    def generate_analysis_report(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        height, width = image.shape[:2]
        
        total_count = len(detections)
        counts_by_maturity = defaultdict(int)
        confidences = []
        green_ratios = []
        
        for det in detections:
            maturity = det.get('maturity', '未知')
            counts_by_maturity[maturity] += 1
            confidences.append(det.get('confidence', 0))
            green_ratios.append(det.get('green_ratio', 0))
        
        avg_confidence = np.mean(confidences) if confidences else 0
        avg_green_ratio = np.mean(green_ratios) if green_ratios else 0
        
        grid_size = min(max(width, height) // 20, 50)
        heatmap = self.generate_heatmap(image, detections, grid_size)
        regions = self._analyze_regions(image, detections, grid_size)
        
        dominant_maturity = max(counts_by_maturity, key=counts_by_maturity.get, default='未知')
        maturity_distribution = {k: v for k, v in counts_by_maturity.items()}
        
        return {
            'total_count': total_count,
            'counts_by_maturity': maturity_distribution,
            'dominant_maturity': dominant_maturity,
            'average_confidence': round(float(avg_confidence), 2),
            'average_green_ratio': round(float(avg_green_ratio), 4),
            'image_dimensions': {'width': width, 'height': height},
            'grid_size': grid_size,
            'regions': regions,
            'heatmap_shape': heatmap.shape,
            'maturity_percentage': {
                k: round(v / total_count * 100, 1) if total_count > 0 else 0
                for k, v in maturity_distribution.items()
            }
        }

    def _analyze_regions(self, image: np.ndarray, detections: List[Dict[str, Any]], grid_size: int) -> List[Dict[str, Any]]:
        height, width = image.shape[:2]
        grid_height = height // grid_size
        grid_width = width // grid_size
        
        regions = []
        region_detections = defaultdict(list)
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            det_center_x = (x1 + x2) // 2
            det_center_y = (y1 + y2) // 2
            
            grid_x = min(grid_width - 1, max(0, det_center_x // grid_size))
            grid_y = min(grid_height - 1, max(0, det_center_y // grid_size))
            
            region_detections[(grid_x, grid_y)].append(det)
        
        for (gx, gy), dets in region_detections.items():
            region_counts = defaultdict(int)
            region_confidences = []
            region_green_ratios = []
            
            for det in dets:
                maturity = det.get('maturity', '未知')
                region_counts[maturity] += 1
                region_confidences.append(det.get('confidence', 0))
                region_green_ratios.append(det.get('green_ratio', 0))
            
            avg_confidence = np.mean(region_confidences) if region_confidences else 0
            avg_green_ratio = np.mean(region_green_ratios) if region_green_ratios else 0
            
            regions.append({
                'grid_x': gx,
                'grid_y': gy,
                'x1': gx * grid_size,
                'y1': gy * grid_size,
                'x2': min((gx + 1) * grid_size, width),
                'y2': min((gy + 1) * grid_size, height),
                'detection_count': len(dets),
                'counts_by_maturity': {k: v for k, v in region_counts.items()},
                'average_confidence': round(float(avg_confidence), 2),
                'average_green_ratio': round(float(avg_green_ratio), 4),
                'dominant_maturity': max(region_counts, key=region_counts.get) if region_counts else '未知'
            })
        
        return sorted(regions, key=lambda r: (r['grid_y'], r['grid_x']))

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
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        for region in regions:
            center_x = (region['x1'] + region['x2']) // 2
            center_y = (region['y1'] + region['y2']) // 2
            
            count = region['detection_count']
            dominant = region['dominant_maturity']
            
            label = f"{count}"
            cv2.putText(result, label, (center_x - 10, center_y),
                        font, 0.5, (255, 255, 255), 2)
            cv2.putText(result, label, (center_x - 10, center_y),
                        font, 0.5, (0, 0, 0), 1)
        
        return result

    def generate_density_map(self, image: np.ndarray, detections: List[Dict[str, Any]], grid_size: int = 50) -> np.ndarray:
        height, width = image.shape[:2]
        grid_height = height // grid_size
        grid_width = width // grid_size
        
        density_map = np.zeros((grid_height, grid_width), dtype=np.float32)
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            det_center_x = (x1 + x2) // 2
            det_center_y = (y1 + y2) // 2
            
            grid_x = min(grid_width - 1, max(0, det_center_x // grid_size))
            grid_y = min(grid_height - 1, max(0, det_center_y // grid_size))
            
            density_map[grid_y, grid_x] += 1
        
        max_density = np.max(density_map) if np.max(density_map) > 0 else 1
        density_map = (density_map / max_density * 255).astype(np.uint8)
        density_map = cv2.applyColorMap(density_map, cv2.COLORMAP_JET)
        density_map = cv2.resize(density_map, (width, height), interpolation=cv2.INTER_CUBIC)
        
        return density_map

    def create_composite_output(self, image: np.ndarray, detections: List[Dict[str, Any]], 
                              grid_size: int = 50, show_grid: bool = True, 
                              show_labels: bool = True, show_heatmap: bool = True) -> np.ndarray:
        result = image.copy()
        
        if show_heatmap:
            heatmap = self.generate_heatmap(image, detections, grid_size)
            result = self.overlay_heatmap(result, heatmap)
        
        if show_grid:
            result = self.draw_region_grid(result, grid_size)
        
        if show_labels:
            result = self.draw_maturity_labels(result, detections)
        
        return result

    def calculate_region_statistics(self, regions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not regions:
            return {
                'total_regions': 0,
                'avg_detections_per_region': 0,
                'regions_by_dominant_maturity': {},
                'most_dense_region': None,
                'least_dense_region': None
            }
        
        total_detections = sum(r['detection_count'] for r in regions)
        avg_detections = total_detections / len(regions)
        
        dominant_counts = defaultdict(int)
        for r in regions:
            dominant_counts[r['dominant_maturity']] += 1
        
        sorted_regions = sorted(regions, key=lambda r: r['detection_count'])
        
        return {
            'total_regions': len(regions),
            'avg_detections_per_region': round(avg_detections, 2),
            'regions_by_dominant_maturity': dict(dominant_counts),
            'most_dense_region': sorted_regions[-1] if sorted_regions else None,
            'least_dense_region': sorted_regions[0] if sorted_regions else None
        }

    def generate_summary_statistics(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not detections:
            return {
                'total_count': 0,
                'maturity_distribution': {},
                'confidence_stats': {'min': 0, 'max': 0, 'avg': 0},
                'green_ratio_stats': {'min': 0, 'max': 0, 'avg': 0},
                'recommendations': []
            }
        
        maturity_dist = defaultdict(int)
        confidences = []
        green_ratios = []
        
        for det in detections:
            maturity_dist[det.get('maturity', '未知')] += 1
            confidences.append(det.get('confidence', 0))
            green_ratios.append(det.get('green_ratio', 0))
        
        recommendations = []
        mature_count = maturity_dist.get('成熟期', 0)
        total = len(detections)
        
        if total > 0:
            mature_percentage = mature_count / total * 100
            
            if mature_percentage > 60:
                recommendations.append("检测区域作物整体成熟度良好，建议及时采收。")
            elif mature_percentage > 30:
                recommendations.append("部分作物已成熟，建议5-7天后再次检测。")
            else:
                recommendations.append("作物整体偏年轻，建议继续观察。")
            
            senile_count = maturity_dist.get('衰老期', 0)
            if senile_count > 0:
                recommendations.append(f"发现 {senile_count} 株衰老植株，建议及时处理。")
        
        return {
            'total_count': len(detections),
            'maturity_distribution': dict(maturity_dist),
            'confidence_stats': {
                'min': round(min(confidences), 2),
                'max': round(max(confidences), 2),
                'avg': round(np.mean(confidences), 2)
            },
            'green_ratio_stats': {
                'min': round(min(green_ratios), 4),
                'max': round(max(green_ratios), 4),
                'avg': round(np.mean(green_ratios), 4)
            },
            'recommendations': recommendations
        }