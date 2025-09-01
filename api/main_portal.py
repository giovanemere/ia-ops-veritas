#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "veritas-portal"})

@app.route('/api/health')
def api_health():
    services = {
        'test_manager': check_service('http://localhost:8870/api/health'),
        'execution_engine': check_service('http://localhost:8871/api/health'),
        'quality_analytics': check_service('http://localhost:8872/api/health'),
        'evidence_manager': check_service('http://localhost:8873/api/health')
    }
    
    return jsonify({
        'status': 'healthy',
        'services': services,
        'portal': 'active'
    })

@app.route('/api/stats')
def stats():
    return jsonify({
        'total_services': 5,
        'active_services': 5,
        'uptime': '99.9%',
        'version': '1.0.0',
        'integrations': {
            'azure_devops': 'ready',
            'gitlab': 'ready',
            'jira': 'ready',
            'github_actions': 'ready'
        }
    })

def check_service(url):
    try:
        response = requests.get(url, timeout=2)
        return 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        return 'unavailable'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8845))
    app.run(host='0.0.0.0', port=port, debug=True)
