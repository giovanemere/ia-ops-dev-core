#!/bin/bash

echo "🧪 Testing IA-Ops Dev Core APIs"
echo "==============================="

BASE_URL="http://localhost"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=$4
    
    echo -n "Testing $method $url... "
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "%{http_code}" -X $method -H "Content-Type: application/json" -d "$data" "$url")
    else
        response=$(curl -s -w "%{http_code}" -X $method "$url")
    fi
    
    status_code="${response: -3}"
    body="${response%???}"
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK${NC} ($status_code)"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        return 1
    fi
}

echo ""
echo "📁 Repository Manager API Tests"
echo "--------------------------------"

# Test Repository Manager
test_endpoint "GET" "$BASE_URL:8860/" "200"
test_endpoint "GET" "$BASE_URL:8860/health" "200"
test_endpoint "GET" "$BASE_URL:8860/repositories" "200"

# Create repository
repo_data='{"name":"test-repo","url":"https://github.com/test/repo","branch":"main","description":"Test repository"}'
test_endpoint "POST" "$BASE_URL:8860/repositories" "$repo_data" "201"

echo ""
echo "📋 Task Manager API Tests"
echo "-------------------------"

# Test Task Manager
test_endpoint "GET" "$BASE_URL:8861/" "200"
test_endpoint "GET" "$BASE_URL:8861/health" "200"
test_endpoint "GET" "$BASE_URL:8861/tasks" "200"

# Create task
task_data='{"name":"test-task","type":"build","command":"echo hello","repository_id":1}'
test_endpoint "POST" "$BASE_URL:8861/tasks" "$task_data" "201"

echo ""
echo "📊 Log Manager API Tests"
echo "------------------------"

test_endpoint "GET" "$BASE_URL:8862/health" "200"

echo ""
echo "🔄 DataSync Manager API Tests"
echo "-----------------------------"

test_endpoint "GET" "$BASE_URL:8863/health" "200"

echo ""
echo "🏃 GitHub Runner Manager API Tests"
echo "----------------------------------"

test_endpoint "GET" "$BASE_URL:8864/health" "200"

echo ""
echo "📚 TechDocs Builder API Tests"
echo "-----------------------------"

test_endpoint "GET" "$BASE_URL:8865/health" "200"

echo ""
echo "🔍 API Examples for Frontend Development"
echo "======================================="

echo ""
echo "📝 Repository Management:"
echo "  GET    $BASE_URL:8860/repositories           # List repositories"
echo "  POST   $BASE_URL:8860/repositories           # Create repository"
echo "  GET    $BASE_URL:8860/repositories/1         # Get repository"
echo "  PUT    $BASE_URL:8860/repositories/1         # Update repository"
echo "  DELETE $BASE_URL:8860/repositories/1         # Delete repository"

echo ""
echo "📝 Task Management:"
echo "  GET    $BASE_URL:8861/tasks                  # List tasks"
echo "  POST   $BASE_URL:8861/tasks                  # Create task"
echo "  GET    $BASE_URL:8861/tasks/1                # Get task"
echo "  POST   $BASE_URL:8861/tasks/1/execute        # Execute task"
echo "  GET    $BASE_URL:8861/tasks/1/logs           # Get task logs"

echo ""
echo "📝 Example JSON Payloads:"
echo "  Repository: $repo_data"
echo "  Task: $task_data"

echo ""
echo "💡 Use these endpoints to build your frontend!"
