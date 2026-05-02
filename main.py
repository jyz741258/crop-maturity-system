import os
import sys
import argparse
import shutil
from config import config

def run_preprocessing():
    print("\n=== Running Data Preprocessing ===")
    from data_preprocess import process_dataset
    
    if os.path.exists(config.PROCESSED_DATA_DIR):
        shutil.rmtree(config.PROCESSED_DATA_DIR)
    
    process_dataset(config.RAW_DATA_DIR, config.PROCESSED_DATA_DIR, config.IMAGE_SIZE)
    print("Data preprocessing completed!")

def run_augmentation():
    print("\n=== Running Data Augmentation ===")
    from data_augmentation import augment_dataset
    
    train_dir = os.path.join(config.PROCESSED_DATA_DIR, 'train')
    aug_train_dir = os.path.join(config.AUGMENTED_DATA_DIR, 'train')
    
    if not os.path.exists(train_dir):
        print("Error: Processed training data not found. Run preprocessing first.")
        return
    
    if os.path.exists(aug_train_dir):
        shutil.rmtree(aug_train_dir)
    
    augment_dataset(train_dir, aug_train_dir, config.NUM_AUGMENTATIONS)
    
    val_dir = os.path.join(config.PROCESSED_DATA_DIR, 'val')
    aug_val_dir = os.path.join(config.AUGMENTED_DATA_DIR, 'val')
    if os.path.exists(aug_val_dir):
        shutil.rmtree(aug_val_dir)
    shutil.copytree(val_dir, aug_val_dir)
    
    test_dir = os.path.join(config.PROCESSED_DATA_DIR, 'test')
    aug_test_dir = os.path.join(config.AUGMENTED_DATA_DIR, 'test')
    if os.path.exists(aug_test_dir):
        shutil.rmtree(aug_test_dir)
    shutil.copytree(test_dir, aug_test_dir)
    
    print("Data augmentation completed!")

def run_training():
    print("\n=== Running Model Training ===")
    from train_model import main as train_main
    
    if not os.path.exists(config.AUGMENTED_DATA_DIR):
        print("Error: Augmented data not found. Run augmentation first.")
        return
    
    train_main()
    print("Model training completed!")

def run_evaluation():
    print("\n=== Running Model Evaluation ===")
    from evaluate_model import main as eval_main
    
    model_path = os.path.join(config.MODEL_SAVE_DIR, 'best_model.pth')
    if not os.path.exists(model_path):
        print("Error: Model not found. Run training first.")
        return
    
    eval_main()
    print("Model evaluation completed!")

def run_all():
    print("=== Running Complete Pipeline ===")
    
    run_preprocessing()
    run_augmentation()
    run_training()
    run_evaluation()
    
    print("\n=== Pipeline Completed Successfully ===")

def show_help():
    help_text = """
Crop Leaf Image Classification Pipeline

Usage:
    python main.py [options]

Options:
    -h, --help          Show this help message
    --preprocess        Run data preprocessing only
    --augment           Run data augmentation only
    --train             Run model training only
    --evaluate          Run model evaluation only
    --all               Run the complete pipeline

Example:
    python main.py --all           # Run all steps
    python main.py --preprocess    # Only preprocess data
    python main.py --train         # Only train the model
    """
    print(help_text)

def main():
    parser = argparse.ArgumentParser(description='Crop Leaf Image Classification Pipeline')
    parser.add_argument('--preprocess', action='store_true', help='Run data preprocessing')
    parser.add_argument('--augment', action='store_true', help='Run data augmentation')
    parser.add_argument('--train', action='store_true', help='Run model training')
    parser.add_argument('--evaluate', action='store_true', help='Run model evaluation')
    parser.add_argument('--all', action='store_true', help='Run complete pipeline')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        show_help()
        return
    
    if args.all:
        run_all()
    else:
        if args.preprocess:
            run_preprocessing()
        if args.augment:
            run_augmentation()
        if args.train:
            run_training()
        if args.evaluate:
            run_evaluation()

if __name__ == '__main__':
    main()