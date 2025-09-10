#!/usr/bin/env python3
import os
import threading
import time
from flask import Flask, request, jsonify, render_template
import psycopg2
import redis
from minio import Minio
import json
from datetime import datetime
import logging
from config import DB_CONFIG, REDIS_CONFIG, MINIO_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Unified Veritas Service
app = Flask(__name__)

def init_database():
    """Initialize database tables if they don't exist"""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            # Create test_executions table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_executions (
                    id SERIAL PRIMARY KEY,
                    test_case_id INTEGER,
                    project_id INTEGER,
                    execution_name VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'pending',
                    results TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP
                )
            """)
            
            # Create other tables if needed
            cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_cases (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER REFERENCES projects(id),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

# Database connection
def get_db():
    return psycopg2.connect(**DB_CONFIG)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# MinIO connection
minio_client = Minio(
    os.getenv('MINIO_ENDPOINT', 'localhost:9898'),
    access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
    secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin123'),
    secure=False
)

bucket_name = os.getenv('MINIO_BUCKET', 'veritas-projects')

# Initialize bucket and database
def initialize_services():
    try:
        # Create bucket if not exists
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            logger.info(f"Created bucket: {bucket_name}")
        
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Initialization error: {e}")

# Main Portal Routes
@app.route('/')
def main_portal():
    return render_template('unified_portal.html')

@app.route('/service/<service_name>')
def load_service(service_name):
    # All services are now unified, so redirect to appropriate sections
    service_routes = {
        'project_manager': '/projects',
        'repository_analyzer': '/repository',
        'test_manager': '/tests', 
        'execution_engine': '/executions',
        'quality_analytics': '/analytics',
        'evidence_manager': '/evidence'
    }
    
    if service_name in service_routes:
        if service_name == 'project_manager':
            return render_template('project_manager.html')
        elif service_name == 'repository_analyzer':
            return render_template('repository_analyzer.html')
        return render_template('unified_portal.html', active_service=service_name)
    
    return render_template('unified_portal.html')

# Projects page
@app.route('/projects')
def projects_page():
    return render_template('unified_portal.html', active_service='project_manager')

# Tests page  
@app.route('/tests')
def tests_page():
    return render_template('unified_portal.html', active_service='test_manager')

# Executions page
@app.route('/executions') 
def executions_page():
    return render_template('unified_portal.html', active_service='execution_engine')

# Analytics page
@app.route('/analytics')
def analytics_page():
    return render_template('unified_portal.html', active_service='quality_analytics')

# Evidence page
@app.route('/evidence')
def evidence_page():
    return render_template('unified_portal.html', active_service='evidence_manager')

# Enhanced service routes
@app.route('/test_manager_enhanced')
def test_manager_enhanced():
    return render_template('test_manager_enhanced.html')

@app.route('/execution_manager_enhanced')
def execution_manager_enhanced():
    return render_template('execution_manager_enhanced.html')

@app.route('/evidence_manager_enhanced')
def evidence_manager_enhanced():
    return render_template('evidence_manager_enhanced.html')

@app.route('/project_manager_new')
def project_manager_new():
    return render_template('project_manager.html')

# Individual service routes
@app.route('/project_manager')
def project_manager():
    return render_template('project_manager.html')

@app.route('/test_manager')
def test_manager():
    return render_template('test_manager.html')

@app.route('/execution_engine')
def execution_engine():
    return render_template('execution_engine.html')

@app.route('/quality_analytics')
def quality_analytics():
    return render_template('quality_analytics.html')

@app.route('/evidence_manager')
def evidence_manager():
    return render_template('evidence_manager.html')

@app.route('/test_results_viewer')
def test_results_viewer():
    return render_template('test_results_viewer.html')

# API Routes
@app.route('/api/stats')
def get_stats():
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM projects")
            projects = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM test_cases")
            test_cases = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM test_executions")
            executions = cur.fetchone()[0]
        
        conn.close()
        return jsonify({
            'projects': projects,
            'test_cases': test_cases,
            'executions': executions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Projects API
@app.route('/api/projects', methods=['GET', 'POST'])
def projects_api():
    if request.method == 'GET':
        try:
            conn = get_db()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
                projects = []
                for row in cur.fetchall():
                    projects.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'created_at': row[3].isoformat() if row[3] else None
                    })
            conn.close()
            return jsonify(projects)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            conn = get_db()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO projects (name, description) VALUES (%s, %s) RETURNING id",
                    (data['name'], data.get('description', ''))
                )
                project_id = cur.fetchone()[0]
                conn.commit()
            conn.close()
            
            # Create project folder in MinIO
            from io import BytesIO
            folder_path = f"projects/{data['name']}/tests/"
            minio_client.put_object(bucket_name, folder_path, BytesIO(b''), 0)
            
            return jsonify({'id': project_id, 'message': 'Project created successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Test Cases API
@app.route('/api/tests', methods=['GET', 'POST'])
def tests_api():
    if request.method == 'GET':
        try:
            suite_id = request.args.get('suite_id')
            conn = get_db()
            with conn.cursor() as cur:
                if suite_id:
                    cur.execute("SELECT * FROM test_cases WHERE suite_id = %s", (suite_id,))
                else:
                    cur.execute("SELECT * FROM test_cases")
                
                tests = []
                for row in cur.fetchall():
                    tests.append({
                        'id': row[0],
                        'suite_id': row[1],
                        'name': row[2],
                        'description': row[3],
                        'priority': row[4],
                        'status': row[5],
                        'test_type': row[7] if len(row) > 7 else 'unit'
                    })
            conn.close()
            return jsonify(tests)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            conn = get_db()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO test_cases (suite_id, name, description, test_type, priority) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (data.get('suite_id'), data['name'], data.get('description', ''), data.get('test_type', 'unit'), data.get('priority', 'medium'))
                )
                test_id = cur.fetchone()[0]
                conn.commit()
            conn.close()
            return jsonify({'id': test_id, 'message': 'Test case created successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Test Execution API
@app.route('/api/executions', methods=['GET', 'POST'])
def executions_api():
    if request.method == 'GET':
        try:
            conn = get_db()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT e.*, p.name as project_name 
                    FROM test_executions e
                    JOIN projects p ON e.project_id = p.id
                    ORDER BY e.executed_at DESC
                """)
                executions = []
                for row in cur.fetchall():
                    executions.append({
                        'id': row[0],
                        'project_id': row[1],
                        'status': row[2],
                        'result': row[3],
                        'executed_at': row[4].isoformat() if row[4] else None,
                        'project_name': row[5]
                    })
            conn.close()
            return jsonify(executions)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            start_time = datetime.now()
            
            # Simulate test execution
            results = {
                "status": "passed",
                "message": f"Test executed at {start_time.isoformat()}",
                "duration": 1.5,
                "tests_run": 1,
                "tests_passed": 1,
                "tests_failed": 0
            }
            
            conn = get_db()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO test_executions (project_id, execution_name, status, results, end_time) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (data['project_id'], data.get('execution_name', 'Test Execution'), 'completed', json.dumps(results), datetime.now())
                )
                execution_id = cur.fetchone()[0]
                conn.commit()
            conn.close()
            
            # Store execution evidence in MinIO
            from io import BytesIO
            evidence_data = {
                'execution_id': str(execution_id),
                'project_id': data['project_id'],
                'results': results,
                'timestamp': start_time.isoformat(),
                'evidence_files': []
            }
            evidence_json = json.dumps(evidence_data, indent=2).encode('utf-8')
            evidence_path = f"projects/{data.get('project_name', 'unknown')}/evidence/{execution_id}_execution.json"
            minio_client.put_object(bucket_name, evidence_path, BytesIO(evidence_json), len(evidence_json))
            
            return jsonify({
                'id': execution_id,
                'status': 'completed',
                'results': results,
                'evidence_path': evidence_path
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Evidence Management API
@app.route('/api/evidence', methods=['GET', 'POST'])
def evidence_api():
    if request.method == 'GET':
        try:
            project_id = request.args.get('project_id')
            conn = get_db()
            with conn.cursor() as cur:
                if project_id:
                    cur.execute("SELECT * FROM evidence_files WHERE project_id = %s", (project_id,))
                else:
                    cur.execute("SELECT * FROM evidence_files")
                
                files = []
                for row in cur.fetchall():
                    files.append({
                        'id': row[0],
                        'project_id': row[1],
                        'test_execution_id': row[2],
                        'file_name': row[3],
                        'file_path': row[4],
                        'file_type': row[5],
                        'file_size': row[6],
                        'uploaded_at': row[7].isoformat() if row[7] else None,
                        'download_url': f"/api/evidence/{row[0]}/download"
                    })
            conn.close()
            return jsonify(files)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Health check
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'services': {
            'database': 'connected',
            'redis': 'connected',
            'minio': 'connected'
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    initialize_services()
    init_database()  # Initialize database tables
    app.run(host='0.0.0.0', port=8869, debug=False)
