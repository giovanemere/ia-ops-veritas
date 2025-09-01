#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🧪 IA-Ops Veritas - Service Status${NC}"
echo "=================================="

# Check Docker containers
echo -e "${YELLOW}📦 Container Status:${NC}"
docker ps --filter "name=iaops-test-manager\|iaops-test-execution-engine\|iaops-quality-analytics\|iaops-evidence-manager" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo -e "${YELLOW}🔍 Health Check:${NC}"

services=("8870:Test Manager" "8871:Test Execution Engine" "8872:Quality Analytics" "8873:Evidence Manager")

for service in "${services[@]}"; do
    port=$(echo $service | cut -d: -f1)
    name=$(echo $service | cut -d: -f2)
    
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name (port $port) - Healthy${NC}"
    else
        echo -e "${RED}❌ $name (port $port) - Not responding${NC}"
    fi
done

echo ""
echo -e "${BLUE}📊 Access URLs:${NC}"
echo -e "   Test Manager:          ${YELLOW}http://localhost:8870${NC}"
echo -e "   Test Execution Engine: ${YELLOW}http://localhost:8871${NC}"
echo -e "   Quality Analytics:     ${YELLOW}http://localhost:8872${NC}"
echo -e "   Evidence Manager:      ${YELLOW}http://localhost:8873${NC}"
