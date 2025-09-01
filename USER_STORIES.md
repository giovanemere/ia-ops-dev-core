# 📋 Historias de Usuario - IA-Ops Veritas Integration

## 🎯 Epic: Portal de Pruebas Automatizadas

### Historia 1: Visualización de Estado de Servicios
**Como** desarrollador  
**Quiero** ver el estado en tiempo real de todos los servicios de IA-Ops Dev Core  
**Para** monitorear la salud del sistema antes de ejecutar pruebas

#### Criterios de Aceptación:
- [ ] Mostrar estado online/offline de cada servicio
- [ ] Indicar tiempo de respuesta de cada servicio
- [ ] Mostrar integración con bases de datos (PostgreSQL, Redis, MinIO)
- [ ] Auto-refresh cada 30 segundos
- [ ] Alertas visuales para servicios offline

#### Endpoints:
```
GET http://localhost:8870/api/status
GET http://localhost:8860/health (Repository Manager)
GET http://localhost:8861/health (Task Manager)
GET http://localhost:8862/health (Log Manager)
GET http://localhost:8863/health (DataSync Manager)
GET http://localhost:8864/health (GitHub Runner Manager)
GET http://localhost:8865/health (TechDocs Builder)
```

---

### Historia 2: Pruebas Automatizadas de APIs
**Como** QA Engineer  
**Quiero** ejecutar pruebas automatizadas de todos los endpoints  
**Para** validar el funcionamiento correcto de las APIs

#### Criterios de Aceptación:
- [ ] Ejecutar pruebas CRUD para Repository Manager
- [ ] Ejecutar pruebas de Task Manager con Redis
- [ ] Validar Log Manager con PostgreSQL
- [ ] Probar DataSync Manager con MinIO
- [ ] Generar reporte de resultados
- [ ] Mostrar métricas de rendimiento

#### Test Cases:
```javascript
// Repository Manager Tests
POST /api/v1/repositories - Create repository
GET /api/v1/repositories - List repositories  
GET /api/v1/repositories/{id} - Get repository
PUT /api/v1/repositories/{id} - Update repository
DELETE /api/v1/repositories/{id} - Delete repository
POST /api/v1/repositories/{id}/sync - Sync repository

// Task Manager Tests
POST /api/v1/tasks - Create task
GET /api/v1/tasks - List tasks
POST /api/v1/tasks/{id}/execute - Execute task
GET /api/v1/tasks/{id}/logs - Get task logs
```

---

### Historia 3: Pruebas de Integración
**Como** DevOps Engineer  
**Quiero** ejecutar pruebas de integración entre servicios  
**Para** validar el flujo completo del sistema

#### Criterios de Aceptación:
- [ ] Crear repositorio → Crear tarea → Ejecutar → Ver logs
- [ ] Validar sincronización con MinIO
- [ ] Probar cola de tareas en Redis
- [ ] Verificar persistencia en PostgreSQL
- [ ] Medir tiempo de respuesta end-to-end

#### Workflow Test:
```javascript
const integrationTest = async () => {
  // 1. Create repository
  const repo = await createRepository({
    name: "test-integration",
    url: "https://github.com/test/repo.git",
    branch: "main"
  });
  
  // 2. Create task for repository
  const task = await createTask({
    name: "integration-build",
    type: "build",
    repository_id: repo.id,
    command: "npm install && npm run build"
  });
  
  // 3. Execute task
  const execution = await executeTask(task.id);
  
  // 4. Verify logs
  const logs = await getTaskLogs(task.id);
  
  // 5. Create backup
  const backup = await createBackup({
    name: `backup-${repo.id}`,
    source: `repository-${repo.id}`,
    destination: "minio://backups/"
  });
  
  return { repo, task, execution, logs, backup };
};
```

---

### Historia 4: Dashboard de Métricas
**Como** Product Manager  
**Quiero** ver métricas de rendimiento y disponibilidad  
**Para** tomar decisiones sobre la infraestructura

#### Criterios de Aceptación:
- [ ] Mostrar uptime de servicios
- [ ] Gráficos de tiempo de respuesta
- [ ] Estadísticas de pruebas (pass/fail)
- [ ] Alertas de rendimiento
- [ ] Exportar reportes

#### Métricas:
```javascript
const metrics = {
  services: {
    repository_manager: {
      uptime: "99.9%",
      avg_response_time: "120ms",
      requests_per_minute: 45,
      error_rate: "0.1%"
    },
    task_manager: {
      uptime: "99.8%", 
      avg_response_time: "200ms",
      active_tasks: 12,
      completed_tasks: 1250
    }
  },
  databases: {
    postgresql: { status: "healthy", connections: 15 },
    redis: { status: "healthy", memory_usage: "45%" },
    minio: { status: "healthy", storage_used: "2.3GB" }
  }
};
```

---

### Historia 5: Pruebas de Carga
**Como** Performance Engineer  
**Quiero** ejecutar pruebas de carga en los servicios  
**Para** validar la capacidad del sistema

#### Criterios de Aceptación:
- [ ] Ejecutar 100 requests concurrentes
- [ ] Medir degradación de rendimiento
- [ ] Identificar cuellos de botella
- [ ] Generar reporte de capacidad
- [ ] Alertas de límites

#### Load Test Configuration:
```javascript
const loadTest = {
  concurrent_users: 50,
  duration: "5m",
  ramp_up: "30s",
  scenarios: [
    {
      name: "repository_crud",
      weight: 40,
      endpoints: [
        "GET /api/v1/repositories",
        "POST /api/v1/repositories", 
        "GET /api/v1/repositories/{id}"
      ]
    },
    {
      name: "task_execution",
      weight: 60,
      endpoints: [
        "POST /api/v1/tasks",
        "POST /api/v1/tasks/{id}/execute",
        "GET /api/v1/tasks/{id}/logs"
      ]
    }
  ]
};
```

---

## 🔧 Especificaciones Técnicas

### API Base URLs
```
Repository Manager: http://localhost:8860
Task Manager: http://localhost:8861
Log Manager: http://localhost:8862
DataSync Manager: http://localhost:8863
GitHub Runner Manager: http://localhost:8864
TechDocs Builder: http://localhost:8865
Swagger Portal: http://localhost:8870
```

### Authentication
```javascript
// No authentication required for testing environment
// Production will use JWT tokens
```

### Response Format
```javascript
// Success Response
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed successfully"
}

// Error Response  
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

### Test Data Templates
```javascript
const testData = {
  repository: {
    name: "veritas-test-repo",
    url: "https://github.com/test/veritas.git",
    branch: "main",
    description: "Test repository for Veritas"
  },
  task: {
    name: "veritas-test-task",
    type: "test",
    repository_id: 1,
    command: "npm test",
    environment: { NODE_ENV: "test" }
  },
  log: {
    service: "veritas-testing",
    level: "info", 
    message: "Test execution completed",
    metadata: { test_id: "12345" }
  }
};
```

---

## 🚀 Implementación Sugerida

### Estructura de Proyecto para ia-ops-veritas:
```
ia-ops-veritas/
├── src/
│   ├── components/
│   │   ├── ServiceStatus.jsx
│   │   ├── TestRunner.jsx
│   │   ├── MetricsDashboard.jsx
│   │   └── LoadTester.jsx
│   ├── services/
│   │   ├── apiClient.js
│   │   ├── testRunner.js
│   │   └── metricsCollector.js
│   ├── tests/
│   │   ├── integration/
│   │   ├── performance/
│   │   └── unit/
│   └── utils/
├── config/
│   ├── endpoints.js
│   ├── testSuites.js
│   └── loadTestConfig.js
└── docs/
    ├── API_INTEGRATION.md
    └── TEST_SCENARIOS.md
```

### Configuración de Endpoints:
```javascript
// config/endpoints.js
export const ENDPOINTS = {
  SWAGGER_PORTAL: 'http://localhost:8870',
  REPOSITORY_MANAGER: 'http://localhost:8860',
  TASK_MANAGER: 'http://localhost:8861',
  LOG_MANAGER: 'http://localhost:8862',
  DATASYNC_MANAGER: 'http://localhost:8863',
  GITHUB_RUNNER_MANAGER: 'http://localhost:8864',
  TECHDOCS_BUILDER: 'http://localhost:8865'
};
```

---

**🎯 Estas historias de usuario están listas para implementar en ia-ops-veritas y crear un portal completo de pruebas automatizadas.**
