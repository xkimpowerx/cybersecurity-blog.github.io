from flask import Flask, send_from_directory, jsonify
import subprocess
import traceback
import logging
import sys
import os

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return send_from_directory('.', '@index.html')

@app.route('/run-search')
def run_search():
    try:
        app.logger.info("Starting search...")
        result = subprocess.run([sys.executable, 'PH_API.py'], capture_output=True, text=True, timeout=60)
        app.logger.info("Search completed. Output: %s", result.stdout)
        app.logger.info("Search errors (if any): %s", result.stderr)
        return jsonify({'output': result.stdout if result.stdout else result.stderr})
    except subprocess.TimeoutExpired:
        app.logger.error("Search operation timed out")
        return jsonify({'output': "The search operation timed out."}), 500
    except Exception as e:
        app.logger.error("An error occurred: %s", str(e))
        app.logger.error("Current working directory: %s", os.getcwd())
        app.logger.error("Files in current directory: %s", os.listdir())
        app.logger.error(traceback.format_exc())
        return jsonify({'output': f"An error occurred: {str(e)}"}), 500

@app.route('/test')
def test():
    return jsonify({'output': 'Test successful'})

if __name__ == '__main__':
    app.run(debug=True)
