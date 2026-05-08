import os
import re

def clean_non_ascii(file_path):
    """清理文件中的非ASCII字符"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 移除所有非ASCII字符
        clean_content = re.sub(r'[^\x00-\x7F]', '', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(clean_content)
        
        print(f"Cleaned: {file_path}")
        return True
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")
        return False

def main():
    templates_dir = r'E:\crop-maturity-system\templates'
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            file_path = os.path.join(templates_dir, filename)
            clean_non_ascii(file_path)
    
    print("\nAll templates cleaned!")

if __name__ == '__main__':
    main()