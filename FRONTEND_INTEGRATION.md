# 🔗 Integración Frontend-Backend: ia-ops-docs ↔ ia-ops-dev-core

## 🏗️ Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────────┐
│                 IA-Ops Portal (Frontend)                        │
│                    Port: 8845                                   │
│                git@github.com:giovanemere/ia-ops-docs.git       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Dashboard │ Repositories │ Tasks │ Logs │ Testing │ Files     │
│     │            │          │       │        │        │        │
│     ▼            ▼          ▼       ▼        ▼        ▼        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    API Gateway Layer                            │
│                  (Frontend Proxy)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│              IA-Ops Dev Core Services (Backend)                 │
│            git@github.com:giovanemere/ia-ops-dev-core.git       │
│                                                                 │
│  Repository Manager (8860) │ Task Manager (8861)               │
│  Log Manager (8862)        │ DataSync Manager (8863)           │
│  GitHub Runner (8864)      │ TechDocs Builder (8865)           │
│                                                                 │
│              Swagger Portal (8870)                              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    Database Layer                               │
│  PostgreSQL (5434) │ Redis (6380) │ MinIO (9898)              │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Configuración de Integración

### 1. Variables de Entorno para Frontend

Actualizar `/home/giovanemere/ia-ops/ia-ops-docs/.env`:

```bash
# IA-Ops Portal Configuration
PORTAL_PORT=8845
PORTAL_HOST=0.0.0.0

# Backend Services URLs
DEV_CORE_BASE_URL=http://localhost:8870
REPOSITORY_MANAGER_URL=http://localhost:8860
TASK_MANAGER_URL=http://localhost:8861
LOG_MANAGER_URL=http://localhost:8862
DATASYNC_MANAGER_URL=http://localhost:8863
GITHUB_RUNNER_MANAGER_URL=http://localhost:8864
TECHDOCS_BUILDER_URL=http://localhost:8865

# Swagger Documentation
SWAGGER_PORTAL_URL=http://localhost:8870
API_DOCS_ENABLED=true

# Testing Integration
VERITAS_BASE_URL=http://localhost:8870
TESTING_ENABLED=true

# MinIO Integration (existing)
MINIO_REST_API_URL=http://localhost:8848
MINIO_CONSOLE_URL=http://localhost:9899

# Database Monitoring
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5434
REDIS_HOST=localhost
REDIS_PORT=6380
MINIO_HOST=localhost
MINIO_PORT=9898
```

### 2. API Client para Frontend

Crear `/home/giovanemere/ia-ops/ia-ops-docs/web-interface/api_client.py`:

```python
import requests
import os
from typing import Dict, Any, Optional

class IAOpsApiClient:
    def __init__(self):
        self.base_urls = {
            'swagger_portal': os.getenv('SWAGGER_PORTAL_URL', 'http://localhost:8870'),
            'repository': os.getenv('REPOSITORY_MANAGER_URL', 'http://localhost:8860'),
            'task': os.getenv('TASK_MANAGER_URL', 'http://localhost:8861'),
            'log': os.getenv('LOG_MANAGER_URL', 'http://localhost:8862'),
            'datasync': os.getenv('DATASYNC_MANAGER_URL', 'http://localhost:8863'),
            'github_runner': os.getenv('GITHUB_RUNNER_MANAGER_URL', 'http://localhost:8864'),
            'techdocs': os.getenv('TECHDOCS_BUILDER_URL', 'http://localhost:8865')
        }
    
    def get_services_status(self) -> Dict[str, Any]:
        """Get status of all backend services"""
        try:
            response = requests.get(f"{self.base_urls['swagger_portal']}/api/status", timeout=10)
            return response.json()
        except Exception as e:
            return {'error': str(e), 'services_online': 0}
    
    def get_repositories(self) -> Dict[str, Any]:
        """Get all repositories"""
        try:
            response = requests.get(f"{self.base_urls['repository']}/api/v1/repositories", timeout=10)
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_repository(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new repository"""
        try:
            response = requests.post(
                f"{self.base_urls['repository']}/api/v1/repositories",
                json=data,
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_tasks(self) -> Dict[str, Any]:
        """Get all tasks"""
        try:
            response = requests.get(f"{self.base_urls['task']}/api/v1/tasks", timeout=10)
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new task"""
        try:
            response = requests.post(
                f"{self.base_urls['task']}/api/v1/tasks",
                json=data,
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute_task(self, task_id: int) -> Dict[str, Any]:
        """Execute task"""
        try:
            response = requests.post(
                f"{self.base_urls['task']}/api/v1/tasks/{task_id}/execute",
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_logs(self, service: Optional[str] = None) -> Dict[str, Any]:
        """Get logs"""
        try:
            url = f"{self.base_urls['log']}/api/v1/logs"
            if service:
                url += f"/{service}"
            response = requests.get(url, timeout=10)
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}
```

### 3. Actualizar Frontend App

Modificar `/home/giovanemere/ia-ops/ia-ops-docs/web-interface/app.py`:

```python
from api_client import IAOpsApiClient

# Initialize API client
api_client = IAOpsApiClient()

@app.route('/api/dashboard')
@document_api("Dashboard data with backend services status")
def dashboard_data():
    """Get dashboard data from backend services"""
    try:
        # Get services status
        services_status = api_client.get_services_status()
        
        # Get repositories count
        repositories = api_client.get_repositories()
        repo_count = len(repositories.get('data', [])) if repositories.get('success') else 0
        
        # Get tasks count
        tasks = api_client.get_tasks()
        task_count = len(tasks.get('data', [])) if tasks.get('success') else 0
        
        return jsonify({
            'success': True,
            'data': {
                'services': services_status,
                'repositories': repo_count,
                'tasks': task_count,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repositories')
@document_api("Repository management", "GET")
def get_repositories():
    """Proxy to repository manager"""
    return jsonify(api_client.get_repositories())

@app.route('/api/repositories', methods=['POST'])
@document_api("Create repository", "POST")
def create_repository():
    """Proxy to create repository"""
    data = request.get_json()
    return jsonify(api_client.create_repository(data))

@app.route('/api/tasks')
@document_api("Task management", "GET")
def get_tasks():
    """Proxy to task manager"""
    return jsonify(api_client.get_tasks())

@app.route('/api/tasks', methods=['POST'])
@document_api("Create task", "POST")
def create_task():
    """Proxy to create task"""
    data = request.get_json()
    return jsonify(api_client.create_task(data))

@app.route('/api/tasks/<int:task_id>/execute', methods=['POST'])
@document_api("Execute task", "POST")
def execute_task(task_id):
    """Proxy to execute task"""
    return jsonify(api_client.execute_task(task_id))

@app.route('/api/logs')
@app.route('/api/logs/<service>')
@document_api("Log management", "GET")
def get_logs(service=None):
    """Proxy to log manager"""
    return jsonify(api_client.get_logs(service))
```

## 🚀 Deployment Strategy

### 1. Docker Compose Integration

Crear `/home/giovanemere/ia-ops/ia-ops-docs/docker-compose.integrated.yml`:

```yaml
version: '3.8'

services:
  # Frontend Portal
  ia-ops-portal:
    build: ./web-interface
    container_name: ia-ops-portal
    ports:
      - "8845:8845"
    environment:
      - SWAGGER_PORTAL_URL=http://ia-ops-swagger-portal:8870
      - REPOSITORY_MANAGER_URL=http://ia-ops-repository-manager:8850
      - TASK_MANAGER_URL=http://ia-ops-task-manager:8851
      - LOG_MANAGER_URL=http://ia-ops-log-manager:8852
    networks:
      - ia-ops-network
    depends_on:
      - ia-ops-swagger-portal

  # Include backend services
  ia-ops-swagger-portal:
    image: ia-ops-dev-core/swagger-portal
    container_name: ia-ops-swagger-portal
    ports:
      - "8870:8870"
    networks:
      - ia-ops-network

networks:
  ia-ops-network:
    external: true
    name: iaops-dev-core-network
```

### 2. Startup Scripts

Crear `/home/giovanemere/ia-ops/ia-ops-docs/start-integrated.sh`:

```bash
#!/bin/bash

echo "🚀 Starting IA-Ops Integrated System..."

# Start backend services first
cd ../ia-ops-dev-core
./scripts/start-with-swagger.sh

# Wait for backend to be ready
echo "⏳ Waiting for backend services..."
sleep 15

# Start frontend
cd ../ia-ops-docs
docker-compose -f docker-compose.integrated.yml up -d

echo "✅ IA-Ops Integrated System Started!"
echo "🌐 Frontend Portal: http://localhost:8845"
echo "📚 Backend Swagger: http://localhost:8870"
```

## 📱 Frontend Components Integration

### 1. Dashboard Component

```javascript
// static/js/dashboard.js
class Dashboard {
    constructor() {
        this.apiClient = new ApiClient();
        this.refreshInterval = 30000; // 30 seconds
    }

    async loadDashboard() {
        try {
            const response = await this.apiClient.get('/api/dashboard');
            this.updateDashboard(response.data);
        } catch (error) {
            console.error('Dashboard load error:', error);
        }
    }

    updateDashboard(data) {
        // Update services status
        this.updateServicesStatus(data.services);
        
        // Update counters
        document.getElementById('repo-count').textContent = data.repositories;
        document.getElementById('task-count').textContent = data.tasks;
        
        // Update timestamp
        document.getElementById('last-update').textContent = 
            new Date(data.timestamp).toLocaleString();
    }

    updateServicesStatus(services) {
        const statusContainer = document.getElementById('services-status');
        statusContainer.innerHTML = '';
        
        Object.entries(services.services || {}).forEach(([service, status]) => {
            const statusElement = document.createElement('div');
            statusElement.className = `service-status ${status.success ? 'online' : 'offline'}`;
            statusElement.innerHTML = `
                <span class="service-name">${service}</span>
                <span class="status-indicator"></span>
            `;
            statusContainer.appendChild(statusElement);
        });
    }

    startAutoRefresh() {
        setInterval(() => this.loadDashboard(), this.refreshInterval);
    }
}
```

### 2. Repository Management Component

```javascript
// static/js/repositories.js
class RepositoryManager {
    constructor() {
        this.apiClient = new ApiClient();
    }

    async loadRepositories() {
        try {
            const response = await this.apiClient.get('/api/repositories');
            this.displayRepositories(response.data);
        } catch (error) {
            this.showError('Failed to load repositories');
        }
    }

    async createRepository(formData) {
        try {
            const response = await this.apiClient.post('/api/repositories', formData);
            if (response.success) {
                this.showSuccess('Repository created successfully');
                this.loadRepositories();
            } else {
                this.showError(response.error.message);
            }
        } catch (error) {
            this.showError('Failed to create repository');
        }
    }

    displayRepositories(repositories) {
        const container = document.getElementById('repositories-list');
        container.innerHTML = repositories.map(repo => `
            <div class="repository-card">
                <h3>${repo.name}</h3>
                <p>${repo.description}</p>
                <div class="repo-actions">
                    <button onclick="repositoryManager.syncRepository(${repo.id})">
                        Sync
                    </button>
                    <a href="${repo.url}" target="_blank">View</a>
                </div>
            </div>
        `).join('');
    }
}
```

## 🔄 Data Flow

### Request Flow:
1. **Frontend** (8845) → User interaction
2. **Frontend API** → Proxy request to backend
3. **Backend Services** (8860-8865) → Process request
4. **Database** (PostgreSQL/Redis/MinIO) → Data operations
5. **Backend** → Return response
6. **Frontend** → Display results

### Real-time Updates:
```javascript
// WebSocket integration for real-time updates
class RealTimeUpdates {
    constructor() {
        this.ws = new WebSocket('ws://localhost:8870/ws');
        this.setupEventHandlers();
    }

    setupEventHandlers() {
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleUpdate(data);
        };
    }

    handleUpdate(data) {
        switch (data.type) {
            case 'service_status':
                dashboard.updateServicesStatus(data.payload);
                break;
            case 'task_completed':
                taskManager.refreshTask(data.payload.task_id);
                break;
            case 'new_log':
                logManager.addLog(data.payload);
                break;
        }
    }
}
```

## 🧪 Testing Integration

### Frontend Tests for Backend Integration:
```javascript
// tests/integration.test.js
describe('Backend Integration', () => {
    test('should connect to all backend services', async () => {
        const response = await fetch('/api/dashboard');
        const data = await response.json();
        
        expect(data.success).toBe(true);
        expect(data.data.services.services_online).toBeGreaterThan(0);
    });

    test('should create repository via backend', async () => {
        const repoData = {
            name: 'test-repo',
            url: 'https://github.com/test/repo.git',
            branch: 'main'
        };
        
        const response = await fetch('/api/repositories', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(repoData)
        });
        
        const result = await response.json();
        expect(result.success).toBe(true);
        expect(result.data.name).toBe('test-repo');
    });
});
```

---

## 🚀 Next Steps

1. **Update Frontend Environment**: Add backend service URLs
2. **Implement API Client**: Create proxy layer in frontend
3. **Update Frontend Components**: Integrate with backend APIs
4. **Test Integration**: Verify frontend-backend communication
5. **Deploy Integrated System**: Use integrated docker-compose

**🎯 Esta integración permite que el frontend ia-ops-docs consuma todos los servicios del backend ia-ops-dev-core de manera transparente y eficiente.**
