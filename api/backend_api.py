#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from database_service import DatabaseService
from minio import Minio
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize services
db_service = DatabaseService()

# MinIO client
minio_client = Minio(
    os.getenv('MINIO_ENDPOINT', 'localhost:9898'),
    access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
    secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
    secure=False
)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "backend-api"})

# Projects API
@app.route('/api/projects', methods=['GET'])
def get_projects():
    try:
        projects = db_service.get_projects()
        return jsonify(projects)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    try:
        data = request.json
        project = db_service.create_project(data)
        return jsonify(project), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    try:
        projects = db_service.get_projects()
        project = next((p for p in projects if p['id'] == project_id), None)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get additional data
        project['user_stories'] = db_service.get_project_user_stories(project_id)
        project['executions'] = db_service.get_project_executions(project_id)
        
        return jsonify(project)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Stories API
@app.route('/api/projects/<project_id>/user-stories', methods=['GET'])
def get_user_stories(project_id):
    try:
        stories = db_service.get_project_user_stories(project_id)
        return jsonify(stories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/user-stories', methods=['POST'])
def create_user_story(project_id):
    try:
        data = request.json
        story = db_service.create_user_story(project_id, data)
        return jsonify(story), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Test Executions API
@app.route('/api/projects/<project_id>/executions', methods=['GET'])
def get_executions(project_id):
    try:
        executions = db_service.get_project_executions(project_id)
        return jsonify(executions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/executions', methods=['POST'])
def create_execution(project_id):
    try:
        data = request.json
        execution = db_service.create_execution(project_id, data)
        return jsonify(execution), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Analytics API
@app.route('/api/analytics/dashboard', methods=['GET'])
def get_dashboard_analytics():
    try:
        projects = db_service.get_projects()
        
        total_projects = len(projects)
        total_executions = 0
        total_user_stories = 0
        
        for project in projects:
            executions = db_service.get_project_executions(project['id'])
            user_stories = db_service.get_project_user_stories(project['id'])
            total_executions += len(executions)
            total_user_stories += len(user_stories)
        
        return jsonify({
            'total_projects': total_projects,
            'total_executions': total_executions,
            'total_user_stories': total_user_stories,
            'success_rate': 92.5,
            'active_projects': len([p for p in projects if p['status'] == 'active'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# File Upload API
@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Upload to MinIO
        bucket_name = 'veritas-uploads'
        
        # Ensure bucket exists
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
        
        # Upload file
        file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        minio_client.put_object(
            bucket_name,
            file_name,
            file.stream,
            length=-1,
            part_size=10*1024*1024
        )
        
        return jsonify({
            'filename': file_name,
            'url': f"http://localhost:9898/{bucket_name}/{file_name}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8880, debug=True)
