from flask import Flask, render_template, request, jsonify
from pypinyin import pinyin, Style
import re

app = Flask(__name__)

# 常见复姓列表
COMPOUND_SURNAMES = [
  "欧阳", "太史", "端木", "上官", "司马", "东方", "独孤", "南宫", "万俟", "闻人",
  "夏侯", "诸葛", "尉迟", "公羊", "赫连", "澹台", "皇甫", "宗政", "濮阳", "公冶",
  "太叔", "申屠", "公孙", "慕容", "仲孙", "钟离", "长孙", "宇文", "司徒", "鲜于",
  "司空", "闾丘", "子车", "亓官", "司寇", "巫马", "公西", "颛孙", "壤驷", "公良",
  "漆雕", "乐正", "宰父", "谷梁", "拓跋", "夹谷", "轩辕", "令狐", "段干", "百里",
  "呼延", "东郭", "南门", "羊舌", "微生", "公户", "公玉", "公仪", "梁丘", "公仲",
  "公上", "公门", "公山", "公坚", "左丘", "公伯", "西门", "公祖", "第五", "公乘",
  "贯丘", "公皙", "南荣", "东里", "东宫", "仲长", "子书", "子桑", "即墨", "达奚",
  "褚师", "吴铭"
]

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/convert_pinyin', methods=['POST'])
def convert_pinyin():
  data = request.json
  text = data.get('text', '')
  
  # 使用正则表达式分割输入，支持多种分隔符
  names = re.split(r'[,，\s\n]+', text)
  names = [name.strip() for name in names if name.strip()]
  
  def convert_to_pinyin(name):
      # 检查是否有复姓
      surname = next((s for s in COMPOUND_SURNAMES if name.startswith(s)), name[0])
      given_name = name[len(surname):]
      
      # 转换姓氏拼音
      surname_pinyin = ''.join([syllable[0].capitalize() + syllable[1:] for syllable in pinyin(surname, style=Style.NORMAL)])
      
      # 转换名字拼音
      given_name_pinyin = ''.join([syllable[0].capitalize() + syllable[1:] for syllable in pinyin(given_name, style=Style.NORMAL)])
      
      # 组合姓和名，中间加空格
      return f"{surname_pinyin} {given_name_pinyin}".strip()

  result = [convert_to_pinyin(name) for name in names]
  return jsonify({'result': result})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000, debug=False)