from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from tools.pinyin_converter import process_names
from tools.irr_calculator import calculate_real_irr
from tools.watermark import add_watermark
from tools.zerox_ocr import process_file
import os
import logging
import uuid
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 设置日志
logging.basicConfig(level=logging.DEBUG)

# 工具列表
TOOLS = [
    {"name": "Pinyin Converter", "display_name": "拼音转换器"},
    {"name": "Irr Calculator", "display_name": "IRR 计算器"},
    {"name": "Image Watermark", "display_name": "图片水印"},
    {"name": "Zerox OCR", "display_name": "文档OCR"}
]

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['MAX_CONTENT_LENGTH'] = 52428800  # 50MB

@app.route('/')
def home():
    return render_template('index.html', tools=TOOLS)

@app.route('/convert_pinyin', methods=['POST'])
def convert_pinyin():
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'error': '未提供文本'}), 400

        text = data['text']
        logging.debug(f"收到拼音转换请求: {text}")

        result = process_names(text)
        return jsonify({'result': result})

    except Exception as e:
        logging.error(f"拼音转换出现意外错误: {str(e)}")
        return jsonify({'error': '发生意外错误'}), 500

@app.route('/calculate_irr', methods=['POST'])
def calculate_irr():
    try:
        data = request.json
        if not data or 'principal' not in data or 'payment' not in data or 'periods' not in data:
            return jsonify({'error': '缺少必要参数'}), 400

        principal = float(data['principal'])
        payment = float(data['payment'])
        periods = int(data['periods'])

        logging.debug(f"收到IRR计算请求: principal={principal}, payment={payment}, periods={periods}")

        result = calculate_real_irr(principal, payment, periods)
        return jsonify({'result': {
            'annual_irr': f"{result['annual_irr']*100:.2f}%",
            'monthly_irr': f"{result['monthly_irr']*100:.2f}%"
        }})

    except ValueError as ve:
        logging.error(f"IRR计算出现值错误: {str(ve)}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging.error(f"IRR计算出现意外错误: {str(e)}")
        return jsonify({'error': '发生意外错误，请检查输入数据'}), 500

@app.route('/add_watermark', methods=['POST'])
def watermark():
    try:
        logging.debug(f"接收到的表单数据: {request.form}")
        logging.debug(f"接收到的文件: {request.files}")
        if 'image' not in request.files:
            return jsonify({'error': '没有上传图片'}), 400
        
        image = request.files['image']
        mark = request.form.get('mark', '')
        color = request.form.get('color', '#000000')
        size = int(request.form.get('size', 50))
        opacity = float(request.form.get('opacity', 0.5))
        angle = int(request.form.get('angle', 30))
        space = int(request.form.get('space', 75))
        
        if not image.filename:
            return jsonify({'error': '没有选择图片'}), 400
        
        image_path = os.path.join('uploads', image.filename)
        image.save(image_path)
        
        font_family = "./font/青鸟华光简琥珀.ttf"  # 确保这个字体文件存在
        
        output_path = add_watermark(image_path, mark, color, font_family, size, opacity, angle, space)
        
        return jsonify({'result': output_path})
    
    except Exception as e:
        logging.error(f"添加水印时出错: {str(e)}")
        return jsonify({'error': '处理图片时出错'}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

@app.route('/zerox_ocr', methods=['GET', 'POST'])
def zerox_ocr():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            # 处理文件
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join('uploads', unique_filename)
            file.save(file_path)
            
            try:
                result = process_file(file_path)
                os.remove(file_path)  # 处理完成后删除文件
                if result is None:
                    return jsonify({'error': 'OCR 处理失败'}), 500
                return jsonify(result)
            except Exception as e:
                os.remove(file_path)  # 发生错误时也删除文件
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': '不支持的文件类型'}), 400
    
    return render_template('zerox_ocr.html')

# 定期清理上传文件的函数（可以通过定时任务调用）
def cleanup_uploads():
    uploads_dir = 'uploads'
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
