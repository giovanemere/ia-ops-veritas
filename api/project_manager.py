#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
import requests
import subprocess
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

class ProjectManager:
    def __init__(self):
        self.projects_file = '/tmp/projects.json'
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
        project = {
            'id': str(uuid.uuid4()),
            'name': data['name'],
            'repository': data['repository'],
            'description': data.get('description', ''),
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'test_suites': [],
            'user_stories': [],
            'test_plans': [],
            'execution_plans': [],
            'reports': []
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
        }
    }
    
    return jsonify(dashboard_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8874, debug=True)
