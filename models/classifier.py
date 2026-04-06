# models/classifier.py
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pandas as pd
import os

class MaturityClassifier:
    """成熟度分类器"""
    
    def __init__(self, model_path=None):
        self.model = None
        self.feature_names = []
        self.classes = ['幼嫩期', '成熟期', '过熟期', '衰老期']
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self._init_model()
    
    def _init_model(self):
        """初始化模型（随机森林 + 梯度提升集成）"""
        self.rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.gb_model = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        self.svm_model = SVC(
            kernel='rbf',
            C=10,
            gamma='scale',
            probability=True,
            random_state=42
        )
        
        self.use_ensemble = True
    
    def train(self, X, y, feature_names=None):
        """训练模型"""
        X = np.array(X)
        y = np.array(y)
        
        if feature_names:
            self.feature_names = feature_names
        
        # 划分训练集和验证集
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 训练各个模型
        self.rf_model.fit(X_train, y_train)
        self.gb_model.fit(X_train, y_train)
        self.svm_model.fit(X_train, y_train)
        
        # 评估
        rf_acc = self.rf_model.score(X_val, y_val)
        gb_acc = self.gb_model.score(X_val, y_val)
        svm_acc = self.svm_model.score(X_val, y_val)
        
        print(f"随机森林验证准确率: {rf_acc:.4f}")
        print(f"梯度提升验证准确率: {gb_acc:.4f}")
        print(f"SVM验证准确率: {svm_acc:.4f}")
        
        # 交叉验证
        cv_scores = cross_val_score(self.rf_model, X_train, y_train, cv=5)
        print(f"交叉验证平均准确率: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        return {
            'rf_accuracy': rf_acc,
            'gb_accuracy': gb_acc,
            'svm_accuracy': svm_acc,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
    
    def predict(self, features):
        """预测单个样本"""
        features = np.array(features).reshape(1, -1)
        
        if self.use_ensemble:
            # 集成预测（投票）
            rf_prob = self.rf_model.predict_proba(features)[0]
            gb_prob = self.gb_model.predict_proba(features)[0]
            svm_prob = self.svm_model.predict_proba(features)[0]
            
            # 加权投票
            ensemble_prob = (rf_prob + gb_prob + svm_prob) / 3
            predicted_class = self.classes[np.argmax(ensemble_prob)]
            confidence = np.max(ensemble_prob) * 100
            
            # 各类别概率
            probabilities = {
                self.classes[i]: float(ensemble_prob[i]) 
                for i in range(len(self.classes))
            }
        else:
            predicted_class = self.rf_model.predict(features)[0]
            confidence = np.max(self.rf_model.predict_proba(features)[0]) * 100
            probabilities = {
                self.classes[i]: float(self.rf_model.predict_proba(features)[0][i])
                for i in range(len(self.classes))
            }
        
        return {
            'maturity': predicted_class,
            'confidence': round(confidence, 2),
            'probabilities': probabilities
        }
    
    def predict_batch(self, features_list):
        """批量预测"""
        results = []
        for features in features_list:
            results.append(self.predict(features))
        return results
    
    def save_model(self, model_path):
        """保存模型"""
        model_data = {
            'rf_model': self.rf_model,
            'gb_model': self.gb_model,
            'svm_model': self.svm_model,
            'feature_names': self.feature_names,
            'classes': self.classes,
            'use_ensemble': self.use_ensemble
        }
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"模型已保存至: {model_path}")
    
    def load_model(self, model_path):
        """加载模型"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.rf_model = model_data['rf_model']
        self.gb_model = model_data['gb_model']
        self.svm_model = model_data['svm_model']
        self.feature_names = model_data['feature_names']
        self.classes = model_data['classes']
        self.use_ensemble = model_data['use_ensemble']
        
        print(f"模型已加载: {model_path}")