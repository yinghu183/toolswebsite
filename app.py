from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from tools.pinyin_converter import process_names
from tools.irr_calculator import calculate_real_irr
from tools.watermark import add_watermark
from tools.zerox_ocr import process_file_sync
import os
import logging
import uuid
import shutil
from werkzeug.utils import secure_filename
import asyncio
import traceback
from pyzerox.core.types import ZeroxOutput
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 设置日志
logging.basicConfig(level=logging.DEBUG)

# 工具列表
TOOLS = [
    {"name": "Pinyin Converter", "display_name": "拼音转换器"},
    {"name": "Irr Calculator", "display_name": "IRR 计算器"},
    {"name": "Image Watermark", "display_name": "图片水印"},
    {"name": "Zerox OCR", "display_name": "文档OCR"}
]

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'odt', 'ott', 'rtf', 'txt', 'html', 'htm', 'xml', 'wps', 'wpd', 'xls', 'xlsx', 'ods', 'ots', 'csv', 'tsv', 'ppt', 'pptx', 'odp', 'otp'}

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
        
        # 生成唯一的临时文件名
        temp_filename = f"temp_{uuid.uuid4()}_{secure_filename(image.filename)}"
        image_path = os.path.join('uploads', temp_filename)
        image.save(image_path)
        
        try:
            font_family = "./font/青鸟华光简琥珀.ttf"
            watermarked_filename = add_watermark(image_path, mark, color, font_family, size, opacity, angle, space)
            
            # 返回处理后的文件名，用于下载
            return jsonify({'result': watermarked_filename})
        finally:
            # 删除原始临时文件
            if os.path.exists(image_path):
                os.remove(image_path)
    
    except Exception as e:
        logging.error(f"添加水印时出错: {str(e)}")
        return jsonify({'error': '处理图片时出错'}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        file_path = os.path.join('uploads', filename)
        response = send_file(file_path, as_attachment=True)
        
        # 在发送文件后安排删除任务
        @response.call_on_close
        def delete_file():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logging.debug(f"已删除文件: {file_path}")
            except Exception as e:
                logging.error(f"删除文件时出错: {str(e)}")
        
        return response
    except Exception as e:
        logging.error(f"下载文件时出错: {str(e)}")
        return "文件下载失败", 404

@app.route('/zerox_ocr', methods=['GET', 'POST'])
def zerox_ocr():
    if request.method == 'POST':
        if 'file' not in request.files:
            app.logger.error("No file part in the request")
            return jsonify({'error': '没有上传文件'}), 400

        file = request.files['file']
        api_key = request.form.get('apiKey')
        api_base = request.form.get('apiBase')
        model = request.form.get('model')

        if not api_key or not model:
            return jsonify({'error': 'API Key 和模型为必填项'}), 400
        if not api_base:
            api_base = "https://api.openai.com/v1"  # 可设为默认

        app.logger.info(f"Received file: {file.filename}")

        if file.filename == '':
            app.logger.error("No selected file")
            return jsonify({'error': '没有选择文件'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join('uploads', unique_filename)
            file.save(file_path)
            app.logger.info(f"Processing file: {file_path}")

            try:
                result = process_file_sync(file_path, api_key, api_base, model)
                app.logger.info(f"OCR result received successfully")

                # 处理completion_time
                completion_time = float(result.completion_time)
                if completion_time > 1000:
                    completion_time = completion_time / 1000

                # 构建markdown内容
                try:
                    markdown_content = f"# OCR 结果\n\n"
                    markdown_content += f"文件名: {result.file_name}\n"
                    markdown_content += f"处理时间: {completion_time:.2f} 秒\n"
                    markdown_content += f"输入 tokens: {result.input_tokens}\n"
                    markdown_content += f"输出 tokens: {result.output_tokens}\n\n"

                    for page in result.pages:
                        markdown_content += f"## 第 {page.page} 页\n\n"
                        markdown_content += page.content + "\n\n"

                    # 确保markdown_content是有效的字符串
                    markdown_content = markdown_content.replace('\x00', '')  # 移除空字符
                    
                    app.logger.info("Markdown content generated successfully")
                    return jsonify({'markdown': markdown_content}), 200

                except Exception as e:
                    app.logger.error(f"Error generating markdown content: {str(e)}")
                    app.logger.error(traceback.format_exc())
                    return jsonify({'error': f"生成markdown内容时出错 - {str(e)}"}), 500

            except Exception as e:
                app.logger.error(f"Error in zerox_ocr: {str(e)}")
                app.logger.error(traceback.format_exc())
                return jsonify({'error': f"处理文件时出错 - {str(e)}"}), 500
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            app.logger.error(f"Invalid file type: {file.filename}")
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

@app.route('/image_watermark')
def image_watermark():
    return render_template('image_watermark.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
