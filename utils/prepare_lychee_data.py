import os
import shutil
from pathlib import Path

class LycheeDataPreparer:
    """荔枝数据预处理工具"""
    
    def __init__(self, source_dir, target_dir):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.category_mapping = {
            'Early_Bud': '幼嫩期',
            'Young': '幼嫩期', 
            'Healthy': '成熟期',
            'Senescent_Leaves': '衰老期'
        }
    
    def prepare_data(self):
        """准备荔枝数据"""
        print("开始准备荔枝数据...")
        
        lychee_target = self.target_dir / 'Lychee'
        lychee_target.mkdir(parents=True, exist_ok=True)
        
        # 创建成熟度子目录
        maturity_dirs = ['幼嫩期', '成熟期', '衰老期']
        for m_dir in maturity_dirs:
            (lychee_target / m_dir).mkdir(exist_ok=True)
        
        # 遍历源目录中的子文件夹
        source_lychee = self.source_dir / 'Lychee'
        if not source_lychee.exists():
            print(f"错误：源目录不存在: {source_lychee}")
            return False
        
        for category_folder in source_lychee.iterdir():
            if not category_folder.is_dir():
                continue
            
            category_name = category_folder.name
            if category_name not in self.category_mapping:
                print(f"警告：未知类别 {category_name}，跳过")
                continue
            
            target_maturity = self.category_mapping[category_name]
            target_folder = lychee_target / target_maturity
            
            # 复制文件
            file_count = 0
            for img_file in category_folder.glob('*.jpg'):
                try:
                    shutil.copy(str(img_file), str(target_folder / img_file.name))
                    file_count += 1
                except Exception as e:
                    print(f"复制文件失败 {img_file.name}: {e}")
            
            print(f"已复制 {file_count} 张图片: {category_name} → {target_maturity}")
        
        print("荔枝数据准备完成！")
        return True

if __name__ == '__main__':
    # 使用示例
    source_directory = r'E:\crop-image'
    target_directory = r'E:\crop-image'
    
    preparer = LycheeDataPreparer(source_directory, target_directory)
    preparer.prepare_data()