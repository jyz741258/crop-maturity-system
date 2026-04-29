import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import warnings
import pandas as pd
import pickle

warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORT_FOLDER'] = 'reports'
app.config['OUTPUT_FOLDER'] = 'output'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('temp', exist_ok=True)

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

try:
    if os.path.exists('models/maturity_model.pkl'):
        maturity_classifier.load_model('models/maturity_model.pkl')
        print("已加载预训练模型")
except Exception as e:
    print(f"模型加载失败: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/batch')
def batch():
    return render_template('batch.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/crops')
def crops():
    return render_template('crops.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/api/analyze_field', methods=['POST'])
def analyze_field():
    try:
        if 'image' not in request.files:
            return jsonify({'error': '未上传图片'}), 400
        
        file = request.files['image']
        crop_type = request.form.get('crop_type', 'tea')
        
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
        
        for det in detections:
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
        
        counts_by_maturity = {}
        for det in detections:
            maturity = det.get('maturity', '未知')
            counts_by_maturity[maturity] = counts_by_maturity.get(maturity, 0) + 1
        
        total_count = len(detections)
        avg_confidence = np.mean([det.get('confidence', 0) for det in detections]) if detections else 0
        avg_green_ratio = np.mean([det.get('green_ratio', 0) for det in detections]) if detections else 0
        
        marked_image = visualizer.draw_maturity_boxes(image, detections)
        result_image_path = os.path.join(app.config['OUTPUT_FOLDER'], f'result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg')
        cv2.imwrite(result_image_path, marked_image)
        
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'total_count': total_count,
            'counts_by_maturity': counts_by_maturity,
            'average_confidence': round(avg_confidence, 2),
            'average_green_ratio': round(avg_green_ratio, 4),
            'marked_image_path': result_image_path,
            'download_url': f'/download_result/{os.path.basename(result_image_path)}',
            'detections': detections,
            'crop_type': crop_type,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze_video', methods=['POST'])
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
def download_result(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    try:
        data = request.get_json()
        results = data.get('results')
        crop_type = data.get('crop_type', 'tea')
        
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