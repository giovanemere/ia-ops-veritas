import os

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'host.docker.internal'),
    'port': int(os.getenv('POSTGRES_PORT', '5434')),
    'database': os.getenv('POSTGRES_DB', 'veritas_db'),
    'user': os.getenv('POSTGRES_USER', 'veritas'),
    'password': os.getenv('POSTGRES_PASSWORD', 'veritas123')
}

# Redis Configuration
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'host.docker.internal'),
    'port': int(os.getenv('REDIS_PORT', '6380'))
}

# MinIO Configuration
MINIO_CONFIG = {
    'endpoint': os.getenv('MINIO_ENDPOINT', 'host.docker.internal:9898'),
    'access_key': os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
    'secret_key': os.getenv('MINIO_SECRET_KEY', 'minioadmin123'),
    'bucket': os.getenv('MINIO_BUCKET', 'veritas-projects')
}
