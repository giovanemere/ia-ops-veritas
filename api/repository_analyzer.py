#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import git
import os
import json
import tempfile
import shutil
from pathlib import Path
import re

app = Flask(__name__)
CORS(app)

class RepositoryAnalyzer:
    def __init__(self):
        self.temp_dir = '/tmp/repo_analysis'
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def clone_and_analyze(self, repo_url, project_name):
        repo_path = os.path.join(self.temp_dir, project_name)
        
        # Clean existing directory
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        
        try:
            # Clone repository
            repo = git.Repo.clone_from(repo_url, repo_path)
            
            # Analyze structure
            analysis = {
                'repository': repo_url,
                'project_name': project_name,
                'structure': self.analyze_structure(repo_path),
                'languages': self.detect_languages(repo_path),
                'frameworks': self.detect_frameworks(repo_path),
                'api_endpoints': self.find_api_endpoints(repo_path),
                'database_models': self.find_database_models(repo_path),
                'components': self.identify_components(repo_path),
                'complexity_metrics': self.calculate_complexity(repo_path)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_structure(self, repo_path):
        structure = {}
        for root, dirs, files in os.walk(repo_path):
            if '.git' in root:
                continue
            rel_path = os.path.relpath(root, repo_path)
            structure[rel_path] = {
                'directories': dirs,
                'files': files,
                'file_count': len(files)
            }
        return structure
    
    def detect_languages(self, repo_path):
        languages = {}
        extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.php': 'PHP',
            '.rb': 'Ruby'
        }
        
        for root, dirs, files in os.walk(repo_path):
            if '.git' in root:
                continue
            for file in files:
                ext = Path(file).suffix
                if ext in extensions:
                    lang = extensions[ext]
                    languages[lang] = languages.get(lang, 0) + 1
        
        return languages
    
    def detect_frameworks(self, repo_path):
        frameworks = []
        
        # Check for common framework files
        framework_indicators = {
            'requirements.txt': ['Flask', 'Django', 'FastAPI'],
            'package.json': ['React', 'Vue', 'Angular', 'Express'],
            'Dockerfile': ['Docker'],
            'docker-compose.yml': ['Docker Compose'],
            'pom.xml': ['Maven', 'Spring'],
            'build.gradle': ['Gradle', 'Spring Boot']
        }
        
        for root, dirs, files in os.walk(repo_path):
            if '.git' in root:
                continue
            for file in files:
                if file in framework_indicators:
                    frameworks.extend(framework_indicators[file])
        
        return list(set(frameworks))
    
    def find_api_endpoints(self, repo_path):
        endpoints = []
        
        for root, dirs, files in os.walk(repo_path):
            if '.git' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Find Flask routes
                            routes = re.findall(r'@app\.route\([\'"]([^\'"]+)[\'"].*?\)', content)
                            for route in routes:
                                endpoints.append({
                                    'path': route,
                                    'file': file,
                                    'type': 'Flask Route'
                                })
                    except:
                        continue
        
        return endpoints
    
    def find_database_models(self, repo_path):
        models = []
        
        for root, dirs, files in os.walk(repo_path):
            if '.git' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Find SQLAlchemy models
                            model_classes = re.findall(r'class\s+(\w+).*?db\.Model', content)
                            for model in model_classes:
                                models.append({
                                    'name': model,
                                    'file': file,
                                    'type': 'SQLAlchemy Model'
                                })
                    except:
                        continue
        
        return models
    
    def identify_components(self, repo_path):
        components = []
        
        # Common component patterns
        component_patterns = {
            'Authentication': ['auth', 'login', 'user', 'session'],
            'API': ['api', 'endpoint', 'route'],
            'Database': ['db', 'model', 'schema', 'migration'],
            'Frontend': ['static', 'template', 'ui', 'component'],
            'Testing': ['test', 'spec', 'pytest'],
            'Configuration': ['config', 'settings', 'env'],
            'Documentation': ['doc', 'readme', 'guide']
        }
        
        for root, dirs, files in os.walk(repo_path):
            if '.git' in root:
                continue
            path_lower = root.lower()
            for component, patterns in component_patterns.items():
                if any(pattern in path_lower for pattern in patterns):
                    if component not in components:
                        components.append(component)
        
        return components
    
    def calculate_complexity(self, repo_path):
        total_files = 0
        total_lines = 0
        
        for root, dirs, files in os.walk(repo_path):
            if '.git' in root:
                continue
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java')):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            total_lines += len(f.readlines())
                    except:
                        continue
        
        complexity = 'Low'
        if total_files > 50 or total_lines > 5000:
            complexity = 'Medium'
        if total_files > 100 or total_lines > 10000:
            complexity = 'High'
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'complexity_level': complexity
        }

analyzer = RepositoryAnalyzer()

@app.route('/')
def index():
    return render_template('repository_analyzer.html')

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "repository-analyzer"})

@app.route('/api/analyze', methods=['POST'])
def analyze_repository():
    data = request.json
    repo_url = data.get('repository_url')
    project_name = data.get('project_name', 'temp_project')
    
    if not repo_url:
        return jsonify({'error': 'Repository URL is required'}), 400
    
    analysis = analyzer.clone_and_analyze(repo_url, project_name)
    return jsonify(analysis)

@app.route('/api/generate-user-stories', methods=['POST'])
def generate_user_stories():
    data = request.json
    analysis = data.get('analysis', {})
    
    user_stories = []
    components = analysis.get('components', [])
    
    # Generate user stories based on components
    story_templates = {
        'Authentication': {
            'title': 'User Authentication System',
            'description': 'As a user, I want to securely authenticate to access the system',
            'acceptance_criteria': [
                'User can login with valid credentials',
                'Invalid login attempts are handled properly',
                'User sessions are managed securely',
                'User can logout successfully'
            ]
        },
        'API': {
            'title': 'API Integration',
            'description': 'As a developer, I want to integrate with system APIs',
            'acceptance_criteria': [
                'API endpoints respond correctly',
                'Error handling is implemented',
                'Response format is consistent',
                'Authentication is required where needed'
            ]
        },
        'Database': {
            'title': 'Data Management',
            'description': 'As a system, I want to manage data reliably',
            'acceptance_criteria': [
                'Data is stored correctly',
                'Data integrity is maintained',
                'Queries perform efficiently',
                'Backup and recovery work'
            ]
        }
    }
    
    for component in components:
        if component in story_templates:
            template = story_templates[component]
            user_stories.append({
                'id': f'US{len(user_stories)+1:03d}',
                'component': component,
                'title': template['title'],
                'description': template['description'],
                'acceptance_criteria': template['acceptance_criteria'],
                'priority': 'High' if component in ['Authentication', 'API'] else 'Medium'
            })
    
    return jsonify(user_stories)

@app.route('/api/generate-test-plans', methods=['POST'])
def generate_test_plans():
    data = request.json
    user_stories = data.get('user_stories', [])
    
    test_plans = []
    
    for story in user_stories:
        test_cases = []
        for i, criteria in enumerate(story['acceptance_criteria']):
            test_cases.append({
                'id': f'TC{len(test_cases)+1:03d}',
                'name': criteria,
                'description': f'Test case for: {criteria}',
                'priority': story['priority'],
                'type': 'Functional',
                'steps': [
                    'Setup test environment',
                    'Execute test scenario',
                    'Verify expected results'
                ]
            })
        
        test_plans.append({
            'id': f'TP{len(test_plans)+1:03d}',
            'name': f'{story["component"]} Test Plan',
            'user_story_id': story['id'],
            'description': f'Test plan for {story["title"]}',
            'test_cases': test_cases
        })
    
    return jsonify(test_plans)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8875, debug=True)
