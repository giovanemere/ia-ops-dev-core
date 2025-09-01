# 🧪 Guía de Pruebas - IA-Ops Dev Core Services

## 📋 Resumen

Esta guía proporciona métodos de prueba completos para todos los servicios de IA-Ops Dev Core, integrados con PostgreSQL, Redis y MinIO.

## 🏗️ Arquitectura de Servicios

### Servicios Disponibles
- **Repository Manager** (Puerto 8860) - PostgreSQL + MinIO
- **Task Manager** (Puerto 8861) - PostgreSQL + Redis
- **Log Manager** (Puerto 8862) - PostgreSQL
- **DataSync Manager** (Puerto 8863) - PostgreSQL + MinIO
- **GitHub Runner Manager** (Puerto 8864) - PostgreSQL
- **TechDocs Builder** (Puerto 8865) - PostgreSQL

### Integración de Bases de Datos
- **PostgreSQL**: Base de datos principal para todos los servicios
- **Redis**: Cache y cola de tareas (Task Manager)
- **MinIO**: Almacenamiento de archivos (Repository Manager, DataSync)

## 🚀 Configuración de Pruebas

### Prerrequisitos
```bash
# Instalar dependencias
pip install requests aiohttp

# Verificar servicios activos
./scripts/status.sh
```

### Variables de Entorno
```bash
# Base URLs de servicios
REPOSITORY_MANAGER_URL=http://localhost:8860
TASK_MANAGER_URL=http://localhost:8861
LOG_MANAGER_URL=http://localhost:8862
DATASYNC_MANAGER_URL=http://localhost:8863
GITHUB_RUNNER_MANAGER_URL=http://localhost:8864
TECHDOCS_BUILDER_URL=http://localhost:8865

# Bases de datos
DATABASE_URL=postgresql://postgres:postgres@localhost:5434/iaops
REDIS_URL=redis://localhost:6380/0
MINIO_ENDPOINT=localhost:9898
```

## 🔧 Métodos de Prueba

### 1. Pruebas Básicas
```python
from test_api_methods import IAOpsTestClient

client = IAOpsTestClient()

# Health checks de todos los servicios
health_results = client.test_all_health_checks()
```

### 2. Pruebas por Servicio

#### Repository Manager
```python
# Crear repositorio
repo_data = {
    "name": "test-repo",
    "url": "https://github.com/user/repo.git",
    "branch": "main",
    "description": "Test repository"
}
result = client.test_create_repository(repo_data)

# Listar repositorios
repos = client.test_get_repositories()

# Sincronizar repositorio
sync_result = client.test_sync_repository(repo_id)
```

#### Task Manager
```python
# Crear tarea
task_data = {
    "name": "build-task",
    "type": "build",
    "repository_id": 1,
    "command": "npm install && npm run build",
    "environment": {"NODE_ENV": "production"}
}
result = client.test_create_task(task_data)

# Ejecutar tarea
execution = client.test_execute_task(task_id)

# Obtener logs de tarea
logs = client.test_get_task_logs(task_id)
```

#### Log Manager
```python
# Crear log
log_data = {
    "service": "test-service",
    "level": "info",
    "message": "Test message",
    "metadata": {"user": "test"}
}
result = client.test_create_log(log_data)

# Buscar logs
search_results = client.test_search_logs("error")

# Logs por servicio
service_logs = client.test_get_logs_by_service("repository-manager")
```

#### DataSync Manager
```python
# Crear trabajo de sincronización
sync_job = {
    "name": "backup-repos",
    "source": "postgresql://repos",
    "destination": "minio://backups/"
}
result = client.test_create_sync_job(sync_job)

# Crear backup
backup_data = {
    "name": "daily-backup",
    "source": "repositories",
    "destination": "minio://daily-backups/"
}
backup = client.test_create_backup(backup_data)
```

### 3. Pruebas de Integración
```python
# Workflow completo
workflow_result = client.test_full_workflow()

# Pruebas de conectividad de bases de datos
from service_tests import ServiceTester
tester = ServiceTester()
integration_results = tester.run_integration_tests()
```

### 4. Pruebas de Rendimiento
```python
from performance_tests import PerformanceTester
import asyncio

async def run_performance():
    tester = PerformanceTester()
    results = await tester.run_full_performance_suite()
    return results

# Ejecutar
results = asyncio.run(run_performance())
```

## 📊 Ejecutar Pruebas

### Pruebas Completas
```bash
# Ejecutar todas las pruebas
cd /home/giovanemere/ia-ops/ia-ops-dev-core/tests
python service_tests.py

# Solo pruebas de rendimiento
python performance_tests.py

# Pruebas específicas
python test_api_methods.py
```

### Resultados Esperados

#### Health Checks
```json
{
  "repository": {"success": true, "status_code": 200},
  "task": {"success": true, "status_code": 200},
  "log": {"success": true, "status_code": 200},
  "datasync": {"success": true, "status_code": 200},
  "github_runner": {"success": true, "status_code": 200},
  "techdocs": {"success": true, "status_code": 200}
}
```

#### Respuesta Estándar
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "example",
    "created_at": "2025-09-01T21:00:00Z"
  },
  "message": "Operation completed successfully"
}
```

## 🔍 Validación de Integración

### PostgreSQL
- Verificar conexión a través de Repository Manager
- Validar operaciones CRUD en todas las tablas
- Comprobar transacciones y rollbacks

### Redis
- Verificar cache de tareas en Task Manager
- Validar cola de trabajos
- Comprobar expiración de cache

### MinIO
- Verificar subida de archivos en Repository Manager
- Validar backups en DataSync Manager
- Comprobar políticas de acceso

## 🚨 Troubleshooting

### Errores Comunes

#### Conexión de Base de Datos
```bash
# Verificar PostgreSQL
docker exec -it iaops-postgres psql -U postgres -d iaops -c "SELECT 1;"

# Verificar Redis
docker exec -it iaops-redis redis-cli ping

# Verificar MinIO
curl http://localhost:9898/minio/health/live
```

#### Servicios No Disponibles
```bash
# Verificar estado de contenedores
docker ps | grep iaops

# Reiniciar servicios
./scripts/restart.sh

# Ver logs de errores
./scripts/logs.sh
```

#### Problemas de Red
```bash
# Verificar red Docker
docker network ls | grep iaops

# Verificar conectividad entre servicios
docker exec iaops-repository-manager curl -f http://iaops-task-manager:8851/health
```

## 📈 Métricas de Rendimiento

### Objetivos de Rendimiento
- **Tiempo de respuesta**: < 200ms para operaciones básicas
- **Throughput**: > 100 requests/segundo por servicio
- **Disponibilidad**: > 99.9%
- **Tasa de error**: < 0.1%

### Monitoreo
```python
# Métricas en tiempo real
async def monitor_services():
    tester = PerformanceTester()
    while True:
        results = await tester.test_all_services_performance()
        print(f"Avg response time: {results['repository']['avg_response_time']*1000:.2f}ms")
        await asyncio.sleep(60)
```

## 🔧 Personalización de Pruebas

### Agregar Nuevas Pruebas
```python
class CustomTester(IAOpsTestClient):
    def test_custom_endpoint(self, data):
        return self._request('POST', 'repository', '/custom', data)
    
    def test_business_logic(self):
        # Lógica específica del negocio
        pass
```

### Configurar Datos de Prueba
```python
# Modificar datos en test_api_methods.py
CUSTOM_REPOSITORY = {
    "name": "custom-repo",
    "url": "https://github.com/custom/repo.git",
    "branch": "develop",
    "description": "Custom test repository"
}
```

## 📝 Reportes

### Generar Reporte HTML
```python
def generate_html_report(results):
    html = f"""
    <html>
    <head><title>IA-Ops Test Report</title></head>
    <body>
        <h1>Test Results</h1>
        <pre>{json.dumps(results, indent=2)}</pre>
    </body>
    </html>
    """
    with open('test_report.html', 'w') as f:
        f.write(html)
```

### Integración con CI/CD
```yaml
# .github/workflows/test.yml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        run: |
          cd tests
          python service_tests.py
          python performance_tests.py
```

## 🎯 Casos de Uso para Frontend

### Validación de Formularios
```javascript
// Validar antes de enviar
const validateRepository = async (repoData) => {
  const response = await fetch('http://localhost:8860/repositories', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(repoData)
  });
  return response.json();
};
```

### Monitoreo en Tiempo Real
```javascript
// WebSocket para logs en tiempo real
const ws = new WebSocket('ws://localhost:8862/logs/stream');
ws.onmessage = (event) => {
  const log = JSON.parse(event.data);
  updateLogDisplay(log);
};
```

### Gestión de Estado
```javascript
// Estado de tareas
const taskStatus = await fetch('http://localhost:8861/tasks/1');
const task = await taskStatus.json();

if (task.data.status === 'running') {
  // Mostrar progreso
  showProgress(task.data.progress);
}
```

---

**🚀 Esta guía proporciona todo lo necesario para que el frontend desarrolle las funcionalidades de manera eficiente y confiable.**
