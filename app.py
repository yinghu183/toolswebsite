from flask import Flask, render_template, jsonify, request
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
        if hasattr(module, 'handle_request'):
            tool_name = module_name.replace('_', ' ').title()
            tools[tool_name.lower()] = getattr(module, 'handle_request')

print("Loaded tools:", list(tools.keys()))

@app.route('/')
def home():
    return render_template('index.html', tools=tools.keys())

@app.route('/api/<tool_name>', methods=['POST'])
def api_endpoint(tool_name):
    print(f"Received request for tool: {tool_name}")
    print(f"Available tools: {list(tools.keys())}")
    
    tool_func = tools.get(tool_name.lower())
    if tool_func:
        try:
            return tool_func(request)
        except Exception as e:
            print(f"Error executing {tool_name}: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    print(f"Tool not found: {tool_name}")
    return jsonify({'error': 'Tool not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)