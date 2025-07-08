import os
import asyncio
from flask import Flask, render_template, request, send_from_directory, jsonify, url_for
from werkzeug.utils import secure_filename
from tools.pinyin_converter import convert_to_pinyin
from tools.irr_calculator import calculate_irr_api
from tools.watermark import add_watermark_to_image
from tools.zerox_ocr import process_document

app = Flask(__name__)

# 配置上传文件的存储位置和允许的文件类型
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # 工具列表
    tools = [
        {"name": "中文姓名转拼音", "url": url_for('pinyin_converter')},
        {"name": "信用卡分期IRR计算", "url": url_for('irr_calculator_page')},
        {"name": "图片加水印", "url": url_for('image_watermark_page')},
        {"name": "文档OCR", "url": url_for('zerox_ocr_page')}
    ]
    ai_tools = [
        {"name": "作文润色", "url": "https://yashe.pro/work_page/polish"},
        {"name": "英语词典", "url": "https://yashe.pro/work_page/dict"},
        {"name": "多语言翻译", "url": "https://yashe.pro/work_page/translate"}
    ]
    external_links = [
        {"name": "即时工具", "url": "https://www.123apps.net/cn/"},
        {"name": "Aisell", "url": "https://aisell.co/"},
        {"name": "AI工具集", "url": "https://ai-bot.cn/"},
        {"name": "AI导航", "url": "https://www.ainav.cn/"}
    ]
    return render_template('index.html', tools=tools, ai_tools=ai_tools, external_links=external_links)

@app.route('/pinyin', methods=['GET', 'POST'])
def pinyin_converter():
    pinyin_result = ""
    if request.method == 'POST':
        names = request.form.get('names')
        if names:
            pinyin_result = convert_to_pinyin(names)
    return render_template('pinyin_converter.html', pinyin_result=pinyin_result)

@app.route('/irr_calculator', methods=['GET', 'POST'])
def irr_calculator_page():
    result = None
    if request.method == 'POST':
        data = request.form
        principal = float(data.get('principal'))
        monthly_payment = float(data.get('monthly_payment'))
        periods = int(data.get('periods'))
        fee = float(data.get('fee', 0))
        result = calculate_irr_api(principal, monthly_payment, periods, fee)
    return render_template('irr_calculator.html', result=result)

@app.route('/image_watermark', methods=['GET'])
def image_watermark_page():
    return render_template('image_watermark.html')

@app.route('/image_watermark/process', methods=['POST'])
def image_watermark_process():
    if 'image' not in request.files:
        return jsonify({"error": "没有文件部分"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "没有选择文件"}), 400
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)

            watermark_text = request.form.get('watermark_text', 'Default Watermark')
            output_filename = 'watermarked_' + filename
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            add_watermark_to_image(input_path, output_path, watermark_text)

            return jsonify({"url": url_for('uploaded_file', filename=output_filename)})
        except Exception as e:
            return jsonify({"error": f"处理图像时出错: {str(e)}"}), 500
    return jsonify({"error": "文件类型不允许"}), 400

@app.route('/zerox_ocr', methods=['GET'])
def zerox_ocr_page():
    return render_template('zerox_ocr.html')

@app.route('/zerox_ocr/process', methods=['POST'])
def zerox_ocr_process():
    if 'document' not in request.files:
        return jsonify({"error": "请求中没有找到文件部分"}), 400
    file = request.files['document']
    if file.filename == '':
        return jsonify({"error": "没有选择要上传的文件"}), 400

    api_key = request.form.get('apiKey')
    if not api_key:
        return jsonify({"error": "API Key 是必需的"}), 400
        
    model = request.form.get('model', 'gpt-4o') # 默认使用 gpt-4o

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # 调用异步函数
            result = asyncio.run(process_document(file_path, api_key, model))
            
            # 清理上传的文件
            os.remove(file_path)

            # 将 ZeroxOutput 对象转换为字典以便序列化
            pages_content = [page.content for page in result.pages]
            markdown_content = "\n\n---\n\n".join(pages_content)
            
            return jsonify({
                "markdown": markdown_content,
                "fileName": result.file_name,
                "totalPages": len(result.pages),
                "completionTime": result.completion_time
            })

        except Exception as e:
            # 关键修正：当发生任何错误时，都返回一个 JSON 对象
            app.logger.error(f"OCR 处理失败: {str(e)}") # 在服务器后台记录详细错误
            return jsonify({"error": f"处理文件时出错，请检查API Key或文件格式。服务器日志: {str(e)}"}), 500

    return jsonify({"error": "不允许的文件类型"}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)