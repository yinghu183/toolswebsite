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
        name_parts = name.strip().split()
        pinyin_parts = []
        for part in name_parts:
            pinyin_list = pinyin(part, style=Style.NORMAL)
            pinyin_part = ''.join([syllable[0] for syllable in pinyin_list])
            pinyin_parts.append(pinyin_part)
        return ' '.join(pinyin_parts)

    result = [convert_to_pinyin(name) for name in names]
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)