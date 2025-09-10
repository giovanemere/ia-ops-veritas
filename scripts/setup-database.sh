#!/bin/bash

echo "🗄️ Setting up Veritas Database..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until docker exec veritas-postgres pg_isready -U postgres; do
  sleep 2
done

# Create database and tables
echo "📊 Creating database schema..."
docker exec -i veritas-postgres psql -U postgres << 'EOF'
-- Create database
CREATE DATABASE veritas;

-- Connect to veritas database
\c veritas;

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    repository_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test suites table
CREATE TABLE IF NOT EXISTS test_suites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test cases table
CREATE TABLE IF NOT EXISTS test_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    suite_id UUID REFERENCES test_suites(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_type VARCHAR(50),
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test executions table
CREATE TABLE IF NOT EXISTS test_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    suite_id UUID REFERENCES test_suites(id),
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    environment VARCHAR(100),
    total_tests INTEGER DEFAULT 0,
    passed_tests INTEGER DEFAULT 0,
    failed_tests INTEGER DEFAULT 0,
    coverage_percentage DECIMAL(5,2),
    minio_report_path VARCHAR(500)
);

-- Test results table
CREATE TABLE IF NOT EXISTS test_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID REFERENCES test_executions(id) ON DELETE CASCADE,
    test_case_id UUID REFERENCES test_cases(id),
    status VARCHAR(20),
    duration_ms INTEGER,
    error_message TEXT,
    minio_evidence_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Evidence table
CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_result_id UUID REFERENCES test_results(id) ON DELETE CASCADE,
    evidence_type VARCHAR(50),
    filename VARCHAR(255),
    minio_bucket VARCHAR(100),
    minio_object_path VARCHAR(500),
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quality metrics table
CREATE TABLE IF NOT EXISTS quality_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    execution_id UUID REFERENCES test_executions(id),
    metric_name VARCHAR(100),
    metric_value DECIMAL(10,4),
    metric_unit VARCHAR(20),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configuration table
CREATE TABLE IF NOT EXISTS configuration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default configuration
INSERT INTO configuration (config_key, config_value, description) VALUES
('minio_endpoint', '172.21.48.1:9898', 'MinIO server endpoint'),
('minio_bucket', 'veritas-storage', 'Default MinIO bucket for all storage'),
('redis_endpoint', 'veritas-redis:6379', 'Redis cache endpoint'),
('cache_ttl', '3600', 'Default cache TTL in seconds')
ON CONFLICT (config_key) DO NOTHING;

-- Sample data
INSERT INTO projects (name, description, repository_url) VALUES
('Sample Test Project', 'Demo project for testing', 'https://github.com/sample/repo.git')
ON CONFLICT DO NOTHING;

EOF

echo "✅ Database setup completed!"

# Setup MinIO bucket
echo "🪣 Setting up MinIO bucket..."
docker exec minio-server mc alias set local http://localhost:9000 minioadmin minioadmin123
docker exec minio-server mc mb local/veritas-storage --ignore-existing
docker exec minio-server mc policy set public local/veritas-storage

echo "✅ MinIO bucket setup completed!"
echo "🎉 Veritas infrastructure is ready!"
