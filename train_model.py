import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.deep_learning_model import train_model_main, DeepLearningMaturityDetector

def main():
    import argparse
    parser = argparse.ArgumentParser(description='训练叶片成熟度检测深度学习模型')
    parser.add_argument('--data_dir', type=str, required=True, help='数据集目录，包含各成熟度子文件夹')
    parser.add_argument('--save_path', type=str, default='models/leaf_maturity_model.pth', help='模型保存路径')
    parser.add_argument('--epochs', type=int, default=20, help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=32, help='批量大小')
    parser.add_argument('--lr', type=float, default=0.0001, help='学习率')
    parser.add_argument('--test', action='store_true', help='测试现有模型')
    
    args = parser.parse_args()
    
    if args.test:
        print("测试现有模型...")
        detector = DeepLearningMaturityDetector(args.save_path)
        if detector.model:
            print("模型加载成功，准备进行推理测试")
        else:
            print("模型加载失败")
    else:
        print(f"开始训练模型...")
        print(f"数据集目录: {args.data_dir}")
        print(f"模型保存路径: {args.save_path}")
        print(f"训练轮数: {args.epochs}")
        print(f"批量大小: {args.batch_size}")
        print(f"学习率: {args.lr}")
        
        result = train_model_main(args.data_dir, args.save_path)
        
        print("\n训练完成！")
        print(f"最佳验证准确率: {result['best_val_acc']:.4f}")
        print(f"测试准确率: {result['test_acc']:.4f}")

if __name__ == '__main__':
    main()