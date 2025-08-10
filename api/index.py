import json
import os
import subprocess
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

def application(environ, start_response):
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
    try:
        command = [sys.executable, '-c', code_to_run]
        logging.info(f"Running command: {command}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        error = result.stderr
        logging.info(f"Subprocess stdout: {output}")
        logging.info(f"Subprocess stderr: {error}")
    except Exception as e:
        logging.error(f"Exception during subprocess execution: {e}")
        error = str(e)

    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)
    return [json.dumps({
        'output': output,
        'error': error,
        'result': None
    }).encode()]