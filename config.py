# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = 'uploads'
    REPORT_FOLDER = 'reports'
    TEMP_FOLDER = 'temp'
    DATA_FOLDER = 'data'
    MODEL_FOLDER = 'models'
    
    # 图片处理配置
    TARGET_SIZE = (800, 600)
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    # 成熟度阈值（可调参数）
    MATURITY_THRESHOLDS = {
        '幼嫩期': {'green_ratio_min': 0.45, 'green_ratio_max': 1.0},
        '成熟期': {'green_ratio_min': 0.35, 'green_ratio_max': 0.45},
        '过熟期': {'green_ratio_min': 0.20, 'green_ratio_max': 0.35},
        '衰老期': {'green_ratio_min': 0.00, 'green_ratio_max': 0.20}
    }
    
    # 作物类型配置
    CROP_TYPES = {
        '茶叶': {'optimal_green_ratio': 0.40, 'harvest_days': 5},
        '烟叶': {'optimal_green_ratio': 0.38, 'harvest_days': 7},
        '桑叶': {'optimal_green_ratio': 0.42, 'harvest_days': 4},
        '其他': {'optimal_green_ratio': 0.40, 'harvest_days': 5}
    }
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}