#!/usr/bin/env python3
"""
Test Manager API
Gestión de casos de prueba para IA-Ops Veritas
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from enum import Enum

app = Flask(__name__)
CORS(app)

# Configuración
TEST_CASES_FILE = '/app/data/test_cases.json'
TEST_SUITES_FILE = '/app/data/test_suites.json'

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"

class TestPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

def load_test_cases():
    """Cargar casos de prueba"""
    if os.path.exists(TEST_CASES_FILE):
        with open(TEST_CASES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_test_cases(cases):
    """Guardar casos de prueba"""
    os.makedirs(os.path.dirname(TEST_CASES_FILE), exist_ok=True)
    with open(TEST_CASES_FILE, 'w') as f:
        json.dump(cases, f, indent=2)

def load_test_suites():
    """Cargar suites de prueba"""
    if os.path.exists(TEST_SUITES_FILE):
        with open(TEST_SUITES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_test_suites(suites):
    """Guardar suites de prueba"""
    os.makedirs(os.path.dirname(TEST_SUITES_FILE), exist_ok=True)
    with open(TEST_SUITES_FILE, 'w') as f:
        json.dump(suites, f, indent=2)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'test-manager'})

@app.route('/test-cases', methods=['GET'])
def list_test_cases():
    """Listar casos de prueba"""
    cases = load_test_cases()
    suite_filter = request.args.get('suite')
    status_filter = request.args.get('status')
    
    if suite_filter:
        cases = [c for c in cases if c.get('suite') == suite_filter]
    if status_filter:
        cases = [c for c in cases if c.get('status') == status_filter]
    
    return jsonify({
        'test_cases': cases,
        'count': len(cases)
    })

@app.route('/test-cases', methods=['POST'])
def create_test_case():
    """Crear caso de prueba"""
    data = request.get_json()
    
    required_fields = ['title', 'description', 'suite']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    cases = load_test_cases()
    
    new_case = {
        'id': len(cases) + 1,
        'title': data['title'],
        'description': data['description'],
        'suite': data['suite'],
        'priority': data.get('priority', TestPriority.MEDIUM.value),
        'status': data.get('status', TestStatus.DRAFT.value),
        'steps': data.get('steps', []),
        'expected_result': data.get('expected_result', ''),
        'tags': data.get('tags', []),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'created_by': data.get('created_by', 'system'),
        'execution_count': 0,
        'last_execution': None,
        'last_result': None
    }
    
    cases.append(new_case)
    save_test_cases(cases)
    
    logger.info(f"Test case created: {new_case['title']}")
    return jsonify(new_case), 201

@app.route('/test-cases/<int:case_id>', methods=['GET'])
def get_test_case(case_id):
    """Obtener caso de prueba específico"""
    cases = load_test_cases()
    case = next((c for c in cases if c['id'] == case_id), None)
    
    if not case:
        return jsonify({'error': 'Test case not found'}), 404
    
    return jsonify(case)

@app.route('/test-cases/<int:case_id>', methods=['PUT'])
def update_test_case(case_id):
    """Actualizar caso de prueba"""
    data = request.get_json()
    cases = load_test_cases()
    
    case = next((c for c in cases if c['id'] == case_id), None)
    if not case:
        return jsonify({'error': 'Test case not found'}), 404
    
    # Actualizar campos permitidos
    updatable_fields = ['title', 'description', 'priority', 'status', 'steps', 'expected_result', 'tags']
    for field in updatable_fields:
        if field in data:
            case[field] = data[field]
    
    case['updated_at'] = datetime.now().isoformat()
    save_test_cases(cases)
    
    logger.info(f"Test case updated: {case['title']}")
    return jsonify(case)

@app.route('/test-cases/<int:case_id>', methods=['DELETE'])
def delete_test_case(case_id):
    """Eliminar caso de prueba"""
    cases = load_test_cases()
    case = next((c for c in cases if c['id'] == case_id), None)
    
    if not case:
        return jsonify({'error': 'Test case not found'}), 404
    
    cases = [c for c in cases if c['id'] != case_id]
    save_test_cases(cases)
    
    logger.info(f"Test case deleted: {case['title']}")
    return jsonify({'message': 'Test case deleted successfully'})

@app.route('/test-suites', methods=['GET'])
def list_test_suites():
    """Listar suites de prueba"""
    suites = load_test_suites()
    return jsonify({
        'test_suites': suites,
        'count': len(suites)
    })

@app.route('/test-suites', methods=['POST'])
def create_test_suite():
    """Crear suite de prueba"""
    data = request.get_json()
    
    required_fields = ['name', 'description']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    suites = load_test_suites()
    
    new_suite = {
        'id': len(suites) + 1,
        'name': data['name'],
        'description': data['description'],
        'repository': data.get('repository', ''),
        'created_at': datetime.now().isoformat(),
        'test_count': 0,
        'last_execution': None
    }
    
    suites.append(new_suite)
    save_test_suites(suites)
    
    logger.info(f"Test suite created: {new_suite['name']}")
    return jsonify(new_suite), 201

@app.route('/stats', methods=['GET'])
def get_stats():
    """Estadísticas de testing"""
    cases = load_test_cases()
    suites = load_test_suites()
    
    stats = {
        'total_cases': len(cases),
        'total_suites': len(suites),
        'cases_by_status': {
            'draft': len([c for c in cases if c.get('status') == TestStatus.DRAFT.value]),
            'active': len([c for c in cases if c.get('status') == TestStatus.ACTIVE.value]),
            'deprecated': len([c for c in cases if c.get('status') == TestStatus.DEPRECATED.value])
        },
        'cases_by_priority': {
            'low': len([c for c in cases if c.get('priority') == TestPriority.LOW.value]),
            'medium': len([c for c in cases if c.get('priority') == TestPriority.MEDIUM.value]),
            'high': len([c for c in cases if c.get('priority') == TestPriority.HIGH.value]),
            'critical': len([c for c in cases if c.get('priority') == TestPriority.CRITICAL.value])
        }
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8870, debug=False)
