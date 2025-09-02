# Service Layer Architecture

## Overview

El **Service Layer** de IA-Ops Dev Core actúa como una capa de abstracción unificada que centraliza toda la lógica de negocio y proporciona una API consistente para el frontend y clientes externos.

## Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[ia-ops-docs Frontend :8080]
        EXT[External Clients]
    end
    
    subgraph "Service Layer"
        SL[IA-Ops Service Layer :8800]
        subgraph "Core Services"
            PM[Provider Management]
            RM[Repository Management] 
            TM[Task Management]
            TO[Task Orchestration]
        end
    end
    
    subgraph "Provider Integrations"
        GH[GitHub API]
        AZ[Azure Services]
        AWS[AWS Services]
        GCP[GCP Services]
        AI[OpenAI API]
    end
    
    subgraph "Infrastructure Layer"
        PG[(PostgreSQL :5432)]
        RD[(Redis :6379)]
        MN[(MinIO :9898)]
    end
    
    FE --> SL
    EXT --> SL
    SL --> PM
    SL --> RM
    SL --> TM
    SL --> TO
    PM --> GH
    PM --> AZ
    PM --> AWS
    PM --> GCP
    PM --> AI
    SL --> PG
    SL --> RD
    SL --> MN
```

## Key Components

### 1. **Service Layer Core (Port 8800)**
- **Single Entry Point**: Todas las requests pasan por el Service Layer
- **Unified API**: Endpoints consistentes con formato estándar
- **Legacy Compatibility**: Mantiene compatibilidad con URLs existentes
- **Auto Documentation**: Swagger UI integrado en `/docs`

### 2. **Core Services**

#### Provider Management
- Gestión CRUD de providers (GitHub, Azure, AWS, GCP, OpenAI)
- Test de conexión automático
- Credenciales encriptadas
- Configuración dinámica

#### Repository Management
- Integración con GitHub API
- Clonado automático de repositorios
- Construcción de documentación MkDocs
- Almacenamiento en MinIO

#### Task Management
- Gestión de tareas asíncronas
- Cola de trabajos con Redis
- Monitoreo de estado
- Logs centralizados

#### Task Orchestration
- Coordinación de tareas complejas
- Workflows multi-step
- Manejo de dependencias
- Rollback automático

### 3. **Provider Integrations**
- **GitHub**: Repositorios, organizaciones, webhooks
- **Azure**: Resource Groups, Storage, Service Principals
- **AWS**: S3, STS, EC2, Lambda
- **GCP**: Storage, Compute, Service Accounts
- **OpenAI**: Modelos, Completions, Embeddings

## Benefits

### For Frontend
- **Simplified Integration**: Un solo endpoint para todas las funcionalidades
- **Consistent Responses**: Formato estándar para todas las respuestas
- **Error Handling**: Gestión centralizada de errores
- **Backward Compatibility**: Migración gradual sin breaking changes

### For Backend
- **Clean Architecture**: Separación clara de responsabilidades
- **Reusability**: Servicios compartidos entre endpoints
- **Maintainability**: Código más limpio y organizado
- **Scalability**: Fácil agregar nuevos servicios

### For Infrastructure
- **Resource Efficiency**: Reutiliza PostgreSQL, Redis y MinIO existentes
- **Consistency**: Configuración centralizada
- **Monitoring**: Health checks y métricas unificadas

## API Endpoints

### Core Endpoints
```
GET  /                           # Service information
GET  /health                     # Health check
GET  /docs                       # Swagger documentation
GET  /api/v1/dashboard          # Dashboard data
```

### Provider Management
```
GET  /api/v1/providers                    # List providers
POST /api/v1/providers                    # Create provider
POST /api/v1/providers/test-connection    # Test connection
```

### Repository Management
```
GET  /api/v1/repositories        # List repositories
POST /api/v1/repositories        # Create repository
POST /api/v1/projects            # Create complete project
```

### Task Management
```
GET  /api/v1/tasks               # List tasks
POST /api/v1/tasks               # Create task
GET  /api/v1/tasks/{id}          # Get task
PUT  /api/v1/tasks/{id}          # Update task
```

### Legacy Compatibility
```
GET  /providers                  # Compatible with existing frontend
POST /providers                  # Compatible with existing frontend
GET  /repository/repositories    # Compatible with existing frontend
POST /config/test-connection     # Compatible with existing frontend
```

## Response Format

All responses follow the standard `ServiceResponse` format:

```json
{
  "success": true,
  "data": {
    // Endpoint-specific data
  },
  "message": "Descriptive message",
  "error": null,
  "timestamp": "2025-09-02T02:44:07.269720"
}
```

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379

# MinIO
MINIO_ENDPOINT=localhost:9898
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Providers (optional)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### Database Configuration
The Service Layer uses centralized configuration stored in PostgreSQL:

```sql
-- System configuration
SELECT * FROM system_config WHERE config_type = 'service_layer';

-- Provider configuration
SELECT * FROM providers WHERE active = true;
```

## Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  service-layer:
    build:
      context: .
      dockerfile: Dockerfile.service-layer
    ports:
      - "8800:8800"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
      - minio
```

### Health Checks
```bash
# Service Layer health
curl http://localhost:8800/health

# Individual service health
curl http://localhost:8800/api/v1/providers/health
curl http://localhost:8800/api/v1/repositories/health
curl http://localhost:8800/api/v1/tasks/health
```

## Monitoring

### Metrics
- Request count and latency
- Error rates by endpoint
- Provider connection status
- Task queue length
- Database connection pool

### Logging
- Structured JSON logs
- Request/response tracing
- Error stack traces
- Performance metrics

### Alerts
- Service health degradation
- Provider connection failures
- High error rates
- Resource exhaustion

## Next Steps

1. **Frontend Integration**: Update frontend to use Service Layer endpoints
2. **Provider Expansion**: Add more cloud providers and services
3. **Advanced Orchestration**: Implement complex workflow management
4. **Performance Optimization**: Add caching and connection pooling
5. **Security Enhancement**: Implement authentication and authorization
