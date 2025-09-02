#!/bin/bash

echo "🚀 Setting up IA-Ops Complete Solution"
echo "======================================"

# Step 1: Initialize Database
echo "1. 📊 Initializing PostgreSQL Database..."
python3 init_database.py

# Step 2: Run SQL initialization
echo "2. 🗄️ Creating database tables and inserting configuration..."
if command -v psql &> /dev/null; then
    PGPASSWORD=iaops_password psql -h localhost -p 5434 -U iaops_user -d iaops_db -f init_database.sql
    echo "✅ Database initialized successfully"
else
    echo "⚠️ psql not found. Please run init_database.sql manually:"
    echo "   PGPASSWORD=iaops_password psql -h localhost -p 5434 -U iaops_user -d iaops_db -f init_database.sql"
fi

# Step 3: Create MinIO bucket
echo "3. 📦 Setting up MinIO single bucket..."
if command -v mc &> /dev/null; then
    mc alias set iaops http://localhost:9898 minioadmin minioadmin123
    mc mb iaops/ia-ops-storage 2>/dev/null || echo "Bucket already exists"
    mc policy set public iaops/ia-ops-storage
    echo "✅ MinIO bucket 'ia-ops-storage' configured"
else
    echo "⚠️ MinIO client (mc) not found. Please create bucket manually:"
    echo "   Bucket name: ia-ops-storage"
    echo "   Access: http://localhost:9899/"
fi

# Step 4: Test Redis connection
echo "4. 🔄 Testing Redis cache connection..."
if command -v redis-cli &> /dev/null; then
    redis-cli -h localhost -p 6380 ping
    if [ $? -eq 0 ]; then
        echo "✅ Redis cache is accessible"
    else
        echo "❌ Redis cache connection failed"
    fi
else
    echo "⚠️ redis-cli not found. Please verify Redis is running on localhost:6380"
fi

# Step 5: Load environment variables
echo "5. ⚙️ Loading environment configuration..."
if [ -f ".env.production" ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env.production not found"
fi

# Step 6: Verify services configuration
echo "6. 🔧 Verifying solution configuration..."
python3 verify_complete_solution.py

echo ""
echo "🎉 IA-Ops Solution Setup Complete!"
echo "=================================="
echo "📦 Single Bucket: ia-ops-storage"
echo "🗄️ PostgreSQL: localhost:5434"
echo "🔄 Redis Cache: localhost:6380"
echo "🌐 MinIO Console: http://localhost:9899/"
echo ""
echo "🚀 Ready to start all services!"
echo "Run: docker-compose -f docker-compose.production.yml up -d"
