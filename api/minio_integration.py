#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime
import uuid

class MinIOReportsService:
    def __init__(self):
        self.minio_host = "localhost:9898"
        self.bucket_name = "veritas-reports"
        self.base_url = f"http://{self.minio_host}/minio/{self.bucket_name}"
    
    def upload_report(self, project_id, report_type, content, filename=None):
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_{timestamp}.html"
        
        # For now, return a mock URL - in production, implement actual MinIO upload
        return f"{self.base_url}/projects/{project_id}/reports/{filename}"
    
    def generate_execution_report(self, project_data, execution_results):
        template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Test Report - {project_data.get('name', 'Unknown')}</title>
    <link rel="stylesheet" href="http://localhost:8869/static/css/main.css">
    <link rel="stylesheet" href="http://localhost:8869/static/css/components.css">
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <h1>📊 Test Execution Report</h1>
                <div class="subtitle">{project_data.get('name', 'Unknown Project')}</div>
            </div>
        </div>
    </header>
    
    <div class="container">
        <div class="nav-breadcrumb">
            <a href="http://localhost:8869">Portal</a> <span>/</span>
            <a href="http://localhost:8874">Projects</a> <span>/</span>
            <span>{project_data.get('name', 'Unknown')}</span> <span>/</span>
            <span>Report</span>
        </div>

        <section class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{execution_results.get('total_tests', 0)}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{execution_results.get('passed_tests', 0)}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{execution_results.get('failed_tests', 0)}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{execution_results.get('pass_rate', 0)}%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
        </section>

        <section class="service-card">
            <h3>📋 Execution Details</h3>
            <div class="form-row">
                <div><strong>Execution ID:</strong> {execution_results.get('execution_id', 'N/A')}</div>
                <div><strong>Start Time:</strong> {execution_results.get('start_time', 'N/A')}</div>
                <div><strong>Duration:</strong> {execution_results.get('duration', 'N/A')}</div>
                <div><strong>Environment:</strong> {execution_results.get('environment', 'Production')}</div>
            </div>
        </section>

        <section class="service-card">
            <h3>🧪 Test Results</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Test Case</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Message</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_test_rows(execution_results.get('test_cases', []))}
                </tbody>
            </table>
        </section>
    </div>
</body>
</html>
        """
        return template
    
    def _generate_test_rows(self, test_cases):
        rows = ""
        for test in test_cases:
            status_class = "badge-success" if test.get('status') == 'passed' else "badge-error"
            rows += f"""
            <tr>
                <td>{test.get('name', 'Unknown Test')}</td>
                <td><span class="badge {status_class}">{test.get('status', 'unknown').upper()}</span></td>
                <td>{test.get('duration', 'N/A')}</td>
                <td>{test.get('message', '')}</td>
            </tr>
            """
        return rows
    
    def get_project_reports_url(self, project_id):
        return f"{self.base_url}/projects/{project_id}/reports/"
    
    def get_project_dashboard_url(self, project_id):
        return f"{self.base_url}/projects/{project_id}/dashboard/"
