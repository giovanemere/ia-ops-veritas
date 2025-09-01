#!/usr/bin/env python3
"""
Test Execution Engine API
Motor de ejecución de pruebas para IA-Ops Veritas
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from enum import Enum
import requests

app = Flask(__name__)
CORS(app)

# Configuración
EXECUTIONS_FILE = '/app/data/test_executions.json'
DEV_CORE_TASK_URL = os.getenv('DEV_CORE_TASK_URL', 'http://localhost:8861')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

def load_executions():
    """Cargar ejecuciones de prueba"""
    if os.path.exists(EXECUTIONS_FILE):
        with open(EXECUTIONS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_executions(executions):
    """Guardar ejecuciones de prueba"""
    os.makedirs(os.path.dirname(EXECUTIONS_FILE), exist_ok=True)
    with open(EXECUTIONS_FILE, 'w') as f:
        json.dump(executions, f, indent=2)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'test-execution-engine'})

@app.route('/executions', methods=['GET'])
def list_executions():
    """Listar ejecuciones de prueba"""
    executions = load_executions()
    status_filter = request.args.get('status')
    suite_filter = request.args.get('suite')
    
    if status_filter:
        executions = [e for e in executions if e.get('status') == status_filter]
    if suite_filter:
        executions = [e for e in executions if e.get('suite') == suite_filter]
    
    return jsonify({
        'executions': executions,
        'count': len(executions)
    })

@app.route('/executions', methods=['POST'])
def create_execution():
    """Crear nueva ejecución de prueba"""
    data = request.get_json()
    
    required_fields = ['test_case_id', 'suite']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    executions = load_executions()
    
    new_execution = {
        'id': len(executions) + 1,
        'test_case_id': data['test_case_id'],
        'suite': data['suite'],
        'status': ExecutionStatus.QUEUED.value,
        'created_at': datetime.now().isoformat(),
        'started_at': None,
        'completed_at': None,
        'duration': None,
        'result': None,
        'error_message': None,
        'evidence_files': [],
        'environment': data.get('environment', 'default'),
        'executor': data.get('executor', 'system'),
        'parameters': data.get('parameters', {})
    }
    
    executions.append(new_execution)
    save_executions(executions)
    
    # Crear tarea en Dev Core
    try:
        task_data = {
            'name': f"Test Execution - Case {data['test_case_id']}",
            'type': 'test',
            'description': f"Executing test case {data['test_case_id']} in suite {data['suite']}",
            'metadata': {
                'execution_id': new_execution['id'],
                'test_case_id': data['test_case_id'],
                'suite': data['suite']
            }
        }
        
        response = requests.post(f"{DEV_CORE_TASK_URL}/tasks", json=task_data, timeout=5)
        if response.status_code == 201:
            task = response.json()
            new_execution['task_id'] = task['id']
            save_executions(executions)
    except Exception as e:
        logger.warning(f"Failed to create task in Dev Core: {str(e)}")
    
    logger.info(f"Test execution created: {new_execution['id']}")
    return jsonify(new_execution), 201

@app.route('/executions/<int:execution_id>', methods=['GET'])
def get_execution(execution_id):
    """Obtener ejecución específica"""
    executions = load_executions()
    execution = next((e for e in executions if e['id'] == execution_id), None)
    
    if not execution:
        return jsonify({'error': 'Execution not found'}), 404
    
    return jsonify(execution)

@app.route('/executions/<int:execution_id>/start', methods=['POST'])
def start_execution(execution_id):
    """Iniciar ejecución de prueba"""
    executions = load_executions()
    execution = next((e for e in executions if e['id'] == execution_id), None)
    
    if not execution:
        return jsonify({'error': 'Execution not found'}), 404
    
    if execution['status'] != ExecutionStatus.QUEUED.value:
        return jsonify({'error': 'Execution is not in queued status'}), 400
    
    execution['status'] = ExecutionStatus.RUNNING.value
    execution['started_at'] = datetime.now().isoformat()
    save_executions(executions)
    
    # Aquí iría la lógica real de ejecución de pruebas
    # Por ahora simulamos el proceso
    
    logger.info(f"Test execution started: {execution_id}")
    return jsonify({'message': 'Test execution started', 'execution': execution})

@app.route('/executions/<int:execution_id>/complete', methods=['POST'])
def complete_execution(execution_id):
    """Completar ejecución de prueba"""
    data = request.get_json()
    executions = load_executions()
    execution = next((e for e in executions if e['id'] == execution_id), None)
    
    if not execution:
        return jsonify({'error': 'Execution not found'}), 404
    
    execution['status'] = data.get('status', ExecutionStatus.PASSED.value)
    execution['completed_at'] = datetime.now().isoformat()
    execution['result'] = data.get('result', {})
    execution['error_message'] = data.get('error_message')
    execution['evidence_files'] = data.get('evidence_files', [])
    
    # Calcular duración
    if execution['started_at']:
        start_time = datetime.fromisoformat(execution['started_at'])
        end_time = datetime.fromisoformat(execution['completed_at'])
        execution['duration'] = (end_time - start_time).total_seconds()
    
    save_executions(executions)
    
    logger.info(f"Test execution completed: {execution_id} - Status: {execution['status']}")
    return jsonify(execution)

@app.route('/executions/batch', methods=['POST'])
def batch_execution():
    """Ejecutar múltiples casos de prueba"""
    data = request.get_json()
    
    required_fields = ['test_case_ids', 'suite']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    executions = []
    for case_id in data['test_case_ids']:
        execution_data = {
            'test_case_id': case_id,
            'suite': data['suite'],
            'environment': data.get('environment', 'default'),
            'executor': data.get('executor', 'system'),
            'parameters': data.get('parameters', {})
        }
        
        # Crear ejecución individual
        response = create_execution_internal(execution_data)
        if response:
            executions.append(response)
    
    return jsonify({
        'message': f'Batch execution created for {len(executions)} test cases',
        'executions': executions
    })

def create_execution_internal(data):
    """Función interna para crear ejecución"""
    executions = load_executions()
    
    new_execution = {
        'id': len(executions) + 1,
        'test_case_id': data['test_case_id'],
        'suite': data['suite'],
        'status': ExecutionStatus.QUEUED.value,
        'created_at': datetime.now().isoformat(),
        'started_at': None,
        'completed_at': None,
        'duration': None,
        'result': None,
        'error_message': None,
        'evidence_files': [],
        'environment': data.get('environment', 'default'),
        'executor': data.get('executor', 'system'),
        'parameters': data.get('parameters', {})
    }
    
    executions.append(new_execution)
    save_executions(executions)
    
    return new_execution

@app.route('/stats', methods=['GET'])
def execution_stats():
    """Estadísticas de ejecución"""
    executions = load_executions()
    
    stats = {
        'total_executions': len(executions),
        'by_status': {
            'queued': len([e for e in executions if e.get('status') == ExecutionStatus.QUEUED.value]),
            'running': len([e for e in executions if e.get('status') == ExecutionStatus.RUNNING.value]),
            'passed': len([e for e in executions if e.get('status') == ExecutionStatus.PASSED.value]),
            'failed': len([e for e in executions if e.get('status') == ExecutionStatus.FAILED.value]),
            'error': len([e for e in executions if e.get('status') == ExecutionStatus.ERROR.value])
        },
        'success_rate': 0
    }
    
    # Calcular tasa de éxito
    completed = stats['by_status']['passed'] + stats['by_status']['failed']
    if completed > 0:
        stats['success_rate'] = round((stats['by_status']['passed'] / completed) * 100, 2)
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8871, debug=False)
