import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template, send_file, session, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import warnings
import pandas as pd
import pickle
from functools import wraps

warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)
app.secret_key = 'crop_maturity_secret_key_2026'

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORT_FOLDER'] = 'reports'
app.config['OUTPUT_FOLDER'] = 'output'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('temp', exist_ok=True)

try:
    from models.crop_detector import CropDetector
    from models.feature_extractor import FeatureExtractor
    from models.classifier import MaturityClassifier
    from models.maturity_detector import MaturityDetector
    from utils.visualizer import ImageVisualizer
    from utils.video_processor import VideoProcessor
    from utils.export_utils import ExportUtils
    from utils.dashboard_config import DashboardConfig
    from data.maturity_standards import get_maturity_stage, get_all_crop_types, get_crop_standards

    crop_detector = CropDetector()
    feature_extractor = FeatureExtractor()
    maturity_classifier = MaturityClassifier()
    visualizer = ImageVisualizer()
    maturity_detector = MaturityDetector()
    export_utils = ExportUtils()
    dashboard_config = DashboardConfig()

    if os.path.exists('models/maturity_model.pkl'):
        maturity_classifier.load_model('models/maturity_model.pkl')
        print("已加载预训练模型")
except Exception as e:
    print(f"模型加载失败: {e}")

users = {
    'admin': {'password': 'admin123', 'name': '管理员'},
    'user': {'password': 'user123', 'name': '普通用户'}
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['name'] = users[username]['name']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', username=session.get('name'))

@app.route('/analysis')
@login_required
def analysis():
    return render_template('analysis.html', username=session.get('name'))

@app.route('/batch')
@login_required
def batch():
    return render_template('batch.html', username=session.get('name'))

@app.route('/history')
@login_required
def history():
    return render_template('history.html', username=session.get('name'))

@app.route('/crops')
@login_required
def crops():
    return render_template('crops.html', username=session.get('name'))

@app.route('/help')
def help_page():
    return render_template('help.html', username=session.get('name'))

@app.route('/ai')
def ai_assistant():
    return render_template('ai_assistant.html')

@app.route('/region')
@login_required
def region_analysis():
    return render_template('region_analysis.html')

@app.route('/result')
@login_required
def result():
    return render_template('result.html', username=session.get('name'))

def classify_detection_type(bbox, image_shape):
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1
    area = width * height
    image_area = image_shape[0] * image_shape[1]
    
    bbox_aspect_ratio = width / height if height > 0 else 1
    
    if area > image_area * 0.15:
        return 'plant'
    elif 0.7 < bbox_aspect_ratio < 1.5:
        return 'leaf'
    elif bbox_aspect_ratio > 2 or bbox_aspect_ratio < 0.5:
        return 'leaf'
    else:
        return 'leaf'

def analyze_single_crop(image, bbox, crop_type, index):
    x1, y1, x2, y2 = bbox
    crop_roi = image[y1:y2, x1:x2]
    
    if crop_roi.size == 0:
        return None
    
    features = feature_extractor.extract_all_features(crop_roi)
    green_ratio = features.get('green_ratio', 0.5)
    leaf_count = features.get('leaf_count', 1)
    maturity_result = get_maturity_stage(crop_type, green_ratio)
    
    detection_type = classify_detection_type(bbox, image.shape)
    
    return {
        'id': f'DET-{index:03d}',
        'bbox': [int(x1), int(y1), int(x2), int(y2)],
        'detection_type': detection_type,
        'confidence': 0.95,
        'green_ratio': green_ratio,
        'leaf_count': leaf_count,
        'maturity': maturity_result['stage'],
        'quality_score': maturity_result['quality_score'],
        'color_code': maturity_result['color_code'],
        'features': features
    }

@app.route('/api/analyze_region', methods=['POST'])
@login_required
def analyze_region():
    try:
        if 'image' not in request.files:
            return jsonify({'error': '未上传图片'}), 400
        
        file = request.files['image']
        crop_type = request.form.get('crop_type', 'tea')
        grid_size = int(request.form.get('grid_size', 50))
        
        if file.filename == '':
            return jsonify({'error': '未选择图片'}), 400
        
        temp_path = os.path.join('temp', f'temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{secure_filename(file.filename)}')
        file.save(temp_path)
        
        image = cv2.imread(temp_path)
        if image is None:
            os.remove(temp_path)
            return jsonify({'error': '图片读取失败'}), 400
        
        image = cv2.resize(image, (800, 600))
        
        detections = crop_detector.detect_crops(image)
        
        for idx, det in enumerate(detections):
            x1, y1, x2, y2 = det['bbox']
            crop_roi = image[y1:y2, x1:x2]
            
            if crop_roi.size > 0:
                features = feature_extractor.extract_all_features(crop_roi)
                green_ratio = features.get('green_ratio', 0.5)
                maturity_result = get_maturity_stage(crop_type, green_ratio)
                
                det['green_ratio'] = green_ratio
                det['maturity'] = maturity_result['stage']
                det['quality_score'] = maturity_result['quality_score']
                det['color_code'] = maturity_result['color_code']
        
        from utils.heatmap_generator import HeatmapGenerator
        heatmap_gen = HeatmapGenerator()
        
        heatmap_image = heatmap_gen.generate_maturity_heatmap(image, detections, grid_size)
        grid_image = heatmap_gen.draw_region_grid(image, grid_size)
        regions = heatmap_gen._analyze_regions(image, detections, grid_size)
        labeled_image = heatmap_gen.draw_region_labels(heatmap_image, regions)
        
        heatmap_path = os.path.join(app.config['OUTPUT_FOLDER'], f'heatmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
        labeled_path = os.path.join(app.config['OUTPUT_FOLDER'], f'labeled_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
        
        cv2.imwrite(heatmap_path, heatmap_image)
        cv2.imwrite(labeled_path, labeled_image)
        
        analysis_report = heatmap_gen.generate_analysis_report(image, detections)
        
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            **analysis_report,
            'heatmap_image_path': heatmap_path,
            'labeled_image_path': labeled_path,
            'heatmap_download_url': f'/download_result/{os.path.basename(heatmap_path)}',
            'labeled_download_url': f'/download_result/{os.path.basename(labeled_path)}',
            'detections': detections,
            'crop_type': crop_type,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze_field', methods=['POST'])
@login_required
def analyze_field():
    try:
        if 'image' not in request.files:
            return jsonify({'error': '未上传图片'}), 400
        
        file = request.files['image']
        crop_type = request.form.get('crop_type', 'tea')
        analysis_mode = request.form.get('analysis_mode', 'auto')
        
        if file.filename == '':
            return jsonify({'error': '未选择图片'}), 400
        
        temp_path = os.path.join('temp', f'temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{secure_filename(file.filename)}')
        file.save(temp_path)
        
        image = cv2.imread(temp_path)
        if image is None:
            os.remove(temp_path)
            return jsonify({'error': '图片读取失败'}), 400
        
        original_height, original_width = image.shape[:2]
        image = cv2.resize(image, (800, 600))
        
        detections = crop_detector.detect_crops(image)
        
        analyzed_detections = []
        for idx, det in enumerate(detections):
            bbox = det.get('bbox', [0, 0, 100, 100])
            analyzed = analyze_single_crop(image, bbox, crop_type, idx + 1)
            if analyzed:
                analyzed['original_confidence'] = det.get('confidence', 0)
                analyzed_detections.append(analyzed)
        
        if not analyzed_detections:
            center_x, center_y = 400, 300
            default_bbox = [center_x - 100, center_y - 100, center_x + 100, center_y + 100]
            default_det = analyze_single_crop(image, default_bbox, crop_type, 1)
            if default_det:
                analyzed_detections = [default_det]
        
        plant_count = sum(1 for d in analyzed_detections if d['detection_type'] == 'plant')
        leaf_count = sum(1 for d in analyzed_detections if d['detection_type'] == 'leaf')
        total_leaves_detected = sum(d.get('leaf_count', 1) for d in analyzed_detections)
        
        counts_by_maturity = {}
        for det in analyzed_detections:
            maturity = det.get('maturity', '未知')
            counts_by_maturity[maturity] = counts_by_maturity.get(maturity, 0) + 1
        
        total_count = len(analyzed_detections)
        avg_confidence = np.mean([det.get('confidence', 0) for det in analyzed_detections]) if analyzed_detections else 0
        avg_green_ratio = np.mean([det.get('green_ratio', 0) for det in analyzed_detections]) if analyzed_detections else 0
        avg_quality_score = np.mean([det.get('quality_score', 0) for det in analyzed_detections]) if analyzed_detections else 0
        
        marked_image = visualizer.draw_maturity_boxes_with_stats(image, analyzed_detections)
        result_image_path = os.path.join(app.config['OUTPUT_FOLDER'], f'result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
        cv2.imwrite(result_image_path, marked_image)
        
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'total_count': total_count,
            'plant_count': plant_count,
            'leaf_count': leaf_count,
            'total_leaves_detected': total_leaves_detected,
            'counts_by_maturity': counts_by_maturity,
            'average_confidence': round(avg_confidence, 2),
            'average_green_ratio': round(avg_green_ratio, 4),
            'average_quality_score': round(avg_quality_score, 2),
            'marked_image_path': result_image_path,
            'download_url': f'/download_result/{os.path.basename(result_image_path)}',
            'detections': analyzed_detections,
            'crop_type': crop_type,
            'analysis_mode': analysis_mode,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'image_dimensions': {'width': original_width, 'height': original_height}
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze_video', methods=['POST'])
@login_required
def analyze_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': '未上传视频'}), 400
        
        file = request.files['video']
        crop_type = request.form.get('crop_type', 'tea')
        
        if file.filename == '':
            return jsonify({'error': '未选择视频'}), 400
        
        temp_path = os.path.join('temp', f'temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{secure_filename(file.filename)}')
        file.save(temp_path)
        
        processor = VideoProcessor(crop_type=crop_type)
        result = processor.analyze_video_summary(temp_path)
        
        os.remove(temp_path)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'crop_type': crop_type,
            **result,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process_video', methods=['POST'])
@login_required
def process_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': '未上传视频'}), 400
        
        file = request.files['video']
        crop_type = request.form.get('crop_type', 'tea')
        
        if file.filename == '':
            return jsonify({'error': '未选择视频'}), 400
        
        input_path = os.path.join('temp', f'input_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{secure_filename(file.filename)}')
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4')
        file.save(input_path)
        
        processor = VideoProcessor(crop_type=crop_type)
        result = processor.process_video(input_path, output_path)
        
        os.remove(input_path)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'crop_type': crop_type,
            'output_video_path': output_path,
            'download_url': f'/download_result/{os.path.basename(output_path)}',
            **result,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crop_types', methods=['GET'])
def get_crop_types_api():
    return jsonify({
        'crop_types': get_all_crop_types(),
        'standards': {crop: get_crop_standards(crop) for crop in get_all_crop_types()}
    })

@app.route('/api/maturity_standards', methods=['GET'])
def get_maturity_standards_api():
    crop_type = request.args.get('crop_type', 'tea')
    return jsonify(get_crop_standards(crop_type))

@app.route('/download_result/<filename>')
@login_required
def download_result(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    try:
        print("\n=== API generate_report called ===")
        print(f"Session: {dict(session)}")
        print(f"Session username: {session.get('username')}")
        print(f"Request method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Request headers: {dict(request.headers)}")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if data is None:
            print("ERROR: Data is None")
            return jsonify({'error': '请求数据为空或格式错误'}), 400
            
        results = data.get('results')
        crop_type = data.get('crop_type', 'tea')
        
        print(f"Results: {results}")
        print(f"Crop type: {crop_type}")
        
        if not results:
            return jsonify({'error': '无分析结果'}), 400
        
        report_data = []
        for r in results:
            report_data.append({
                '检测编号': r.get('id', ''),
                '成熟度': r.get('maturity', ''),
                '置信度(%)': r.get('confidence', 0),
                '绿色占比(%)': round(r.get('green_ratio', 0) * 100, 2),
                '品质评分': r.get('quality_score', 0),
                '边界框': str(r.get('bbox', []))
            })
        
        df = pd.DataFrame(report_data)
        report_path = os.path.join(app.config['REPORT_FOLDER'], f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        df.to_csv(report_path, index=False, encoding='utf-8-sig')
        
        total_count = len(results)
        counts_by_maturity = {}
        for r in results:
            maturity = r.get('maturity', '未知')
            counts_by_maturity[maturity] = counts_by_maturity.get(maturity, 0) + 1
        
        return jsonify({
            'success': True,
            'report_path': report_path,
            'download_url': f'/download_report/{os.path.basename(report_path)}',
            'summary': {
                'total_count': total_count,
                'counts_by_maturity': counts_by_maturity,
                'crop_type': crop_type
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_report/<filename>')
def download_report(filename):
    return send_file(os.path.join(app.config['REPORT_FOLDER'], filename), as_attachment=True)

def get_ai_response(question):
    question = question.lower().strip()
    
    keyword_mappings = {
        '功能': ['功能', '作用', '能做什么', '有什么用', '介绍', '功能介绍'],
        '上传图片': ['上传图片', '上传', '图片上传', '怎么上传', '如何上传'],
        '下载报告': ['下载报告', '报告下载', '导出报告', '下载', '导出'],
        '支持作物': ['支持作物', '作物类型', '有哪些作物', '作物种类'],
        '批量分析': ['批量分析', '批量处理', '批量上传'],
        '结果解读': ['结果解读', '如何解读', '怎么看结果', '结果分析'],
        '视频分析': ['视频分析', '视频检测', '视频上传'],
        '历史记录': ['历史记录', '历史', '记录', '查看记录'],
        '登录': ['登录', '账号', '密码', '登录系统'],
        '仪表盘': ['仪表盘', 'dashboard', '首页'],
        '成熟度标准': ['成熟度标准', '成熟度判定', '判定标准', '成熟度分级', '分级标准'],
        '帮助': ['帮助', '帮助中心', '使用说明', '使用指南'],
        '快捷键': ['快捷键', '快捷方式', '键盘操作']
    }
    
    responses = {
        '功能': '''
            本系统提供以下主要功能：

            📷 图片分析
            - 单图分析：上传单张作物叶片图片进行成熟度检测 [跳转:分析页面]
            - 批量分析：一次性上传多张图片进行批量处理 [跳转:批量分析]

            🎬 视频分析
            - 视频检测：上传视频文件进行实时监测 [跳转:分析页面]
            - 帧分析：对视频每一帧进行作物检测和成熟度判断

            📊 数据可视化
            - 仪表盘：展示检测统计图表 [跳转:仪表盘]
            - 成熟度分布：饼图、折线图、雷达图展示

            📝 报告管理
            - 报告下载：生成并下载CSV格式的分析报告
            - 历史记录：查看和管理以往的检测记录 [跳转:历史记录]

            🌱 作物管理
            - 作物库：管理支持的作物类型 [跳转:作物库]
            - 标准维护：查看成熟度判定标准
        ''',
        '上传图片': '''
            上传图片进行分析的步骤：

            1. 进入分析页面
               - 登录系统后，点击左侧导航栏的「分析」，进入[跳转:分析页面]分析页面[/跳转]

            2. 上传图片
               - 点击上传区域，或拖拽图片到指定位置
               - 支持格式：JPG、PNG、BMP、GIF

            3. 选择作物类型
               - 从下拉菜单中选择对应的作物类型
               - 当前支持：生菜、菠菜、芹菜、茶叶、烟叶、桑叶

            4. 开始分析
               - 点击「开始分析」按钮
               - 等待几秒后显示分析结果

            5. 查看结果
               - 页面会显示标注后的图片
               - 包含成熟度统计和品质评分
        ''',
        '下载报告': '''
            下载分析报告的步骤：

            1. 完成分析
               - 在[跳转:分析页面]单图分析[/跳转]或[跳转:批量分析]批量分析[/跳转]页面完成图片分析

            2. 进入结果页面
               - 分析完成后会自动跳转到结果页面

            3. 下载报告
               - 点击「下载报告」按钮
               - 系统生成CSV格式报告并自动下载

            📋 报告内容
            - 检测编号：唯一标识
            - 成熟度：作物成熟阶段
            - 置信度：检测置信度百分比
            - 绿色占比：叶片绿色比例
            - 品质评分：综合品质评分（0-100分）
            - 边界框：检测目标位置

            📁 批量报告
            - [跳转:批量分析]批量分析[/跳转]完成后可下载汇总报告
            - 包含所有图片的分析结果
        ''',
        '支持作物': '''
            当前系统支持以下6种叶用经济作物：

            🥬 蔬菜类
            - 生菜（Lettuce）：GB/T 18407.1-2001标准
            - 菠菜（Spinach）：NY/T 5008-2016标准
            - 芹菜（Celery）：NY/T 5008-2016标准

            🌿 经济作物类
            - 茶叶（Tea）：GB/T 23776-2018标准
            - 烟叶（Tobacco）：GB 2635-2018标准
            - 桑叶（Mulberry）：NY/T 1187-2006标准

            ➕ 添加新作物
            1. 在 E:\\crop-image 目录下创建以作物名称命名的文件夹
            2. 将作物图片放入该文件夹
            3. 更新 config.py 中的 CLASSES 列表
            4. 在 data/maturity_standards.py 中添加成熟度判定标准
        ''',
        '批量分析': '''
            使用批量分析功能：

            1. 进入批量分析页面
               - 点击左侧导航栏的「批量分析」，进入[跳转:批量分析]批量分析页面[/跳转]

            2. 上传图片
               - 点击上传区域选择多张图片
               - 或拖拽整个文件夹到上传区域

            3. 选择作物类型
               - 选择要分析的作物类型

            4. 开始分析
               - 点击「开始批量分析」按钮
               - 等待所有图片分析完成

            5. 查看结果
               - 每张图片显示分析结果缩略图
               - 可点击查看详细分析报告

            6. 下载汇总报告
               - 点击「下载汇总报告」按钮
               - 获取所有图片的分析结果CSV文件

            ⚡ 提示
            - 建议每次批量分析不超过50张图片
            - 图片大小建议控制在2MB以内
        ''',
        '结果解读': '''
            分析结果解读：

            📊 核心指标
            - 成熟度：作物当前的生长阶段
              - 🌱 幼嫩期：叶片尚小，颜色浅绿
              - 🌿 成熟期：叶片充分展开，颜色深绿（最佳采收期）
              - 🍂 过熟期：叶片开始老化，颜色变浅
              - 🥀 衰老期：叶片黄化、干枯

            - 置信度：模型对检测结果的信心程度
              - ≥90%：非常可靠
              - 70%-90%：较可靠
              - <70%：建议人工复核

            - 绿色占比：叶片中绿色区域的百分比
              - 反映叶片的健康程度

            - 品质评分：综合评估作物品质（0-100分）
              - ≥90分：优质
              - 70-89分：良好
              - <70分：较差

            🏷️ 图片标记
            - 不同颜色框表示不同成熟度
            - 绿色：成熟期
            - 橙色：幼嫩期
            - 黄色：过熟期
            - 灰色：衰老期

            📈 统计面板
            - 右上角显示检测统计
            - 包含整株作物数、单叶数、总叶片数
        ''',
        '视频分析': '''
            使用视频分析功能：

            1. 进入视频分析页面
               - 在[跳转:分析页面]分析页面[/跳转]切换到「视频分析」标签

            2. 上传视频
               - 点击上传区域选择视频文件
               - 支持格式：MP4（推荐）

            3. 选择作物类型
               - 选择视频中作物的类型

            4. 开始分析
               - 点击「开始分析」按钮
               - 系统会逐帧分析视频中的作物

            5. 查看结果
               - 生成带标记的输出视频
               - 显示视频分析摘要报告

            📊 分析内容
            - 每帧检测到的作物数量
            - 不同成熟度的分布统计
            - 平均置信度和品质评分

            ⚡ 提示
            - 建议视频时长不超过5分钟
            - 分辨率建议1080p以下
            - 分析时间约为视频时长的2-3倍
        ''',
        '历史记录': '''
            查看和管理历史记录：

            1. 进入历史记录页面
               - 点击左侧导航栏的「历史记录」，进入[跳转:历史记录]历史记录页面[/跳转]

            2. 浏览记录
               - 按时间顺序显示所有检测记录
               - 包含检测时间、作物类型、检测数量

            3. 筛选记录
               - 支持按时间范围筛选
               - 支持按作物类型筛选

            4. 操作记录
               - 👁️ 查看：查看详细分析结果
               - 📥 下载：下载单条记录的报告
               - 🗑️ 删除：删除选中的记录

            5. 分页导航
               - 使用分页按钮浏览多页记录
               - 每页显示10条记录

            💾 数据存储
            - 历史记录保存在本地数据库
            - 分析结果图片保存在本地文件系统
            - 建议定期备份数据
        ''',
        '登录': '''
            登录系统：

            1. 访问欢迎页
               - 打开浏览器访问 http://localhost:5000

            2. 点击登录
               - 点击「登录系统」按钮

            3. 输入账号
               - 用户名：admin | 密码：admin123（管理员）
               - 用户名：user | 密码：user123（普通用户）

            4. 登录成功
               - 自动跳转到[跳转:仪表盘]仪表盘[/跳转]页面

            🔒 权限说明
            - 管理员：完整功能访问权限
            - 普通用户：部分功能受限

            🚪 退出登录
            - 点击右上角用户头像
            - 选择「退出登录」
        ''',
        '仪表盘': '''
            仪表盘功能介绍：

            📊 核心统计
            - 今日检测总数
            - 成熟作物数量
            - 幼嫩作物数量
            - 成熟率统计

            📈 数据图表
            - 成熟度分布饼图
            - 检测趋势折线图
            - 特征对比雷达图
            - 品质评分柱状图

            🔄 操作功能
            - 刷新数据：重新加载统计数据
            - 导出报告：下载仪表盘数据CSV

            ⚡ 实时更新
            - 数据每5分钟自动刷新
            - 可手动点击刷新按钮

            📱 响应式设计
            - 支持桌面端和移动端
            - 自适应布局
        ''',
        '成熟度标准': '''
            成熟度判定标准参考权威农业标准：

            📚 参考标准
            - GB/T 23776-2018 茶叶感官审评方法
            - GB 2635-2018 烤烟
            - NY/T 1187-2006 桑树栽培技术规程
            - GB/T 18407.1-2001 无公害蔬菜安全要求
            - NY/T 5008-2016 无公害食品 绿叶蔬菜类

            🎯 判定依据
            - 绿色占比：叶片中绿色区域的百分比
            - 叶片大小：叶片长度或植株直径
            - 颜色特征：颜色深浅和均匀度

            🏷️ 分级标准
            - 幼嫩期：绿色占比较高，叶片尚小，颜色浅绿，建议继续生长
            - 成熟期：绿色占比适中，叶片充分展开，颜色深绿，最佳采收期
            - 过熟期：绿色占比较低，叶片开始老化，颜色变浅，尽快采收
            - 衰老期：绿色占比很低，叶片黄化、干枯，无采收价值
        ''',
        '帮助': '''
            系统帮助与支持：

            📖 快速入门
            1. 登录系统
            2. 进入分析页面
            3. 上传作物图片
            4. 选择作物类型
            5. 点击开始分析
            6. 查看分析结果
            7. 下载分析报告

            💡 使用技巧
            - 上传清晰的作物图片
            - 确保叶片占据画面主要部分
            - 避免强烈反光和阴影
            - 批量分析时控制图片数量

            📞 问题反馈
            - 遇到问题请查看控制台错误信息
            - 可联系系统管理员获取帮助

            🔧 系统要求
            - 浏览器：Chrome、Firefox、Edge
            - 网络：稳定的网络连接
            - 硬件：建议配置较高的GPU（视频分析）
        ''',
        '快捷键': '''
            系统快捷键：

            ⌨️ 全局快捷键
            - Ctrl + S：保存当前页面
            - Ctrl + R：刷新页面
            - Ctrl + F：页面搜索

            📱 导航快捷键
            - 1：跳转到仪表盘
            - 2：跳转到分析页面
            - 3：跳转到批量分析
            - 4：跳转到历史记录
            - 5：跳转到作物库
            - 6：跳转到帮助页面

            💡 分析快捷键
            - Enter：确认操作
            - Esc：取消操作
            - Space：暂停/继续视频

            ⚡ 提示
            - 快捷键在登录后生效
            - 部分快捷键需聚焦对应区域
        '''
    }
    
    for key, keywords in keyword_mappings.items():
        for keyword in keywords:
            if keyword in question:
                return responses.get(key, responses['功能']).strip()
    
    return '''
        您好！我是作物成熟度检测系统的AI助手。我可以帮助您了解以下内容：
        
        📷 **功能介绍**
        - 单图分析：上传单张图片检测作物成熟度
        - 批量分析：一次性处理多张图片
        - 视频分析：分析视频中的作物状态
        - 仪表盘：查看检测统计图表
        - 历史记录：管理检测记录
        - 作物库：查看支持的作物类型
        
        🎯 **常见问题**
        - 如何上传图片进行分析？
        - 如何下载分析报告？
        - 系统支持哪些作物类型？
        - 分析结果如何解读？
        - 成熟度判定标准是什么？
        
        📚 **帮助主题**
        - 登录与权限
        - 操作指南
        - 快捷键
        - 系统要求
        
        请问您想了解哪方面的内容？
    '''.strip()

@app.route('/api/ai/ask', methods=['POST'])
def ai_ask():
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        answer = get_ai_response(question)
        
        return jsonify({
            'success': True,
            'answer': answer,
            'question': question
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze_maturity', methods=['POST'])
@login_required
def analyze_maturity():
    try:
        if 'image' not in request.files:
            return jsonify({'error': '未上传图片'}), 400
        
        file = request.files['image']
        crop_type = request.form.get('crop_type', 'Tomato')
        
        if file.filename == '':
            return jsonify({'error': '未选择图片'}), 400
        
        temp_path = os.path.join('temp', f'temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{secure_filename(file.filename)}')
        file.save(temp_path)
        
        results = maturity_detector.detect_crops(temp_path)
        
        for res in results:
            res['crop_type'] = crop_type
        
        summary = export_utils.generate_summary(results)
        
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'detections': results,
            'summary': summary,
            'crop_type': crop_type,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export_data', methods=['POST'])
@login_required
def export_data():
    try:
        data = request.get_json()
        export_format = data.get('format', 'csv')
        analysis_data = data.get('data', [])
        
        if not analysis_data:
            return jsonify({'error': '无数据可导出'}), 400
        
        file_path = None
        
        if export_format == 'csv':
            file_path = export_utils.export_to_csv(analysis_data)
        elif export_format == 'excel':
            file_path = export_utils.export_to_excel(analysis_data)
        elif export_format == 'pdf':
            file_path = export_utils.export_to_pdf(analysis_data)
        elif export_format == 'json':
            file_path = export_utils.export_as_json(analysis_data)
        
        if not file_path:
            return jsonify({'error': '导出失败'}), 500
        
        return jsonify({
            'success': True,
            'file_path': file_path,
            'download_url': f'/download_export/{os.path.basename(file_path)}',
            'format': export_format
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_export/<filename>')
@login_required
def download_export(filename):
    return send_file(os.path.join('exports', filename), as_attachment=True)

@app.route('/api/dashboard/config', methods=['GET', 'POST'])
@login_required
def dashboard_config_api():
    if request.method == 'GET':
        return jsonify(dashboard_config.to_dict())
    
    try:
        data = request.get_json()
        dashboard_config.update_config(data)
        return jsonify({'success': True, 'config': dashboard_config.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/toggle_chart', methods=['POST'])
@login_required
def toggle_chart():
    try:
        data = request.get_json()
        chart_id = data.get('chart_id')
        
        if dashboard_config.toggle_chart(chart_id):
            return jsonify({'success': True, 'chart_id': chart_id, 'visible': True})
        return jsonify({'error': '图表不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/toggle_stat', methods=['POST'])
@login_required
def toggle_stat():
    try:
        data = request.get_json()
        stat_id = data.get('stat_id')
        
        if dashboard_config.toggle_stat_card(stat_id):
            return jsonify({'success': True, 'stat_id': stat_id})
        return jsonify({'error': '统计项不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/reset', methods=['POST'])
@login_required
def reset_dashboard_config():
    try:
        dashboard_config.reset_to_default()
        return jsonify({'success': True, 'config': dashboard_config.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        from pyngrok import ngrok
        
        public_url = ngrok.connect(5000).public_url
        print(f"🌐 内网穿透已启动！")
        print(f"📡 公网访问地址: {public_url}")
        print(f"🔗 本地访问地址: http://localhost:5000")
        
    except Exception as e:
        print(f"⚠️ 内网穿透启动失败: {e}")
        print(f"🔗 本地访问地址: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)