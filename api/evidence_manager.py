#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime
import uuid
import io
import psycopg2
import redis
import json
from minio import Minio

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use existing PostgreSQL and Redis
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
    with open('/app/templates/evidence_manager.html', 'r') as f:
        return f.read()

@app.route('/health', methods=['GET'])
def health():
    status = {"service": "evidence-manager", "timestamp": datetime.utcnow().isoformat()}
    
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

@app.route('/api/evidence', methods=['POST'])
def upload_evidence():
    try:
        data = request.get_json()
        test_id = data.get('test_id')
        filename = data.get('filename', f'evidence_{uuid.uuid4().hex[:8]}.txt')
        content = data.get('content', '')
        
        if not test_id:
            return jsonify({"error": "test_id is required"}), 400
        
        # Single bucket for all storage
        bucket = get_config('minio_bucket', 'veritas-storage')
        object_name = f"evidence/{datetime.now().strftime('%Y/%m/%d')}/{filename}"
        
        # Upload to MinIO
        client = get_minio()
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        
        content_bytes = content.encode('utf-8')
        client.put_object(bucket, object_name, io.BytesIO(content_bytes), len(content_bytes))
        
        # Save to database
        evidence_id = str(uuid.uuid4())
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO evidence (id, test_result_id, evidence_type, filename, 
                                        minio_bucket, minio_object_path, file_size)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (evidence_id, test_id, 'file', filename, bucket, object_name, len(content_bytes)))
                conn.commit()
        
        # Clear cache
        try:
            get_redis().delete("evidence_list")
        except:
            pass
        
        endpoint = get_config('minio_endpoint')
        return jsonify({
            "evidence_id": evidence_id,
            "filename": filename,
            "bucket": bucket,
            "object_path": object_name,
            "file_url": f"http://{endpoint}/{bucket}/{object_name}",
            "console_url": f"http://localhost:9899/browser/{bucket}/{object_name}",
            "uploaded_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports', methods=['POST'])
def generate_report():
    try:
        data = request.get_json()
        
        report_content = f"""
        <html><head><title>Test Report</title></head>
        <body><h1>Test Report</h1><p>Generated: {datetime.utcnow().isoformat()}</p>
        <pre>{json.dumps(data, indent=2)}</pre></body></html>
        """
        
        # Single bucket for all storage
        bucket = get_config('minio_bucket', 'veritas-storage')
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.html"
        object_name = f"reports/{datetime.now().strftime('%Y/%m/%d')}/{filename}"
        
        # Upload to MinIO
        client = get_minio()
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        
        content_bytes = report_content.encode('utf-8')
        client.put_object(bucket, object_name, io.BytesIO(content_bytes), len(content_bytes), 'text/html')
        
        endpoint = get_config('minio_endpoint')
        return jsonify({
            "filename": filename,
            "bucket": bucket,
            "object_path": object_name,
            "file_url": f"http://{endpoint}/{bucket}/{object_name}",
            "console_url": f"http://localhost:9899/browser/{bucket}/{object_name}",
            "generated_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8873))
    app.run(host='0.0.0.0', port=port, debug=False)
