from flask import Flask, request, jsonify
import os
import io
import contextlib
import traceback

app = Flask(__name__)

@app.route('/', methods=['POST'])
def execute():
    auth_header = request.headers.get('Authorization').replace('Bearer ', '')
    if auth_header != os.environ.get('PASSWORD'):
        return jsonify({"error": "Unauthorized"}), 401

    code = request.data.decode('utf-8')
    
    stdout = io.StringIO()
    result = None
    try:
        with contextlib.redirect_stdout(stdout):
            exec(code)
        
        lines = code.strip().split('\n')
        if lines:
            last_line = lines[-1]
            try:
                compile(last_line, '<string>', 'eval')
                result = eval(last_line, {"__builtins__": __builtins__}, locals())
            except:
                pass

    except Exception as e:
        return jsonify({"error": traceback.format_exc()}), 400

    return jsonify({
        "output": stdout.getvalue(),
        "result": result
    })

if __name__ == '__main__':
    app.run()
