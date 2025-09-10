# 🧪 Tests - IA-Ops Dev Core Services

Conjunto completo de pruebas para validar el funcionamiento de todos los servicios de IA-Ops Dev Core integrados con PostgreSQL, Redis y MinIO.

## 📁 Archivos de Prueba

| Archivo | Descripción |
|---------|-------------|
| `test_api_methods.py` | Métodos base para pruebas de API |
| `service_tests.py` | Pruebas completas por servicio |
| `performance_tests.py` | Pruebas de rendimiento y carga |
| `quick_test.py` | Pruebas rápidas de validación |
| `TESTING_GUIDE.md` | Guía completa de pruebas |

## 🚀 Ejecución Rápida

### Prueba Rápida (Recomendado para Frontend)
```bash
cd /home/giovanemere/ia-ops/ia-ops-dev-core/tests
python quick_test.py
```

### Pruebas Completas
```bash
# Todas las pruebas por servicio
python service_tests.py

# Solo pruebas de rendimiento
python performance_tests.py

# Métodos individuales
python test_api_methods.py
```

## 📊 Servicios Integrados

### Arquitectura Actual
- **PostgreSQL**: Base de datos principal (Puerto 5434)
- **Redis**: Cache y colas (Puerto 6380)
- **MinIO**: Almacenamiento de archivos (Puerto 9898)

### Servicios API
- **Repository Manager**: `localhost:8860` (PostgreSQL + MinIO)
- **Task Manager**: `localhost:8861` (PostgreSQL + Redis)
- **Log Manager**: `localhost:8862` (PostgreSQL)
- **DataSync Manager**: `localhost:8863` (PostgreSQL + MinIO)
- **GitHub Runner Manager**: `localhost:8864` (PostgreSQL)
- **TechDocs Builder**: `localhost:8865` (PostgreSQL)

## 🔧 Para Desarrolladores Frontend

### Validación Básica
```python
from test_api_methods import IAOpsTestClient

client = IAOpsTestClient()

# Verificar que todos los servicios estén activos
health = client.test_all_health_checks()
print(health)
```

### Datos de Ejemplo
```python
# Repositorio de ejemplo
repo_data = {
    "name": "mi-proyecto",
    "url": "https://github.com/usuario/proyecto.git",
    "branch": "main",
    "description": "Mi proyecto de ejemplo"
}

# Crear repositorio
result = client.test_create_repository(repo_data)
```

### Workflow Completo
```python
# Test de workflow completo (crear repo -> tarea -> log -> backup)
workflow = client.test_full_workflow()
```

## 📈 Resultados Esperados

### Health Check Exitoso
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

### Respuesta API Estándar
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "ejemplo",
    "created_at": "2025-09-01T21:00:00Z"
  },
  "message": "Operation completed successfully"
}
```

## 🚨 Troubleshooting

### Servicios No Disponibles
```bash
# Verificar estado
cd /home/giovanemere/ia-ops/ia-ops-dev-core
./scripts/status.sh

# Reiniciar si es necesario
./scripts/restart.sh
```

### Problemas de Base de Datos
```bash
# Verificar PostgreSQL
docker exec -it iaops-postgres psql -U postgres -d iaops -c "SELECT 1;"

# Verificar Redis
docker exec -it iaops-redis redis-cli ping

# Verificar MinIO
curl http://localhost:9898/minio/health/live
```

## 📝 Archivos Generados

Después de ejecutar las pruebas se generan:
- `test_results.json` - Resultados de pruebas por servicio
- `performance_results.json` - Métricas de rendimiento
- `test_report.html` - Reporte visual (opcional)

## 🎯 Casos de Uso Frontend

### 1. Validación de Formularios
```javascript
// Validar datos antes de enviar
const validateRepo = async (repoData) => {
  const response = await fetch('http://localhost:8860/repositories', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(repoData)
  });
  return response.ok;
};
```

### 2. Monitoreo de Tareas
```javascript
// Verificar estado de tarea
const checkTaskStatus = async (taskId) => {
  const response = await fetch(`http://localhost:8861/tasks/${taskId}`);
  const task = await response.json();
  return task.data.status; // 'pending', 'running', 'completed', 'failed'
};
```

### 3. Logs en Tiempo Real
```javascript
// Obtener logs recientes
const getRecentLogs = async (service) => {
  const response = await fetch(`http://localhost:8862/logs/${service}`);
  const logs = await response.json();
  return logs.data;
};
```

---

**🚀 Estos métodos de prueba proporcionan todo lo necesario para que el frontend desarrolle las funcionalidades de manera confiable y eficiente.**
