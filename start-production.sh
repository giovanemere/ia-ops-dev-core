#!/bin/bash

echo "🚀 IA-Ops Dev Core - Production Deployment"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    source .env
    echo "✅ Environment variables loaded"
else
    echo "⚠️  No .env file found, using defaults"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs test-results
echo "✅ Directories created"

# Pull latest images
echo "📥 Pulling latest images from Docker Hub..."
docker-compose -f docker-compose.production.yml pull

if [ $? -ne 0 ]; then
    echo "❌ Failed to pull images"
    exit 1
fi

echo "✅ Images pulled successfully"

# Start services
echo "🚀 Starting IA-Ops services..."
docker-compose -f docker-compose.production.yml up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services"
    exit 1
fi

echo "✅ Services started successfully"

# Wait and verify
echo "⏳ Waiting for services to initialize..."
sleep 15

# Run verification
./verify-services.sh

echo ""
echo "🎉 IA-Ops Dev Core is now running in production mode!"
echo ""
echo "📊 Management Commands:"
echo "======================"
echo "View logs:    docker-compose -f docker-compose.production.yml logs -f"
echo "Stop services: docker-compose -f docker-compose.production.yml down"
echo "Restart:      docker-compose -f docker-compose.production.yml restart"
echo "Status:       docker-compose -f docker-compose.production.yml ps"
