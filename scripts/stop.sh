#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🧪 Stopping IA-Ops Veritas Testing Platform${NC}"
echo "=============================================="

cd "$PROJECT_DIR/docker"
docker compose down

echo -e "${GREEN}✅ Veritas Testing Platform stopped!${NC}"
