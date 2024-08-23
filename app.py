from flask import Flask, render_template, jsonify
import importlib
import os

app = Flask(__name__)

# 动态加载工具
tools = {}
tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
for filename in os.listdir(tools_dir):
    if filename.endswith('.py') and not filename.startswith('__'):
        module_name = filename[:-3]
        module = importlib.import_module(f'tools.{module_name}')
        tool_name = module_name.replace('_', ' ').title()
        tools[tool_name] = getattr(module, 'handle_request')

@app.route('/')
def home():
    return render_template('index.html', tools=tools.keys())

@app.route('/api/<tool_name>', methods=['POST'])
def api_endpoint(tool_name):
    tool_func = tools.get(tool_name.replace(' ', '_').lower())
    if tool_func:
        return tool_func()
    return jsonify({'error': 'Tool not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)