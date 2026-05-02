import os
import random
import shutil
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

class DataAugmentor:
    def __init__(self):
        self.augmentations = [
            self.random_flip,
            self.random_rotate,
            self.random_crop,
            self.random_brightness,
            self.random_contrast,
            self.random_saturation,
            self.random_blur,
            self.random_noise
        ]
    
    def random_flip(self, img, p=0.5):
        """随机翻转"""
        if random.random() < p:
            flip_type = random.choice(['horizontal', 'vertical', 'both'])
            if flip_type == 'horizontal':
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif flip_type == 'vertical':
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            else:
                img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
        return img
    
    def random_rotate(self, img, p=0.5, max_angle=30):
        """随机旋转"""
        if random.random() < p:
            angle = random.uniform(-max_angle, max_angle)
            img = img.rotate(angle, expand=True, fillcolor=(0, 0, 0))
            img = img.resize((256, 256), Image.LANCZOS)
        return img
    
    def random_crop(self, img, p=0.5, crop_ratio=0.8):
        """随机裁剪"""
        if random.random() < p:
            width, height = img.size
            crop_width = int(width * crop_ratio)
            crop_height = int(height * crop_ratio)
            x = random.randint(0, width - crop_width)
            y = random.randint(0, height - crop_height)
            img = img.crop((x, y, x + crop_width, y + crop_height))
            img = img.resize((256, 256), Image.LANCZOS)
        return img
    
    def random_brightness(self, img, p=0.5, factor_range=(0.7, 1.3)):
        """随机亮度调整"""
        if random.random() < p:
            factor = random.uniform(*factor_range)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(factor)
        return img
    
    def random_contrast(self, img, p=0.5, factor_range=(0.7, 1.3)):
        """随机对比度调整"""
        if random.random() < p:
            factor = random.uniform(*factor_range)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(factor)
        return img
    
    def random_saturation(self, img, p=0.5, factor_range=(0.7, 1.3)):
        """随机饱和度调整"""
        if random.random() < p:
            factor = random.uniform(*factor_range)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(factor)
        return img
    
    def random_blur(self, img, p=0.3, radius_range=(1, 3)):
        """随机模糊"""
        if random.random() < p:
            radius = random.uniform(*radius_range)
            img = img.filter(ImageFilter.GaussianBlur(radius=radius))
        return img
    
    def random_noise(self, img, p=0.3, noise_level=0.05):
        """随机添加噪声"""
        if random.random() < p:
            img_array = np.array(img)
            noise = np.random.normal(0, noise_level * 255, img_array.shape)
            img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(img_array)
        return img
    
    def apply_augmentation(self, img, num_transforms=3):
        """随机应用多个增强变换"""
        transforms = random.sample(self.augmentations, num_transforms)
        for transform in transforms:
            img = transform(img)
        return img
    
    def generate_augmented_images(self, input_path, output_dir, num_augmentations=5):
        """为单张图片生成多张增强图片"""
        try:
            with Image.open(input_path) as img:
                img = img.convert('RGB')
                basename = os.path.basename(input_path)
                name, ext = os.path.splitext(basename)
                
                augmented_images = []
                for i in range(num_augmentations):
                    augmented = self.apply_augmentation(img.copy())
                    aug_name = f"{name}_aug_{i}.jpg"
                    aug_path = os.path.join(output_dir, aug_name)
                    augmented.save(aug_path, 'JPEG')
                    augmented_images.append(aug_path)
                
                return augmented_images
        except Exception as e:
            print(f"Error augmenting {input_path}: {e}")
            return []

def augment_dataset(input_dir, output_dir, num_augmentations=5):
    """对训练集进行数据增强"""
    augmentor = DataAugmentor()
    class_names = sorted(os.listdir(input_dir))
    
    for class_name in class_names:
        class_dir = os.path.join(input_dir, class_name)
        if not os.path.isdir(class_dir):
            continue
        
        output_class_dir = os.path.join(output_dir, class_name)
        os.makedirs(output_class_dir, exist_ok=True)
        
        for filename in os.listdir(class_dir):
            if filename.lower().endswith('.jpg'):
                img_path = os.path.join(class_dir, filename)
                shutil.copy(img_path, output_class_dir)
                augmentor.generate_augmented_images(img_path, output_class_dir, num_augmentations)
    
    print(f"数据增强完成，保存到: {output_dir}")

if __name__ == '__main__':
    import shutil
    input_train_dir = r'E:\crop-image-processed\train'
    output_train_dir = r'E:\crop-image-augmented\train'
    
    if os.path.exists(output_train_dir):
        shutil.rmtree(output_train_dir)
    
    augment_dataset(input_train_dir, output_train_dir, num_augmentations=5)