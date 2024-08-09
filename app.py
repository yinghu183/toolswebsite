from flask import Flask, render_template, request, jsonify
from pypinyin import pinyin, Style, lazy_pinyin
import re
import logging

app = Flask(__name__)

# 设置日志
logging.basicConfig(level=logging.DEBUG)

# 常见复姓列表，按长度排序以确保优先匹配更长的复姓
COMPOUND_SURNAMES = sorted([
  "欧阳", "太史", "端木", "上官", "司马", "东方", "独孤", "南宫", "万俟", "闻人",
  "夏侯", "诸葛", "尉迟", "公羊", "赫连", "澹台", "皇甫", "宗政", "濮阳", "公冶",
  "太叔", "申屠", "公孙", "慕容", "仲孙", "钟离", "长孙", "宇文", "司徒", "鲜于",
  "司空", "闾丘", "子车", "亓官", "司寇", "巫马", "公西", "颛孙", "壤驷", "公良",
  "漆雕", "乐正", "宰父", "谷梁", "拓跋", "夹谷", "轩辕", "令狐", "段干", "百里",
  "呼延", "东郭", "南门", "羊舌", "微生", "公户", "公玉", "公仪", "梁丘", "公仲",
  "公上", "公门", "公山", "公坚", "左丘", "公伯", "西门", "公祖", "第五", "公乘",
  "贯丘", "公皙", "南荣", "东里", "东宫", "仲长", "子书", "子桑", "即墨", "达奚",
  "褚师", "吴铭"
], key=len, reverse=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/convert_pinyin', methods=['POST'])
def convert_pinyin():
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        text = data['text']
        logging.debug(f"Received text: {text}")

        # 使用正则表达式分割输入，支持多种分隔符
        names = re.split(r'[,，\s\n]+', text)
        names = [name.strip() for name in names if name.strip()]
        logging.debug(f"Parsed names: {names}")

        result = []
        for name in names:
            if not name:
                result.append("Error: Empty name")
                continue

            try:
                pinyin_name = convert_to_pinyin(name)
                result.append(pinyin_name)
            except Exception as e:
                logging.error(f"Error converting name '{name}': {str(e)}")
                result.append(f"Error converting {name}: {str(e)}")

        logging.debug(f"Conversion result: {result}")
        return jsonify({'result': result})

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

def convert_to_pinyin(name):
    # 检查是否有复姓
    surname = next((s for s in COMPOUND_SURNAMES if name.startswith(s)), name[0])
    given_name = name[len(surname):]

    # 转换姓氏拼音
    surname_pinyin = ''.join([syllable.capitalize() for syllable in lazy_pinyin(surname, style=Style.NORMAL)])

    # 转换名字拼音
    given_name_pinyin = ''.join([syllable.capitalize() for syllable in lazy_pinyin(given_name, style=Style.NORMAL)])

    # 组合姓和名，中间加空格
    return f"{surname_pinyin} {given_name_pinyin}".strip()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
