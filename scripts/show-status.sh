#!/bin/bash

echo "🧪 Veritas Testing Platform - Status Report"
echo "=========================================="
echo ""

# Check service status
echo "📊 Service Status:"
docker ps --filter "name=iaops-veritas-unified" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null

echo ""
echo "🔍 Health Check:"
health_response=$(curl -s http://localhost:8869/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Service is healthy"
    echo "$health_response" | jq . 2>/dev/null || echo "$health_response"
else
    echo "❌ Service is not responding"
fi

echo ""
echo "📈 Statistics:"
stats_response=$(curl -s http://localhost:8869/api/stats 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "$stats_response" | jq . 2>/dev/null || echo "$stats_response"
else
    echo "❌ Cannot retrieve statistics"
fi

echo ""
echo "🗂️  MinIO Storage:"
echo "  📊 Console: http://localhost:9899"
echo "  🗂️  Bucket: veritas-projects"
echo "  🔑 Credentials: minioadmin / minioadmin123"

echo ""
echo "🌐 Access URLs:"
echo "  🏠 Main Portal: http://localhost:8869"
echo "  📊 MinIO Console: http://localhost:9899"

echo ""
echo "🔧 Management Commands:"
echo "  View logs: docker logs iaops-veritas-unified -f"
echo "  Stop service: docker-compose down"
echo "  Restart: ./scripts/start-unified.sh"
echo "  Status: ./scripts/show-status.sh"

echo ""
echo "📁 Storage Organization:"
echo "  ├── projects/           # Testing projects"
echo "  │   └── {project-name}/ # Individual projects"
echo "  ├── templates/          # Reusable templates"
echo "  ├── shared/             # Shared resources"
echo "  ├── archives/           # Completed projects"
echo "  └── temp/               # Temporary files"

echo ""
echo "✨ Veritas is running in unified mode for optimal performance!"
