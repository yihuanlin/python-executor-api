from flask import Flask, request, jsonify
import os
import io
import contextlib
import traceback

app = Flask(__name__)

@app.route('/', methods=['POST'])
def execute():
    auth_header = request.headers.get('Authorization')
    if auth_header != os.environ.get('PASSWORD'):
        return jsonify({"error": "Unauthorized"}), 401

    code = request.data.decode('utf-8')
    
    stdout = io.StringIO()
    result = None
    code_locals = {}
    try:
        with contextlib.redirect_stdout(stdout):
            exec(code, globals(), code_locals)
        
        lines = code.strip().split('\n')
        if lines:
            last_line = lines[-1]
            try:
                # To avoid re-executing code that has side effects, 
                # we will only eval if it's a simple expression
                compile(last_line, '<string>', 'eval')
                result = eval(last_line, globals(), code_locals)
            except:
                pass # Ignore if the last line is not an expression

    except Exception as e:
        return jsonify({"error": traceback.format_exc()}), 400

    return jsonify({
        "output": stdout.getvalue(),
        "result": result
    })

if __name__ == '__main__':
    app.run()