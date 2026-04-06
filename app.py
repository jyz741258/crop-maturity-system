# app.py - 叶用经济作物成熟度判别系统（完整整合版）
import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import io
import json
from datetime import datetime
import warnings
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler 

warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# 配置
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORT_FOLDER'] = 'reports'

# 创建必要的文件夹
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)
os.makedirs('temp', exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)


# ==================== 增强版特征提取器 ====================
class FeatureExtractor:
    """增强版特征提取器"""
    
    def __init__(self):
        self.feature_names = []
    
    def extract_all_features(self, image):
        """提取所有特征"""
        features = {}
        features.update(self.extract_color_features_enhanced(image))
        features.update(self.extract_texture_features_enhanced(image))
        features.update(self.extract_morphology_features_enhanced(image))
        features.update(self.extract_spectral_features(image))
        return features
    
    def extract_color_features_enhanced(self, image):
        """增强的颜色特征提取"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        rgb = image / 255.0
        
        features = {}
        
        # HSV颜色空间特征
        for i, channel in enumerate(['H', 'S', 'V']):
            features[f'hsv_{channel}_mean'] = float(np.mean(hsv[:, :, i]))
            features[f'hsv_{channel}_std'] = float(np.std(hsv[:, :, i]))
        
        # LAB颜色空间特征
        for i, channel in enumerate(['L', 'A', 'B']):
            features[f'lab_{channel}_mean'] = float(np.mean(lab[:, :, i]))
            features[f'lab_{channel}_std'] = float(np.std(lab[:, :, i]))
        
        # 绿色和黄色比例
        green_mask = (hsv[:, :, 0] >= 35) & (hsv[:, :, 0] <= 85)
        features['green_ratio'] = float(np.sum(green_mask) / (image.shape[0] * image.shape[1]))
        
        yellow_mask = (hsv[:, :, 0] >= 15) & (hsv[:, :, 0] <= 35)
        features['yellow_ratio'] = float(np.sum(yellow_mask) / (image.shape[0] * image.shape[1]))
        
        # 颜色矩
        for i, channel in enumerate(['R', 'G', 'B']):
            channel_data = rgb[:, :, i]
            features[f'color_moment_1_{channel}'] = float(np.mean(channel_data))
            features[f'color_moment_2_{channel}'] = float(np.std(channel_data))
        
        return features
    
    def extract_texture_features_enhanced(self, image):
        """增强的纹理特征提取"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        features = {}
        
        # GLCM特征
        glcm = graycomatrix(gray, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], 256, symmetric=True, normed=True)
        
        features['glcm_contrast'] = float(graycoprops(glcm, 'contrast').mean())
        features['glcm_dissimilarity'] = float(graycoprops(glcm, 'dissimilarity').mean())
        features['glcm_homogeneity'] = float(graycoprops(glcm, 'homogeneity').mean())
        features['glcm_energy'] = float(graycoprops(glcm, 'energy').mean())
        features['glcm_correlation'] = float(graycoprops(glcm, 'correlation').mean())
        
        # LBP纹理特征
        radius = 3
        n_points = 8 * radius
        lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
        lbp_hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, n_points + 3), range=(0, n_points + 2))
        lbp_hist = lbp_hist.astype("float")
        lbp_hist /= (lbp_hist.sum() + 1e-6)
        
        for i, val in enumerate(lbp_hist[:8]):
            features[f'lbp_bin_{i}'] = float(val)
        
        # 边缘密度
        edges = cv2.Canny(gray, 50, 150)
        features['edge_density'] = float(np.sum(edges > 0) / (image.shape[0] * image.shape[1]))
        
        return features
    
    def extract_morphology_features_enhanced(self, image):
        """增强的形态特征提取"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        features = {
            'leaf_area': 0, 'leaf_perimeter': 0, 'circularity': 0,
            'leaf_area_ratio': 0, 'aspect_ratio': 1, 'convexity': 0, 'extent': 0
        }
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            perimeter = cv2.arcLength(largest, True)
            
            features['leaf_area'] = float(area)
            features['leaf_perimeter'] = float(perimeter)
            features['leaf_area_ratio'] = float(area / (image.shape[0] * image.shape[1]))
            
            if perimeter > 0:
                features['circularity'] = float(4 * np.pi * area / (perimeter * perimeter))
            
            # 凸包特征
            hull = cv2.convexHull(largest)
            hull_area = cv2.contourArea(hull)
            if hull_area > 0:
                features['convexity'] = float(area / hull_area)
            
            # 外接矩形特征
            rect = cv2.minAreaRect(largest)
            width, height = rect[1]
            if min(width, height) > 0:
                features['aspect_ratio'] = float(max(width, height) / min(width, height))
                features['extent'] = float(area / (width * height))
        
        return features
    
    def extract_spectral_features(self, image):
        """提取光谱特征（植被指数模拟）"""
        rgb = image / 255.0
        r, g, b = rgb[:, :, 2], rgb[:, :, 1], rgb[:, :, 0]
        
        features = {}
        
        # 模拟植被指数
        ndvi_like = (g - r) / (g + r + 1e-6)
        features['ndvi_like_mean'] = float(np.mean(ndvi_like))
        features['ndvi_like_std'] = float(np.std(ndvi_like))
        
        # 绿色叶绿素指数
        gci = g / (r + 1e-6)
        features['gci_mean'] = float(np.mean(gci))
        features['gci_std'] = float(np.std(gci))
        
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


# ==================== 机器学习分类器 ====================
class MaturityClassifier:
    """成熟度分类器"""
    
    def __init__(self, model_path=None):
        self.classes = ['幼嫩期', '成熟期', '过熟期', '衰老期']
        self.feature_names = []
        self._init_models()
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def _init_models(self):
        """初始化模型"""
        self.rf_model = RandomForestClassifier(
            n_estimators=200, max_depth=15,
            min_samples_split=5, random_state=42, n_jobs=-1
        )
        self.gb_model = GradientBoostingClassifier(
            n_estimators=150, learning_rate=0.1, max_depth=5, random_state=42
        )
        self.svm_model = SVC(kernel='rbf', C=10, probability=True, random_state=42)
        self.scaler = StandardScaler()

        n_features = 100  # 特征数量
        dummy_data = np.random.randn(10, n_features)  # 10个样本，100个特征
        self.scaler.fit(dummy_data)
        self.use_ensemble = True
    
    def train(self, X, y, feature_names=None):
        """训练模型"""
        X = np.array(X)
        y = np.array(y)
        
        if feature_names:
            self.feature_names = feature_names
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 标准化
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # 训练模型
        self.rf_model.fit(X_train_scaled, y_train)
        self.gb_model.fit(X_train_scaled, y_train)
        self.svm_model.fit(X_train_scaled, y_train)
        
        # 评估
        metrics = {
            'rf_accuracy': float(self.rf_model.score(X_val_scaled, y_val)),
            'gb_accuracy': float(self.gb_model.score(X_val_scaled, y_val)),
            'svm_accuracy': float(self.svm_model.score(X_val_scaled, y_val))
        }
        
        cv_scores = cross_val_score(self.rf_model, X_train_scaled, y_train, cv=5)
        metrics['cv_mean'] = float(cv_scores.mean())
        metrics['cv_std'] = float(cv_scores.std())
        
        return metrics
    
    def predict(self, features):
        """预测单个样本"""
        features = np.array(features).reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        
        if self.use_ensemble:
            rf_prob = self.rf_model.predict_proba(features_scaled)[0]
            gb_prob = self.gb_model.predict_proba(features_scaled)[0]
            svm_prob = self.svm_model.predict_proba(features_scaled)[0]
            ensemble_prob = (rf_prob + gb_prob + svm_prob) / 3
            predicted_class = self.classes[np.argmax(ensemble_prob)]
            confidence = float(np.max(ensemble_prob) * 100)
            probabilities = {self.classes[i]: float(ensemble_prob[i]) for i in range(len(self.classes))}
        else:
            predicted_class = self.rf_model.predict(features_scaled)[0]
            confidence = float(np.max(self.rf_model.predict_proba(features_scaled)[0]) * 100)
            probabilities = None
        
        return {'maturity': predicted_class, 'confidence': round(confidence, 2), 'probabilities': probabilities}
    
    def save_model(self, model_path):
        """保存模型"""
        model_data = {
            'rf_model': self.rf_model, 'gb_model': self.gb_model, 'svm_model': self.svm_model,
            'scaler': self.scaler, 'feature_names': self.feature_names,
            'classes': self.classes, 'use_ensemble': self.use_ensemble
        }
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, model_path):
        """加载模型"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        self.rf_model = model_data['rf_model']
        self.gb_model = model_data['gb_model']
        self.svm_model = model_data['svm_model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.classes = model_data['classes']
        self.use_ensemble = model_data['use_ensemble']


# ==================== 数据管理器 ====================
class DataManager:
    """数据管理模块"""
    
    def __init__(self, data_folder='data'):
        self.data_folder = data_folder
        self.annotation_file = os.path.join(data_folder, 'annotations.csv')
        os.makedirs(data_folder, exist_ok=True)
    
    def save_annotation(self, image_path, maturity, annotator='user'):
        """保存标注"""
        df = self.load_annotations()
        new_record = pd.DataFrame([{
            'image_path': image_path, 'maturity': maturity,
            'annotator': annotator, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])
        df = pd.concat([df, new_record], ignore_index=True)
        df.to_csv(self.annotation_file, index=False, encoding='utf-8-sig')
        return True
    
    def load_annotations(self):
        """加载标注数据"""
        if os.path.exists(self.annotation_file):
            return pd.read_csv(self.annotation_file)
        return pd.DataFrame(columns=['image_path', 'maturity', 'annotator', 'timestamp'])
    
    def export_training_data(self, feature_extractor, output_file='training_data.csv'):
        """导出训练数据"""
        annotations = self.load_annotations()
        training_data = []
        
        for _, row in annotations.iterrows():
            image_path = row['image_path']
            maturity = row['maturity']
            if os.path.exists(image_path):
                image = cv2.imread(image_path)
                if image is not None:
                    image = cv2.resize(image, (800, 600))
                    features = feature_extractor.extract_all_features(image)
                    feature_vector = feature_extractor.get_feature_vector(features)
                    record = {'maturity': maturity}
                    for i, val in enumerate(feature_vector):
                        record[f'feature_{i}'] = val
                    training_data.append(record)
        
        df = pd.DataFrame(training_data)
        output_path = os.path.join(self.data_folder, output_file)
        df.to_csv(output_path, index=False)
        return output_path
    
    def get_statistics(self):
        """获取数据统计"""
        annotations = self.load_annotations()
        if len(annotations) == 0:
            return {'total': 0, 'by_maturity': {}}
        return {
            'total': len(annotations),
            'by_maturity': annotations['maturity'].value_counts().to_dict(),
            'by_annotator': annotations['annotator'].value_counts().to_dict()
        }


# ==================== 原有成熟度判别系统 ====================
class CropMaturitySystem:
    """基于规则的成熟度判别系统"""
    
    def __init__(self):
        self.maturity_stages = {
            '幼嫩期': {'green_ratio_range': (0.45, 1.0), 'quality_score': 85, 'color_code': '#f39c12', 'icon': '🌱'},
            '成熟期': {'green_ratio_range': (0.35, 0.45), 'quality_score': 95, 'color_code': '#27ae60', 'icon': '🌿'},
            '过熟期': {'green_ratio_range': (0.20, 0.35), 'quality_score': 70, 'color_code': '#e67e22', 'icon': '🍂'},
            '衰老期': {'green_ratio_range': (0.0, 0.20), 'quality_score': 40, 'color_code': '#95a5a6', 'icon': '🥀'}
        }
        self.crop_types = {
            '茶叶': {'optimal_green_ratio': 0.40},
            '烟叶': {'optimal_green_ratio': 0.38},
            '桑叶': {'optimal_green_ratio': 0.42},
            '其他': {'optimal_green_ratio': 0.40}
        }
    
    def extract_color_features(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_green, upper_green = np.array([35, 30, 30]), np.array([85, 255, 255])
        green_ratio = np.sum(cv2.inRange(hsv, lower_green, upper_green) > 0) / (image.shape[0] * image.shape[1])
        return {'green_ratio': float(green_ratio)}
    
    def extract_texture_features(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return {'edge_density': float(np.sum(edges > 0) / (image.shape[0] * image.shape[1]))}
    
    def determine_maturity(self, color_features, texture_features, crop_type='茶叶'):
        green_ratio = color_features['green_ratio']
        optimal = self.crop_types.get(crop_type, self.crop_types['茶叶'])['optimal_green_ratio']
        
        if green_ratio >= optimal * 1.1:
            maturity = '幼嫩期'
        elif green_ratio >= optimal:
            maturity = '成熟期'
        elif green_ratio >= 0.20:
            maturity = '过熟期'
        else:
            maturity = '衰老期'
        
        stage = self.maturity_stages[maturity]
        confidence = 50 + (green_ratio - stage['green_ratio_range'][0]) / (stage['green_ratio_range'][1] - stage['green_ratio_range'][0] + 0.001) * 50
        confidence = max(0, min(100, confidence))
        
        return {
            'maturity': maturity, 'confidence': round(confidence, 2),
            'green_ratio': round(green_ratio * 100, 2), 'quality_score': stage['quality_score']
        }
    
    def analyze_image(self, image_path, crop_type='茶叶'):
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            image = cv2.resize(image, (800, 600))
            color_features = self.extract_color_features(image)
            texture_features = self.extract_texture_features(image)
            maturity_result = self.determine_maturity(color_features, texture_features, crop_type)
            
            return {
                'filename': os.path.basename(image_path), 'crop_type': crop_type,
                'maturity': maturity_result['maturity'], 'confidence': maturity_result['confidence'],
                'green_ratio': maturity_result['green_ratio'], 'quality_score': maturity_result['quality_score'],
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'recommendation': self.generate_recommendation(maturity_result, crop_type)
            }
        except Exception as e:
            print(f"分析出错: {str(e)}")
            return None
    
    def generate_recommendation(self, maturity_result, crop_type):
        maturity = maturity_result['maturity']
        if maturity == '幼嫩期':
            return f"当前{crop_type}处于幼嫩期，建议等待采收。"
        elif maturity == '成熟期':
            return f"当前{crop_type}已达到最佳采收期，建议在3-5天内完成采收。"
        elif maturity == '过熟期':
            return f"当前{crop_type}已进入过熟期，请立即采收！"
        else:
            return f"当前{crop_type}已进入衰老期，不建议采收。"
    
    def batch_analyze(self, folder_path, crop_type='茶叶'):
        results = []
        for file in os.listdir(folder_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                result = self.analyze_image(os.path.join(folder_path, file), crop_type)
                if result:
                    results.append(result)
        return results, {'total': len(results)} if results else None


# ==================== 初始化 ====================
maturity_system = CropMaturitySystem()
feature_extractor = FeatureExtractor()
maturity_classifier = MaturityClassifier()
data_manager = DataManager()

# 尝试加载已有模型
model_path = 'models/maturity_model.pkl'
if os.path.exists(model_path):
    try:
        maturity_classifier.load_model(model_path)
        print("已加载预训练模型")
    except:
        print("模型加载失败，将使用规则判断")


# ==================== API路由 ====================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """分析单张图片（规则判断）"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': '未上传图片'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': '未选择图片'}), 400
        
        crop_type = request.form.get('crop_type', '茶叶')
        temp_path = os.path.join('temp', f'temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{secure_filename(file.filename)}')
        file.save(temp_path)
        
        result = maturity_system.analyze_image(temp_path, crop_type)
        os.remove(temp_path)
        
        if result:
            return jsonify(result)
        return jsonify({'error': '图片分析失败'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze_enhanced', methods=['POST'])
def analyze_enhanced():
    """增强版图片分析（机器学习）"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': '未上传图片'}), 400
        
        file = request.files['image']
        crop_type = request.form.get('crop_type', '茶叶')
        temp_path = os.path.join('temp', f'temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{secure_filename(file.filename)}')
        file.save(temp_path)
        
        image = cv2.imread(temp_path)
        if image is None:
            os.remove(temp_path)
            return jsonify({'error': '图片读取失败'}), 400
        image = cv2.resize(image, (800, 600))
        
        # 机器学习预测
        features = feature_extractor.extract_all_features(image)
        feature_vector = feature_extractor.get_feature_vector(features)
        ml_result = maturity_classifier.predict(feature_vector)
        
        # 规则判断
        rule_result = maturity_system.analyze_image(temp_path, crop_type)
        os.remove(temp_path)
        
        return jsonify({
            'ml_prediction': ml_result,
            'rule_prediction': rule_result,
            'crop_type': crop_type
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch_analyze', methods=['POST'])
def batch_analyze():
    """批量分析"""
    try:
        data = request.get_json()
        folder_path = data.get('folder_path')
        crop_type = data.get('crop_type', '茶叶')
        
        if not folder_path or not os.path.exists(folder_path):
            return jsonify({'error': '文件夹路径无效'}), 400
        
        results, stats = maturity_system.batch_analyze(folder_path, crop_type)
        return jsonify({'results': results, 'stats': stats, 'total': len(results)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/train_model', methods=['POST'])
def train_model():
    """训练模型"""
    try:
        training_file = data_manager.export_training_data(feature_extractor)
        train_df = pd.read_csv(training_file)
        
        if len(train_df) < 10:
            return jsonify({'error': '训练数据不足，至少需要10条标注数据'}), 400
        
        X = train_df[[col for col in train_df.columns if col.startswith('feature_')]].values
        y = train_df['maturity'].values
        
        metrics = maturity_classifier.train(X, y, feature_extractor.feature_names)
        maturity_classifier.save_model('models/maturity_model.pkl')
        
        return jsonify({'success': True, 'metrics': metrics, 'training_samples': len(train_df)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/annotate', methods=['POST'])
def annotate_image():
    """标注图片"""
    try:
        data = request.get_json()
        result = data_manager.save_annotation(data.get('image_path'), data.get('maturity'))
        return jsonify({'success': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/data_stats', methods=['GET'])
def get_data_stats():
    """获取数据统计"""
    return jsonify(data_manager.get_statistics())


@app.route('/api/feature_importance', methods=['GET'])
def get_feature_importance():
    """获取特征重要性"""
    if maturity_classifier.rf_model is None:
        return jsonify({'error': '模型未训练'}), 400
    
    importances = maturity_classifier.rf_model.feature_importances_
    features = maturity_classifier.feature_names
    
    importance_list = [
        {'feature': features[i] if i < len(features) else f'feature_{i}', 'importance': float(importances[i])}
        for i in range(min(len(importances), len(features)))
    ]
    importance_list.sort(key=lambda x: x['importance'], reverse=True)
    
    return jsonify(importance_list[:20])


@app.route('/api/maturity_stages', methods=['GET'])
def get_maturity_stages():
    return jsonify(maturity_system.maturity_stages)


@app.route('/api/crop_types', methods=['GET'])
def get_crop_types():
    return jsonify(maturity_system.crop_types)


@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    try:
        data = request.get_json()
        results = data.get('results')
        if not results:
            return jsonify({'error': '无分析结果'}), 400
        
        report_data = []
        for r in results:
            report_data.append({
                '文件名': r.get('filename'), '作物类型': r.get('crop_type'),
                '成熟度': r.get('maturity'), '置信度(%)': r.get('confidence'),
                '绿色占比(%)': r.get('green_ratio'), '品质评分': r.get('quality_score'),
                '采收建议': r.get('recommendation'), '分析时间': r.get('analysis_time')
            })
        
        df = pd.DataFrame(report_data)
        report_path = os.path.join(app.config['REPORT_FOLDER'], f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        df.to_csv(report_path, index=False, encoding='utf-8-sig')
        
        return jsonify({'success': True, 'report_path': report_path, 'download_url': f'/download_report/{os.path.basename(report_path)}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download_report/<filename>')
def download_report(filename):
    return send_file(os.path.join(app.config['REPORT_FOLDER'], filename), as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)