import os

# 英文到中文的映射
translation_map = {
    # 通用
    'Crop Maturity System': '作物成熟度分析系统',
    'Dashboard': '仪表盘',
    'Single Analysis': '单图分析',
    'Batch Analysis': '批量分析',
    'History': '历史记录',
    'Crops': '作物库',
    'Help': '帮助',
    'Search records...': '搜索记录...',
    'Profile': '个人资料',
    'Settings': '系统设置',
    'Help Center': '帮助中心',
    'Logout': '退出登录',
    'Guest': '访客',
    'Admin': '系统管理员',
    'User': '普通用户',
    'Toggle sidebar': '切换侧边栏',
    'Toggle theme': '切换主题',
    
    # 侧边栏
    'Quick Actions': '快捷操作',
    'New Analysis': '新建分析',
    'Video Analysis': '视频分析',
    'Generate Report': '生成报告',
    'AI Assistant': 'AI助手',
    'Region Analysis': '区域分析',
    'Recent Records': '最近检测',
    'View All': '查看全部',
    'Crop Selection': '快速选择作物',
    'Pepper': '甜椒',
    'tea': '茶叶',
    'tobacco': '烟叶',
    'mulberry': '桑叶',
    'lettuce': '生菜',
    'spinach': '菠菜',
    'celery': '芹菜',
    'Today Stats': '今日统计',
    'Detections': '检测次数',
    'Crops': '检测作物',
    'Mature': '成熟率',
    'System Online': '系统运行正常',
    
    # 仪表盘
    'Welcome back! Here is your crop detection overview': '欢迎回来！这是您的作物检测概览',
    'Export Report': '导出报告',
    'Refresh Data': '刷新数据',
    'Total Today': '今日检测总数',
    'Mature Crops': '成熟作物数',
    'Maturity Rate': '整体成熟率',
    'Avg Time(s)': '平均分析时长(秒)',
    'Maturity Distribution': '成熟度分布',
    'Today': '今日',
    'This Week': '本周',
    'This Month': '本月',
    'Detection Trend': '检测趋势',
    '7 Days': '7天',
    '30 Days': '30天',
    '90 Days': '90天',
    'Quality Score': '品质评分分布',
    'Feature Analysis': '特征分析',
    'Recent': '最近',
    'Records': '记录',
    'Crop Distribution': '作物类型分布',
    'completed': '完成',
    
    # 欢迎页
    'Welcome': '欢迎',
    'Page': '页',
    'Based on AI crop maturity detection and analysis platform': '基于人工智能的作物成熟度检测与分析平台',
    'Image Recognition': '图像识别',
    'Data Analysis': '数据分析',
    'Enter System': '进入系统',
    'Usage Help': '使用帮助',
    'Version': '版本',
}

def translate_file(file_path):
    """翻译单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 进行翻译替换
        for en, zh in translation_map.items():
            content = content.replace(en, zh)
        
        # 确保以UTF-8编码保存
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Translated: {file_path}")
        return True
    except Exception as e:
        print(f"Error translating {file_path}: {e}")
        return False

def main():
    templates_dir = r'E:\crop-maturity-system\templates'
    
    # 按特定顺序处理文件，确保翻译一致性
    priority_files = ['navbar.html', 'sidebar.html', 'index.html', 'welcome.html']
    
    # 先处理优先文件
    for filename in priority_files:
        file_path = os.path.join(templates_dir, filename)
        if os.path.exists(file_path):
            translate_file(file_path)
    
    # 处理其他文件
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html') and filename not in priority_files:
            file_path = os.path.join(templates_dir, filename)
            translate_file(file_path)
    
    print("\nAll templates translated to Chinese!")

if __name__ == '__main__':
    main()