# 🚀 IA-Ops Dev Core - Unified Service

**Servicio unificado simplificado**: Todos los servicios de IA-Ops en un solo contenedor FastAPI, reutilizando la infraestructura existente (PostgreSQL, Redis, MinIO).

## 🎯 Ventajas de la Arquitectura Unificada

### ✅ **Simplificación**
- **Un solo contenedor** en lugar de 6+ servicios separados
- **Configuración única** y centralizada
- **Gestión simplificada** con un script de administración
- **Menor consumo de recursos**

### 🔄 **Reutilización de Infraestructura**
- **PostgreSQL existente** (puerto 5434)
- **Redis existente** (puerto 6380) 
- **MinIO existente** (puertos 9898/9899)
- **Sin duplicación** de servicios de base de datos

### ⚡ **Rendimiento Mejorado**
- **Comunicación interna** sin overhead de red
- **Inicio más rápido** (un solo contenedor)
- **Menos latencia** entre componentes

## 🏗️ Arquitectura Simplificada

```mermaid
graph TB
    subgraph "Unified Service :8800"
        US[IA-Ops Unified Service<br/>FastAPI Application]
        RM[Repository Manager]
        TM[Task Manager]
        LM[Log Manager]
        DS[DataSync Manager]
        PA[Provider Admin]
        
        US --> RM
        US --> TM
        US --> LM
        US --> DS
        US --> PA
    end
    
    subgraph "Existing Infrastructure"
        PG[(PostgreSQL :5434)]
        RD[(Redis :6380)]
        MN[(MinIO :9898)]
    end
    
    US --> PG
    US --> RD
    US --> MN
```

## 🚀 Inicio Rápido

### 1. **Iniciar Servicio Unificado**
```bash
# Usar script de gestión
./manage-simple.sh start

# O manualmente
docker-compose -f docker-compose.unified.yml up -d
```

### 2. **Verificar Estado**
```bash
./manage-simple.sh status
```

### 3. **Probar Endpoints**
```bash
./manage-simple.sh test
```

## 🌐 URLs de Acceso

### **Servicio Principal**
- **Servicio Unificado**: http://localhost:8800
- **Documentación API**: http://localhost:8800/docs
- **Health Check**: http://localhost:8800/health

### **APIs por Módulo**
| Módulo | Endpoint Base | Funcionalidad |
|--------|---------------|---------------|
| **Repository Manager** | `/repository` | Gestión de repositorios GitHub |
| **Task Manager** | `/tasks` | Gestión de tareas y procesos |
| **Log Manager** | `/logs` | Visualización y gestión de logs |
| **DataSync Manager** | `/datasync` | Sincronización de datos |
| **Provider Admin** | `/providers` | Administración de providers |

### **Infraestructura Reutilizada**
| Servicio | Puerto | Acceso |
|----------|--------|--------|
| **PostgreSQL** | 5434 | Base de datos principal |
| **Redis** | 6380 | Cache y colas |
| **MinIO** | 9898 | Almacenamiento de archivos |
| **MinIO Console** | 9899 | Interfaz web MinIO |

## 🛠️ Gestión del Servicio

### **Script de Administración**
```bash
# Comandos disponibles
./manage-simple.sh {start|stop|restart|rebuild|status|logs|test}

# Ejemplos
./manage-simple.sh start     # Iniciar servicio
./manage-simple.sh stop      # Detener servicio
./manage-simple.sh restart   # Reiniciar servicio
./manage-simple.sh rebuild   # Reconstruir y reiniciar
./manage-simple.sh status    # Ver estado
./manage-simple.sh logs      # Ver logs en tiempo real
./manage-simple.sh test      # Probar todos los endpoints
```

### **Comandos Docker Directos**
```bash
# Iniciar
docker-compose -f docker-compose.unified.yml up -d

# Detener
docker-compose -f docker-compose.unified.yml down

# Ver logs
docker logs iaops-unified -f

# Reconstruir
docker-compose -f docker-compose.unified.yml up -d --build
```

## 📋 Endpoints Disponibles

### **Repository Manager**
```bash
GET  /repository/health           # Health check
GET  /repository/repositories     # Listar repositorios
POST /repository/clone           # Clonar repositorio
```

### **Task Manager**
```bash
GET  /tasks/health               # Health check
GET  /tasks                      # Listar tareas
POST /tasks                      # Crear tarea
```

### **Log Manager**
```bash
GET  /logs/health                # Health check
GET  /logs                       # Obtener logs
POST /logs                       # Agregar log
```

### **DataSync Manager**
```bash
GET  /datasync/health            # Health check
GET  /datasync/status            # Estado de sincronizaciones
POST /datasync/sync              # Iniciar sincronización
```

### **Provider Admin**
```bash
GET  /providers/health           # Health check
GET  /providers                  # Listar providers
POST /providers                  # Crear provider
```

## 🧪 Ejemplos de Uso

### **Clonar Repositorio**
```bash
curl -X POST http://localhost:8800/repository/clone \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/user/repo.git", "branch": "main"}'
```

### **Crear Tarea**
```bash
curl -X POST http://localhost:8800/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "Deploy App", "description": "Deploy to production"}'
```

### **Agregar Log**
```bash
curl -X POST http://localhost:8800/logs \
  -H "Content-Type: application/json" \
  -d '{"level": "INFO", "message": "Application started"}'
```

### **Crear Provider**
```bash
curl -X POST http://localhost:8800/providers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GitHub Main",
    "type": "github",
    "description": "Main GitHub integration",
    "config": {"token": "ghp_xxx", "username": "user"}
  }'
```

## 🔧 Configuración

### **Variables de Entorno**
```bash
DATABASE_URL=postgresql://iaops:iaops123@host.docker.internal:5434/iaops_db
REDIS_URL=redis://host.docker.internal:6380/0
MINIO_ENDPOINT=host.docker.internal:9898
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### **Puertos Utilizados**
- **8800**: Servicio unificado IA-Ops
- **5434**: PostgreSQL (reutilizado)
- **6380**: Redis (reutilizado)
- **9898**: MinIO API (reutilizado)
- **9899**: MinIO Console (reutilizado)

## 📊 Monitoreo

### **Health Checks**
```bash
# Servicio principal
curl http://localhost:8800/health

# Módulos individuales
curl http://localhost:8800/repository/health
curl http://localhost:8800/tasks/health
curl http://localhost:8800/logs/health
curl http://localhost:8800/datasync/health
curl http://localhost:8800/providers/health
```

### **Estado de Contenedores**
```bash
docker ps --filter name=iaops-unified
```

## 🚀 Migración desde Arquitectura Multi-Contenedor

### **Detener Servicios Anteriores**
```bash
# Detener servicios individuales
docker-compose -f docker-compose.yml down

# Mantener infraestructura (PostgreSQL, Redis, MinIO)
# Solo iniciar el servicio unificado
./manage-simple.sh start
```

### **Ventajas de la Migración**
- ✅ **Menos complejidad** de gestión
- ✅ **Menor uso de recursos**
- ✅ **Configuración más simple**
- ✅ **Inicio más rápido**
- ✅ **Misma funcionalidad** en un solo lugar

## 🔗 Integración con Frontend

El servicio unificado mantiene **compatibilidad completa** con el frontend existente:

```javascript
// Mismo patrón de URLs, solo cambia el puerto base
const API_BASE = 'http://localhost:8800';

// Repository API
fetch(`${API_BASE}/repository/repositories`)

// Tasks API  
fetch(`${API_BASE}/tasks`)

// Providers API
fetch(`${API_BASE}/providers`)
```

## 📄 Documentación Adicional

- **[API Documentation](http://localhost:8800/docs)** - Swagger UI automática
- **[README Original](./README.md)** - Documentación de arquitectura multi-contenedor
- **[Frontend Integration](./FRONTEND_INTEGRATION.md)** - Guía de integración frontend

---

**🎯 IA-Ops Dev Core Unified - Simplicidad sin comprometer funcionalidad**
