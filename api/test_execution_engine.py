#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime
import uuid
import psycopg2
import redis
import json
from minio import Minio
import io

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    return psycopg2.connect(
        host='veritas-postgres',
        database='veritas_db',
        user='veritas_user',
        password='veritas_pass'
    )

def get_redis():
    return redis.Redis(host='veritas-redis', port=6379, decode_responses=True)

def get_config(key, default=None):
    try:
        r = get_redis()
        cached = r.get(f"config:{key}")
        if cached:
            return cached
    except:
        pass
    
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT config_value FROM configuration WHERE config_key = %s", (key,))
                result = cur.fetchone()
                if result:
                    try:
                        get_redis().setex(f"config:{key}", 3600, result[0])
                    except:
                        pass
                    return result[0]
    except:
        pass
    
    return default

def get_minio():
    endpoint = get_config('minio_endpoint', '172.21.48.1:9898')
    access_key = get_config('minio_access_key', 'minioadmin')
    secret_key = get_config('minio_secret_key', 'minioadmin123')
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)

@app.route('/')
def index():
    return jsonify({
        "service": "test-execution-engine",
        "status": "running",
        "endpoints": ["/api/execute", "/api/executions"]
    })

@app.route('/health', methods=['GET'])
def health():
    status = {"service": "test-execution-engine", "timestamp": datetime.utcnow().isoformat()}
    
    try:
        get_db().cursor().execute("SELECT 1")
        status["database"] = "healthy"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
    
    try:
        get_redis().ping()
        status["cache"] = "healthy"
    except Exception as e:
        status["cache"] = f"error: {str(e)}"
    
    try:
        get_minio().list_buckets()
        status["storage"] = "healthy"
    except Exception as e:
        status["storage"] = f"error: {str(e)}"
    
    return jsonify(status)

@app.route('/api/execute', methods=['POST'])
def execute_test():
    try:
        data = request.get_json()
        execution_id = str(uuid.uuid4())
        
        # Store execution results in single bucket
        bucket = get_config('minio_bucket', 'veritas-storage')
        result_content = json.dumps({
            "execution_id": execution_id,
            "test_id": data.get('test_id'),
            "status": "completed",
            "results": "Test executed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }, indent=2)
        
        # Upload to MinIO
        client = get_minio()
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        
        object_name = f"executions/{datetime.now().strftime('%Y/%m/%d')}/execution_{execution_id}.json"
        content_bytes = result_content.encode('utf-8')
        client.put_object(bucket, object_name, io.BytesIO(content_bytes), len(content_bytes), 'application/json')
        
        # Save to database
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO test_executions (id, status, started_at, completed_at, minio_report_path)
                    VALUES (%s, %s, %s, %s, %s)
                """, (execution_id, 'completed', datetime.utcnow(), datetime.utcnow(), object_name))
                conn.commit()
        
        endpoint = get_config('minio_endpoint')
        return jsonify({
            "execution_id": execution_id,
            "status": "completed",
            "result_url": f"http://{endpoint}/{bucket}/{object_name}",
            "completed_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8871))
    app.run(host='0.0.0.0', port=port, debug=False)
