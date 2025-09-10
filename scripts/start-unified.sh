#!/bin/bash

echo "🧪 Starting Veritas Unified Service..."

# Change to project directory
cd "$(dirname "$0")/.."

# Stop existing services
echo "🛑 Stopping existing Veritas services..."
docker-compose down 2>/dev/null || true
docker-compose -f docker/docker-compose.yml down 2>/dev/null || true
docker-compose -f docker/docker-compose.unified.yml down 2>/dev/null || true

# Remove old containers
echo "🧹 Cleaning up old containers..."
docker rm -f $(docker ps -aq --filter "name=iaops-veritas-*" --filter "name=iaops-test-*" --filter "name=iaops-evidence-*" --filter "name=iaops-quality-*") 2>/dev/null || true

# Setup MinIO projects organization
echo "🗂️  Setting up MinIO projects organization..."
if [ -d "temp_venv" ]; then
    temp_venv/bin/python scripts/setup-minio-projects.py
else
    echo "⚠️  Skipping MinIO setup (no virtual environment)"
fi

# Build and start unified service
echo "🚀 Building and starting unified Veritas service..."
docker-compose up --build -d

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 15

# Check health
echo "🔍 Checking service health..."
for i in {1..30}; do
    if curl -s http://localhost:8869/health > /dev/null; then
        echo "✅ Veritas Unified Service is ready!"
        break
    fi
    echo "⏳ Waiting for service... ($i/30)"
    sleep 2
done

# Show status
echo ""
echo "📊 Service Status:"
docker ps --filter "name=iaops-veritas-unified" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🌐 Access URLs:"
echo "  🏠 Main Portal: http://localhost:8869"
echo "  📊 MinIO Console: http://localhost:9899"
echo ""
echo "🔧 Management Commands:"
echo "  View logs: docker logs iaops-veritas-unified -f"
echo "  Stop service: docker-compose down"
echo "  Restart: ./scripts/start-unified.sh"
echo ""
echo "✨ Veritas Unified Service started successfully!"
