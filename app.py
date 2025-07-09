from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, make_response
from werkzeug.middleware.proxy_fix import ProxyFix
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
import threading
import subprocess # 1. 导入 subprocess 模块

app = Flask(__name__)

# 添加 ProxyFix 中间件
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# 配置CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"]
    }
})

# ... (其他中间件和配置保持不变) ...
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    if request.endpoint == 'zerox_ocr' and request.method == 'POST':
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

logging.basicConfig(level=logging.DEBUG)

TOOLS = [
    {"name": "Pinyin Converter", "display_name": "拼音转换器"},
    {"name": "Irr Calculator", "display_name": "IRR 计算器"},
    {"name": "Image Watermark", "display_name": "图片水印"},
    {"name": "Zerox OCR", "display_name": "文档OCR"}
]

# 注意：这个列表现在仅用于文档目的，实际逻辑不再依赖它
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'odt', 'ott', 'rtf', 'txt', 'html', 'htm', 'xml', 'wps', 'wpd', 'xls', 'xlsx', 'ods', 'ots', 'csv', 'tsv', 'ppt', 'pptx', 'odp', 'otp', 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['MAX_CONTENT_LENGTH'] = 52428800

# 2. 新增文件转换的辅助函数
def convert_to_pdf_if_needed(file_path):
    """
    如果文件不是PDF，则使用LibreOffice将其转换为PDF。
    返回最终可用于OCR的PDF文件路径。
    """
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()

    # 如果是图片格式，也进行转换
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    is_office_doc = file_ext not in ['.pdf'] + image_extensions
    is_image = file_ext in image_extensions

    if file_ext == '.pdf':
        app.logger.info(f"File '{file_name}' is already a PDF. No conversion needed.")
        return file_path

    app.logger.info(f"Converting '{file_name}' to PDF...")
    output_dir = os.path.dirname(file_path)
    
    try:
        command = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, file_path]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            app.logger.error(f"LibreOffice conversion failed. Stderr: {result.stderr}")
            raise RuntimeError(f"File conversion to PDF failed: {result.stderr}")
        
        pdf_filename = os.path.splitext(file_name)[0] + '.pdf'
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        if not os.path.exists(pdf_path):
            app.logger.error(f"Conversion command succeeded, but output PDF not found at {pdf_path}")
            raise FileNotFoundError("Converted PDF file not found.")

        app.logger.info(f"Successfully converted to '{os.path.basename(pdf_path)}'.")
        return pdf_path

    except FileNotFoundError:
        app.logger.error("`libreoffice` command not found. Is LibreOffice installed in the environment?")
        raise RuntimeError("File conversion utility is not available on the server.")
    except Exception as e:
        app.logger.error(f"An exception occurred during file conversion: {e}")
        raise

# ... (home, convert_pinyin, calculate_irr, watermark, download_file 等路由保持不变) ...
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
        temp_filename = f"temp_{uuid.uuid4()}_{secure_filename(image.filename)}"
        image_path = os.path.join('uploads', temp_filename)
        image.save(image_path)
        try:
            font_family = "./font/青鸟华光简琥珀.ttf"
            watermarked_filename = add_watermark(image_path, mark, color, font_family, size, opacity, angle, space)
            return jsonify({'result': watermarked_filename})
        finally:
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

output_dir = os.path.join(os.getcwd(), 'output')
if not os.path.exists(output_dir):
    os.makedirs(output_dir, mode=0o777)
else:
    os.chmod(output_dir, 0o777)

# 3. 使用新的转换逻辑重构 zerox_ocr 路由
@app.route('/zerox_ocr', methods=['GET', 'POST', 'OPTIONS'])
def zerox_ocr():
    if request.method == 'OPTIONS':
        return '', 204
    
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
            api_base = "https://api.openai.com/v1"

        if file.filename == '':
            app.logger.error("No selected file")
            return jsonify({'error': '没有选择文件'}), 400

        # 不再使用旧的 allowed_file 检查
        try:
            original_filename = secure_filename(file.filename)
            upload_path = os.path.join('uploads', f"{uuid.uuid4()}_{original_filename}")
            os.makedirs('uploads', exist_ok=True)
            file.save(upload_path)
            
            # 关键改动：调用转换函数
            ocr_ready_file_path = convert_to_pdf_if_needed(upload_path)
            
            output_filename = f"{str(uuid.uuid4()).replace('-', '_')}_{os.path.splitext(original_filename)[0]}.md"
            output_file_path = os.path.join('output', output_filename)
            download_url = url_for('download_markdown', filename=output_filename, _external=True)
            
            def process_ocr():
                try:
                    # 将转换后的PDF文件路径传给OCR函数
                    process_file_sync(ocr_ready_file_path, api_key, api_base, model, output_file_path)
                    app.logger.info(f"OCR result received successfully for {original_filename}")
                except Exception as e:
                    app.logger.error(f"Error in background OCR process: {str(e)}")
                finally:
                    # 清理所有中间文件
                    if os.path.exists(upload_path):
                        os.remove(upload_path)
                    if ocr_ready_file_path != upload_path and os.path.exists(ocr_ready_file_path):
                        os.remove(ocr_ready_file_path)
            
            thread = threading.Thread(target=process_ocr)
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': '文件上传成功，正在转换并处理中...',
                'download_url': download_url
            })

        except Exception as e:
            app.logger.error(f"Error in zerox_ocr: {str(e)}")
            app.logger.error(traceback.format_exc())
            if 'upload_path' in locals() and os.path.exists(upload_path):
                os.remove(upload_path)
            return jsonify({'error': f"处理文件时出错: {str(e)}"}), 500

    return render_template('zerox_ocr.html')


@app.route('/check_ocr_status/<filename>')
def check_ocr_status(filename):
    file_path = os.path.join('output', filename)
    if os.path.exists(file_path):
        return jsonify({
            'status': 'completed',
            'download_url': url_for('download_markdown', filename=filename, _external=True)
        })
    else:
        return jsonify({'status': 'processing'})

@app.route('/download_markdown/<filename>')
def download_markdown(filename):
    try:
        return send_file(
            os.path.join('output', filename),
            as_attachment=True,
            download_name=filename,
            mimetype='text/markdown'
        )
    except Exception as e:
        app.logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': '文件下载失败'}), 404

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