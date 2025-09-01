#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
import requests
import subprocess
from datetime import datetime
import uuid

# Simple MinIO service without external dependency
class MinIOReportsService:
    def __init__(self):
        self.minio_host = "localhost:9898"
        self.bucket_name = "veritas-reports"
        self.base_url = f"http://{self.minio_host}/minio/{self.bucket_name}"
    
    def get_project_reports_url(self, project_id):
        return f"{self.base_url}/projects/{project_id}/reports/"
    
    def get_project_dashboard_url(self, project_id):
        return f"{self.base_url}/projects/{project_id}/dashboard/"

app = Flask(__name__)
CORS(app)

class ProjectManager:
    def __init__(self):
        self.projects_file = '/tmp/projects.json'
        self.minio_service = MinIOReportsService()
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        os.makedirs('/tmp', exist_ok=True)
        if not os.path.exists(self.projects_file):
            with open(self.projects_file, 'w') as f:
                json.dump([], f)
    
    def get_projects(self):
        with open(self.projects_file, 'r') as f:
            return json.load(f)
    
    def save_projects(self, projects):
        with open(self.projects_file, 'w') as f:
            json.dump(projects, f, indent=2)
    
    def create_project(self, data):
        projects = self.get_projects()
        project_id = str(uuid.uuid4())
        project = {
            'id': project_id,
            'name': data['name'],
            'repository': data['repository'],
            'description': data.get('description', ''),
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'test_suites': [],
            'user_stories': [],
            'test_plans': [],
            'execution_plans': [],
            'reports': [],
            'minio_reports_url': self.minio_service.get_project_reports_url(project_id),
            'minio_dashboard_url': self.minio_service.get_project_dashboard_url(project_id)
        }
        projects.append(project)
        self.save_projects(projects)
        return project

project_manager = ProjectManager()

@app.route('/')
def index():
    return render_template('project_manager.html')

@app.route('/api/projects', methods=['GET'])
def get_projects():
    return jsonify(project_manager.get_projects())

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    project = project_manager.create_project(data)
    return jsonify(project), 201

@app.route('/api/projects/<project_id>/analyze', methods=['POST'])
def analyze_repository(project_id):
    projects = project_manager.get_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Repository analysis
    analysis = analyze_repo_structure(project['repository'])
    
    # Generate user stories
    user_stories = generate_user_stories(analysis)
    
    # Generate test plans
    test_plans = generate_test_plans(user_stories)
    
    # Update project
    project['user_stories'] = user_stories
    project['test_plans'] = test_plans
    project['analysis'] = analysis
    
    project_manager.save_projects(projects)
    
    return jsonify({
        'analysis': analysis,
        'user_stories': user_stories,
        'test_plans': test_plans
    })

def analyze_repo_structure(repo_url):
    return {
        'languages': ['Python', 'JavaScript', 'Docker'],
        'frameworks': ['Flask', 'React', 'Docker'],
        'files_count': 45,
        'api_endpoints': 12,
        'components': ['Authentication', 'API', 'Database', 'Frontend'],
        'complexity': 'Medium',
        'test_coverage': '65%'
    }

def generate_user_stories(analysis):
    return [
        {
            'id': 'US001',
            'title': 'User Authentication',
            'description': 'As a user, I want to authenticate securely',
            'acceptance_criteria': ['Login with credentials', 'Session management', 'Logout functionality'],
            'priority': 'High'
        },
        {
            'id': 'US002', 
            'title': 'API Integration',
            'description': 'As a developer, I want to integrate with APIs',
            'acceptance_criteria': ['REST API calls', 'Error handling', 'Response validation'],
            'priority': 'High'
        }
    ]

def generate_test_plans(user_stories):
    return [
        {
            'id': 'TP001',
            'name': 'Authentication Test Plan',
            'user_story': 'US001',
            'test_cases': [
                {'id': 'TC001', 'name': 'Valid Login', 'priority': 'High'},
                {'id': 'TC002', 'name': 'Invalid Credentials', 'priority': 'High'},
                {'id': 'TC003', 'name': 'Session Timeout', 'priority': 'Medium'}
            ]
        }
    ]

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "project-manager"})

@app.route('/api/projects/<project_id>/reports', methods=['GET'])
def get_project_reports(project_id):
    projects = project_manager.get_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify({
        'reports_url': project.get('minio_reports_url'),
        'dashboard_url': project.get('minio_dashboard_url'),
        'reports': project.get('reports', [])
    })

@app.route('/api/projects/<project_id>/generate-report', methods=['POST'])
def generate_project_report(project_id):
    projects = project_manager.get_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Mock execution results
    execution_results = {
        'execution_id': str(uuid.uuid4()),
        'total_tests': 25,
        'passed_tests': 23,
        'failed_tests': 2,
        'pass_rate': 92,
        'start_time': datetime.now().isoformat(),
        'duration': '5m 32s',
        'environment': 'Production',
        'test_cases': [
            {'name': 'User Authentication Test', 'status': 'passed', 'duration': '1.2s', 'message': 'All assertions passed'},
            {'name': 'API Integration Test', 'status': 'passed', 'duration': '2.1s', 'message': 'Response validation successful'},
            {'name': 'Database Connection Test', 'status': 'failed', 'duration': '0.8s', 'message': 'Connection timeout'},
        ]
    }
    
    # Generate report
    report_content = project_manager.minio_service.generate_execution_report(project, execution_results)
    report_url = project_manager.minio_service.upload_report(project_id, 'execution', report_content)
    
    # Update project reports
    project['reports'].append({
        'id': str(uuid.uuid4()),
        'type': 'execution',
        'url': report_url,
        'created_at': datetime.now().isoformat(),
        'execution_results': execution_results
    })
    
    project_manager.save_projects(projects)
    
    return jsonify({
        'report_url': report_url,
        'execution_results': execution_results
    })

@app.route('/api/projects/<project_id>/dashboard')
def project_dashboard(project_id):
    projects = project_manager.get_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    dashboard_data = {
        'project': project,
        'stats': {
            'total_user_stories': len(project.get('user_stories', [])),
            'total_test_plans': len(project.get('test_plans', [])),
            'total_test_cases': sum(len(tp.get('test_cases', [])) for tp in project.get('test_plans', [])),
            'execution_rate': '85%',
            'pass_rate': '92%'
        },
        'minio_urls': {
            'reports': project.get('minio_reports_url'),
            'dashboard': project.get('minio_dashboard_url')
        }
    }
    
    return jsonify(dashboard_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8874, debug=True)
