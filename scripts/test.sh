#!/bin/bash

echo "🧪 Testing IA-Ops Dev Core Services"
echo "=================================="

services=(
    "8860:Repository Manager"
    "8861:Task Manager"
    "8862:Log Manager"
    "8863:DataSync Manager"
    "8864:GitHub Runner Manager"
    "8865:TechDocs Builder"
)

for service in "${services[@]}"; do
    port=$(echo $service | cut -d: -f1)
    name=$(echo $service | cut -d: -f2)
    
    echo -n "Testing $name (port $port)... "
    
    if curl -s -f http://localhost:$port/health > /dev/null; then
        echo "✅ OK"
    else
        echo "❌ FAIL"
    fi
done

echo ""
echo "🔗 Service URLs:"
echo "   Repository Manager:    http://localhost:8860"
echo "   Task Manager:          http://localhost:8861"
echo "   Log Manager:           http://localhost:8862"
echo "   DataSync Manager:      http://localhost:8863"
echo "   GitHub Runner Manager: http://localhost:8864"
echo "   TechDocs Builder:      http://localhost:8865"
