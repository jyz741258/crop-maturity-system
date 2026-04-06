# utils/data_manager.py
import os
import cv2
import pandas as pd
import numpy as np
from datetime import datetime
import json

class DataManager:
    """数据管理模块"""
    
    def __init__(self, data_folder='data'):
        self.data_folder = data_folder
        self.raw_folder = os.path.join(data_folder, 'raw')
        self.processed_folder = os.path.join(data_folder, 'processed')
        self.annotation_file = os.path.join(data_folder, 'annotations.csv')
        
        os.makedirs(self.raw_folder, exist_ok=True)
        os.makedirs(self.processed_folder, exist_ok=True)
    
    def load_annotations(self):
        """加载标注数据"""
        if os.path.exists(self.annotation_file):
            return pd.read_csv(self.annotation_file)
        else:
            return pd.DataFrame(columns=['image_path', 'maturity', 'annotator', 'timestamp'])
    
    def save_annotation(self, image_path, maturity, annotator='user'):
        """保存标注"""
        df = self.load_annotations()
        
        new_record = pd.DataFrame([{
            'image_path': image_path,
            'maturity': maturity,
            'annotator': annotator,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])
        
        df = pd.concat([df, new_record], ignore_index=True)
        df.to_csv(self.annotation_file, index=False, encoding='utf-8-sig')
        
        return True
    
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
                    features = feature_extractor.extract_all_features(image)
                    feature_vector = feature_extractor.get_feature_vector(features)
                    
                    record = {'maturity': maturity}
                    for i, value in enumerate(feature_vector):
                        record[f'feature_{i}'] = value
                    
                    training_data.append(record)
        
        df = pd.DataFrame(training_data)
        output_path = os.path.join(self.processed_folder, output_file)
        df.to_csv(output_path, index=False)
        
        print(f"训练数据已导出: {output_path}, 共 {len(df)} 条记录")
        return output_path
    
    def get_statistics(self):
        """获取数据统计"""
        annotations = self.load_annotations()
        
        if len(annotations) == 0:
            return {'total': 0, 'by_maturity': {}}
        
        stats = {
            'total': len(annotations),
            'by_maturity': annotations['maturity'].value_counts().to_dict(),
            'by_annotator': annotations['annotator'].value_counts().to_dict(),
            'date_range': {
                'min': annotations['timestamp'].min() if len(annotations) > 0 else None,
                'max': annotations['timestamp'].max() if len(annotations) > 0 else None
            }
        }
        
        return stats