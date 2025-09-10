#!/usr/bin/env python3
"""
Script to organize MinIO storage by projects for Veritas
"""
import os
from minio import Minio
from minio.error import S3Error
import json
from io import BytesIO

def setup_minio_projects():
    # MinIO connection
    client = Minio(
        'localhost:9898',
        access_key='minioadmin',
        secret_key='minioadmin123',
        secure=False
    )
    
    bucket_name = 'veritas-projects'
    
    try:
        # Create main bucket if not exists
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"✅ Created bucket: {bucket_name}")
        else:
            print(f"✅ Bucket already exists: {bucket_name}")
        
        # Create organized folder structure
        folders = [
            'projects/',
            'projects/sample-project/',
            'projects/sample-project/tests/',
            'projects/sample-project/evidence/',
            'projects/sample-project/reports/',
            'templates/',
            'templates/test-cases/',
            'templates/reports/',
            'shared/',
            'shared/assets/',
            'shared/configs/',
            'archives/',
            'archives/completed-projects/',
            'temp/',
            'temp/uploads/'
        ]
        
        for folder in folders:
            try:
                # Create empty object to represent folder
                client.put_object(bucket_name, folder, BytesIO(b''), 0)
                print(f"📁 Created folder: {folder}")
            except S3Error as e:
                if 'already exists' not in str(e):
                    print(f"❌ Error creating folder {folder}: {e}")
        
        # Create a sample project structure
        sample_config = {
            "project_name": "sample-project",
            "description": "Sample testing project for demonstration",
            "created_at": "2024-01-01T00:00:00Z",
            "test_types": ["unit", "integration", "e2e"],
            "storage_paths": {
                "tests": "projects/sample-project/tests/",
                "evidence": "projects/sample-project/evidence/",
                "reports": "projects/sample-project/reports/"
            }
        }
        
        config_json = json.dumps(sample_config, indent=2).encode('utf-8')
        client.put_object(
            bucket_name, 
            'projects/sample-project/config.json', 
            BytesIO(config_json), 
            len(config_json),
            content_type='application/json'
        )
        print("📄 Created sample project configuration")
        
        # Create README for organization
        readme_content = """# Veritas Projects Storage Organization

## Folder Structure:

### /projects/
- Contains all testing projects
- Each project has its own subfolder
- Structure: /projects/{project-name}/

### /projects/{project-name}/
- tests/ - Test case files and scripts
- evidence/ - Test execution evidence (screenshots, logs, etc.)
- reports/ - Generated test reports
- config.json - Project configuration

### /templates/
- Reusable templates for test cases and reports
- test-cases/ - Test case templates
- reports/ - Report templates

### /shared/
- Shared resources across projects
- assets/ - Common assets (images, files)
- configs/ - Shared configuration files

### /archives/
- Completed or archived projects
- completed-projects/ - Archived project data

### /temp/
- Temporary files and uploads
- uploads/ - Temporary upload area

## Usage:
1. Create new project folder under /projects/
2. Use the folder structure for organized storage
3. Reference files using the organized paths
4. Archive completed projects to /archives/

Access via: http://localhost:9899 (MinIO Console)
""".encode('utf-8')
        
        client.put_object(
            bucket_name,
            'README.md',
            BytesIO(readme_content),
            len(readme_content),
            content_type='text/markdown'
        )
        print("📖 Created storage organization README")
        
        print(f"\n🎉 MinIO storage organized successfully!")
        print(f"📊 Access MinIO Console: http://localhost:9899")
        print(f"🗂️  Bucket: {bucket_name}")
        print(f"🔑 Credentials: minioadmin / minioadmin123")
        
    except Exception as e:
        print(f"❌ Error setting up MinIO: {e}")

if __name__ == "__main__":
    setup_minio_projects()
