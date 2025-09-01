#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

class TestResultsViewer:
    def __init__(self):
        self.results_dir = '/tmp/test_results'
        os.makedirs(self.results_dir, exist_ok=True)
    
    def generate_test_report(self, project_name, execution_data):
        report_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate metrics
        total_tests = len(execution_data.get('test_cases', []))
        passed_tests = len([t for t in execution_data.get('test_cases', []) if t.get('status') == 'passed'])
        failed_tests = total_tests - passed_tests
        pass_rate = round((passed_tests / total_tests * 100) if total_tests > 0 else 0, 1)
        
        # Generate HTML report
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Results - {project_name}</title>
    <link rel="stylesheet" href="http://localhost:8876/static/css/main.css">
    <style>
        body {{ background: var(--light-bg); }}
        .test-report {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .test-case {{ 
            background: var(--card-bg); 
            border-radius: 0.75rem; 
            padding: 1.5rem; 
            margin: 1rem 0; 
            border-left: 4px solid var(--border-color);
            box-shadow: var(--shadow);
        }}
        .test-case.passed {{ border-left-color: var(--success-color); }}
        .test-case.failed {{ border-left-color: var(--error-color); }}
        .test-header {{ display: flex; justify-content: between; align-items: center; margin-bottom: 1rem; }}
        .test-status {{ 
            padding: 0.25rem 0.75rem; 
            border-radius: 9999px; 
            font-size: 0.75rem; 
            font-weight: 600;
        }}
        .status-passed {{ background: rgba(16, 185, 129, 0.1); color: var(--success-color); }}
        .status-failed {{ background: rgba(239, 68, 68, 0.1); color: var(--error-color); }}
        .test-details {{ background: var(--light-bg); padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }}
        .metric-card {{ 
            background: var(--card-bg); 
            padding: 1.5rem; 
            border-radius: 0.75rem; 
            text-align: center;
            box-shadow: var(--shadow);
        }}
        .metric-value {{ font-size: 2rem; font-weight: 700; color: var(--accent-color); }}
        .metric-label {{ color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.5rem; }}
        .execution-summary {{ 
            background: var(--gradient-primary); 
            color: white; 
            padding: 2rem; 
            border-radius: 1rem; 
            margin-bottom: 2rem;
        }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }}
        .summary-item {{ text-align: center; }}
        .summary-value {{ font-size: 1.5rem; font-weight: 600; }}
        .summary-label {{ opacity: 0.8; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <div class="test-report">
        <div class="execution-summary">
            <h1>📊 Test Execution Report</h1>
            <p style="opacity: 0.9; margin: 0.5rem 0 2rem 0;">Project: {project_name} | Execution ID: {execution_data.get('execution_id', report_id)}</p>
            
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-value">{total_tests}</div>
                    <div class="summary-label">Total Tests</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">{passed_tests}</div>
                    <div class="summary-label">Passed</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">{failed_tests}</div>
                    <div class="summary-label">Failed</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">{pass_rate}%</div>
                    <div class="summary-label">Pass Rate</div>
                </div>
            </div>
        </div>
        
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{execution_data.get('duration', 'N/A')}</div>
                <div class="metric-label">Duration</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{execution_data.get('environment', 'Production')}</div>
                <div class="metric-label">Environment</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{execution_data.get('coverage', '85')}%</div>
                <div class="metric-label">Code Coverage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{datetime.now().strftime('%H:%M')}</div>
                <div class="metric-label">Execution Time</div>
            </div>
        </div>
        
        <h2 style="margin: 2rem 0 1rem 0; color: var(--text-primary);">🧪 Test Cases Details</h2>
        
        {self._generate_test_cases_html(execution_data.get('test_cases', []))}
        
        <div style="text-align: center; margin-top: 3rem; padding: 2rem; background: var(--card-bg); border-radius: 1rem;">
            <h3>📋 Report Generated</h3>
            <p style="color: var(--text-secondary);">
                Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')} | Report ID: {report_id}
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        # Save report
        filename = f"test_report_{timestamp}_{report_id}.html"
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return {
            'report_id': report_id,
            'filename': filename,
            'filepath': filepath,
            'url': f'/test-results/{filename}',
            'metrics': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'pass_rate': pass_rate
            }
        }
    
    def _generate_test_cases_html(self, test_cases):
        html = ""
        for i, test_case in enumerate(test_cases):
            status = test_case.get('status', 'unknown')
            status_class = 'passed' if status == 'passed' else 'failed'
            
            html += f"""
            <div class="test-case {status_class}">
                <div class="test-header">
                    <h3 style="margin: 0; color: var(--text-primary);">
                        {i+1}. {test_case.get('name', 'Unknown Test')}
                    </h3>
                    <span class="test-status status-{status}">{status.upper()}</span>
                </div>
                
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                    {test_case.get('description', 'No description available')}
                </p>
                
                <div class="test-details">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                        <div>
                            <strong>Duration:</strong> {test_case.get('duration', 'N/A')}
                        </div>
                        <div>
                            <strong>Priority:</strong> {test_case.get('priority', 'Medium')}
                        </div>
                        <div>
                            <strong>Category:</strong> {test_case.get('category', 'Functional')}
                        </div>
                    </div>
                    
                    {f'<div style="margin-top: 1rem;"><strong>Message:</strong> {test_case.get("message", "")}</div>' if test_case.get("message") else ''}
                    
                    {f'<div style="margin-top: 1rem;"><strong>Error Details:</strong><pre style="background: rgba(239, 68, 68, 0.1); padding: 1rem; border-radius: 0.5rem; overflow-x: auto;">{test_case.get("error_details", "")}</pre></div>' if test_case.get("error_details") else ''}
                </div>
            </div>
            """
        
        return html

viewer = TestResultsViewer()

@app.route('/')
def index():
    return render_template('test_results_viewer.html')

@app.route('/test-results/<filename>')
def serve_test_result(filename):
    return send_from_directory(viewer.results_dir, filename)

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    data = request.json
    project_name = data.get('project_name', 'Unknown Project')
    execution_data = data.get('execution_data', {})
    
    report = viewer.generate_test_report(project_name, execution_data)
    return jsonify(report)

@app.route('/api/reports', methods=['GET'])
def list_reports():
    reports = []
    for filename in os.listdir(viewer.results_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(viewer.results_dir, filename)
            stat = os.stat(filepath)
            reports.append({
                'filename': filename,
                'url': f'/test-results/{filename}',
                'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'size': stat.st_size
            })
    
    return jsonify(sorted(reports, key=lambda x: x['created_at'], reverse=True))

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "test-results-viewer"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8877, debug=True)
