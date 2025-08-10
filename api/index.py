import subprocess
import sys
import logging
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['POST'])
def execute():
    logging.info("Request received")
    auth_header = request.headers.get('Authorization')
    password = os.environ.get('PASSWORD')
    if not password or auth_header != f"Bearer {password}":
        logging.warning("Unauthorized request")
        return jsonify({"error": "Unauthorized"}), 401

    code_to_run = request.data.decode('utf-8')
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
            timeout=30 # Add a timeout for security
        )
        output = result.stdout
        error = result.stderr
        logging.info(f"Subprocess stdout: {output}")
        logging.info(f"Subprocess stderr: {error}")
    except Exception as e:
        logging.error(f"Exception during subprocess execution: {e}")
        error = str(e)

    return jsonify({
        "output": output,
        "error": error,
        "result": None
    })
