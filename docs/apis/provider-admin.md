# Provider Administration API

La API de Administración de Providers permite gestionar múltiples proveedores de servicios en la nube y externos de forma centralizada.

## 🌐 Información General

- **Puerto**: 8866
- **Base URL**: `http://localhost:8866/api/v1`
- **Documentación Swagger**: http://localhost:8866/docs/
- **Health Check**: `GET /api/v1/health/`

## 🔧 Providers Soportados

### GitHub
- Gestión de repositorios
- Integración con organizaciones
- Webhooks y tokens

### Azure
- Resource Groups
- Storage Accounts
- Service Principals

### AWS
- S3 Buckets
- IAM Roles
- EC2 Instances

### GCP
- Storage Buckets
- Service Accounts
- Projects

### OpenAI
- Modelos disponibles
- Organizaciones
- Rate limits

## 📊 Endpoints Principales

### Gestión de Providers

#### Listar Providers
```http
GET /api/v1/providers/
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "GitHub Principal",
      "type": "github",
      "description": "Integración principal con GitHub",
      "is_active": true,
      "config": {
        "username": "mi-usuario",
        "organization": "mi-org"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "message": "Found 1 providers"
}
```

#### Crear Provider
```http
POST /api/v1/providers/
Content-Type: application/json

{
  "name": "GitHub Corporativo",
  "type": "github",
  "description": "Integración con GitHub Enterprise",
  "is_active": true,
  "config": {
    "token": "ghp_xxxxxxxxxxxxxxxxxxxx",
    "username": "empresa",
    "organization": "mi-empresa"
  }
}
```

#### Obtener Provider
```http
GET /api/v1/providers/{id}
```

#### Actualizar Provider
```http
PUT /api/v1/providers/{id}
Content-Type: application/json

{
  "name": "GitHub Actualizado",
  "description": "Descripción actualizada",
  "is_active": false
}
```

#### Eliminar Provider
```http
DELETE /api/v1/providers/{id}
```

### Configuración y Testing

#### Obtener Requisitos de Configuración
```http
GET /api/v1/config/requirements/{provider_type}
```

**Ejemplo para GitHub:**
```json
{
  "success": true,
  "data": {
    "provider_type": "github",
    "requirements": {
      "token": {
        "type": "string",
        "required": true,
        "description": "GitHub Personal Access Token"
      },
      "username": {
        "type": "string",
        "required": false,
        "description": "GitHub Username"
      },
      "organization": {
        "type": "string",
        "required": false,
        "description": "GitHub Organization"
      }
    }
  }
}
```

#### Probar Conexión
```http
POST /api/v1/config/test-connection
Content-Type: application/json

{
  "provider_type": "github",
  "config": {
    "token": "ghp_xxxxxxxxxxxxxxxxxxxx"
  }
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "data": {
    "username": "mi-usuario",
    "name": "Mi Nombre",
    "email": "mi@email.com"
  },
  "message": "Connection test completed"
}
```

### Gestión de Credenciales

#### Listar Credenciales
```http
GET /api/v1/providers/{id}/credentials
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "provider_id": 1,
      "credential_type": "token",
      "credential_name": "GitHub Token Principal",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "expires_at": "2024-12-31T23:59:59Z"
    }
  ]
}
```

#### Crear Credencial
```http
POST /api/v1/providers/{id}/credentials
Content-Type: application/json

{
  "credential_type": "token",
  "credential_name": "GitHub Token Backup",
  "credential_value": "ghp_backup_token_here",
  "expires_at": "2024-12-31T23:59:59"
}
```

## 🔒 Configuración por Provider

### GitHub
```json
{
  "name": "GitHub Principal",
  "type": "github",
  "config": {
    "token": "ghp_xxxxxxxxxxxxxxxxxxxx",
    "username": "mi-usuario",
    "organization": "mi-organizacion"
  }
}
```

**Permisos necesarios:**
- `repo` - Acceso a repositorios
- `read:org` - Leer organización
- `read:user` - Leer usuario

### Azure
```json
{
  "name": "Azure Corporativo",
  "type": "azure",
  "config": {
    "subscription_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "client_secret": "secreto-aqui",
    "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  }
}
```

### AWS
```json
{
  "name": "AWS Producción",
  "type": "aws",
  "config": {
    "access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "region": "us-east-1"
  }
}
```

### GCP
```json
{
  "name": "GCP Principal",
  "type": "gcp",
  "config": {
    "project_id": "mi-proyecto-gcp",
    "service_account_key": "{\"type\": \"service_account\", ...}"
  }
}
```

### OpenAI
```json
{
  "name": "OpenAI API",
  "type": "openai",
  "config": {
    "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "organization": "org-xxxxxxxxxxxxxxxxxxxxxxxx"
  }
}
```

## 🛡️ Seguridad

### Encriptación
- Las credenciales se almacenan encriptadas
- Uso de claves de encriptación rotativas
- Acceso controlado por roles

### Variables de Entorno
```bash
DATABASE_URL=postgresql://user:pass@localhost:5434/iaops
ENCRYPTION_KEY=your-encryption-key-here
PROVIDER_ADMIN_SECRET=admin-secret
```

### Auditoría
- Registro de todas las operaciones
- Logs de conexiones exitosas/fallidas
- Tracking de cambios en configuración

## 📈 Monitoreo

### Health Check
```bash
curl http://localhost:8866/api/v1/health/
```

### Métricas Disponibles
- Número de providers activos
- Conexiones exitosas/fallidas
- Tiempo de respuesta por provider
- Uso de credenciales

## 🔄 Integración

### Con Repository Manager
```python
# El Repository Manager usa providers configurados
import requests

# Listar repositorios usando provider configurado
response = requests.get(
    "http://localhost:8860/api/v1/github/repositories",
    params={"provider_id": 1}
)
```

### Con Frontend
```javascript
// Obtener providers disponibles
const providers = await fetch('/api/v1/providers/')
  .then(res => res.json());

// Probar conexión
const testResult = await fetch('/api/v1/config/test-connection', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    provider_type: 'github',
    config: {token: 'ghp_...'}
  })
});
```

## 🚀 Ejemplos de Uso

### Configurar GitHub Provider Completo
```python
import requests

base_url = "http://localhost:8866/api/v1"

# 1. Obtener requisitos
requirements = requests.get(f"{base_url}/config/requirements/github")
print(requirements.json())

# 2. Probar conexión
test_data = {
    "provider_type": "github",
    "config": {
        "token": "ghp_xxxxxxxxxxxxxxxxxxxx"
    }
}
test_result = requests.post(f"{base_url}/config/test-connection", json=test_data)
print(test_result.json())

# 3. Crear provider
provider_data = {
    "name": "GitHub Principal",
    "type": "github",
    "description": "Integración principal con GitHub",
    "config": {
        "token": "ghp_xxxxxxxxxxxxxxxxxxxx",
        "username": "mi-usuario"
    }
}
provider = requests.post(f"{base_url}/providers/", json=provider_data)
print(provider.json())
```

### Gestión de Múltiples Providers
```python
# Crear múltiples providers
providers_config = [
    {
        "name": "GitHub Desarrollo",
        "type": "github",
        "config": {"token": "ghp_dev_token"}
    },
    {
        "name": "AWS Producción",
        "type": "aws",
        "config": {
            "access_key_id": "AKIA...",
            "secret_access_key": "...",
            "region": "us-east-1"
        }
    }
]

for config in providers_config:
    response = requests.post(f"{base_url}/providers/", json=config)
    print(f"Created: {response.json()['data']['name']}")
```

## 🔧 Troubleshooting

### Errores Comunes

#### Token Inválido
```json
{
  "success": false,
  "error": "Invalid token or insufficient permissions"
}
```

#### Provider No Encontrado
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Provider not found"
  }
}
```

#### Configuración Incompleta
```json
{
  "success": false,
  "error": {
    "code": "MISSING_FIELDS",
    "message": "name and type are required"
  }
}
```

### Verificación de Estado
```bash
# Verificar servicio
curl http://localhost:8866/api/v1/health/

# Listar providers
curl http://localhost:8866/api/v1/providers/

# Probar conexión específica
curl -X POST http://localhost:8866/api/v1/config/test-connection \
  -H "Content-Type: application/json" \
  -d '{"provider_type": "github", "config": {"token": "..."}}'
```
