import json
import os
import io
import contextlib
import traceback

def app(environ, start_response):
    headers = {}
    for key, value in environ.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].replace('_', '-').title()
            headers[header_name] = value

    auth_header = headers.get('Authorization')
    password = os.environ.get('PASSWORD')
    if not password or auth_header != f"Bearer {password}":
        status = '401 Unauthorized'
        headers = [('Content-type', 'application/json')]
        start_response(status, headers)
        return [json.dumps({'error': 'Unauthorized'}).encode()]

    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        content_length = 0

    code_to_run = environ['wsgi.input'].read(content_length).decode('utf-8')
    
    output = ""
    result_value = None
    execution_error = None

    stdout_buffer = io.StringIO()
    code_globals = {}
    code_locals = {}

    try:
        with contextlib.redirect_stdout(stdout_buffer):
            exec(code_to_run, code_globals, code_locals)
        
        output = stdout_buffer.getvalue()

        lines = code_to_run.strip().split('\n')
        if lines:
            last_line = lines[-1]
            try:
                compiled_code = compile(last_line, '<string>', 'eval')
                result_value = eval(compiled_code, code_globals, code_locals)
            except SyntaxError:
                pass
            except Exception as eval_e:
                execution_error = traceback.format_exc()
                pass

    except Exception as e:
        execution_error += traceback.format_exc()

    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    
    response_data = {
        'output': output,
        'result': result_value
    }

    if execution_error:
        response_data['error'] = execution_error
        status = '400 Bad Request'

    start_response(status, headers)
    return [json.dumps(response_data).encode()]
