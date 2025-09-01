#!/bin/bash

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🚀 Starting IA-Ops Dev Core Services${NC}"
echo "===================================="

# Setup environment
if [ ! -f "$PROJECT_DIR/docker/.env" ]; then
    echo -e "${YELLOW}⚙️  Creating environment file...${NC}"
    cp "$PROJECT_DIR/docker/.env.example" "$PROJECT_DIR/docker/.env"
fi

# Create directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/logs"

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
cd "$PROJECT_DIR/docker"
docker compose up -d

# Wait for services
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Verify services
echo -e "${YELLOW}🔍 Verifying services...${NC}"
services=("8860:Repository Manager" "8861:Task Manager" "8862:Log Manager" "8863:DataSync Manager" "8864:GitHub Runner Manager" "8865:TechDocs Builder Manager")

for service in "${services[@]}"; do
    port=$(echo $service | cut -d: -f1)
    name=$(echo $service | cut -d: -f2)
    
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  $name is not responding${NC}"
    fi
done

echo ""
echo -e "${GREEN}🎉 Dev Core Services started!${NC}"
echo ""
echo -e "${BLUE}📊 Access URLs:${NC}"
echo -e "   Repository Manager:    ${YELLOW}http://localhost:8860${NC}"
echo -e "   Task Manager:          ${YELLOW}http://localhost:8861${NC}"
echo -e "   Log Manager:           ${YELLOW}http://localhost:8862${NC}"
echo -e "   DataSync Manager:      ${YELLOW}http://localhost:8863${NC}"
echo -e "   GitHub Runner Manager: ${YELLOW}http://localhost:8864${NC}"
echo -e "   TechDocs Builder:      ${YELLOW}http://localhost:8865${NC}"
