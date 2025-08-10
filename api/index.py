import json
import os
import subprocess
import sys
import logging
import io
import contextlib
import traceback

logging.basicConfig(level=logging.DEBUG)

def app(environ, start_response):
    logging.info("Request received")
    auth_header = environ.get('HTTP_AUTHORIZATION')
    password = os.environ.get('PASSWORD')
    if not password or auth_header != f"Bearer {password}":
        logging.warning("Unauthorized request")
        status = '401 Unauthorized'
        headers = [('Content-type', 'application/json')]
        start_response(status, headers)
        return [json.dumps({'error': 'Unauthorized'}).encode()]

    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        content_length = 0

    code_to_run = environ['wsgi.input'].read(content_length).decode('utf-8')
    logging.info(f"Code to run: {code_to_run}")

    output = ""
    error = ""
    result_value = None

    stdout_buffer = io.StringIO()
    code_globals = {}
    code_locals = {}

    try:
        with contextlib.redirect_stdout(stdout_buffer):
            exec(code_to_run, code_globals, code_locals)
        
        output = stdout_buffer.getvalue()
        logging.info(f"Exec stdout: {output}")

        lines = code_to_run.strip().split('\n')
        if lines:
            last_line = lines[-1]
            try:
                # Try to evaluate the last line as an expression
                # This will raise a SyntaxError if it's a statement
                compiled_code = compile(last_line, '<string>', 'eval')
                result_value = eval(compiled_code, code_globals, code_locals)
            except SyntaxError:
                # Not an expression, so no result value
                pass
            except Exception as eval_e:
                logging.warning(f"Exception during eval: {eval_e}")

    except Exception as e:
        logging.error(f"Exception during exec: {e}")
        error = traceback.format_exc()

    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)
    return [json.dumps({
        'output': output,
        'error': error,
        'result': result_value
    }).encode()]
