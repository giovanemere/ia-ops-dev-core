# 🛠️ IA-Ops Dev Core Services

Servicios centrales de desarrollo para el ecosistema IA-Ops: gestión de repositorios, tareas y logs.

## 🚀 Servicios Incluidos

- **📁 Repository Manager** - Gestión de repositorios (puerto 8850)
- **📋 Task Manager** - Gestión de tareas y builds (puerto 8851)
- **📊 Log Manager** - Visualización de logs (puerto 8852)

## 📁 Estructura del Proyecto

```
ia-ops-dev-core/
├── api/                       # APIs de servicios
│   ├── repository_manager.py  # Gestión de repositorios
│   ├── task_manager.py        # Gestión de tareas
│   └── log_manager.py         # Gestión de logs
├── services/                  # Servicios independientes
│   ├── repositories/          # Servicio de repositorios
│   ├── tasks/                 # Servicio de tareas
│   └── logs/                  # Servicio de logs
├── docker/                    # Configuraciones Docker
│   ├── docker-compose.yml     # Servicios principales
│   └── .env.example          # Variables de entorno
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

# 3. Iniciar servicios
./scripts/start.sh

# 4. Verificar servicios
./scripts/status.sh
```

## 🌐 URLs de Acceso

- **Repository Manager**: http://localhost:8850
- **Task Manager**: http://localhost:8851
- **Log Manager**: http://localhost:8852

## 🔗 Integración con IA-Ops

Este repositorio se integra con:
- **ia-ops-docs** - Proyecto principal
- **ia-ops-minio** - Almacenamiento
- **ia-ops-backstage** - Portal Backstage

## 📊 Características

### Repository Manager (8850)
- Gestión CRUD de repositorios
- Sincronización con GitHub
- Integración con MinIO
- API REST completa

### Task Manager (8851)
- Cola de tareas de build
- Monitoreo de progreso
- Logs detallados
- Retry automático

### Log Manager (8852)
- Visualización de logs en tiempo real
- Filtros avanzados
- Exportación de logs
- Dashboard de métricas

## 🚀 Comandos Rápidos

```bash
# Iniciar todos los servicios
./scripts/start.sh

# Detener servicios
./scripts/stop.sh

# Ver estado
./scripts/status.sh

# Ver logs
./scripts/logs.sh
```

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

**🚀 Parte del ecosistema IA-Ops**
