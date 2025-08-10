from wsgiref.simple_server import make_server
import json
import os
import subprocess
import sys

def application(environ, start_response):
    auth_header = environ.get('HTTP_AUTHORIZATION')
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

    try:
        result = subprocess.run(
            [sys.executable, '-c', code_to_run],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        error = result.stderr
    except Exception as e:
        status = '500 Internal Server Error'
        headers = [('Content-type', 'application/json')]
        start_response(status, headers)
        return [json.dumps({'error': str(e)}).encode()]

    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)
    return [json.dumps({
        'output': output,
        'error': error,
        'result': None
    }).encode()]