#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📊 IA-Ops Dev Core Services Status"
echo "=================================="

cd "$PROJECT_DIR/docker"
docker compose ps

echo ""
echo "🔍 Health Checks:"

services=("8850:Repository Manager" "8851:Task Manager" "8852:Log Manager")

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
