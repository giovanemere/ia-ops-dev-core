#!/bin/bash

echo "🔗 IA-Ops Frontend-Backend Integration Setup"
echo "============================================="

# Check if ia-ops-docs exists
DOCS_PATH="/home/giovanemere/ia-ops/ia-ops-docs"
if [ ! -d "$DOCS_PATH" ]; then
    echo "❌ ia-ops-docs not found at $DOCS_PATH"
    echo "Please clone it first: git clone git@github.com:giovanemere/ia-ops-docs.git"
    exit 1
fi

echo "✅ Found ia-ops-docs at $DOCS_PATH"

# Copy integration files
echo "📁 Copying integration files..."

# Copy API client
cp api_client.py "$DOCS_PATH/web-interface/"
echo "✅ Copied API client"

# Copy frontend routes (append to existing app.py)
echo "📝 Adding routes to app.py..."
cat frontend_routes.py >> "$DOCS_PATH/web-interface/app.py"
echo "✅ Added frontend routes"

# Copy environment configuration
cp .env.frontend "$DOCS_PATH/.env.integration"
echo "✅ Copied environment configuration"

# Update requirements.txt
echo "📦 Updating requirements..."
echo "requests>=2.31.0" >> "$DOCS_PATH/web-interface/requirements.txt"
echo "✅ Updated requirements"

# Create integration docker-compose
cat > "$DOCS_PATH/docker-compose.integrated.yml" << 'EOF'
version: '3.8'

services:
  # Frontend Portal
  ia-ops-portal:
    build: ./web-interface
    container_name: ia-ops-portal
    ports:
      - "8845:8845"
    environment:
      - SWAGGER_PORTAL_URL=http://host.docker.internal:8870
      - REPOSITORY_MANAGER_URL=http://host.docker.internal:8860
      - TASK_MANAGER_URL=http://host.docker.internal:8861
      - LOG_MANAGER_URL=http://host.docker.internal:8862
      - DATASYNC_MANAGER_URL=http://host.docker.internal:8863
      - GITHUB_RUNNER_MANAGER_URL=http://host.docker.internal:8864
      - TECHDOCS_BUILDER_URL=http://host.docker.internal:8865
      - MINIO_REST_API_URL=http://host.docker.internal:8848
      - MINIO_CONSOLE_URL=http://host.docker.internal:9899
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - ia-ops-network
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - minio-rest-api
    restart: unless-stopped

  # MinIO REST API (existing)
  minio-rest-api:
    build: ./minio-rest-api
    container_name: ia-ops-minio-rest-api
    ports:
      - "8848:8848"
    environment:
      - MINIO_ENDPOINT=host.docker.internal:9898
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin123
    networks:
      - ia-ops-network
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped

networks:
  ia-ops-network:
    driver: bridge
    name: ia-ops-integrated-network
EOF

echo "✅ Created integrated docker-compose"

# Create startup script
cat > "$DOCS_PATH/start-integrated.sh" << 'EOF'
#!/bin/bash

echo "🚀 Starting IA-Ops Integrated System..."

# Start backend services first
echo "📡 Starting backend services..."
cd ../ia-ops-dev-core
./scripts/start-with-swagger.sh

# Wait for backend to be ready
echo "⏳ Waiting for backend services to be ready..."
sleep 20

# Check backend health
echo "🏥 Checking backend health..."
for port in 8860 8861 8862 8863 8864 8865 8870; do
    if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1 || curl -s -f "http://localhost:$port/api/status" > /dev/null 2>&1; then
        echo "✅ Service on port $port: Online"
    else
        echo "❌ Service on port $port: Offline"
    fi
done

# Start frontend
echo "🌐 Starting frontend portal..."
cd ../ia-ops-docs
docker-compose -f docker-compose.integrated.yml up -d

echo ""
echo "🎉 IA-Ops Integrated System Started!"
echo "=================================="
echo "🌐 Frontend Portal: http://localhost:8845"
echo "📚 Backend Swagger: http://localhost:8870"
echo "📁 Repository Manager: http://localhost:8860/docs/"
echo "📋 Task Manager: http://localhost:8861/docs/"
echo "📊 Log Manager: http://localhost:8862/docs/"
echo ""
echo "🧪 Test integration: curl http://localhost:8845/api/integration/test"
EOF

chmod +x "$DOCS_PATH/start-integrated.sh"
echo "✅ Created startup script"

# Create JavaScript API client for frontend
cat > "$DOCS_PATH/web-interface/static/js/api-client.js" << 'EOF'
/**
 * JavaScript API Client for IA-Ops Frontend
 */
class IAOpsApiClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
        this.timeout = 10000;
    }

    async request(method, endpoint, data = null) {
        const config = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            signal: AbortSignal.timeout(this.timeout)
        };

        if (data) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, config);
            const result = await response.json();
            return {
                success: response.ok,
                status: response.status,
                data: result
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Dashboard
    async getDashboard() {
        return this.request('GET', '/api/dashboard');
    }

    async getServicesStatus() {
        return this.request('GET', '/api/services/status');
    }

    // Repositories
    async getRepositories() {
        return this.request('GET', '/api/repositories');
    }

    async createRepository(data) {
        return this.request('POST', '/api/repositories', data);
    }

    async updateRepository(id, data) {
        return this.request('PUT', `/api/repositories/${id}`, data);
    }

    async deleteRepository(id) {
        return this.request('DELETE', `/api/repositories/${id}`);
    }

    async syncRepository(id) {
        return this.request('POST', `/api/repositories/${id}/sync`);
    }

    // Tasks
    async getTasks() {
        return this.request('GET', '/api/tasks');
    }

    async createTask(data) {
        return this.request('POST', '/api/tasks', data);
    }

    async executeTask(id) {
        return this.request('POST', `/api/tasks/${id}/execute`);
    }

    async getTaskLogs(id) {
        return this.request('GET', `/api/tasks/${id}/logs`);
    }

    // Logs
    async getLogs(service = null, limit = 100) {
        const endpoint = service ? `/api/logs/${service}` : '/api/logs';
        return this.request('GET', `${endpoint}?limit=${limit}`);
    }

    async searchLogs(query, limit = 100) {
        return this.request('GET', `/api/logs/search?q=${encodeURIComponent(query)}&limit=${limit}`);
    }

    // Integration test
    async testIntegration() {
        return this.request('GET', '/api/integration/test');
    }
}

// Global instance
window.iaOpsApi = new IAOpsApiClient();
EOF

echo "✅ Created JavaScript API client"

# Create integration test page
cat > "$DOCS_PATH/web-interface/templates/integration-test.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA-Ops Integration Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test-result { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
        .loading { background-color: #fff3cd; color: #856404; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🔗 IA-Ops Integration Test</h1>
    
    <button onclick="testIntegration()">Test Backend Integration</button>
    <button onclick="testServices()">Test All Services</button>
    <button onclick="testWorkflow()">Test Complete Workflow</button>
    
    <div id="results"></div>

    <script src="/static/js/api-client.js"></script>
    <script>
        async function testIntegration() {
            showResult('Testing backend integration...', 'loading');
            
            try {
                const result = await iaOpsApi.testIntegration();
                if (result.success) {
                    showResult(`✅ Integration successful! ${result.data.services_online}/${result.data.total_services} services online`, 'success');
                } else {
                    showResult(`❌ Integration failed: ${result.error}`, 'error');
                }
            } catch (error) {
                showResult(`❌ Integration test error: ${error.message}`, 'error');
            }
        }

        async function testServices() {
            showResult('Testing individual services...', 'loading');
            
            const services = ['repositories', 'tasks', 'logs'];
            const results = [];
            
            for (const service of services) {
                try {
                    const result = await iaOpsApi.request('GET', `/api/${service}`);
                    results.push(`${service}: ${result.success ? '✅' : '❌'}`);
                } catch (error) {
                    results.push(`${service}: ❌ ${error.message}`);
                }
            }
            
            showResult(`Service tests:\n${results.join('\n')}`, 'success');
        }

        async function testWorkflow() {
            showResult('Testing complete workflow...', 'loading');
            
            try {
                // 1. Create repository
                const repoResult = await iaOpsApi.createRepository({
                    name: 'integration-test-repo',
                    url: 'https://github.com/test/integration.git',
                    branch: 'main',
                    description: 'Integration test repository'
                });
                
                if (!repoResult.success) {
                    throw new Error('Failed to create repository');
                }
                
                const repoId = repoResult.data.data.id;
                
                // 2. Create task
                const taskResult = await iaOpsApi.createTask({
                    name: 'integration-test-task',
                    type: 'test',
                    repository_id: repoId,
                    command: 'echo "Integration test successful"'
                });
                
                if (!taskResult.success) {
                    throw new Error('Failed to create task');
                }
                
                const taskId = taskResult.data.data.id;
                
                // 3. Execute task
                const executeResult = await iaOpsApi.executeTask(taskId);
                
                if (!executeResult.success) {
                    throw new Error('Failed to execute task');
                }
                
                showResult('✅ Complete workflow test successful!', 'success');
                
            } catch (error) {
                showResult(`❌ Workflow test failed: ${error.message}`, 'error');
            }
        }

        function showResult(message, type) {
            const results = document.getElementById('results');
            const div = document.createElement('div');
            div.className = `test-result ${type}`;
            div.textContent = message;
            results.appendChild(div);
        }
    </script>
</body>
</html>
EOF

echo "✅ Created integration test page"

echo ""
echo "🎉 Integration Setup Complete!"
echo "=============================="
echo ""
echo "📁 Files copied to ia-ops-docs:"
echo "  ✅ web-interface/api_client.py"
echo "  ✅ web-interface/static/js/api-client.js"
echo "  ✅ web-interface/templates/integration-test.html"
echo "  ✅ docker-compose.integrated.yml"
echo "  ✅ start-integrated.sh"
echo "  ✅ .env.integration"
echo ""
echo "🚀 Next Steps:"
echo "1. cd $DOCS_PATH"
echo "2. Review and merge .env.integration into .env"
echo "3. ./start-integrated.sh"
echo "4. Access http://localhost:8845"
echo "5. Test integration at http://localhost:8845/integration-test"
echo ""
echo "🔗 Integration URLs:"
echo "  Frontend Portal: http://localhost:8845"
echo "  Backend Swagger: http://localhost:8870"
echo "  Integration Test: http://localhost:8845/integration-test"
EOF

chmod +x integrate.sh
echo "✅ Created integration script"
