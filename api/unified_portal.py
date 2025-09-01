#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# Service URLs
SERVICES = {
    'project_manager': 'http://localhost:8874',
    'repository_analyzer': 'http://localhost:8875',
    'test_manager': 'http://localhost:8870',
    'execution_engine': 'http://localhost:8871',
    'quality_analytics': 'http://localhost:8872',
    'evidence_manager': 'http://localhost:8873'
}

@app.route('/')
def index():
    return render_template('unified_portal.html')

@app.route('/service/<service_name>')
def load_service(service_name):
    if service_name not in SERVICES:
        return "Service not found", 404
    
    service_url = SERVICES[service_name]
    return render_template('unified_portal.html', active_service=service_name, service_url=service_url)

@app.route('/api/proxy/<service_name>/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_service(service_name, endpoint):
    if service_name not in SERVICES:
        return jsonify({'error': 'Service not found'}), 404
    
    service_url = SERVICES[service_name]
    target_url = f"{service_url}/api/{endpoint}"
    
    try:
        if request.method == 'GET':
            response = requests.get(target_url, params=request.args)
        elif request.method == 'POST':
            response = requests.post(target_url, json=request.json)
        elif request.method == 'PUT':
            response = requests.put(target_url, json=request.json)
        elif request.method == 'DELETE':
            response = requests.delete(target_url)
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "unified-portal"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8876, debug=True)
