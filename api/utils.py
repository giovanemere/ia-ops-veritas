import os
import redis
import psycopg2
from minio import Minio
import json
from datetime import datetime, timedelta
import logging
from config_manager import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        # Only basic connection from env, everything else from config DB
        self.host = os.getenv('POSTGRES_HOST', 'veritas-postgres')
        self.database = os.getenv('POSTGRES_DB', 'veritas')
        self.user = os.getenv('POSTGRES_USER', 'postgres')
        self.password = os.getenv('POSTGRES_PASSWORD', 'postgres123')
        self._connection = None
    
    def get_connection(self):
        if not self._connection or self._connection.closed:
            pool_size = config.get_config('db_connection_pool_size', 10)
            self._connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
        return self._connection
    
    def execute_query(self, query, params=None):
        timeout = config.get_config('db_query_timeout', 30)
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if cur.description:
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in cur.fetchall()]
                return []

class CacheManager:
    def __init__(self):
        # Redis connection from config
        self.host = config.get_config('redis_host', 'veritas-redis')
        self.port = config.get_config('redis_port', 6379)
        self._redis_client = None
    
    def get_client(self):
        if not self._redis_client:
            self._redis_client = redis.Redis(
                host=self.host, 
                port=self.port, 
                decode_responses=True
            )
        return self._redis_client
    
    def get(self, key):
        try:
            client = self.get_client()
            data = client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key, value, ttl=None):
        try:
            if ttl is None:
                ttl = config.get_config('cache_ttl_default', 3600)
            
            client = self.get_client()
            client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key):
        try:
            client = self.get_client()
            client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern):
        """Clear all keys matching pattern"""
        try:
            client = self.get_client()
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return False

class StorageManager:
    def __init__(self):
        self._client = None
        self._bucket = None
    
    def get_client(self):
        if not self._client:
            endpoint = config.get_config('minio_endpoint', '172.21.48.1:9898')
            access_key = config.get_config('minio_access_key', 'minioadmin')
            secret_key = config.get_config('minio_secret_key', 'minioadmin123')
            secure = config.get_config('minio_secure', False)
            
            self._client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
        return self._client
    
    def get_bucket(self):
        if not self._bucket:
            self._bucket = config.get_config('minio_bucket', 'veritas-storage')
            self._ensure_bucket()
        return self._bucket
    
    def _ensure_bucket(self):
        try:
            client = self.get_client()
            if not client.bucket_exists(self._bucket):
                client.make_bucket(self._bucket)
                logger.info(f"Created MinIO bucket: {self._bucket}")
        except Exception as e:
            logger.error(f"Bucket creation error: {e}")
    
    def upload_file(self, object_name, data, content_type='application/octet-stream', storage_type='general'):
        """Upload file to MinIO with organized paths"""
        try:
            from io import BytesIO
            
            # Get storage paths from config
            storage_paths = config.get_config('storage_paths', {})
            base_path = storage_paths.get(storage_type, 'general')
            
            # Organize by date
            date_path = datetime.now().strftime('%Y/%m/%d')
            full_object_name = f"{base_path}/{date_path}/{object_name}"
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            client = self.get_client()
            bucket = self.get_bucket()
            
            client.put_object(
                bucket,
                full_object_name,
                BytesIO(data),
                length=len(data),
                content_type=content_type
            )
            
            endpoint = config.get_config('minio_endpoint')
            return {
                'url': f"http://{endpoint}/{bucket}/{full_object_name}",
                'bucket': bucket,
                'object_name': full_object_name,
                'size': len(data)
            }
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return None
    
    def get_file_url(self, object_name):
        """Get public URL for file"""
        endpoint = config.get_config('minio_endpoint')
        bucket = self.get_bucket()
        return f"http://{endpoint}/{bucket}/{object_name}"
    
    def delete_file(self, object_name):
        """Delete file from MinIO"""
        try:
            client = self.get_client()
            bucket = self.get_bucket()
            client.remove_object(bucket, object_name)
            return True
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
    
    def list_files(self, prefix='', limit=100):
        """List files in bucket with prefix"""
        try:
            client = self.get_client()
            bucket = self.get_bucket()
            
            objects = client.list_objects(bucket, prefix=prefix, recursive=True)
            files = []
            
            for obj in objects:
                if len(files) >= limit:
                    break
                files.append({
                    'name': obj.object_name,
                    'size': obj.size,
                    'last_modified': obj.last_modified.isoformat() if obj.last_modified else None,
                    'url': self.get_file_url(obj.object_name)
                })
            
            return files
        except Exception as e:
            logger.error(f"List files error: {e}")
            return []

# Global instances
db = DatabaseManager()
cache = CacheManager()
storage = StorageManager()
