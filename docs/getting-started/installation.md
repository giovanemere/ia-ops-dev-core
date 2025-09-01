# Instalación

Esta guía te ayudará a instalar y configurar IA-Ops Dev Core Services en tu entorno.

## 📋 Requisitos Previos

### Software Requerido
- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Git** >= 2.30
- **Python** >= 3.11 (opcional, para desarrollo)

### Puertos Requeridos
Asegúrate de que estos puertos estén disponibles:

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Repository Manager | 8860 | API principal |
| Task Manager | 8861 | Gestión tareas |
| Log Manager | 8862 | Visualización logs |
| DataSync Manager | 8863 | Sincronización |
| GitHub Runner | 8864 | Gestión runners |
| TechDocs Builder | 8865 | Constructor docs |
| Swagger Portal | 8870 | Portal documentación |
| Testing Portal | 18860-18862 | Mock services |
| PostgreSQL | 5434 | Base de datos |
| Redis | 6380 | Cache |
| MinIO | 9898-9899 | Almacenamiento |

## 🚀 Instalación Rápida

### 1. Clonar Repositorio
```bash
git clone https://github.com/giovanemere/ia-ops-dev-core.git
cd ia-ops-dev-core
```

### 2. Configurar Variables de Entorno
```bash
# Copiar configuración de ejemplo
cp docker/.env.example docker/.env

# Editar configuración (opcional)
nano docker/.env
```

### 3. Desplegar con Docker Hub
```bash
# Opción 1: Script automatizado (recomendado)
./start-production.sh

# Opción 2: Docker Compose manual
docker-compose -f docker-compose.production.yml up -d
```

### 4. Verificar Instalación
```bash
# Verificar servicios
./verify-services.sh

# Ver estado de contenedores
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## 🔧 Instalación para Desarrollo

### 1. Configuración Local
```bash
# Instalar dependencias Python (opcional)
pip install -r api/requirements.txt

# Configurar GitHub token (opcional)
export GITHUB_TOKEN="your_github_token_here"
```

### 2. Desplegar Servicios de Desarrollo
```bash
# Usar configuración de desarrollo
docker-compose -f docker/docker-compose.yml up -d
```

### 3. Configurar Base de Datos
```bash
# Las tablas se crean automáticamente al iniciar
# Verificar conexión
docker exec -it iaops-postgres psql -U iaops -d iaops -c "\dt"
```

## 🌐 Verificación de Instalación

### Health Checks
```bash
# Verificar servicios principales
curl http://localhost:8870/health  # Swagger Portal
curl http://localhost:8860/health  # Repository Manager
curl http://localhost:18860/health # Testing Portal
```

### Acceso a Portales
1. **Swagger Portal**: http://localhost:8870
2. **Testing Portal**: http://localhost:18860
3. **MinIO Console**: http://localhost:9899

### Verificar Logs
```bash
# Ver logs de servicios
docker logs iaops-repository-manager
docker logs iaops-swagger-portal
docker logs iaops-testing-portal
```

## 🐳 Configuración Docker Hub

### Variables de Entorno para Producción
```bash
# En docker/.env
POSTGRES_DB=iaops
POSTGRES_USER=iaops
POSTGRES_PASSWORD=secure_password
REDIS_PASSWORD=redis_password
MINIO_ROOT_USER=minio
MINIO_ROOT_PASSWORD=minio_password
```

### Imágenes Docker Hub
Las siguientes imágenes se descargarán automáticamente:

```bash
edissonz8809/ia-ops-repository-manager:2.0.0
edissonz8809/ia-ops-task-manager:2.0.0
edissonz8809/ia-ops-log-manager:2.0.0
edissonz8809/ia-ops-datasync-manager:2.0.0
edissonz8809/ia-ops-github-runner:2.0.0
edissonz8809/ia-ops-techdocs-builder:2.0.0
edissonz8809/ia-ops-swagger-portal:2.0.0
edissonz8809/ia-ops-testing-portal:2.0.0
```

## 🔍 Solución de Problemas

### Problemas Comunes

#### Puerto en Uso
```bash
# Verificar puertos ocupados
netstat -tulpn | grep :8870

# Detener servicios conflictivos
docker-compose down
```

#### Permisos de Docker
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

#### Servicios No Responden
```bash
# Reiniciar servicios específicos
docker restart iaops-repository-manager
docker restart iaops-swagger-portal

# Ver logs detallados
docker logs -f iaops-repository-manager
```

### Verificación de Conectividad

#### Base de Datos
```bash
# Conectar a PostgreSQL
docker exec -it iaops-postgres psql -U iaops -d iaops

# Verificar tablas
\dt
```

#### Redis
```bash
# Conectar a Redis
docker exec -it iaops-redis redis-cli

# Verificar conexión
ping
```

#### MinIO
```bash
# Verificar buckets
docker exec -it iaops-minio mc ls local/
```

## 📚 Próximos Pasos

Una vez completada la instalación:

1. [**Configuración**](configuration.md) - Personalizar servicios
2. [**Primer Uso**](first-use.md) - Crear tu primer proyecto
3. [**APIs**](../apis/repository-manager.md) - Explorar endpoints disponibles
4. [**Testing**](../testing/testing-portal.md) - Usar el portal de pruebas

## 🆘 Soporte

Si encuentras problemas durante la instalación:

1. Revisa los [logs de servicios](#verificar-logs)
2. Consulta la [solución de problemas](#solución-de-problemas)
3. Crea un [issue en GitHub](https://github.com/giovanemere/ia-ops-dev-core/issues)
