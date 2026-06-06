# 叶用经济作物成熟度检测系统

基于计算机视觉和深度学习的叶用经济作物成熟度自动检测系统。

## ✨ 功能特性

- **多作物支持**：茶叶、烟叶、桑叶、生菜、菠菜、芹菜
- **4级成熟度检测**：幼嫩期、成熟期、过熟期、衰老期
- **双模式识别**：传统颜色分析 + 深度学习模型
- **丰富可视化**：热力图、标记图片、统计报告
- **智能问答**：基于知识库的农业咨询服务

## 📁 项目结构

```
crop-maturity-system/
├── app.py                      # Flask主应用
├── train_model.py              # 深度学习训练脚本
├── create_demo_model.py        # 演示模型创建
├── models/
│   ├── maturity_detector.py    # 成熟度检测核心
│   └── deep_learning_model.py  # 深度学习模型
├── utils/
│   ├── visualizer.py           # 可视化工具
│   ├── video_processor.py      # 视频处理
│   └── export_utils.py         # 导出工具
├── data/
│   ├── maturity_standards.py   # 成熟度标准
│   └── knowledge_base.py       # 农业知识库
├── templates/                  # 前端模板
├── static/                     # 静态资源
└── crop-image/                 # 数据集
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Flask
- OpenCV
- PyTorch (可选，用于深度学习)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python app.py
```

访问 `http://localhost:5000` 开始使用。

## 📊 数据集结构

```
crop-image/
├── tea/
│   ├── 幼嫩期/
│   ├── 成熟期/
│   ├── 过熟期/
│   └── 衰老期/
├── tobacco/
├── mulberry/
├── lettuce/
├── spinach/
└── celery/
```

## 🤖 深度学习训练

### 训练模型

```bash
python train_model.py --data_dir crop-image/tea --save_path models/leaf_maturity_model.pth --epochs 20
```

### 测试模型

```bash
python train_model.py --test
```

## 📝 使用说明

1. 上传叶片图片或视频
2. 选择对应的作物类型
3. 系统自动检测成熟度
4. 查看可视化结果和统计报告
5. 咨询AI助手获取农业知识

## 🔬 成熟度标准

- **幼嫩期**：叶片嫩绿，叶片柔软
- **成熟期**：叶片翠绿，有韧性，最佳采收期
- **过熟期**：叶片偏黄，开始纤维化
- **衰老期**：叶片枯黄，失去经济价值

## 📄 许可证

本项目仅供学习和研究使用。
