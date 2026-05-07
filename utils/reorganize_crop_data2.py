import os
import shutil
import random
from pathlib import Path

class CropDataReorganizer:
    """作物数据重新组织工具 - 处理 crop-maturity-system/crop-image 目录"""
    
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.maturity_classes = ['幼嫩期', '成熟期', '衰老期']
        # 荔枝的类别映射
        self.lychee_mapping = {
            'Early_Bud': '幼嫩期',
            'Young': '幼嫩期',
            'Healthy': '成熟期',
            'Senescent_Leaves': '衰老期'
        }
    
    def reorganize_all_crops(self):
        """重新组织所有作物的数据"""
        print("开始重新组织 crop-image 中的作物数据...\n")
        
        crops = ['Pepper__bell', 'Potato', 'Tomato', 'Lychee']
        
        for crop in crops:
            print(f"处理作物: {crop}")
            crop_dir = self.base_dir / crop
            
            if not crop_dir.exists():
                print(f"  警告：目录不存在: {crop_dir}")
                print()
                continue
            
            if crop == 'Lychee':
                self.reorganize_lychee(crop_dir)
            else:
                self.reorganize_other_crops(crop_dir)
            
            print()
        
        print("所有作物数据重新组织完成！")
    
    def reorganize_other_crops(self, crop_dir):
        """重新组织甜椒、土豆、番茄（图片直接在文件夹中）"""
        # 获取所有图片文件
        all_images = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG']:
            all_images.extend(list(crop_dir.glob(ext)))
        
        if not all_images:
            print(f"  警告：未找到图片文件")
            return
        
        print(f"  找到 {len(all_images)} 张图片")
        
        # 随机打乱
        random.shuffle(all_images)
        
        # 按比例分配（3:4:3）
        total = len(all_images)
        young_count = int(total * 0.3)
        mature_count = int(total * 0.4)
        senile_count = total - young_count - mature_count
        
        print(f"  分配方案: 幼嫩期={young_count}, 成熟期={mature_count}, 衰老期={senile_count}")
        
        # 创建成熟度子目录
        for maturity in self.maturity_classes:
            (crop_dir / maturity).mkdir(exist_ok=True)
        
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
        
        # 删除原始文件
        for item in crop_dir.iterdir():
            if item.is_file():
                item.unlink()
        
        print(f"  已完成分配")
    
    def reorganize_lychee(self, crop_dir):
        """重新组织荔枝（已有4个子文件夹）"""
        # 创建新的成熟度子目录
        for maturity in self.maturity_classes:
            (crop_dir / maturity).mkdir(exist_ok=True)
        
        total_count = 0
        
        # 遍历荔枝的4个子文件夹
        for src_folder in crop_dir.iterdir():
            if not src_folder.is_dir():
                continue
            
            folder_name = src_folder.name
            if folder_name not in self.lychee_mapping:
                continue
            
            target_maturity = self.lychee_mapping[folder_name]
            target_folder = crop_dir / target_maturity
            
            # 复制文件
            file_count = 0
            for img_file in src_folder.glob('*.jpg'):
                try:
                    shutil.copy(str(img_file), str(target_folder / img_file.name))
                    file_count += 1
                except Exception as e:
                    print(f"    复制失败 {img_file.name}: {e}")
            
            total_count += file_count
            print(f"    {folder_name} → {target_maturity}: {file_count} 张")
            
            # 删除旧文件夹
            shutil.rmtree(src_folder)
        
        print(f"  总计: {total_count} 张图片")

if __name__ == '__main__':
    base_directory = r'E:\crop-maturity-system\crop-image'
    
    reorganizer = CropDataReorganizer(base_directory)
    reorganizer.reorganize_all_crops()