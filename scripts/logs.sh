#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🧪 IA-Ops Veritas - Service Logs${NC}"
echo "================================="

if [ "$1" ]; then
    case $1 in
        "test-manager"|"tm")
            echo -e "${YELLOW}📊 Test Manager Logs:${NC}"
            docker logs iaops-test-manager --tail=50 -f
            ;;
        "test-execution-engine"|"tee")
            echo -e "${YELLOW}⚙️ Test Execution Engine Logs:${NC}"
            docker logs iaops-test-execution-engine --tail=50 -f
            ;;
        "quality-analytics"|"qa")
            echo -e "${YELLOW}📈 Quality Analytics Logs:${NC}"
            docker logs iaops-quality-analytics --tail=50 -f
            ;;
        "evidence-manager"|"em")
            echo -e "${YELLOW}🔍 Evidence Manager Logs:${NC}"
            docker logs iaops-evidence-manager --tail=50 -f
            ;;
        *)
            echo -e "${YELLOW}Usage: $0 [service]${NC}"
            echo "Services: test-manager (tm), test-execution-engine (tee), quality-analytics (qa), evidence-manager (em)"
            echo "Or run without arguments to see all logs"
            ;;
    esac
else
    echo -e "${YELLOW}📊 All Services Logs:${NC}"
    cd "$PROJECT_DIR/docker"
    docker compose logs --tail=20 -f
fi
