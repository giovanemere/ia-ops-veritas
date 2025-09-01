#!/bin/bash

echo "🚀 Deploying IA-Ops Veritas Full Stack..."

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/infrastructure.yml down

# Clean up
echo "🧹 Cleaning up..."
docker system prune -f

# Start infrastructure (PostgreSQL, Redis, MinIO)
echo "🏗️  Starting infrastructure..."
cd docker
docker-compose -f infrastructure.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for infrastructure to be ready..."
sleep 30

# Start Veritas services
echo "🧪 Starting Veritas services..."
docker-compose -f docker-compose.yml up -d

# Wait for all services
echo "⏳ Waiting for all services to start..."
sleep 45

# Test all services
echo "🔍 Testing services..."
echo "Infrastructure:"
echo "  PostgreSQL: $(docker exec veritas-postgres pg_isready -U veritas_user -d veritas_db > /dev/null 2>&1 && echo '✅' || echo '❌')"
echo "  Redis: $(docker exec veritas-redis redis-cli ping > /dev/null 2>&1 && echo '✅' || echo '❌')"
echo "  MinIO: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:9898/minio/health/live | grep -q 200 && echo '✅' || echo '❌')"

echo ""
echo "Backend API:"
echo "  Backend API: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8880/health | grep -q 200 && echo '✅' || echo '❌')"

echo ""
echo "Frontend:"
echo "  React App: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q 200 && echo '✅' || echo '❌')"

echo ""
echo "Veritas Services:"
echo "  Unified Portal: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8876 | grep -q 200 && echo '✅' || echo '❌')"
echo "  Test Results: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8877 | grep -q 200 && echo '✅' || echo '❌')"
echo "  Project Manager: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8874 | grep -q 200 && echo '✅' || echo '❌')"

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "📱 ACCESS POINTS:"
echo "  🌐 React Frontend: http://localhost:3000"
echo "  🧪 Unified Portal: http://localhost:8876"
echo "  🔧 Backend API: http://localhost:8880"
echo "  🗂️  MinIO Console: http://localhost:9899 (minioadmin/minioadmin)"
echo ""
echo "🔗 INTEGRATION FLOW:"
echo "  Frontend (3000) → Backend API (8880) → PostgreSQL (5432) + Redis (6379) + MinIO (9898)"
echo "  Portal Services (8869-8877) → Backend API → Database"
echo ""
echo "📊 NEXT STEPS:"
echo "  1. Open http://localhost:3000 for React frontend"
echo "  2. Open http://localhost:8876 for unified portal"
echo "  3. Create projects and test the full integration"
