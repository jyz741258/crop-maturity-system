import cv2
import numpy as np
from typing import List, Dict, Any
from data.maturity_standards import get_maturity_color, get_maturity_icon

class ImageVisualizer:
    def __init__(self):
        self.maturity_colors = {
            '幼嫩期': (243, 156, 18),
            '成熟期': (39, 174, 96),
            '过熟期': (230, 126, 34),
            '衰老期': (149, 165, 166)
        }
        
        self.maturity_icons = {
            '幼嫩期': '🌱',
            '成熟期': '🌿',
            '过熟期': '🍂',
            '衰老期': '🥀'
        }

    def draw_maturity_boxes(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        result = image.copy()
        height, width = result.shape[:2]
        
        for idx, det in enumerate(detections):
            x1, y1, x2, y2 = det['bbox']
            maturity = det.get('maturity', '未知')
            confidence = det.get('confidence', 0)
            
            color = self.maturity_colors.get(maturity, (255, 255, 255))
            color_bgr = (color[2], color[1], color[0])
            
            box_thickness = max(2, min(4, int((x2 - x1 + y2 - y1) / 100)))
            cv2.rectangle(result, (x1, y1), (x2, y2), color_bgr, box_thickness)
            
            label = f"{self.maturity_icons.get(maturity, '🌿')} {maturity} {confidence:.1f}%"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            
            label_x = x1
            label_y = max(y1, label_size[1] + 5)
            
            cv2.rectangle(result, (label_x, label_y - label_size[1] - 5),
                        (label_x + label_size[0] + 10, label_y + 5), color_bgr, cv2.FILLED)
            cv2.putText(result, label, (label_x + 5, label_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            cv2.putText(result, str(idx + 1), (x1 + 5, y1 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return result

    def draw_count_label(self, image: np.ndarray, total_count: int, counts_by_maturity: Dict[str, int]) -> np.ndarray:
        result = image.copy()
        height, width = result.shape[:2]
        
        legend_y = 30
        legend_x = 20
        spacing = 35
        
        cv2.putText(result, f"总作物数: {total_count}", (legend_x, legend_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        legend_y += spacing
        
        for maturity, count in counts_by_maturity.items():
            color = self.maturity_colors.get(maturity, (255, 255, 255))
            color_bgr = (color[2], color[1], color[0])
            icon = self.maturity_icons.get(maturity, '🌿')
            
            cv2.putText(result, f"{icon} {maturity}: {count}", (legend_x, legend_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_bgr, 2)
            legend_y += spacing
        
        return result

    def draw_heatmap(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        height, width = image.shape[:2]
        heatmap = np.zeros((height, width), dtype=np.float32)
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            maturity_weight = self._get_maturity_weight(det.get('maturity', '成熟期'))
            
            roi = heatmap[y1:y2, x1:x2]
            heatmap[y1:y2, x1:x2] = np.maximum(roi, maturity_weight)
        
        heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        
        overlay = cv2.addWeighted(image, 0.7, heatmap_color, 0.3, 0)
        return overlay

    def _get_maturity_weight(self, maturity: str) -> float:
        weights = {
            '幼嫩期': 0.25,
            '成熟期': 1.0,
            '过熟期': 0.5,
            '衰老期': 0.1
        }
        return weights.get(maturity, 0.5)

    def create_summary_image(self, original_image: np.ndarray, detections: List[Dict[str, Any]],
                            stats: Dict[str, Any]) -> np.ndarray:
        result = self.draw_maturity_boxes(original_image, detections)
        result = self.draw_count_label(result, stats.get('total', 0), stats.get('counts_by_maturity', {}))
        return result

    def save_marked_image(self, image: np.ndarray, output_path: str) -> bool:
        try:
            cv2.imwrite(output_path, image)
            return True
        except Exception as e:
            print(f"保存图片失败: {e}")
            return False

    def generate_statistics_overlay(self, image: np.ndarray, stats: Dict[str, Any]) -> np.ndarray:
        result = image.copy()
        height, width = result.shape[:2]
        
        overlay_height = 120
        overlay = np.zeros((overlay_height, width, 3), dtype=np.uint8)
        overlay[:, :] = (20, 50, 20)
        
        total = stats.get('total', 0)
        mature = stats.get('counts_by_maturity', {}).get('成熟期', 0)
        immature = stats.get('counts_by_maturity', {}).get('幼嫩期', 0)
        overripe = stats.get('counts_by_maturity', {}).get('过熟期', 0)
        senescent = stats.get('counts_by_maturity', {}).get('衰老期', 0)
        
        cv2.putText(overlay, f"大田作物成熟度分析报告", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.putText(overlay, f"总数量: {total} | 成熟期: {mature} | 幼嫩期: {immature} | 过熟期: {overripe} | 衰老期: {senescent}",
                    (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        if total > 0:
            mature_ratio = (mature / total) * 100
            cv2.putText(overlay, f"成熟率: {mature_ratio:.1f}%", (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 2)
        
        result = np.vstack([overlay, result])
        return result