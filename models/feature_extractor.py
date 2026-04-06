# models/feature_extractor.py
import cv2
import numpy as np
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from skimage.color import rgb2lab, deltaE_cie76

class FeatureExtractor:
    """增强版特征提取器"""
    
    def __init__(self):
        self.feature_names = []
    
    def extract_all_features(self, image):
        """提取所有特征"""
        features = {}
        
        # 颜色特征
        features.update(self.extract_color_features(image))
        
        # 纹理特征
        features.update(self.extract_texture_features(image))
        
        # 形态特征
        features.update(self.extract_morphology_features(image))
        
        # 新增：光谱特征
        features.update(self.extract_spectral_features(image))
        
        # 新增：局部特征
        features.update(self.extract_local_features(image))
        
        return features
    
    def extract_color_features(self, image):
        """增强的颜色特征提取"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        rgb = image / 255.0
        
        features = {}
        
        # HSV颜色空间特征
        for i, channel in enumerate(['H', 'S', 'V']):
            features[f'hsv_{channel}_mean'] = np.mean(hsv[:, :, i])
            features[f'hsv_{channel}_std'] = np.std(hsv[:, :, i])
        
        # LAB颜色空间特征
        for i, channel in enumerate(['L', 'A', 'B']):
            features[f'lab_{channel}_mean'] = np.mean(lab[:, :, i])
            features[f'lab_{channel}_std'] = np.std(lab[:, :, i])
        
        # RGB颜色比例
        green_mask = (hsv[:, :, 0] >= 35) & (hsv[:, :, 0] <= 85)
        features['green_ratio'] = np.sum(green_mask) / (image.shape[0] * image.shape[1])
        
        yellow_mask = (hsv[:, :, 0] >= 15) & (hsv[:, :, 0] <= 35)
        features['yellow_ratio'] = np.sum(yellow_mask) / (image.shape[0] * image.shape[1])
        
        # 颜色直方图特征
        for i, channel in enumerate(['R', 'G', 'B']):
            hist = cv2.calcHist([rgb], [i], None, [32], [0, 1])
            features[f'hist_{channel}_mean'] = np.mean(hist)
            features[f'hist_{channel}_std'] = np.std(hist)
        
        # 颜色矩
        for i, channel in enumerate(['R', 'G', 'B']):
            channel_data = rgb[:, :, i]
            features[f'color_moment_1_{channel}'] = np.mean(channel_data)
            features[f'color_moment_2_{channel}'] = np.std(channel_data)
            features[f'color_moment_3_{channel}'] = np.mean(np.abs(channel_data - features[f'color_moment_1_{channel}']) ** 3) ** (1/3)
        
        return features
    
    def extract_texture_features(self, image):
        """增强的纹理特征提取"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        features = {}
        
        # GLCM特征（多方向）
        distances = [1, 3, 5]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
        
        glcm_features = ['contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation']
        
        for d in distances:
            glcm = graycomatrix(gray, [d], angles, 256, symmetric=True, normed=True)
            for feat in glcm_features:
                values = graycoprops(glcm, feat)
                features[f'glcm_{feat}_d{d}_mean'] = np.mean(values)
                features[f'glcm_{feat}_d{d}_std'] = np.std(values)
        
        # LBP特征（多尺度）
        for radius in [1, 2, 3]:
            n_points = 8 * radius
            lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, n_points + 3), range=(0, n_points + 2))
            lbp_hist = lbp_hist.astype("float")
            lbp_hist /= (lbp_hist.sum() + 1e-6)
            
            for i, val in enumerate(lbp_hist[:10]):  # 只取前10个bin
                features[f'lbp_r{radius}_bin{i}'] = val
        
        # Gabor滤波器特征
        from skimage.filters import gabor
        for theta in [0, np.pi/4, np.pi/2, 3*np.pi/4]:
            for frequency in [0.1, 0.3, 0.5]:
                real, imag = gabor(gray, frequency=frequency, theta=theta)
                features[f'gabor_theta{theta:.2f}_freq{frequency}_mean'] = np.mean(real)
                features[f'gabor_theta{theta:.2f}_freq{frequency}_std'] = np.std(real)
        
        return features
    
    def extract_morphology_features(self, image):
        """增强的形态特征提取"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 自适应阈值分割
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY_INV, 11, 2)
        
        # 形态学操作去噪
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        features = {}
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            perimeter = cv2.arcLength(largest, True)
            
            features['leaf_area'] = area
            features['leaf_perimeter'] = perimeter
            features['leaf_area_ratio'] = area / (image.shape[0] * image.shape[1])
            features['circularity'] = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            
            # 凸包特征
            hull = cv2.convexHull(largest)
            hull_area = cv2.contourArea(hull)
            features['convexity'] = area / hull_area if hull_area > 0 else 0
            
            # 外接矩形特征
            rect = cv2.minAreaRect(largest)
            width, height = rect[1]
            features['aspect_ratio'] = max(width, height) / min(width, height) if min(width, height) > 0 else 1
            features['rect_area'] = width * height
            features['extent'] = area / features['rect_area'] if features['rect_area'] > 0 else 0
            
            # Hu矩（形状不变矩）
            moments = cv2.moments(largest)
            hu_moments = cv2.HuMoments(moments).flatten()
            for i, hu in enumerate(hu_moments[:7]):
                features[f'hu_moment_{i}'] = -np.sign(hu) * np.log10(np.abs(hu) + 1e-10)
        else:
            features['leaf_area'] = 0
            features['leaf_perimeter'] = 0
            features['leaf_area_ratio'] = 0
            features['circularity'] = 0
            features['convexity'] = 0
            features['aspect_ratio'] = 1
            features['extent'] = 0
            for i in range(7):
                features[f'hu_moment_{i}'] = 0
        
        return features
    
    def extract_spectral_features(self, image):
        """提取光谱特征（植被指数模拟）"""
        rgb = image / 255.0
        r, g, b = rgb[:, :, 2], rgb[:, :, 1], rgb[:, :, 0]
        
        features = {}
        
        # 模拟植被指数
        # NDVI-like index (使用红和近红外，这里用红和绿近似)
        ndvi_like = (g - r) / (g + r + 1e-6)
        features['ndvi_like_mean'] = np.mean(ndvi_like)
        features['ndvi_like_std'] = np.std(ndvi_like)
        
        # 绿色叶绿素指数
        gci = g / (r + 1e-6)
        features['gci_mean'] = np.mean(gci)
        features['gci_std'] = np.std(gci)
        
        # 红绿比值
        rg_ratio = r / (g + 1e-6)
        features['rg_ratio_mean'] = np.mean(rg_ratio)
        features['rg_ratio_std'] = np.std(rg_ratio)
        
        return features
    
    def extract_local_features(self, image):
        """提取局部特征（SIFT/ORB特征点）"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        features = {}
        
        # ORB特征点
        orb = cv2.ORB_create(nfeatures=500)
        keypoints, descriptors = orb.detectAndCompute(gray, None)
        
        features['n_keypoints'] = len(keypoints)
        
        if keypoints:
            # 关键点分布特征
            kp_sizes = [kp.size for kp in keypoints]
            features['kp_size_mean'] = np.mean(kp_sizes)
            features['kp_size_std'] = np.std(kp_sizes)
            
            kp_responses = [kp.response for kp in keypoints]
            features['kp_response_mean'] = np.mean(kp_responses)
            features['kp_response_std'] = np.std(kp_responses)
        else:
            features['kp_size_mean'] = 0
            features['kp_size_std'] = 0
            features['kp_response_mean'] = 0
            features['kp_response_std'] = 0
        
        return features
    
    def get_feature_vector(self, features_dict):
        """将特征字典转换为向量"""
        vector = []
        self.feature_names = []
        
        for key, value in sorted(features_dict.items()):
            if isinstance(value, (int, float)):
                vector.append(float(value))
                self.feature_names.append(key)
        
        return np.array(vector)