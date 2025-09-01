# 🎨 Frontend Development Guide - IA-Ops Dev Core

## 🚀 Backend Status: ✅ READY FOR FRONTEND DEVELOPMENT

Todos los servicios backend están funcionando correctamente y listos para ser consumidos por el frontend.

---

## 🌐 Available Services & APIs

### 📁 Repository Manager (Port 8860)
**Base URL**: `http://localhost:8860`

#### Endpoints
```javascript
// Get service info
GET /

// List repositories
GET /repositories

// Create repository
POST /repositories
{
  "name": "string",
  "url": "string", 
  "branch": "string",
  "description": "string"
}

// Get repository
GET /repositories/{id}

// Update repository  
PUT /repositories/{id}

// Delete repository
DELETE /repositories/{id}

// Sync repository
POST /repositories/{id}/sync
```

#### Example Usage
```javascript
// Create repository
const createRepo = async () => {
  const response = await fetch('http://localhost:8860/repositories', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'my-project',
      url: 'https://github.com/user/repo',
      branch: 'main',
      description: 'My awesome project'
    })
  });
  return response.json();
};

// List repositories
const getRepos = async () => {
  const response = await fetch('http://localhost:8860/repositories');
  return response.json();
};
```

---

### 📋 Task Manager (Port 8861)
**Base URL**: `http://localhost:8861`

#### Endpoints
```javascript
// List tasks (with filters)
GET /tasks?status=pending&type=build

// Create task
POST /tasks
{
  "name": "string",
  "type": "build|test|deploy|sync",
  "command": "string",
  "repository_id": "integer",
  "environment": {}
}

// Get task
GET /tasks/{id}

// Execute task
POST /tasks/{id}/execute

// Get task logs
GET /tasks/{id}/logs
```

#### Example Usage
```javascript
// Create and execute task
const createTask = async () => {
  const response = await fetch('http://localhost:8861/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'Build Project',
      type: 'build',
      command: 'npm run build',
      repository_id: 1
    })
  });
  return response.json();
};

// Execute task
const executeTask = async (taskId) => {
  const response = await fetch(`http://localhost:8861/tasks/${taskId}/execute`, {
    method: 'POST'
  });
  return response.json();
};

// Monitor task status
const monitorTask = async (taskId) => {
  const response = await fetch(`http://localhost:8861/tasks/${taskId}`);
  const task = await response.json();
  return task.data.status; // pending|running|completed|failed
};
```

---

### 📊 Log Manager (Port 8862)
**Base URL**: `http://localhost:8862`

#### Endpoints
```javascript
// Get service info
GET /

// Health check
GET /health
```

---

### 🔄 DataSync Manager (Port 8863)
**Base URL**: `http://localhost:8863`

#### Endpoints
```javascript
// Get service info  
GET /

// Health check
GET /health
```

---

### 🏃 GitHub Runner Manager (Port 8864)
**Base URL**: `http://localhost:8864`

#### Endpoints
```javascript
// Get service info
GET /

// Health check
GET /health
```

---

### 📚 TechDocs Builder (Port 8865)
**Base URL**: `http://localhost:8865`

#### Endpoints
```javascript
// Get service info
GET /

// Health check  
GET /health
```

---

## 🎯 Frontend Implementation Recommendations

### 1. **Dashboard Components**
```javascript
// Repository Dashboard
- Repository List (GET /repositories)
- Repository Form (POST /repositories)
- Repository Details (GET /repositories/{id})

// Task Dashboard  
- Task Queue (GET /tasks)
- Task Creator (POST /tasks)
- Task Monitor (GET /tasks/{id})
- Task Executor (POST /tasks/{id}/execute)
- Task Logs Viewer (GET /tasks/{id}/logs)
```

### 2. **State Management**
```javascript
// Repository State
{
  repositories: [],
  selectedRepository: null,
  loading: false,
  error: null
}

// Task State
{
  tasks: [],
  selectedTask: null,
  taskLogs: '',
  executing: false,
  loading: false,
  error: null
}
```

### 3. **Real-time Updates**
```javascript
// Poll task status every 2 seconds when executing
const pollTaskStatus = (taskId) => {
  const interval = setInterval(async () => {
    const response = await fetch(`http://localhost:8861/tasks/${taskId}`);
    const task = await response.json();
    
    if (task.data.status === 'completed' || task.data.status === 'failed') {
      clearInterval(interval);
    }
    
    // Update UI with task status
    updateTaskStatus(task.data);
  }, 2000);
};
```

### 4. **Error Handling**
```javascript
const handleApiError = (response) => {
  if (!response.success) {
    throw new Error(response.error.message);
  }
  return response.data;
};
```

---

## 🧪 Testing the APIs

### Quick Test Script
```bash
# Test all services
./scripts/test-apis.sh

# Test specific endpoints
curl http://localhost:8860/repositories
curl http://localhost:8861/tasks
```

### Sample Data Creation
```bash
# Create repository
curl -X POST http://localhost:8860/repositories \
  -H "Content-Type: application/json" \
  -d '{"name":"test-repo","url":"https://github.com/test/repo","branch":"main"}'

# Create task
curl -X POST http://localhost:8861/tasks \
  -H "Content-Type: application/json" \
  -d '{"name":"test-task","type":"build","command":"echo hello","repository_id":1}'

# Execute task
curl -X POST http://localhost:8861/tasks/1/execute
```

---

## 📱 Recommended Frontend Stack

### React/Next.js Example
```javascript
// hooks/useRepositories.js
export const useRepositories = () => {
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchRepos = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8860/repositories');
      const data = await response.json();
      setRepos(data.repositories || data.data);
    } catch (error) {
      console.error('Error fetching repositories:', error);
    } finally {
      setLoading(false);
    }
  };

  const createRepo = async (repoData) => {
    const response = await fetch('http://localhost:8860/repositories', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(repoData)
    });
    
    if (response.ok) {
      fetchRepos(); // Refresh list
    }
    
    return response.json();
  };

  return { repos, loading, fetchRepos, createRepo };
};
```

### Vue.js Example
```javascript
// composables/useRepositories.js
export const useRepositories = () => {
  const repos = ref([]);
  const loading = ref(false);

  const fetchRepos = async () => {
    loading.value = true;
    try {
      const response = await $fetch('http://localhost:8860/repositories');
      repos.value = response.repositories || response.data;
    } catch (error) {
      console.error('Error:', error);
    } finally {
      loading.value = false;
    }
  };

  return { repos, loading, fetchRepos };
};
```

---

## 🔧 Development Setup

1. **Start Backend Services**
   ```bash
   cd ia-ops-dev-core
   ./scripts/start.sh
   ```

2. **Verify Services**
   ```bash
   ./scripts/status.sh
   ./scripts/test-apis.sh
   ```

3. **Create Your Frontend**
   - Use any framework (React, Vue, Angular, etc.)
   - Point to `http://localhost:8860-8865` for APIs
   - Implement the components based on the endpoints above

4. **CORS is Enabled**
   - All services have CORS enabled
   - No additional configuration needed

---

## 🎉 You're Ready to Build!

The backend is fully functional with:
- ✅ Repository management
- ✅ Task execution and monitoring  
- ✅ Real-time status updates
- ✅ Error handling
- ✅ CORS enabled
- ✅ Consistent API responses

Start building your frontend and consume these APIs! 🚀
