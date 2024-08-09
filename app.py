from flask import Flask, render_template, request, jsonify
from pypinyin import pinyin, Style

app = Flask(__name__)

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/convert_pinyin', methods=['POST'])
def convert_pinyin():
  data = request.json
  text = data.get('text', '')
  names = text.split(',')
  
  def convert_to_pinyin(name):
      name = name.strip()
      # 将姓名分为姓和名
      if len(name) > 1:
          surname = name[0]
          given_name = name[1:]
      else:
          surname = name
          given_name = ""

      # 转换姓
      surname_pinyin = pinyin(surname, style=Style.NORMAL)
      surname_pinyin = ''.join(surname_pinyin[0]).capitalize()

      # 转换名
      given_name_pinyin = pinyin(given_name, style=Style.NORMAL)
      given_name_pinyin = ''.join([''.join(p).capitalize() for p in given_name_pinyin])

      # 组合姓和名，中间加空格
      full_name_pinyin = surname_pinyin + ' ' + given_name_pinyin if given_name else surname_pinyin

      return full_name_pinyin.strip()

  result = [convert_to_pinyin(name) for name in names]
  return jsonify({'result': result})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000, debug=False)