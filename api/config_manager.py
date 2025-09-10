import os
import psycopg2
import redis
import json
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.db_host = os.getenv('POSTGRES_HOST', 'veritas-postgres')
        self.db_name = os.getenv('POSTGRES_DB', 'veritas')
        self.db_user = os.getenv('POSTGRES_USER', 'postgres')
        self.db_password = os.getenv('POSTGRES_PASSWORD', 'postgres123')
        self.redis_host = os.getenv('REDIS_HOST', 'veritas-redis')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        self._db_conn = None
        self._redis_conn = None
        self._config_cache = {}
    
    def get_db_connection(self):
        if not self._db_conn or self._db_conn.closed:
            self._db_conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
        return self._db_conn
    
    def get_redis_connection(self):
        if not self._redis_conn:
            self._redis_conn = redis.Redis(
                host=self.redis_host, 
                port=self.redis_port, 
                decode_responses=True
            )
        return self._redis_conn
    
    def get_config(self, key, default=None):
        # Check memory cache
        if key in self._config_cache:
            return self._config_cache[key]
        
        try:
            # Check Redis
            redis_conn = self.get_redis_connection()
            cached_value = redis_conn.get(f"config:{key}")
            if cached_value:
                value = json.loads(cached_value) if cached_value.startswith('{') else cached_value
                self._config_cache[key] = value
                return value
        except:
            pass
        
        try:
            # Get from database
            db_conn = self.get_db_connection()
            with db_conn.cursor() as cur:
                cur.execute("SELECT config_value FROM configuration WHERE config_key = %s", (key,))
                result = cur.fetchone()
                if result:
                    value = json.loads(result[0]) if result[0].startswith('{') else result[0]
                    # Cache it
                    try:
                        redis_conn.setex(f"config:{key}", 3600, result[0])
                    except:
                        pass
                    self._config_cache[key] = value
                    return value
        except Exception as e:
            logger.error(f"Config error for {key}: {e}")
        
        return default

config = ConfigManager()
