#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime
import uuid
import random

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for demo
executions = []

@app.route('/')
def index():
    with open('/app/templates/execution_engine.html', 'r') as f:
        return f.read()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "test-execution-engine"})

@app.route('/api/executions', methods=['GET'])
def get_executions():
    return jsonify({"executions": executions, "total": len(executions)})

@app.route('/api/executions', methods=['POST'])
def create_execution():
    data = request.get_json()
    execution = {
        "id": str(uuid.uuid4()),
        "test_id": data.get("test_id"),
        "test_name": data.get("test_name", "Unknown Test"),
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "environment": data.get("environment", "test"),
        "progress": 0
    }
    executions.append(execution)
    return jsonify(execution), 201

@app.route('/api/executions/<execution_id>', methods=['GET'])
def get_execution(execution_id):
    execution = next((e for e in executions if e["id"] == execution_id), None)
    if not execution:
        return jsonify({"error": "Execution not found"}), 404
    return jsonify(execution)

@app.route('/api/executions/<execution_id>/complete', methods=['POST'])
def complete_execution(execution_id):
    execution = next((e for e in executions if e["id"] == execution_id), None)
    if not execution:
        return jsonify({"error": "Execution not found"}), 404
    
    data = request.get_json()
    execution.update({
        "status": data.get("status", "completed"),
        "completed_at": datetime.utcnow().isoformat(),
        "progress": 100,
        "result": data.get("result", "passed"),
        "duration": data.get("duration", random.randint(5, 120))
    })
    return jsonify(execution)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total = len(executions)
    completed = len([e for e in executions if e.get("status") == "completed"])
    running = len([e for e in executions if e.get("status") == "running"])
    
    return jsonify({
        "total_executions": total,
        "completed": completed,
        "running": running,
        "success_rate": round((completed / total * 100) if total > 0 else 0, 2)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8871))
    app.run(host='0.0.0.0', port=port, debug=False)
