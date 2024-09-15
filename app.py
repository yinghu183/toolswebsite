from flask import Flask, render_template, request, jsonify, send_file
from tools.pinyin_converter import process_names
from tools.irr_calculator import calculate_real_irr
from tools.watermark import add_watermark
import os
import logging

app = Flask(__name__)

# 设置日志
logging.basicConfig(level=logging.DEBUG)

# 工具列表
TOOLS = [
    {"name": "Pinyin Converter", "display_name": "拼音转换器"},
    {"name": "Irr Calculator", "display_name": "IRR 计算器"},
    {"name": "Image Watermark", "display_name": "图片水印"}
]

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
        if 'image' not in request.files:
            return jsonify({'error': '没有上传图片'}), 400
        
        image = request.files['image']
        mark = request.form.get('mark', '')
        color = request.form.get('color', '#000000')
        size = int(request.form.get('size', 50))
        opacity = float(request.form.get('opacity', 0.5))
        angle = int(request.form.get('angle', 30))
        
        if not image.filename:
            return jsonify({'error': '没有选择图片'}), 400
        
        image_path = os.path.join('uploads', image.filename)
        image.save(image_path)
        
        output_path = add_watermark(image_path, mark, color, size, opacity, angle)
        
        return jsonify({'result': output_path})
    
    except Exception as e:
        logging.error(f"添加水印时出错: {str(e)}")
        return jsonify({'error': '处理图片时出错'}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)