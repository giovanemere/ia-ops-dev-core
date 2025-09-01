#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📊 IA-Ops Dev Core Services Status"
echo "=================================="

cd "$PROJECT_DIR/docker"
docker compose ps

echo ""
echo "🔍 Health Checks:"

services=("8860:Repository Manager" "8861:Task Manager" "8862:Log Manager" "8863:DataSync Manager" "8864:GitHub Runner Manager" "8865:TechDocs Builder Manager")

for service in "${services[@]}"; do
    port=$(echo $service | cut -d: -f1)
    name=$(echo $service | cut -d: -f2)
    
    echo -n "$name: "
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy"
    fi
done
