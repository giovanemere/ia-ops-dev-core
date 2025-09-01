# 🧪 API Specifications for IA-Ops Veritas

## 📋 Test Suite Configuration

### Service Health Checks
```javascript
const healthChecks = [
  {
    name: "Repository Manager",
    url: "http://localhost:8860/health",
    expected: { success: true, status_code: 200 }
  },
  {
    name: "Task Manager", 
    url: "http://localhost:8861/health",
    expected: { success: true, status_code: 200 }
  },
  {
    name: "Log Manager",
    url: "http://localhost:8862/health", 
    expected: { success: true, status_code: 200 }
  },
  {
    name: "DataSync Manager",
    url: "http://localhost:8863/health",
    expected: { success: true, status_code: 200 }
  },
  {
    name: "GitHub Runner Manager",
    url: "http://localhost:8864/health",
    expected: { success: true, status_code: 200 }
  },
  {
    name: "TechDocs Builder",
    url: "http://localhost:8865/health",
    expected: { success: true, status_code: 200 }
  }
];
```

### Repository Manager Test Cases
```javascript
const repositoryTests = [
  {
    name: "Create Repository",
    method: "POST",
    url: "http://localhost:8860/api/v1/repositories",
    payload: {
      name: "veritas-test-repo",
      url: "https://github.com/test/veritas.git",
      branch: "main",
      description: "Test repository for Veritas"
    },
    expected: {
      success: true,
      data: {
        id: "number",
        name: "veritas-test-repo",
        status: "active"
      }
    }
  },
  {
    name: "List Repositories",
    method: "GET", 
    url: "http://localhost:8860/api/v1/repositories",
    expected: {
      success: true,
      data: "array"
    }
  },
  {
    name: "Get Repository",
    method: "GET",
    url: "http://localhost:8860/api/v1/repositories/{id}",
    expected: {
      success: true,
      data: {
        id: "number",
        name: "string",
        url: "string",
        branch: "string"
      }
    }
  },
  {
    name: "Update Repository",
    method: "PUT",
    url: "http://localhost:8860/api/v1/repositories/{id}",
    payload: {
      description: "Updated description"
    },
    expected: {
      success: true,
      data: {
        description: "Updated description"
      }
    }
  },
  {
    name: "Sync Repository",
    method: "POST",
    url: "http://localhost:8860/api/v1/repositories/{id}/sync",
    expected: {
      success: true,
      data: {
        status: "active",
        last_sync: "string"
      }
    }
  },
  {
    name: "Delete Repository",
    method: "DELETE",
    url: "http://localhost:8860/api/v1/repositories/{id}",
    expected: {
      success: true,
      data: {
        id: "number"
      }
    }
  }
];
```

### Task Manager Test Cases
```javascript
const taskTests = [
  {
    name: "Create Task",
    method: "POST",
    url: "http://localhost:8861/api/v1/tasks",
    payload: {
      name: "veritas-test-task",
      type: "test",
      repository_id: 1,
      command: "npm test",
      environment: {
        NODE_ENV: "test",
        CI: "true"
      }
    },
    expected: {
      success: true,
      data: {
        id: "number",
        name: "veritas-test-task",
        status: "pending"
      }
    }
  },
  {
    name: "List Tasks",
    method: "GET",
    url: "http://localhost:8861/api/v1/tasks",
    expected: {
      success: true,
      data: "array"
    }
  },
  {
    name: "Get Task",
    method: "GET", 
    url: "http://localhost:8861/api/v1/tasks/{id}",
    expected: {
      success: true,
      data: {
        id: "number",
        name: "string",
        status: "string",
        type: "string"
      }
    }
  },
  {
    name: "Execute Task",
    method: "POST",
    url: "http://localhost:8861/api/v1/tasks/{id}/execute",
    expected: {
      success: true,
      data: {
        id: "number",
        status: "completed",
        started_at: "string",
        completed_at: "string"
      }
    }
  },
  {
    name: "Get Task Logs",
    method: "GET",
    url: "http://localhost:8861/api/v1/tasks/{id}/logs",
    expected: {
      success: true,
      data: {
        task_id: "number",
        logs: "string"
      }
    }
  }
];
```

### Integration Test Scenarios
```javascript
const integrationTests = [
  {
    name: "Complete Workflow",
    description: "Create repo → Create task → Execute → Get logs",
    steps: [
      {
        step: 1,
        action: "Create Repository",
        method: "POST",
        url: "http://localhost:8860/api/v1/repositories",
        payload: {
          name: "integration-test-repo",
          url: "https://github.com/test/integration.git",
          branch: "main"
        },
        store: "repo_id"
      },
      {
        step: 2,
        action: "Create Task",
        method: "POST", 
        url: "http://localhost:8861/api/v1/tasks",
        payload: {
          name: "integration-task",
          type: "build",
          repository_id: "{repo_id}",
          command: "echo 'Integration test'"
        },
        store: "task_id"
      },
      {
        step: 3,
        action: "Execute Task",
        method: "POST",
        url: "http://localhost:8861/api/v1/tasks/{task_id}/execute"
      },
      {
        step: 4,
        action: "Get Task Logs",
        method: "GET",
        url: "http://localhost:8861/api/v1/tasks/{task_id}/logs"
      },
      {
        step: 5,
        action: "Create Log Entry",
        method: "POST",
        url: "http://localhost:8862/api/v1/logs",
        payload: {
          service: "integration-test",
          level: "info",
          message: "Integration test completed successfully"
        }
      }
    ]
  }
];
```

### Performance Test Configuration
```javascript
const performanceTests = [
  {
    name: "Repository Manager Load Test",
    target: "http://localhost:8860",
    scenarios: [
      {
        name: "List Repositories",
        method: "GET",
        url: "/api/v1/repositories",
        weight: 70,
        duration: "2m",
        rate: "10/s"
      },
      {
        name: "Create Repository",
        method: "POST", 
        url: "/api/v1/repositories",
        payload: {
          name: "load-test-{random}",
          url: "https://github.com/test/load-{random}.git",
          branch: "main"
        },
        weight: 30,
        duration: "2m", 
        rate: "5/s"
      }
    ],
    thresholds: {
      http_req_duration: ["p(95)<500"],
      http_req_failed: ["rate<0.1"]
    }
  },
  {
    name: "Task Manager Load Test",
    target: "http://localhost:8861",
    scenarios: [
      {
        name: "List Tasks",
        method: "GET",
        url: "/api/v1/tasks",
        weight: 50,
        duration: "2m",
        rate: "8/s"
      },
      {
        name: "Create and Execute Task",
        method: "POST",
        url: "/api/v1/tasks",
        payload: {
          name: "load-test-task-{random}",
          type: "test",
          command: "echo 'Load test'"
        },
        weight: 50,
        duration: "2m",
        rate: "3/s"
      }
    ],
    thresholds: {
      http_req_duration: ["p(95)<800"],
      http_req_failed: ["rate<0.05"]
    }
  }
];
```

### Database Integration Tests
```javascript
const databaseTests = [
  {
    name: "PostgreSQL Integration",
    description: "Test PostgreSQL connectivity through services",
    tests: [
      {
        service: "Repository Manager",
        action: "Create and retrieve repository",
        validates: "PostgreSQL CRUD operations"
      },
      {
        service: "Task Manager", 
        action: "Create and list tasks",
        validates: "PostgreSQL transactions"
      },
      {
        service: "Log Manager",
        action: "Create and search logs", 
        validates: "PostgreSQL text search"
      }
    ]
  },
  {
    name: "Redis Integration",
    description: "Test Redis connectivity through Task Manager",
    tests: [
      {
        service: "Task Manager",
        action: "Queue task execution",
        validates: "Redis queue operations"
      },
      {
        service: "Task Manager",
        action: "Cache task results",
        validates: "Redis caching"
      }
    ]
  },
  {
    name: "MinIO Integration", 
    description: "Test MinIO connectivity through services",
    tests: [
      {
        service: "Repository Manager",
        action: "Store repository files",
        validates: "MinIO file operations"
      },
      {
        service: "DataSync Manager",
        action: "Create backup",
        validates: "MinIO backup operations"
      }
    ]
  }
];
```

### Error Handling Tests
```javascript
const errorTests = [
  {
    name: "Repository Not Found",
    method: "GET",
    url: "http://localhost:8860/api/v1/repositories/99999",
    expected: {
      success: false,
      error: {
        code: "NOT_FOUND",
        message: "Repository not found"
      },
      status_code: 404
    }
  },
  {
    name: "Invalid Repository Data",
    method: "POST",
    url: "http://localhost:8860/api/v1/repositories",
    payload: {
      name: "",
      url: "invalid-url"
    },
    expected: {
      success: false,
      error: {
        code: "VALIDATION_ERROR"
      },
      status_code: 400
    }
  },
  {
    name: "Task Already Running",
    method: "POST",
    url: "http://localhost:8861/api/v1/tasks/{running_task_id}/execute",
    expected: {
      success: false,
      error: {
        code: "TASK_RUNNING",
        message: "Task is already running"
      },
      status_code: 409
    }
  }
];
```

### Metrics Collection
```javascript
const metricsConfig = {
  collection_interval: 30000, // 30 seconds
  endpoints: [
    {
      name: "Service Status",
      url: "http://localhost:8870/api/status",
      metrics: ["services_online", "response_times"]
    },
    {
      name: "Repository Stats",
      url: "http://localhost:8860/api/v1/repositories",
      metrics: ["total_repositories", "active_repositories"]
    },
    {
      name: "Task Stats", 
      url: "http://localhost:8861/api/v1/tasks",
      metrics: ["total_tasks", "running_tasks", "completed_tasks"]
    }
  ],
  alerts: [
    {
      condition: "services_online < 6",
      message: "Some services are offline",
      severity: "critical"
    },
    {
      condition: "avg_response_time > 1000",
      message: "High response times detected",
      severity: "warning"
    }
  ]
};
```

### Test Execution Order
```javascript
const testSuite = {
  name: "IA-Ops Dev Core Test Suite",
  execution_order: [
    {
      phase: "Health Checks",
      tests: healthChecks,
      required: true,
      timeout: 30000
    },
    {
      phase: "Database Connectivity",
      tests: databaseTests,
      required: true,
      timeout: 60000
    },
    {
      phase: "API Functionality",
      tests: [...repositoryTests, ...taskTests],
      required: true,
      timeout: 120000
    },
    {
      phase: "Integration Scenarios",
      tests: integrationTests,
      required: false,
      timeout: 180000
    },
    {
      phase: "Error Handling",
      tests: errorTests,
      required: false,
      timeout: 60000
    },
    {
      phase: "Performance Testing",
      tests: performanceTests,
      required: false,
      timeout: 300000
    }
  ],
  reporting: {
    format: ["json", "html", "junit"],
    include_metrics: true,
    include_screenshots: false
  }
};
```

---

## 🚀 Implementation Guide for ia-ops-veritas

### 1. Setup API Client
```javascript
// src/services/apiClient.js
class IAOpsApiClient {
  constructor(baseUrl = 'http://localhost:8870') {
    this.baseUrl = baseUrl;
    this.services = {
      repository: 'http://localhost:8860',
      task: 'http://localhost:8861',
      log: 'http://localhost:8862',
      datasync: 'http://localhost:8863',
      github_runner: 'http://localhost:8864',
      techdocs: 'http://localhost:8865'
    };
  }

  async healthCheck(service) {
    const response = await fetch(`${this.services[service]}/health`);
    return response.json();
  }

  async getServiceStatus() {
    const response = await fetch(`${this.baseUrl}/api/status`);
    return response.json();
  }
}
```

### 2. Test Runner Implementation
```javascript
// src/services/testRunner.js
class TestRunner {
  constructor(apiClient) {
    this.apiClient = apiClient;
    this.results = [];
  }

  async runTestSuite(testSuite) {
    for (const phase of testSuite.execution_order) {
      const phaseResults = await this.runPhase(phase);
      this.results.push({
        phase: phase.phase,
        results: phaseResults,
        passed: phaseResults.every(r => r.passed)
      });
    }
    return this.results;
  }

  async runPhase(phase) {
    const results = [];
    for (const test of phase.tests) {
      const result = await this.runTest(test);
      results.push(result);
    }
    return results;
  }
}
```

---

**🎯 Estas especificaciones están listas para implementar en ia-ops-veritas y crear un portal completo de pruebas automatizadas.**
