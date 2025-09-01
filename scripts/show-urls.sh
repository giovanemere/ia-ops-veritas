#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}🧪 IA-Ops Veritas - URLs de Acceso${NC}"
echo "=========================================="
echo ""

echo -e "${PURPLE}🏠 PORTAL PRINCIPAL:${NC}"
echo -e "   ${CYAN}Portal de Navegación:${NC}      ${YELLOW}http://localhost:8869${NC}"
echo ""

echo -e "${PURPLE}🧪 SERVICIOS DE TESTING:${NC}"
echo -e "   ${CYAN}Test Manager:${NC}              ${YELLOW}http://localhost:8870${NC}"
echo -e "   ${CYAN}Test Execution Engine:${NC}     ${YELLOW}http://localhost:8871${NC}"
echo -e "   ${CYAN}Quality Analytics:${NC}         ${YELLOW}http://localhost:8872${NC}"
echo -e "   ${CYAN}Evidence Manager:${NC}          ${YELLOW}http://localhost:8873${NC}"
echo ""

echo -e "${PURPLE}🔗 APIs REST:${NC}"
echo -e "   ${CYAN}Test Manager API:${NC}          ${YELLOW}http://localhost:8870/api${NC}"
echo -e "   ${CYAN}Execution Engine API:${NC}      ${YELLOW}http://localhost:8871/api${NC}"
echo -e "   ${CYAN}Quality Analytics API:${NC}     ${YELLOW}http://localhost:8872/api${NC}"
echo -e "   ${CYAN}Evidence Manager API:${NC}      ${YELLOW}http://localhost:8873/api${NC}"
echo ""

echo -e "${PURPLE}📊 ENDPOINTS DE SALUD:${NC}"
echo -e "   ${CYAN}Portal Health:${NC}             ${YELLOW}http://localhost:8869/health${NC}"
echo -e "   ${CYAN}Test Manager Health:${NC}       ${YELLOW}http://localhost:8870/health${NC}"
echo -e "   ${CYAN}Execution Engine Health:${NC}   ${YELLOW}http://localhost:8871/health${NC}"
echo -e "   ${CYAN}Quality Analytics Health:${NC}  ${YELLOW}http://localhost:8872/health${NC}"
echo -e "   ${CYAN}Evidence Manager Health:${NC}   ${YELLOW}http://localhost:8873/health${NC}"
echo ""

echo -e "${GREEN}✨ RECOMENDACIÓN:${NC}"
echo -e "   ${CYAN}Comienza por el Portal Principal:${NC} ${YELLOW}http://localhost:8869${NC}"
echo -e "   ${CYAN}Desde ahí puedes navegar a todos los servicios${NC}"
echo ""

# Check if services are running
echo -e "${PURPLE}🔍 ESTADO DE SERVICIOS:${NC}"
services=("8869:Portal" "8870:Test Manager" "8871:Execution Engine" "8872:Quality Analytics" "8873:Evidence Manager")

for service in "${services[@]}"; do
    port=$(echo $service | cut -d: -f1)
    name=$(echo $service | cut -d: -f2)
    
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ $name${NC} - Disponible en puerto $port"
    else
        echo -e "   ${YELLOW}⚠️  $name${NC} - No disponible en puerto $port"
    fi
done

echo ""
echo -e "${BLUE}🚀 ¡Disfruta explorando IA-Ops Veritas!${NC}"
