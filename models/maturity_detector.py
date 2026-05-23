import cv2
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import color, feature, filters
import base64
import io

class MaturityDetector:
    def __init__(self):
        self.crop_standards = {
            'Pepper__bell': {
                'name': '甜椒',
                'color_ranges': {
                    'immature': [(35, 43, 46), (77, 255, 255)],
                    'mature': [(25, 43, 46), (34, 255, 255)],
                    'overripe': [(0, 43, 46), (10, 255, 255)]
                },
                'maturity_thresholds': {'green_ratio': 0.6, 'color_variance': 30}
            },
            'Potato': {
                'name': '土豆',
                'color_ranges': {
                    'immature': [(35, 43, 46), (80, 255, 255)],
                    'mature': [(20, 30, 50), (35, 60, 150)],
                    'overripe': [(10, 20, 30), (25, 40, 100)]
                },
                'maturity_thresholds': {'green_ratio': 0.4, 'texture_score': 0.3}
            },
            'Tomato': {
                'name': '番茄',
                'color_ranges': {
                    'immature': [(35, 43, 46), (77, 255, 255)],
                    'mature': [(10, 100, 100), (15, 255, 255)],
                    'overripe': [(0, 100, 100), (8, 255, 255)]
                },
                'maturity_thresholds': {'red_ratio': 0.5, 'color_variance': 40}
            },
            'Lychee': {
                'name': '荔枝',
                'color_ranges': {
                    'immature': [(35, 43, 46), (80, 255, 255)],
                    'mature': [(0, 43, 100), (10, 255, 255)],
                    'overripe': [(10, 43, 100), (20, 255, 255)]
                },
                'maturity_thresholds': {'red_ratio': 0.6, 'texture_score': 0.4}
            }
        }

    def detect_crops(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("无法读取图片")
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            results = []
            contours = self._detect_contours(image)
            
            for i, contour in enumerate(contours[:20]):
                crop_result = self._analyze_single_crop(image, image_hsv, contour, i)
                if crop_result:
                    results.append(crop_result)
            
            return results
        
        except Exception as e:
            print(f"检测错误: {e}")
            return []

    def _detect_contours(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        return [c for c in contours if cv2.contourArea(c) > 100]

    def _analyze_single_crop(self, image, hsv_image, contour, index):
        try:
            x, y, w, h = cv2.boundingRect(contour)
            if w < 20 or h < 20:
                return None
            
            crop_roi = hsv_image[y:y+h, x:x+w]
            rgb_roi = image[y:y+h, x:x+w]
            
            color_features = self._extract_color_features(crop_roi)
            texture_features = self._extract_texture_features(rgb_roi)
            shape_features = self._extract_shape_features(contour)
            
            maturity, confidence = self._classify_maturity(color_features, texture_features)
            
            return {
                'id': f'crop_{index + 1}',
                'bbox': [int(x), int(y), int(x + w), int(y + h)],
                'maturity': maturity,
                'confidence': round(confidence * 100, 1),
                'green_ratio': round(color_features['green_ratio'] * 100, 1),
                'red_ratio': round(color_features['red_ratio'] * 100, 1),
                'color_variance': round(color_features['variance'], 1),
                'texture_score': round(texture_features['score'], 2),
                'shape_score': round(shape_features['score'], 2),
                'quality_score': round(self._calculate_quality(maturity, confidence, texture_features['score']), 1)
            }
        except Exception as e:
            return None

    def _extract_color_features(self, hsv_image):
        h, s, v = cv2.split(hsv_image)
        
        green_mask = cv2.inRange(hsv_image, (35, 43, 46), (77, 255, 255))
        red_mask = cv2.inRange(hsv_image, (0, 43, 46), (10, 255, 255))
        red_mask2 = cv2.inRange(hsv_image, (170, 43, 46), (180, 255, 255))
        red_mask = cv2.bitwise_or(red_mask, red_mask2)
        
        total_pixels = h.size
        green_ratio = cv2.countNonZero(green_mask) / total_pixels if total_pixels > 0 else 0
        red_ratio = cv2.countNonZero(red_mask) / total_pixels if total_pixels > 0 else 0
        
        h_mean, h_std = cv2.meanStdDev(h)
        s_mean, s_std = cv2.meanStdDev(s)
        
        return {
            'green_ratio': green_ratio,
            'red_ratio': red_ratio,
            'hue_mean': float(h_mean[0][0]),
            'hue_std': float(h_std[0][0]),
            'saturation_mean': float(s_mean[0][0]),
            'saturation_std': float(s_std[0][0]),
            'variance': float(h_std[0][0]) + float(s_std[0][0])
        }

    def _extract_texture_features(self, rgb_image):
        try:
            gray = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)
            
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edges = np.sqrt(sobel_x**2 + sobel_y**2)
            
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            glcm = self._compute_glcm(gray)
            
            return {
                'edge_density': np.mean(edges) / 100,
                'laplacian_var': np.var(laplacian) / 1000,
                'contrast': glcm.get('contrast', 0),
                'homogeneity': glcm.get('homogeneity', 0),
                'energy': glcm.get('energy', 0),
                'score': (np.mean(edges) / 100 + np.var(laplacian) / 2000) / 2
            }
        except Exception as e:
            return {'score': 0.5, 'edge_density': 0.5, 'laplacian_var': 0.5}

    def _compute_glcm(self, gray):
        try:
            from skimage.feature import greycomatrix, greycoprops
            
            gray = (gray / 255 * 15).astype(np.uint8)
            glcm = greycomatrix(gray, [1], [0], 16, symmetric=True, normed=True)
            
            return {
                'contrast': float(greycoprops(glcm, 'contrast')[0, 0]),
                'homogeneity': float(greycoprops(glcm, 'homogeneity')[0, 0]),
                'energy': float(greycoprops(glcm, 'energy')[0, 0]),
                'correlation': float(greycoprops(glcm, 'correlation')[0, 0])
            }
        except:
            return {}

    def _extract_shape_features(self, contour):
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            return {'score': 0.5}
        
        circularity = 4 * np.pi * area / (perimeter ** 2)
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h if h > 0 else 1
        
        return {
            'area': area,
            'perimeter': perimeter,
            'circularity': circularity,
            'aspect_ratio': aspect_ratio,
            'score': 0.5 + (circularity - 0.5) * 0.5
        }

    def _classify_maturity(self, color_features, texture_features):
        green_ratio = color_features['green_ratio']
        red_ratio = color_features['red_ratio']
        color_variance = color_features['variance']
        texture_score = texture_features['score']
        
        if green_ratio > 0.6:
            if color_variance < 25:
                return ('幼嫩期', 0.85)
            else:
                return ('生长期', 0.75)
        elif red_ratio > 0.3 or (green_ratio < 0.3 and red_ratio > 0.1):
            if color_variance > 35:
                return ('过熟期', 0.8)
            else:
                return ('成熟期', 0.9)
        else:
            if texture_score > 0.4:
                return ('成熟期', 0.7)
            else:
                return ('生长期', 0.65)

    def _calculate_quality(self, maturity, confidence, texture_score):
        base_score = {
            '幼嫩期': 60,
            '生长期': 75,
            '成熟期': 90,
            '过熟期': 50
        }.get(maturity, 70)
        
        return base_score * (confidence / 100) * (0.8 + texture_score * 0.4)

    def analyze_image_base64(self, base64_image):
        try:
            image_data = base64.b64decode(base64_image.split(',')[1] if ',' in base64_image else base64_image)
            image = Image.open(io.BytesIO(image_data))
            image = np.array(image)
            
            if image.ndim == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            
            temp_path = 'temp_analysis.jpg'
            cv2.imwrite(temp_path, image)
            
            results = self.detect_crops(temp_path)
            
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return results
        except Exception as e:
            print(f"Base64分析错误: {e}")
            return []

    def generate_heatmap(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            green_mask = cv2.inRange(hsv, (35, 43, 46), (77, 255, 255))
            red_mask = cv2.inRange(hsv, (0, 43, 46), (10, 255, 255))
            
            heatmap = np.zeros_like(green_mask, dtype=np.float32)
            heatmap[green_mask > 0] = 0.3
            heatmap[red_mask > 0] = 0.7
            
            heatmap = cv2.GaussianBlur(heatmap, (15, 15), 0)
            
            return heatmap.tolist()
        except Exception as e:
            print(f"热力图生成错误: {e}")
            return None