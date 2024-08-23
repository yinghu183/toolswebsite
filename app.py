from flask import Flask, render_template, request, jsonify
from tools.pinyin_converter import process_names
from tools.irr_calculator import calculate_real_irr
import logging

app = Flask(__name__)

# 设置日志
logging.basicConfig(level=logging.DEBUG)

# 工具列表
TOOLS = [
  {"name": "Pinyin Converter", "display_name": "拼音转换器"},
  {"name": "Irr Calculator", "display_name": "IRR 计算器"}
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
      return jsonify({'result': result})

  except ValueError as ve:
      logging.error(f"IRR计算出现值错误: {str(ve)}")
      return jsonify({'error': str(ve)}), 400
  except Exception as e:
      logging.error(f"IRR计算出现意外错误: {str(e)}")
      return jsonify({'error': '发生意外错误'}), 500

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000, debug=True)