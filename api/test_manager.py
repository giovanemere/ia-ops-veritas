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

@app.route('/')
def index():
    with open('/app/templates/test_manager.html', 'r') as f:
        return f.read()

@app.route('/health', methods=['GET'])
def health():
    status = {"service": "test-manager", "timestamp": datetime.utcnow().isoformat()}
    
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
    
    return jsonify(status)

@app.route('/api/test-cases', methods=['GET'])
def get_test_cases():
    cache_key = "test_cases_list"
    
    try:
        cached = get_redis().get(cache_key)
        if cached:
            return jsonify(json.loads(cached))
    except:
        pass
    
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM test_cases ORDER BY created_at DESC LIMIT 100")
                columns = [desc[0] for desc in cur.description] if cur.description else []
                cases = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        result = {"test_cases": cases}
        try:
            get_redis().setex(cache_key, 300, json.dumps(result, default=str))
        except:
            pass
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"test_cases": [], "error": str(e)}), 500

@app.route('/api/test-cases', methods=['POST'])
def create_test_case():
    try:
        data = request.get_json()
        test_case_id = str(uuid.uuid4())
        
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO test_cases (id, name, description, test_type, priority, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (test_case_id, data.get('name'), data.get('description'), 
                      data.get('test_type', 'unit'), data.get('priority', 'medium'), 'active'))
                conn.commit()
        
        # Clear cache
        try:
            get_redis().delete("test_cases_list")
        except:
            pass
        
        return jsonify({
            "id": test_case_id,
            "name": data.get('name'),
            "created_at": datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8870))
    app.run(host='0.0.0.0', port=port, debug=False)
