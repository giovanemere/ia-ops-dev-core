#!/bin/bash

echo "🔍 IA-Ops Services Verification"
echo "==============================="

# Load environment
source .docker-credentials

# Services to check
services=(
    "Repository Manager:8860:/health"
    "Task Manager:8861:/health"
    "Log Manager:8862:/health"
    "DataSync Manager:8863:/health"
    "GitHub Runner Manager:8864:/health"
    "TechDocs Builder:8865:/health"
    "Swagger Portal:8870:/api/status"
    "Testing Portal:18860:/health"
)

echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "🏥 Health Check Results:"
echo "========================"

all_healthy=true

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    endpoint=$(echo $service | cut -d: -f3)
    
    url="http://localhost:$port$endpoint"
    
    # Try to connect
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo "✅ $name (Port $port): Healthy"
    else
        echo "❌ $name (Port $port): Unhealthy"
        all_healthy=false
    fi
done

echo ""
echo "🌐 Service URLs:"
echo "================"
echo "📚 Swagger Portal: http://localhost:8870"
echo "📁 Repository Manager: http://localhost:8860/docs/"
echo "📋 Task Manager: http://localhost:8861/docs/"
echo "📊 Log Manager: http://localhost:8862/docs/"
echo "🔄 DataSync Manager: http://localhost:8863/docs/"
echo "🏃 GitHub Runner Manager: http://localhost:8864/docs/"
echo "📚 TechDocs Builder: http://localhost:8865/docs/"
echo "🧪 Testing Portal: http://localhost:18860"

echo ""
if [ "$all_healthy" = true ]; then
    echo "🎉 All services are healthy and ready!"
    exit 0
else
    echo "⚠️  Some services are not healthy. Check logs with:"
    echo "   docker-compose logs [service-name]"
    exit 1
fi
