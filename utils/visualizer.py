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

    def draw_maturity_boxes_with_stats(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        result = image.copy()
        height, width = result.shape[:2]
        
        plant_count = sum(1 for d in detections if d.get('detection_type') == 'plant')
        leaf_count = sum(1 for d in detections if d.get('detection_type') == 'leaf')
        total_leaves_detected = sum(d.get('leaf_count', 1) for d in detections)
        
        counts_by_maturity = {}
        for det in detections:
            maturity = det.get('maturity', '未知')
            counts_by_maturity[maturity] = counts_by_maturity.get(maturity, 0) + 1
        
        for idx, det in enumerate(detections):
            x1, y1, x2, y2 = det['bbox']
            maturity = det.get('maturity', '未知')
            confidence = det.get('confidence', 0)
            detection_type = det.get('detection_type', 'leaf')
            leaf_count_det = det.get('leaf_count', 1)
            quality_score = det.get('quality_score', 0)
            
            color = self.maturity_colors.get(maturity, (255, 255, 255))
            color_bgr = (color[2], color[1], color[0])
            
            box_thickness = max(2, min(4, int((x2 - x1 + y2 - y1) / 100)))
            cv2.rectangle(result, (x1, y1), (x2, y2), color_bgr, box_thickness)
            
            if detection_type == 'plant':
                cv2.putText(result, '🌱', (x1 - 15, y1 + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_bgr, 2)
            else:
                cv2.putText(result, '🍃', (x1 - 15, y1 + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_bgr, 2)
            
            cv2.putText(result, str(idx + 1), (x1 + 5, y1 + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            labels = []
            labels.append(f"{self.maturity_icons.get(maturity, '🌿')} {maturity}")
            labels.append(f"置信度: {confidence:.1f}%")
            labels.append(f"品质: {quality_score}分")
            if detection_type == 'plant':
                labels.append(f"叶片数: {leaf_count_det}")
            
            label_y = y2 + 5
            for label_text in labels:
                label_size, _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                if label_y + label_size[1] < height - 10:
                    cv2.putText(result, label_text, (x1, label_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color_bgr, 1)
                    label_y += label_size[1] + 3
        
        legend_bg = np.zeros((110, width, 3), dtype=np.uint8)
        legend_bg[:, :] = (10, 30, 10)
        legend_alpha = 0.8
        
        cv2.putText(legend_bg, f"📊 检测统计", (20, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        stats_text = [
            f"🌱 整株作物: {plant_count} 棵",
            f"🍃 单叶检测: {leaf_count} 片",
            f"📝 总计叶片: {total_leaves_detected} 片",
            f"🔢 检测目标: {len(detections)} 个"
        ]
        
        y_pos = 50
        for text in stats_text:
            cv2.putText(legend_bg, text, (20, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 255, 200), 1)
            y_pos += 20
        
        legend_start_x = width - 200
        legend_start_y = 10
        
        for i in range(legend_bg.shape[0]):
            for j in range(legend_bg.shape[1]):
                if legend_start_y + i < result.shape[0] and legend_start_x + j < result.shape[1]:
                    alpha = legend_alpha
                    result[legend_start_y + i, legend_start_x + j] = (
                        (1 - alpha) * result[legend_start_y + i, legend_start_x + j] +
                        alpha * legend_bg[i, j]
                    ).astype(np.uint8)
        
        cv2.putText(result, f"📊 检测统计", (legend_start_x + 15, legend_start_y + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        y_pos = legend_start_y + 48
        for text in stats_text:
            cv2.putText(result, text, (legend_start_x + 15, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 255, 200), 1)
            y_pos += 18
        
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