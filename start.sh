#!/bin/bash

echo "🚀 Starting IA-Ops Service Layer (using existing infrastructure)..."

# Check existing infrastructure
echo "🔍 Checking existing services..."
if ! docker ps | grep -q "iaops-postgres"; then
    echo "❌ PostgreSQL not running"
    exit 1
fi
if ! docker ps | grep -q "iaops-redis"; then
    echo "❌ Redis not running" 
    exit 1
fi
if ! docker ps | grep -q "iaops-minio-portal"; then
    echo "❌ MinIO not running"
    exit 1
fi
echo "✅ Infrastructure is running"

# Stop existing service layer
docker-compose down 2>/dev/null || true

# Start Service Layer
docker-compose up -d --build

echo "✅ Service Layer started!"

# Start microservices
echo "🔧 Starting microservices..."
cd docker && docker-compose up -d 2>/dev/null || true
cd ..

echo ""
echo "🌐 URLs:"
echo "  🚀 API: http://localhost:8801"
echo "  📚 Docs: http://localhost:8801/docs"
echo "  🔍 Health: http://localhost:8801/health"
echo ""
echo "  🔧 Microservicios:"
echo "     📂 Repository Manager: http://localhost:8860"
echo "     📋 Task Manager: http://localhost:8861"
echo "     📊 Log Manager: http://localhost:8862"
echo "     🔄 DataSync Manager: http://localhost:8863"
echo "     🏃 GitHub Runner Manager: http://localhost:8864"

sleep 5
curl -f http://localhost:8801/health > /dev/null 2>&1 && echo "✅ Service Layer Healthy!" || echo "⚠️ Starting..."
