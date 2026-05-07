import os
import shutil
import random
from pathlib import Path

class CropDataReorganizer:
    """作物数据重新组织工具"""
    
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.maturity_classes = ['幼嫩期', '成熟期', '衰老期']
        self.crops = ['Pepper__bell', 'Potato', 'Tomato', 'Lychee']
    
    def reorganize_all_crops(self):
        """重新组织所有作物的数据"""
        print("开始重新组织作物数据...\n")
        
        for crop in self.crops:
            print(f"处理作物: {crop}")
            self.reorganize_crop(crop)
            print()
        
        print("所有作物数据重新组织完成！")
    
    def reorganize_crop(self, crop_name):
        """重新组织单个作物的数据"""
        crop_dir = self.base_dir / crop_name
        
        if not crop_dir.exists():
            print(f"  警告：目录不存在: {crop_dir}")
            return
        
        # 获取所有图片文件
        all_images = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG']:
            all_images.extend(list(crop_dir.glob(ext)))
        
        # 检查子目录中的图片
        for subdir in crop_dir.iterdir():
            if subdir.is_dir():
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG']:
                    all_images.extend(list(subdir.glob(ext)))
        
        if not all_images:
            print(f"  警告：未找到图片文件")
            return
        
        print(f"  找到 {len(all_images)} 张图片")
        
        # 随机打乱
        random.shuffle(all_images)
        
        # 按比例分配到三个类别（约3:4:3）
        total = len(all_images)
        young_count = int(total * 0.3)
        mature_count = int(total * 0.4)
        senile_count = total - young_count - mature_count
        
        print(f"  分配方案: 幼嫩期={young_count}, 成熟期={mature_count}, 衰老期={senile_count}")
        
        # 创建成熟度子目录
        for maturity in self.maturity_classes:
            (crop_dir / maturity).mkdir(exist_ok=True)
        
        # 删除旧的子目录（如果存在）
        for item in crop_dir.iterdir():
            if item.is_dir() and item.name not in self.maturity_classes:
                shutil.rmtree(item)
                print(f"  删除旧目录: {item.name}")
        
        # 分配图片
        assigned = 0
        
        # 幼嫩期
        for i in range(young_count):
            src = all_images[assigned]
            dst = crop_dir / '幼嫩期' / src.name
            shutil.copy(str(src), str(dst))
            assigned += 1
        
        # 成熟期
        for i in range(mature_count):
            src = all_images[assigned]
            dst = crop_dir / '成熟期' / src.name
            shutil.copy(str(src), str(dst))
            assigned += 1
        
        # 衰老期
        for i in range(senile_count):
            src = all_images[assigned]
            dst = crop_dir / '衰老期' / src.name
            shutil.copy(str(src), str(dst))
            assigned += 1
        
        # 删除原始文件（不在子目录中的文件）
        for item in crop_dir.iterdir():
            if item.is_file():
                item.unlink()
                print(f"  删除原始文件: {item.name}")
        
        print(f"  已完成分配")

if __name__ == '__main__':
    base_directory = r'E:\crop-image'
    
    reorganizer = CropDataReorganizer(base_directory)
    reorganizer.reorganize_all_crops()