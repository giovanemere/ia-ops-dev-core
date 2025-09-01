# 🛠️ IA-Ops Dev Core Services

Servicios centrales de desarrollo para el ecosistema IA-Ops: gestión de repositorios, tareas y logs con documentación Swagger completa.

## 🚀 Servicios Incluidos

- **📁 Repository Manager** - Gestión de repositorios (puerto 8860)
- **📋 Task Manager** - Gestión de tareas y builds (puerto 8861)
- **📊 Log Manager** - Visualización de logs (puerto 8862)
- **🔄 DataSync Manager** - Sincronización de datos (puerto 8863)
- **🏃 GitHub Runner Manager** - Gestión de runners (puerto 8864)
- **📚 TechDocs Builder** - Constructor de documentación (puerto 8865)
- **📖 Swagger Portal** - Portal de documentación API (puerto 8870)

## 📁 Estructura del Proyecto

```
ia-ops-dev-core/
├── api/                       # APIs de servicios
│   ├── repository_manager.py  # Gestión de repositorios
│   ├── task_manager.py        # Gestión de tareas
│   ├── log_manager.py         # Gestión de logs
│   ├── swagger_config.py      # Configuración Swagger
│   ├── swagger_portal.py      # Portal de documentación
│   └── *_swagger.py          # Versiones con Swagger
├── services/                  # Servicios independientes
├── docker/                    # Configuraciones Docker
├── tests/                     # Pruebas completas
├── config/                    # Configuraciones
├── data/                      # Datos persistentes
└── logs/                      # Logs del sistema
```

## 🛠️ Instalación Rápida

```bash
# 1. Clonar repositorio
git clone git@github.com:giovanemere/ia-ops-dev-core.git
cd ia-ops-dev-core

# 2. Configurar entorno
cp docker/.env.example docker/.env

# 3. Iniciar servicios con Swagger
./scripts/start-with-swagger.sh

# 4. Verificar servicios
./scripts/status.sh
```

## 🌐 URLs de Acceso

### Portal Principal
- **📖 Swagger Documentation Portal**: http://localhost:8870

### APIs de Servicios
- **Repository Manager**: http://localhost:8860 | [Docs](http://localhost:8860/docs/)
- **Task Manager**: http://localhost:8861 | [Docs](http://localhost:8861/docs/)
- **Log Manager**: http://localhost:8862 | [Docs](http://localhost:8862/docs/)
- **DataSync Manager**: http://localhost:8863 | [Docs](http://localhost:8863/docs/)
- **GitHub Runner Manager**: http://localhost:8864 | [Docs](http://localhost:8864/docs/)
- **TechDocs Builder**: http://localhost:8865 | [Docs](http://localhost:8865/docs/)

## 🔗 Integración con IA-Ops

Este repositorio se integra con:
- **ia-ops-docs** - Proyecto principal
- **ia-ops-minio** - Almacenamiento
- **ia-ops-backstage** - Portal Backstage
- **ia-ops-veritas** - Portal de pruebas unitarias

## 📊 Características

### Repository Manager (8860)
- Gestión CRUD de repositorios
- Sincronización con GitHub
- Integración con MinIO
- API REST completa con Swagger

### Task Manager (8861)
- Cola de tareas de build
- Monitoreo de progreso
- Logs detallados
- Retry automático
- Integración con Redis

### Log Manager (8862)
- Visualización de logs en tiempo real
- Filtros avanzados
- Exportación de logs
- Dashboard de métricas

### DataSync Manager (8863)
- Sincronización de datos entre servicios
- Backup automático
- Integración con MinIO
- API de sincronización

### GitHub Runner Manager (8864)
- Gestión de runners de GitHub Actions
- Monitoreo de estado
- Configuración automática
- Logs de ejecución

### TechDocs Builder (8865)
- Constructor de documentación MkDocs
- Integración con Material theme
- Soporte para Mermaid
- Build automático

### Swagger Portal (8870)
- Portal centralizado de documentación
- Estado en tiempo real de servicios
- Integración con todas las APIs
- Interface visual moderna

## 🧪 Pruebas y Testing

### Portal de Pruebas Unitarias
- **Repositorio**: [ia-ops-veritas](https://github.com/giovanemere/ia-ops-veritas)
- **Funcionalidad**: Pruebas automatizadas de todos los servicios

### Métodos de Prueba Locales
```bash
# Pruebas rápidas
cd tests
python quick_test.py

# Pruebas completas
python service_tests.py

# Pruebas de rendimiento
python performance_tests.py
```

## 🚀 Comandos Rápidos

```bash
# Iniciar todos los servicios con Swagger
./scripts/start-with-swagger.sh

# Iniciar servicios básicos
./scripts/start.sh

# Detener servicios
./scripts/stop.sh

# Ver estado
./scripts/status.sh

# Ver logs
./scripts/logs.sh
```

## 📚 Documentación API

### Swagger/OpenAPI
Todos los servicios incluyen documentación Swagger completa:

- **Modelos de datos** definidos
- **Endpoints** documentados
- **Ejemplos** de request/response
- **Códigos de error** especificados
- **Pruebas interactivas** disponibles

### Acceso a Documentación
1. **Portal Principal**: http://localhost:8870
2. **APIs Individuales**: http://localhost:{puerto}/docs/
3. **Especificaciones JSON**: http://localhost:{puerto}/swagger.json

## 🗄️ Integración de Bases de Datos

### PostgreSQL
- **Puerto**: 5434
- **Base de datos**: iaops
- **Servicios**: Todos los servicios principales

### Redis
- **Puerto**: 6380
- **Uso**: Cache y colas de tareas
- **Servicios**: Task Manager

### MinIO
- **Puerto**: 9898
- **Uso**: Almacenamiento de archivos
- **Servicios**: Repository Manager, DataSync Manager

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

**🚀 Parte del ecosistema IA-Ops - Backend completo con documentación Swagger**
