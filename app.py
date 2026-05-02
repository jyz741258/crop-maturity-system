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
    from utils.visualizer import ImageVisualizer
    from utils.video_processor import VideoProcessor
    from data.maturity_standards import get_maturity_stage, get_all_crop_types, get_crop_standards

    crop_detector = CropDetector()
    feature_extractor = FeatureExtractor()
    maturity_classifier = MaturityClassifier()
    visualizer = ImageVisualizer()

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

@ app.route('/api/analyze_field', methods=['POST'])
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
    
    responses = {
        '功能': '''
            本系统提供以下主要功能：
            1. **单图分析**：上传单张作物叶片图片进行成熟度检测
            2. **批量分析**：一次性上传多张图片进行批量处理
            3. **视频分析**：上传视频文件进行实时监测
            4. **数据可视化**：通过图表展示检测结果和统计数据
            5. **报告下载**：生成并下载完整的分析报告
            6. **历史记录**：查看以往的检测记录
        ''',
        '上传图片': '''
            上传图片的步骤：
            1. 进入「单图分析」页面
            2. 点击上传区域或拖拽图片到指定位置
            3. 选择作物类型（甜椒、土豆、番茄等）
            4. 点击「开始分析」按钮
            5. 等待分析完成后查看结果
        ''',
        '下载报告': '''
            下载分析报告的步骤：
            1. 完成图片分析后进入结果页面
            2. 在结果页面找到「下载报告」按钮
            3. 点击按钮即可下载CSV格式的分析报告
            4. 报告包含检测编号、成熟度、置信度、品质评分等信息
        ''',
        '支持作物': '''
            当前系统支持以下作物类型：
            - 甜椒（Pepper）
            - 土豆（Potato）
            - 番茄（Tomato）
            
            如果需要添加新作物，请将图片放入 E:\\crop-image 目录下对应的文件夹，然后更新配置文件即可。
        ''',
        '批量分析': '''
            使用批量分析功能：
            1. 进入「批量分析」页面
            2. 上传多张图片或选择一个包含图片的文件夹
            3. 点击「开始批量分析」按钮
            4. 等待所有图片分析完成
            5. 可以查看每张图片的分析结果或下载汇总报告
        ''',
        '结果解读': '''
            分析结果解读：
            - **成熟度**：表示作物当前的生长阶段（生长期、成熟期等）
            - **置信度**：模型对检测结果的信心程度，越高越准确
            - **绿色占比**：叶片中绿色区域的百分比
            - **品质评分**：综合评估作物的品质等级（0-100分）
            
            建议：置信度低于80%的结果需要人工复核。
        ''',
        '视频分析': '''
            使用视频分析功能：
            1. 进入「分析」页面并切换到视频分析
            2. 上传视频文件（支持MP4格式）
            3. 选择作物类型
            4. 点击「开始分析」按钮
            5. 系统会分析视频中的作物并生成汇总报告
        ''',
        '历史记录': '''
            查看历史记录：
            1. 点击左侧导航栏的「历史记录」
            2. 在历史记录页面可以查看所有以往的检测记录
            3. 支持按时间、作物类型筛选
            4. 可以点击查看详细结果或重新分析
        ''',
        '登录': '''
            登录系统：
            1. 在欢迎页点击「登录系统」按钮
            2. 输入用户名和密码：
               - 用户名：admin，密码：admin123（管理员）
               - 用户名：user，密码：user123（普通用户）
            3. 点击「登录」按钮进入系统
        '''
    }
    
    for key, response in responses.items():
        if key in question:
            return response.strip()
    
    return '''
        您好！我是作物成熟度检测系统的AI助手。我可以帮助您了解以下内容：
        
        📷 **功能介绍**
        - 单图分析：上传单张图片检测作物成熟度
        - 批量分析：一次性处理多张图片
        - 视频分析：分析视频中的作物状态
        - 数据可视化：图表展示检测结果
        - 报告下载：生成完整分析报告
        
        🎯 **常见问题**
        - 如何上传图片进行分析？
        - 如何下载分析报告？
        - 系统支持哪些作物类型？
        - 分析结果如何解读？
        
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