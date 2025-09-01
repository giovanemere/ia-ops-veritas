#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    with open('/app/templates/quality_analytics.html', 'r') as f:
        return f.read()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "quality-analytics", "timestamp": datetime.utcnow().isoformat()})

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    return jsonify({
        "code_coverage": 85.2,
        "test_pass_rate": 92.5,
        "code_quality_score": 8.7,
        "technical_debt": "2.5 days",
        "last_updated": datetime.utcnow().isoformat()
    })

@app.route('/api/trends', methods=['GET'])
def get_trends():
    return jsonify({
        "coverage_trend": [80, 82, 85, 85.2],
        "quality_trend": [8.2, 8.5, 8.6, 8.7],
        "dates": ["2024-08-01", "2024-08-15", "2024-08-30", "2024-09-01"]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8872))
    app.run(host='0.0.0.0', port=port, debug=False)
