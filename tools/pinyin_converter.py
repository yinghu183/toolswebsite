from flask import request, jsonify
from pypinyin import pinyin, Style

def handle_request(request):
    try:
        data = request.json
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        result = pinyin(text, style=Style.NORMAL)
        pinyin_result = ' '.join([item[0] for item in result])

        return jsonify({'result': pinyin_result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400