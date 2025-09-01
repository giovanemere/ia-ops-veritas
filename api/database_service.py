#!/usr/bin/env python3
import psycopg2
import redis
import json
from datetime import datetime
import uuid

class DatabaseService:
    def __init__(self):
        self.pg_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'veritas_db',
            'user': 'veritas_user',
            'password': 'veritas_pass'
        }
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.init_database()
    
    def get_pg_connection(self):
        return psycopg2.connect(**self.pg_config)
    
    def init_database(self):
        try:
            conn = self.get_pg_connection()
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    repository VARCHAR(500),
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS test_suites (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id UUID REFERENCES projects(id),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS test_cases (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    suite_id UUID REFERENCES test_suites(id),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    priority VARCHAR(20) DEFAULT 'medium',
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS test_executions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id UUID REFERENCES projects(id),
                    execution_name VARCHAR(255),
                    status VARCHAR(20) DEFAULT 'running',
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    results JSONB,
                    report_url VARCHAR(500)
                );
                
                CREATE TABLE IF NOT EXISTS user_stories (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id UUID REFERENCES projects(id),
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    acceptance_criteria JSONB,
                    priority VARCHAR(20) DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    # Project operations
    def create_project(self, data):
        conn = self.get_pg_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects (name, repository, description)
            VALUES (%s, %s, %s) RETURNING id, created_at
        """, (data['name'], data.get('repository'), data.get('description')))
        
        project_id, created_at = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        # Cache in Redis
        project_data = {
            'id': str(project_id),
            'name': data['name'],
            'repository': data.get('repository'),
            'description': data.get('description'),
            'status': 'active',
            'created_at': created_at.isoformat()
        }
        self.redis_client.setex(f"project:{project_id}", 3600, json.dumps(project_data))
        
        return project_data
    
    def get_projects(self):
        # Try Redis first
        cached_projects = self.redis_client.get("projects:all")
        if cached_projects:
            return json.loads(cached_projects)
        
        # Fallback to PostgreSQL
        conn = self.get_pg_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, repository, description, status, created_at FROM projects ORDER BY created_at DESC")
        projects = []
        
        for row in cursor.fetchall():
            projects.append({
                'id': str(row[0]),
                'name': row[1],
                'repository': row[2],
                'description': row[3],
                'status': row[4],
                'created_at': row[5].isoformat()
            })
        
        cursor.close()
        conn.close()
        
        # Cache for 5 minutes
        self.redis_client.setex("projects:all", 300, json.dumps(projects))
        return projects
    
    # Test execution operations
    def create_execution(self, project_id, execution_data):
        conn = self.get_pg_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO test_executions (project_id, execution_name, results, report_url)
            VALUES (%s, %s, %s, %s) RETURNING id, start_time
        """, (project_id, execution_data.get('name'), json.dumps(execution_data.get('results')), execution_data.get('report_url')))
        
        execution_id, start_time = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'id': str(execution_id),
            'project_id': project_id,
            'start_time': start_time.isoformat(),
            'status': 'completed'
        }
    
    def get_project_executions(self, project_id):
        conn = self.get_pg_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, execution_name, status, start_time, end_time, results, report_url
            FROM test_executions WHERE project_id = %s ORDER BY start_time DESC
        """, (project_id,))
        
        executions = []
        for row in cursor.fetchall():
            executions.append({
                'id': str(row[0]),
                'name': row[1],
                'status': row[2],
                'start_time': row[3].isoformat() if row[3] else None,
                'end_time': row[4].isoformat() if row[4] else None,
                'results': row[5],
                'report_url': row[6]
            })
        
        cursor.close()
        conn.close()
        return executions
    
    # User stories operations
    def create_user_story(self, project_id, story_data):
        conn = self.get_pg_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_stories (project_id, title, description, acceptance_criteria, priority)
            VALUES (%s, %s, %s, %s, %s) RETURNING id, created_at
        """, (project_id, story_data['title'], story_data.get('description'), 
              json.dumps(story_data.get('acceptance_criteria', [])), story_data.get('priority', 'medium')))
        
        story_id, created_at = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'id': str(story_id),
            'project_id': project_id,
            'title': story_data['title'],
            'created_at': created_at.isoformat()
        }
    
    def get_project_user_stories(self, project_id):
        conn = self.get_pg_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, description, acceptance_criteria, priority, created_at
            FROM user_stories WHERE project_id = %s ORDER BY created_at DESC
        """, (project_id,))
        
        stories = []
        for row in cursor.fetchall():
            stories.append({
                'id': str(row[0]),
                'title': row[1],
                'description': row[2],
                'acceptance_criteria': row[3],
                'priority': row[4],
                'created_at': row[5].isoformat()
            })
        
        cursor.close()
        conn.close()
        return stories
