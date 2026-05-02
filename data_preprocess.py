import os
import shutil
from PIL import Image
from sklearn.model_selection import train_test_split
import numpy as np

def get_all_images(data_dir):
    """获取所有图片文件路径"""
    images = []
    labels = []
    class_names = sorted(os.listdir(data_dir))
    
    for class_name in class_names:
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.isdir(class_dir):
            continue
        
        for filename in os.listdir(class_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                images.append(os.path.join(class_dir, filename))
                labels.append(class_name)
    
    return images, labels, class_names

def resize_and_convert(image_path, output_size=(256, 256), output_format='JPEG'):
    """调整图片尺寸并转换格式"""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            img = img.resize(output_size, Image.LANCZOS)
            return img
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def save_image(img, save_path, format='JPEG'):
    """保存图片"""
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path, format=format)
        return True
    except Exception as e:
        print(f"Error saving {save_path}: {e}")
        return False

def split_dataset(images, labels, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
    """划分数据集"""
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-9, "比例总和必须为1"
    
    train_imgs, temp_imgs, train_labels, temp_labels = train_test_split(
        images, labels, train_size=train_ratio, stratify=labels, random_state=42
    )
    
    val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
    val_imgs, test_imgs, val_labels, test_labels = train_test_split(
        temp_imgs, temp_labels, train_size=val_ratio_adjusted, stratify=temp_labels, random_state=42
    )
    
    return {
        'train': (train_imgs, train_labels),
        'val': (val_imgs, val_labels),
        'test': (test_imgs, test_labels)
    }

def process_dataset(input_dir, output_dir, image_size=(256, 256)):
    """处理整个数据集"""
    print(f"正在读取数据: {input_dir}")
    images, labels, class_names = get_all_images(input_dir)
    print(f"共找到 {len(images)} 张图片，{len(class_names)} 个类别: {class_names}")
    
    print("划分数据集...")
    dataset = split_dataset(images, labels)
    
    for split in ['train', 'val', 'test']:
        imgs, lbls = dataset[split]
        print(f"{split}: {len(imgs)} 张图片")
        
        for img_path, label in zip(imgs, lbls):
            img = resize_and_convert(img_path, output_size=image_size)
            if img is None:
                continue
            
            filename = os.path.basename(img_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(output_dir, split, label, f"{name}.jpg")
            
            save_image(img, output_path)
    
    print(f"数据集处理完成，保存到: {output_dir}")
    
    with open(os.path.join(output_dir, 'classes.txt'), 'w', encoding='utf-8') as f:
        for class_name in class_names:
            f.write(class_name + '\n')
    
    print(f"类别列表已保存到: {os.path.join(output_dir, 'classes.txt')}")

if __name__ == '__main__':
    input_directory = r'E:\crop-image'
    output_directory = r'E:\crop-image-processed'
    
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)
    
    process_dataset(input_directory, output_directory, image_size=(256, 256))