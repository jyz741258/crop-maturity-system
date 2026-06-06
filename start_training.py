import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dataset(data_dir):
    if not os.path.exists(data_dir):
        print(f"错误：数据集目录不存在: {data_dir}")
        return False
    
    maturity_folders = ['幼嫩期', '成熟期', '过熟期', '衰老期']
    total_images = 0
    
    print("数据集结构检查：")
    for folder in maturity_folders:
        folder_path = os.path.join(data_dir, folder)
        if os.path.exists(folder_path):
            images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            count = len(images)
            total_images += count
            print(f"  {folder}: {count} 张图片")
        else:
            print(f"  {folder}: 不存在")
    
    print(f"\n总计: {total_images} 张图片")
    return total_images > 0

def main():
    data_dir = 'crop-image/tea'
    save_path = 'models/leaf_maturity_model.pth'
    epochs = 20
    
    print("=" * 50)
    print("叶片成熟度检测模型训练")
    print("=" * 50)
    
    if not check_dataset(data_dir):
        print("数据集不足，训练中止")
        return
    
    print("\n开始训练...")
    
    from models.deep_learning_model import train_model_main
    
    try:
        result = train_model_main(data_dir, save_path)
        
        print("\n" + "=" * 50)
        print("训练完成！")
        print(f"最佳验证准确率: {result['best_val_acc']:.4f}")
        print(f"测试准确率: {result['test_acc']:.4f}")
        print(f"模型已保存到: {save_path}")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n训练失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()