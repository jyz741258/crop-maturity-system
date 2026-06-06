class Config:
    # 数据集路径
    RAW_DATA_DIR = r'E:\crop-image'
    PROCESSED_DATA_DIR = r'E:\crop-image-processed'
    AUGMENTED_DATA_DIR = r'E:\crop-image-augmented'
    MODEL_SAVE_DIR = r'E:\crop-models'
    
    # 图片参数
    IMAGE_SIZE = (256, 256)
    IMAGE_CHANNELS = 3
    IMAGE_FORMAT = 'JPEG'
    
    # 数据集划分比例
    TRAIN_RATIO = 0.7
    VAL_RATIO = 0.2
    TEST_RATIO = 0.1
    
    # 数据增强参数
    NUM_AUGMENTATIONS = 5
    FLIP_PROB = 0.5
    ROTATE_PROB = 0.5
    CROP_PROB = 0.5
    BRIGHTNESS_PROB = 0.5
    
    # 模型训练参数
    MODEL_NAME = 'crop_leaf_classifier'
    BATCH_SIZE = 32
    EPOCHS = 5
    LEARNING_RATE = 0.001
    WEIGHT_DECAY = 0.0001
    EARLY_STOP_PATIENCE = 10
    VALIDATION_FREQ = 1
    
    # 优化器参数
    OPTIMIZER = 'adam'
    ADAM_BETA1 = 0.9
    ADAM_BETA2 = 0.999
    
    # 学习率调度
    USE_LR_SCHEDULER = True
    LR_DECAY_FACTOR = 0.1
    LR_DECAY_PATIENCE = 5
    
    # 数据加载参数
    NUM_WORKERS = 4
    SHUFFLE = True
    PIN_MEMORY = True
    
    # 类别信息
    CLASSES = ['tea', 'tobacco', 'mulberry', 'lettuce', 'spinach', 'celery']
    NUM_CLASSES = len(CLASSES)
    
    # 日志参数
    LOG_DIR = r'E:\crop-logs'
    SAVE_MODEL_EVERY_EPOCH = False
    
    # 评估参数
    CONFUSION_MATRIX_PLOT = True
    CLASSIFICATION_REPORT = True

config = Config()