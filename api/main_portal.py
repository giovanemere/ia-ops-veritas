#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    with open('/app/templates/index.html', 'r') as f:
        return f.read()

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "veritas-portal"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8869))
    app.run(host='0.0.0.0', port=port, debug=False)
