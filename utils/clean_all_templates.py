import os

templates_dir = r'E:\crop-maturity-system\templates'

def clean_html_content(content):
    content = content.replace('?/p>', '</p>')
    content = content.replace('?/span>', '</span>')
    content = content.replace('?/h3>', '</h3>')
    content = content.replace('?/div>', '</div>')
    content = content.replace('?/th>', '</th>')
    content = content.replace('?/h4>', '</h4>')
    content = content.replace('?/td>', '</td>')
    content = content.replace('?42', '')
    content = content.replace('/?/', '/')
    content = content.replace('<!DOCTYPE html>', '<!DOCTYPE html>\n')
    return content

for filename in os.listdir(templates_dir):
    if filename.endswith('.html'):
        file_path = os.path.join(templates_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content = clean_html_content(content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Cleaned: {filename}")
        except Exception as e:
            print(f"Error cleaning {filename}: {e}")

print("\nAll templates cleaned!")