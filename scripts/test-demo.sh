#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🧪 IA-Ops Veritas - Demo de Testing Completo${NC}"
echo "================================================"

echo -e "${YELLOW}📋 1. Creando casos de prueba...${NC}"

# Crear caso de prueba 1
echo -e "${CYAN}   → Creando 'User Registration Test'${NC}"
TEST1_RESPONSE=$(curl -s -X POST http://localhost:8870/api/tests \
  -H "Content-Type: application/json" \
  -d '{
    "name": "User Registration Test",
    "description": "Test complete user registration flow",
    "suite": "Authentication",
    "priority": "high"
  }')

TEST1_ID=$(echo $TEST1_RESPONSE | jq -r '.id')
echo -e "   ✅ Test creado con ID: ${GREEN}$TEST1_ID${NC}"

# Crear caso de prueba 2
echo -e "${CYAN}   → Creando 'Database Connection Test'${NC}"
TEST2_RESPONSE=$(curl -s -X POST http://localhost:8870/api/tests \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Database Connection Test",
    "description": "Test database connectivity and queries",
    "suite": "Infrastructure",
    "priority": "critical"
  }')

TEST2_ID=$(echo $TEST2_RESPONSE | jq -r '.id')
echo -e "   ✅ Test creado con ID: ${GREEN}$TEST2_ID${NC}"

echo ""
echo -e "${YELLOW}🚀 2. Ejecutando pruebas...${NC}"

# Ejecutar prueba 1
echo -e "${CYAN}   → Ejecutando 'User Registration Test'${NC}"
EXEC1_RESPONSE=$(curl -s -X POST http://localhost:8871/api/executions \
  -H "Content-Type: application/json" \
  -d "{
    \"test_id\": \"$TEST1_ID\",
    \"test_name\": \"User Registration Test\",
    \"environment\": \"staging\"
  }")

EXEC1_ID=$(echo $EXEC1_RESPONSE | jq -r '.id')
echo -e "   ✅ Ejecución iniciada con ID: ${GREEN}$EXEC1_ID${NC}"

# Ejecutar prueba 2
echo -e "${CYAN}   → Ejecutando 'Database Connection Test'${NC}"
EXEC2_RESPONSE=$(curl -s -X POST http://localhost:8871/api/executions \
  -H "Content-Type: application/json" \
  -d "{
    \"test_id\": \"$TEST2_ID\",
    \"test_name\": \"Database Connection Test\",
    \"environment\": \"production\"
  }")

EXEC2_ID=$(echo $EXEC2_RESPONSE | jq -r '.id')
echo -e "   ✅ Ejecución iniciada con ID: ${GREEN}$EXEC2_ID${NC}"

echo ""
echo -e "${YELLOW}⏳ 3. Simulando tiempo de ejecución...${NC}"
sleep 3

echo -e "${YELLOW}✅ 4. Completando ejecuciones...${NC}"

# Completar ejecución 1 (exitosa)
echo -e "${CYAN}   → Completando 'User Registration Test'${NC}"
curl -s -X POST http://localhost:8871/api/executions/$EXEC1_ID/complete \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "result": "passed",
    "duration": 67
  }' > /dev/null

echo -e "   ✅ ${GREEN}PASSED${NC} - User Registration Test (67s)"

# Completar ejecución 2 (fallida)
echo -e "${CYAN}   → Completando 'Database Connection Test'${NC}"
curl -s -X POST http://localhost:8871/api/executions/$EXEC2_ID/complete \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "result": "failed",
    "duration": 23
  }' > /dev/null

echo -e "   ❌ ${YELLOW}FAILED${NC} - Database Connection Test (23s)"

echo ""
echo -e "${YELLOW}📊 5. Estadísticas de ejecución:${NC}"
curl -s http://localhost:8871/api/stats | jq -r '"   Total: \(.total_executions) | Completadas: \(.completed) | Tasa de éxito: \(.success_rate)%"'

echo ""
echo -e "${YELLOW}📈 6. Métricas de calidad:${NC}"
curl -s http://localhost:8872/api/metrics | jq -r '"   Cobertura: \(.code_coverage)% | Calidad: \(.code_quality_score)/10 | Tasa de éxito: \(.test_pass_rate)%"'

echo ""
echo -e "${YELLOW}📋 7. Generando reporte de evidencias...${NC}"
REPORT_RESPONSE=$(curl -s -X POST http://localhost:8873/api/reports \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Test Execution Report",
    "type": "pdf",
    "include_evidence": true,
    "include_metrics": true
  }')

REPORT_ID=$(echo $REPORT_RESPONSE | jq -r '.id')
echo -e "   ✅ Reporte generado con ID: ${GREEN}$REPORT_ID${NC}"

echo ""
echo -e "${GREEN}🎉 Demo completado exitosamente!${NC}"
echo ""
echo -e "${BLUE}📊 Resumen de URLs de acceso:${NC}"
echo -e "   Test Manager:          ${YELLOW}http://localhost:8870${NC}"
echo -e "   Test Execution Engine: ${YELLOW}http://localhost:8871${NC}"
echo -e "   Quality Analytics:     ${YELLOW}http://localhost:8872${NC}"
echo -e "   Evidence Manager:      ${YELLOW}http://localhost:8873${NC}"
echo ""
echo -e "${CYAN}💡 Prueba los endpoints manualmente:${NC}"
echo -e "   curl http://localhost:8870/api/tests"
echo -e "   curl http://localhost:8871/api/executions"
echo -e "   curl http://localhost:8872/api/metrics"
echo -e "   curl http://localhost:8873/api/evidence"
