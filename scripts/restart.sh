#!/bin/bash

echo "🔄 Reiniciando IA-Ops Veritas..."

# Reiniciar contenedores Docker
docker-compose restart

echo "✅ Veritas reiniciado"
echo "📊 API disponible en: http://localhost:8081"
echo "📋 Swagger UI: http://localhost:8081/docs"
