#!/bin/bash

echo "🚀 Starting IA-Ops Dev Core Services with Swagger Documentation..."

# Change to docker directory
cd "$(dirname "$0")/../docker"

# Start all services including Swagger portal
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Checking service status..."

services=(
    "Repository Manager:8860"
    "Task Manager:8861" 
    "Log Manager:8862"
    "DataSync Manager:8863"
    "GitHub Runner Manager:8864"
    "TechDocs Builder:8865"
    "Swagger Portal:8870"
)

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1 || curl -s -f "http://localhost:$port/api/status" > /dev/null 2>&1; then
        echo "✅ $name (Port $port): Online"
    else
        echo "❌ $name (Port $port): Offline"
    fi
done

echo ""
echo "🌐 Access URLs:"
echo "📚 Swagger Documentation Portal: http://localhost:8870"
echo "📁 Repository Manager API: http://localhost:8860/docs/"
echo "📋 Task Manager API: http://localhost:8861/docs/"
echo "📊 Log Manager API: http://localhost:8862/docs/"
echo "🔄 DataSync Manager API: http://localhost:8863/docs/"
echo "🏃 GitHub Runner Manager API: http://localhost:8864/docs/"
echo "📚 TechDocs Builder API: http://localhost:8865/docs/"
echo ""
echo "🧪 Testing Portal: https://github.com/giovanemere/ia-ops-veritas"
echo ""
echo "✨ All services started successfully!"
