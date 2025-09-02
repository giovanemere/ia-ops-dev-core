#!/bin/bash

echo "🚀 Starting IA-Ops Service Layer (using existing infrastructure)..."

# Check existing infrastructure
echo "🔍 Checking existing services..."
if ! docker ps | grep -q "iaops-postgres-main"; then
    echo "❌ PostgreSQL not running"
    exit 1
fi
if ! docker ps | grep -q "iaops-redis-main"; then
    echo "❌ Redis not running" 
    exit 1
fi
if ! docker ps | grep -q "ia-ops-minio-portal"; then
    echo "❌ MinIO not running"
    exit 1
fi
echo "✅ Infrastructure is running"

# Stop existing service layer
docker-compose down 2>/dev/null || true

# Start Service Layer
docker-compose up -d --build

echo "✅ Service Layer started!"
echo ""
echo "🌐 URLs:"
echo "  🚀 API: http://localhost:8801"
echo "  📚 Docs: http://localhost:8801/docs"
echo "  🔍 Health: http://localhost:8801/health"

sleep 5
curl -f http://localhost:8801/health > /dev/null 2>&1 && echo "✅ Healthy!" || echo "⚠️ Starting..."
