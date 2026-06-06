import cv2
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import color, feature, filters
import base64
import io
import os

class MaturityDetector:
    def __init__(self, use_deep_learning=False, model_path=None):
        self.use_deep_learning = use_deep_learning
        self.deep_detector = None
        
        if self.use_deep_learning:
            try:
                from models.deep_learning_model import DeepLearningMaturityDetector
                self.deep_detector = DeepLearningMaturityDetector(model_path)
                print("已启用深度学习模型")
            except Exception as e:
                print(f"加载深度学习模型失败，将使用传统算法: {e}")
                self.use_deep_learning = False
        
        self.crop_standards = {
            'tea': {
                'name': '茶叶',
                'color_ranges': {
                    'immature': [(35, 43, 46), (80, 255, 255)],
                    'mature': [(25, 43, 46), (70, 255, 255)],
                    'overripe': [(20, 30, 50), (35, 60, 150)],
                    'senescent': [(10, 20, 30), (25, 40, 100)]
                },
                'maturity_thresholds': {'green_ratio': 0.7, 'texture_score': 0.5}
            },
            'tobacco': {
                'name': '烟叶',
                'color_ranges': {
                    'immature': [(35, 43, 46), (85, 255, 255)],
                    'mature': [(20, 43, 46), (60, 255, 255)],
                    'overripe': [(15, 30, 50), (30, 60, 150)],
                    'senescent': [(10, 20, 30), (25, 40, 100)]
                },
                'maturity_thresholds': {'green_ratio': 0.6, 'color_variance': 35}
            },
            'mulberry': {
                'name': '桑叶',
                'color_ranges': {
                    'immature': [(35, 43, 46), (80, 255, 255)],
                    'mature': [(25, 43, 46), (70, 255, 255)],
                    'overripe': [(20, 30, 50), (35, 60, 150)],
                    'senescent': [(10, 20, 30), (25, 40, 100)]
                },
                'maturity_thresholds': {'green_ratio': 0.65, 'texture_score': 0.45}
            },
            'lettuce': {
                'name': '生菜',
                'color_ranges': {
                    'immature': [(35, 43, 46), (85, 255, 255)],
                    'mature': [(25, 43, 46), (75, 255, 255)],
                    'overripe': [(20, 30, 50), (35, 60, 150)],
                    'senescent': [(10, 20, 30), (25, 40, 100)]
                },
                'maturity_thresholds': {'green_ratio': 0.75, 'color_variance': 30}
            },
            'spinach': {
                'name': '菠菜',
                'color_ranges': {
                    'immature': [(35, 43, 46), (85, 255, 255)],
                    'mature': [(25, 43, 46), (70, 255, 255)],
                    'overripe': [(20, 30, 50), (35, 60, 150)],
                    'senescent': [(10, 20, 30), (25, 40, 100)]
                },
                'maturity_thresholds': {'green_ratio': 0.7, 'texture_score': 0.45}
            },
            'celery': {
                'name': '芹菜',
                'color_ranges': {
                    'immature': [(35, 43, 46), (80, 255, 255)],
                    'mature': [(25, 43, 46), (70, 255, 255)],
                    'overripe': [(20, 30, 50), (35, 60, 150)],
                    'senescent': [(10, 20, 30), (25, 40, 100)]
                },
                'maturity_thresholds': {'green_ratio': 0.65, 'texture_score': 0.5}
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
                crop_result = self._analyze_single_crop(image, image_hsv, contour, i, image_path)
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

    def _analyze_single_crop(self, image, hsv_image, contour, index, image_path=None):
        try:
            x, y, w, h = cv2.boundingRect(contour)
            if w < 20 or h < 20:
                return None
            
            crop_roi = hsv_image[y:y+h, x:x+w]
            rgb_roi = image[y:y+h, x:x+w]
            
            color_features = self._extract_color_features(crop_roi)
            texture_features = self._extract_texture_features(rgb_roi)
            shape_features = self._extract_shape_features(contour)
            
            if self.use_deep_learning and self.deep_detector and image_path:
                roi_path = f'temp_roi_{index}.jpg'
                cv2.imwrite(roi_path, rgb_roi)
                dl_result = self.deep_detector.predict(roi_path)
                os.remove(roi_path)
                
                if dl_result:
                    maturity = dl_result['maturity']
                    confidence = dl_result['confidence']
                else:
                    maturity, confidence = self._classify_maturity(color_features, texture_features)
            else:
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
                'quality_score': round(self._calculate_quality(maturity, confidence, texture_features['score']), 1),
                'detection_type': 'leaf'
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
                return ('成熟期', 0.75)
        elif red_ratio > 0.3 or (green_ratio < 0.3 and red_ratio > 0.1):
            if color_variance > 35:
                return ('衰老期', 0.8)
            else:
                return ('过熟期', 0.9)
        else:
            if texture_score > 0.4:
                return ('成熟期', 0.7)
            else:
                return ('幼嫩期', 0.65)

    def _calculate_quality(self, maturity, confidence, texture_score):
        base_score = {
            '幼嫩期': 70,
            '成熟期': 95,
            '过熟期': 60,
            '衰老期': 30
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