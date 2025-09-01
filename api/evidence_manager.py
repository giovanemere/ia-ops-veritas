#!/usr/bin/env python3
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import logging
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    with open('/app/templates/evidence_manager.html', 'r') as f:
        return f.read()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "evidence-manager", "timestamp": datetime.utcnow().isoformat()})

@app.route('/api/evidence', methods=['GET'])
def get_evidence():
    return jsonify({
        "evidence": [
            {
                "id": "ev001",
                "test_id": "test_001",
                "type": "screenshot",
                "filename": "test_001_screenshot.png",
                "created_at": "2024-09-01T19:00:00Z"
            },
            {
                "id": "ev002", 
                "test_id": "test_002",
                "type": "log",
                "filename": "test_002_execution.log",
                "created_at": "2024-09-01T19:15:00Z"
            }
        ]
    })

@app.route('/api/reports', methods=['GET'])
def get_reports():
    return jsonify({
        "reports": [
            {
                "id": "rpt001",
                "name": "Daily Test Report",
                "type": "pdf",
                "generated_at": "2024-09-01T20:00:00Z",
                "status": "completed"
            }
        ]
    })

@app.route('/api/reports', methods=['POST'])
def generate_report():
    data = request.get_json()
    return jsonify({
        "id": "rpt002",
        "status": "generating",
        "message": "Report generation started"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8873))
    app.run(host='0.0.0.0', port=port, debug=False)
