#!/bin/bash

echo "🧪 IA-Ops Dev Core - Complete API Testing Suite"
echo "==============================================="

BASE_URL="http://localhost"
RESULTS_FILE="/tmp/api-test-results.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0

# Function to test API endpoint
test_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_status=$4
    local description=$5
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "[$TOTAL_TESTS] Testing $description... "
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "%{http_code}" -X $method \
            -H "Content-Type: application/json" \
            -d "$data" "$endpoint" 2>/dev/null)
    else
        response=$(curl -s -w "%{http_code}" -X $method "$endpoint" 2>/dev/null)
    fi
    
    status_code="${response: -3}"
    body="${response%???}"
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} ($status_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Save successful response for frontend reference
        echo "{\"test\": \"$description\", \"method\": \"$method\", \"endpoint\": \"$endpoint\", \"status\": $status_code, \"response\": $body}" >> $RESULTS_FILE
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        echo "Response: $body"
        return 1
    fi
}

# Initialize results file
echo "[]" > $RESULTS_FILE

echo ""
echo -e "${BLUE}🔍 Testing Service Health Checks${NC}"
echo "================================="

test_api "GET" "$BASE_URL:8860/health" "" "200" "Repository Manager Health"
test_api "GET" "$BASE_URL:8861/health" "" "200" "Task Manager Health"
test_api "GET" "$BASE_URL:8862/health" "" "200" "Log Manager Health"
test_api "GET" "$BASE_URL:8863/health" "" "200" "DataSync Manager Health"
test_api "GET" "$BASE_URL:8864/health" "" "200" "GitHub Runner Manager Health"
test_api "GET" "$BASE_URL:8865/health" "" "200" "TechDocs Builder Health"

echo ""
echo -e "${BLUE}📁 Testing Repository Manager API${NC}"
echo "=================================="

# Test service info
test_api "GET" "$BASE_URL:8860/" "" "200" "Repository Manager Info"

# Test list repositories (empty)
test_api "GET" "$BASE_URL:8860/repositories" "" "200" "List Repositories (Empty)"

# Create test repositories
repo1='{"name":"frontend-app","url":"https://github.com/company/frontend","branch":"main","description":"Frontend React application"}'
test_api "POST" "$BASE_URL:8860/repositories" "$repo1" "201" "Create Repository 1"

repo2='{"name":"backend-api","url":"https://github.com/company/backend","branch":"develop","description":"Backend API service"}'
test_api "POST" "$BASE_URL:8860/repositories" "$repo2" "201" "Create Repository 2"

repo3='{"name":"mobile-app","url":"https://github.com/company/mobile","branch":"main","description":"Mobile Flutter app"}'
test_api "POST" "$BASE_URL:8860/repositories" "$repo3" "201" "Create Repository 3"

# Test list repositories (with data)
test_api "GET" "$BASE_URL:8860/repositories" "" "200" "List Repositories (With Data)"

# Test get specific repository
test_api "GET" "$BASE_URL:8860/repositories/1" "" "200" "Get Repository by ID"

# Test update repository
update_repo='{"description":"Updated frontend application with new features"}'
test_api "PUT" "$BASE_URL:8860/repositories/1" "$update_repo" "200" "Update Repository"

# Test repository sync
test_api "POST" "$BASE_URL:8860/repositories/1/sync" "" "200" "Sync Repository"

# Test search repositories
test_api "GET" "$BASE_URL:8860/repositories?search=frontend" "" "200" "Search Repositories"

echo ""
echo -e "${BLUE}📋 Testing Task Manager API${NC}"
echo "============================="

# Test service info
test_api "GET" "$BASE_URL:8861/" "" "200" "Task Manager Info"

# Test list tasks (empty)
test_api "GET" "$BASE_URL:8861/tasks" "" "200" "List Tasks (Empty)"

# Create test tasks
task1='{"name":"Build Frontend","type":"build","command":"npm run build","repository_id":1,"environment":{"NODE_ENV":"production"}}'
test_api "POST" "$BASE_URL:8861/tasks" "$task1" "201" "Create Build Task"

task2='{"name":"Run Tests","type":"test","command":"npm test","repository_id":1}'
test_api "POST" "$BASE_URL:8861/tasks" "$task2" "201" "Create Test Task"

task3='{"name":"Deploy to Staging","type":"deploy","command":"docker deploy staging","repository_id":1}'
test_api "POST" "$BASE_URL:8861/tasks" "$task3" "201" "Create Deploy Task"

task4='{"name":"Backend Build","type":"build","command":"mvn clean package","repository_id":2}'
test_api "POST" "$BASE_URL:8861/tasks" "$task4" "201" "Create Backend Task"

# Test list tasks (with data)
test_api "GET" "$BASE_URL:8861/tasks" "" "200" "List Tasks (With Data)"

# Test get specific task
test_api "GET" "$BASE_URL:8861/tasks/1" "" "200" "Get Task by ID"

# Test filter tasks by status
test_api "GET" "$BASE_URL:8861/tasks?status=pending" "" "200" "Filter Tasks by Status"

# Test filter tasks by type
test_api "GET" "$BASE_URL:8861/tasks?type=build" "" "200" "Filter Tasks by Type"

# Test execute task
test_api "POST" "$BASE_URL:8861/tasks/1/execute" "" "200" "Execute Task"

# Wait a moment for task execution
sleep 3

# Test get task logs
test_api "GET" "$BASE_URL:8861/tasks/1/logs" "" "200" "Get Task Logs"

# Test get updated task status
test_api "GET" "$BASE_URL:8861/tasks/1" "" "200" "Get Updated Task Status"

# Execute more tasks for demo
test_api "POST" "$BASE_URL:8861/tasks/2/execute" "" "200" "Execute Test Task"
test_api "POST" "$BASE_URL:8861/tasks/3/execute" "" "200" "Execute Deploy Task"

echo ""
echo -e "${BLUE}📊 Testing Other Services${NC}"
echo "========================="

# Test other service endpoints
test_api "GET" "$BASE_URL:8862/" "" "200" "Log Manager Info"
test_api "GET" "$BASE_URL:8863/" "" "200" "DataSync Manager Info"
test_api "GET" "$BASE_URL:8864/" "" "200" "GitHub Runner Manager Info"
test_api "GET" "$BASE_URL:8865/" "" "200" "TechDocs Builder Info"

echo ""
echo -e "${BLUE}📈 Test Results Summary${NC}"
echo "======================="

echo -e "Total Tests: ${YELLOW}$TOTAL_TESTS${NC}"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$((TOTAL_TESTS - PASSED_TESTS))${NC}"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "\n${GREEN}🎉 All tests passed! API is ready for frontend development.${NC}"
else
    echo -e "\n${YELLOW}⚠️  Some tests failed. Check the output above.${NC}"
fi

echo ""
echo -e "${BLUE}📋 Frontend Development Data${NC}"
echo "============================"

echo "Current API Data:"
echo "- Repositories: $(curl -s $BASE_URL:8860/repositories | jq -r '.count // 0')"
echo "- Tasks: $(curl -s $BASE_URL:8861/tasks | jq -r '.count // 0')"

echo ""
echo -e "${BLUE}🔗 API Endpoints for Frontend${NC}"
echo "============================="

cat << 'EOF'
Repository Management:
  GET    /repositories              # List all repositories
  POST   /repositories              # Create new repository
  GET    /repositories/{id}         # Get repository details
  PUT    /repositories/{id}         # Update repository
  DELETE /repositories/{id}         # Delete repository
  POST   /repositories/{id}/sync    # Sync repository

Task Management:
  GET    /tasks                     # List all tasks
  POST   /tasks                     # Create new task
  GET    /tasks/{id}                # Get task details
  PUT    /tasks/{id}                # Update task
  DELETE /tasks/{id}                # Delete task
  POST   /tasks/{id}/execute        # Execute task
  GET    /tasks/{id}/logs           # Get task logs

Query Parameters:
  /repositories?search=term         # Search repositories
  /repositories?status=active       # Filter by status
  /tasks?status=pending             # Filter tasks by status
  /tasks?type=build                 # Filter tasks by type
EOF

echo ""
echo -e "${BLUE}📝 Sample API Calls for Frontend${NC}"
echo "==================================="

cat << 'EOF'
// JavaScript Examples

// 1. Fetch repositories
const getRepositories = async () => {
  const response = await fetch('http://localhost:8860/repositories');
  const data = await response.json();
  return data.data; // Array of repositories
};

// 2. Create repository
const createRepository = async (repoData) => {
  const response = await fetch('http://localhost:8860/repositories', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(repoData)
  });
  return response.json();
};

// 3. Execute task and monitor
const executeTask = async (taskId) => {
  const response = await fetch(`http://localhost:8861/tasks/${taskId}/execute`, {
    method: 'POST'
  });
  
  // Poll for status updates
  const pollStatus = setInterval(async () => {
    const statusResponse = await fetch(`http://localhost:8861/tasks/${taskId}`);
    const task = await statusResponse.json();
    
    if (task.data.status === 'completed' || task.data.status === 'failed') {
      clearInterval(pollStatus);
      console.log('Task finished:', task.data.status);
    }
  }, 2000);
};

// 4. Get task logs in real-time
const getTaskLogs = async (taskId) => {
  const response = await fetch(`http://localhost:8861/tasks/${taskId}/logs`);
  const logs = await response.json();
  return logs.data.logs;
};
EOF

echo ""
echo -e "${GREEN}✅ API Testing Complete - Ready for Frontend Development!${NC}"
