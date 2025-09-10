# 🧪 IA-Ops Testing Portal

Portal completo de pruebas automatizadas para IA-Ops Dev Core Services con mocks, performance testing y automatización.

## 🚀 Características

- **Pruebas Unitarias**: Validación de endpoints individuales
- **Pruebas de Integración**: Workflows completos entre servicios
- **Pruebas de Performance**: Carga, estrés y monitoreo continuo
- **Servicios Mock**: Simulación completa para pruebas aisladas
- **Automatización**: CI/CD integration y reportes automáticos
- **Reportes**: JSON, HTML y dashboards visuales

## 📁 Estructura

```
testing-portal/
├── test_cases_complete.json      # Casos de prueba completos
├── mock_services.py              # Servicios mock
├── performance_automation.py     # Automatización de performance
├── test_portal_runner.py         # Runner principal
├── start_testing_portal.sh       # Script de inicio
├── test-results/                 # Resultados de pruebas
└── README.md                     # Esta documentación
```

## 🛠️ Instalación

```bash
# 1. Navegar al directorio
cd /home/giovanemere/ia-ops/ia-ops-dev-core/testing-portal

# 2. Instalar dependencias (automático en primer uso)
./start_testing_portal.sh --help
```

## 🎯 Uso Rápido

### Pruebas con Servicios Mock (Recomendado)
```bash
# Ejecutar todas las pruebas con mocks
./start_testing_portal.sh --mocks

# Solo servicios mock (para desarrollo)
./start_testing_portal.sh --mocks-only
```

### Pruebas con Servicios Reales
```bash
# Primero iniciar backend
cd ../
./scripts/start-with-swagger.sh

# Luego ejecutar pruebas
cd testing-portal
./start_testing_portal.sh --real
```

### Pruebas Específicas
```bash
# Solo pruebas unitarias
./start_testing_portal.sh --suite unit

# Solo pruebas de integración
./start_testing_portal.sh --suite integration

# Solo pruebas de performance
./start_testing_portal.sh --suite performance
```

### Monitoreo Continuo
```bash
# Monitoreo de performance 24/7
./start_testing_portal.sh --monitor
```

## 📊 Tipos de Pruebas

### 1. Pruebas Unitarias
- **Health Checks**: Verificación de estado de servicios
- **CRUD Operations**: Crear, leer, actualizar, eliminar
- **Validation**: Validación de datos de entrada
- **Error Handling**: Manejo de errores y casos edge

### 2. Pruebas de Integración
- **Workflow Completo**: Repositorio → Tarea → Ejecución → Logs
- **Base de Datos**: PostgreSQL, Redis, MinIO
- **Comunicación Cross-Service**: Entre todos los servicios
- **Data Flow**: Flujo de datos end-to-end

### 3. Pruebas de Performance
- **Load Testing**: 10-100 usuarios concurrentes
- **Stress Testing**: Hasta encontrar punto de quiebre
- **Endurance Testing**: Pruebas de larga duración
- **Spike Testing**: Picos de carga súbitos

## 🎭 Servicios Mock

Los servicios mock simulan completamente el comportamiento del backend:

| Servicio | Puerto Mock | Puerto Real | Funcionalidad |
|----------|-------------|-------------|---------------|
| Repository Manager | 18860 | 8860 | CRUD repositorios |
| Task Manager | 18861 | 8861 | Gestión de tareas |
| Log Manager | 18862 | 8862 | Gestión de logs |

### Características de Mocks:
- **Respuestas Realistas**: Datos coherentes con el sistema real
- **Delays Simulados**: Tiempos de respuesta variables
- **Error Simulation**: Simulación de errores aleatorios
- **Auto-increment IDs**: IDs únicos automáticos
- **Template Responses**: Respuestas dinámicas basadas en request

## ⚡ Performance Testing

### Configuración de Carga
```json
{
  "concurrent_users": [10, 25, 50, 100],
  "duration": 300,
  "scenarios": [
    {
      "name": "list_repositories",
      "weight": 70,
      "endpoint": "/api/v1/repositories"
    },
    {
      "name": "create_repository", 
      "weight": 30,
      "endpoint": "/api/v1/repositories",
      "method": "POST"
    }
  ]
}
```

### Métricas Recopiladas
- **Response Time**: Min, Max, Mean, P95, P99
- **Throughput**: Requests per second
- **Error Rate**: Porcentaje de errores
- **System Metrics**: CPU, Memory, Disk, Network

### Thresholds
- **Response Time P95**: < 500ms
- **Error Rate**: < 1%
- **Throughput**: > 100 req/s

## 📈 Reportes

### Formatos Disponibles
- **JSON**: Datos estructurados para integración
- **HTML**: Reportes visuales con gráficos
- **JUnit**: Para integración con CI/CD

### Ejemplo de Reporte
```json
{
  "timestamp": "2025-09-01T23:00:00Z",
  "summary": {
    "total_tests": 45,
    "total_passed": 43,
    "total_failed": 2,
    "success_rate": 95.6
  },
  "test_suites": {
    "unit_tests": {
      "total": 20,
      "passed": 20,
      "failed": 0
    },
    "integration_tests": {
      "total": 15,
      "passed": 13,
      "failed": 2
    },
    "performance_tests": {
      "repository-manager": {
        "response_times": {
          "p95": 245.5,
          "mean": 156.2
        },
        "error_rate": 0.002,
        "throughput": 125.3
      }
    }
  }
}
```

## 🔧 Configuración Avanzada

### Archivo de Configuración
```json
{
  "test_suites": {
    "unit_tests": true,
    "integration_tests": true,
    "performance_tests": true,
    "security_tests": false
  },
  "services": {
    "repository-manager": "http://localhost:8860",
    "task-manager": "http://localhost:8861"
  },
  "thresholds": {
    "response_time_p95": 500,
    "error_rate": 0.01,
    "throughput_min": 100
  },
  "reporting": {
    "formats": ["json", "html"],
    "output_dir": "./test-results"
  }
}
```

### Variables de Entorno
```bash
# URLs de servicios
export REPOSITORY_MANAGER_URL=http://localhost:8860
export TASK_MANAGER_URL=http://localhost:8861

# Configuración de pruebas
export TEST_TIMEOUT=30
export MAX_CONCURRENT_USERS=100
export PERFORMANCE_TEST_DURATION=300
```

## 🚀 Integración CI/CD

### GitHub Actions
```yaml
name: IA-Ops Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Run Tests
        run: |
          cd testing-portal
          ./start_testing_portal.sh --mocks --suite all
      
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: testing-portal/test-results/
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    
    stages {
        stage('Unit Tests') {
            steps {
                sh 'cd testing-portal && ./start_testing_portal.sh --mocks --suite unit'
            }
        }
        
        stage('Integration Tests') {
            steps {
                sh 'cd testing-portal && ./start_testing_portal.sh --real --suite integration'
            }
        }
        
        stage('Performance Tests') {
            when { branch 'main' }
            steps {
                sh 'cd testing-portal && ./start_testing_portal.sh --real --suite performance'
            }
        }
    }
    
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'testing-portal/test-results',
                reportFiles: '*.html',
                reportName: 'Test Report'
            ])
        }
    }
}
```

## 🔍 Troubleshooting

### Servicios Mock No Inician
```bash
# Verificar puertos disponibles
netstat -tulpn | grep :1886

# Matar procesos existentes
pkill -f mock_services.py

# Reiniciar
./start_testing_portal.sh --mocks-only
```

### Servicios Reales No Disponibles
```bash
# Verificar backend
cd ../
./scripts/status.sh

# Iniciar backend si es necesario
./scripts/start-with-swagger.sh

# Verificar conectividad
curl http://localhost:8860/health
```

### Pruebas de Performance Lentas
```bash
# Reducir duración para pruebas rápidas
export PERFORMANCE_TEST_DURATION=60

# Reducir usuarios concurrentes
export MAX_CONCURRENT_USERS=25
```

## 📝 Casos de Uso

### Desarrollo Local
```bash
# Desarrollo con mocks (rápido)
./start_testing_portal.sh --mocks --suite unit

# Verificación antes de commit
./start_testing_portal.sh --real --suite all
```

### Testing en Staging
```bash
# Pruebas completas en staging
./start_testing_portal.sh --real --suite all

# Monitoreo continuo
./start_testing_portal.sh --monitor
```

### Production Monitoring
```bash
# Solo health checks en producción
./start_testing_portal.sh --real --suite unit

# Monitoreo de performance
./start_testing_portal.sh --monitor
```

## 🎯 Próximas Funcionalidades

- [ ] **Security Testing**: Pruebas de seguridad automatizadas
- [ ] **API Contract Testing**: Validación de contratos OpenAPI
- [ ] **Chaos Engineering**: Pruebas de resiliencia
- [ ] **Visual Testing**: Comparación de interfaces
- [ ] **Database Testing**: Pruebas específicas de BD
- [ ] **Mobile Testing**: Pruebas de APIs móviles

---

**🚀 Portal completo de pruebas para IA-Ops Dev Core - Listo para uso en desarrollo, staging y producción**
