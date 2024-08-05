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
    words = text.split(',')
    
    def convert_to_pinyin(word):
        pinyin_list = pinyin(word.strip(), style=Style.NORMAL)
        return ' '.join([''.join([syllable.capitalize() for syllable in word]) for word in pinyin_list])

    result = [convert_to_pinyin(word) for word in words]
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
