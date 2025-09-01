# Configuración de Providers

Esta guía explica cómo configurar y gestionar los diferentes providers externos en IA-Ops Dev Core Services.

## 🔧 Providers Soportados

### 1. **GitHub Provider**
Integración con GitHub para gestión de repositorios.

#### Datos Requeridos:
```json
{
  "token": "ghp_xxxxxxxxxxxxxxxxxxxx",
  "username": "tu-usuario",
  "organization": "tu-organizacion"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `token` | string | ✅ | GitHub Personal Access Token |
| `username` | string | ❌ | Usuario de GitHub |
| `organization` | string | ❌ | Organización de GitHub |

#### Permisos Necesarios:
- `repo` - Acceso completo a repositorios
- `read:org` - Leer información de organización
- `read:user` - Leer información de usuario

### 2. **Azure Provider**
Integración con Microsoft Azure.

#### Datos Requeridos:
```json
{
  "subscription_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "client_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
  "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `subscription_id` | string | ✅ | ID de suscripción de Azure |
| `client_id` | string | ✅ | ID de aplicación (Service Principal) |
| `client_secret` | string | ✅ | Secreto de aplicación |
| `tenant_id` | string | ✅ | ID del tenant de Azure AD |

#### Configuración en Azure:
1. Crear Service Principal en Azure AD
2. Asignar permisos necesarios
3. Generar secreto de aplicación

### 3. **AWS Provider**
Integración con Amazon Web Services.

#### Datos Requeridos:
```json
{
  "access_key_id": "AKIAIOSFODNN7EXAMPLE",
  "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "region": "us-east-1"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `access_key_id` | string | ✅ | AWS Access Key ID |
| `secret_access_key` | string | ✅ | AWS Secret Access Key |
| `region` | string | ✅ | Región de AWS |

#### Permisos IAM Recomendados:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

### 4. **GCP Provider**
Integración con Google Cloud Platform.

#### Datos Requeridos:
```json
{
  "project_id": "mi-proyecto-gcp",
  "service_account_key": "{\"type\": \"service_account\", \"project_id\": \"...\", ...}"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `project_id` | string | ✅ | ID del proyecto de GCP |
| `service_account_key` | json | ✅ | Clave de Service Account (JSON) |

#### Configuración en GCP:
1. Crear Service Account
2. Generar clave JSON
3. Asignar roles necesarios:
   - `Storage Admin`
   - `Viewer`

### 5. **OpenAI Provider**
Integración con OpenAI API.

#### Datos Requeridos:
```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "organization": "org-xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `api_key` | string | ✅ | Clave API de OpenAI |
| `organization` | string | ❌ | ID de organización |

## 🛠️ Gestión via API

### Endpoints Disponibles

#### **Listar Providers**
```bash
GET /api/v1/providers/
```

#### **Crear Provider**
```bash
POST /api/v1/providers/
Content-Type: application/json

{
  "name": "GitHub Principal",
  "type": "github",
  "description": "Integración principal con GitHub",
  "is_active": true,
  "config": {
    "token": "ghp_xxxxxxxxxxxxxxxxxxxx",
    "username": "mi-usuario"
  }
}
```

#### **Obtener Requisitos de Configuración**
```bash
GET /api/v1/config/requirements/github
```

#### **Probar Conexión**
```bash
POST /api/v1/config/test-connection
Content-Type: application/json

{
  "provider_type": "github",
  "config": {
    "token": "ghp_xxxxxxxxxxxxxxxxxxxx"
  }
}
```

#### **Gestionar Credenciales**
```bash
# Listar credenciales (sin valores)
GET /api/v1/providers/{id}/credentials

# Crear credencial
POST /api/v1/providers/{id}/credentials
Content-Type: application/json

{
  "credential_type": "token",
  "credential_name": "GitHub Token",
  "credential_value": "ghp_xxxxxxxxxxxxxxxxxxxx",
  "expires_at": "2024-12-31T23:59:59"
}
```

## 🔒 Seguridad

### Encriptación de Credenciales
- Las credenciales se almacenan encriptadas en la base de datos
- Uso de claves de encriptación rotativas
- Acceso controlado por roles

### Variables de Entorno
```bash
# Configuración de seguridad
ENCRYPTION_KEY=your-encryption-key-here
PROVIDER_ADMIN_SECRET=your-admin-secret

# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5434/iaops
```

### Mejores Prácticas
1. **Rotación de Credenciales**: Rotar tokens regularmente
2. **Principio de Menor Privilegio**: Asignar solo permisos necesarios
3. **Monitoreo**: Auditar acceso a credenciales
4. **Backup Seguro**: Respaldar credenciales de forma segura

## 📊 Monitoreo

### Health Checks
Cada provider incluye verificación de conectividad:

```bash
# Verificar estado del servicio
curl http://localhost:8866/api/v1/health/

# Probar conexión específica
curl -X POST http://localhost:8866/api/v1/config/test-connection \
  -H "Content-Type: application/json" \
  -d '{"provider_type": "github", "config": {"token": "..."}}'
```

### Logs y Auditoría
- Registro de todas las operaciones
- Logs de conexiones exitosas/fallidas
- Auditoría de cambios en configuración

## 🚀 Ejemplos de Uso

### Configurar GitHub Provider
```python
import requests

# Crear provider
provider_data = {
    "name": "GitHub Corporativo",
    "type": "github",
    "description": "Integración con GitHub Enterprise",
    "config": {
        "token": "ghp_xxxxxxxxxxxxxxxxxxxx",
        "organization": "mi-empresa"
    }
}

response = requests.post(
    "http://localhost:8866/api/v1/providers/",
    json=provider_data
)

print(response.json())
```

### Probar Conexión AWS
```python
# Probar conexión
test_data = {
    "provider_type": "aws",
    "config": {
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "region": "us-east-1"
    }
}

response = requests.post(
    "http://localhost:8866/api/v1/config/test-connection",
    json=test_data
)

print(response.json())
```

## 🔧 Configuración Avanzada

### Variables de Entorno por Provider

#### GitHub
```bash
GITHUB_DEFAULT_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

#### AWS
```bash
AWS_DEFAULT_REGION=us-east-1
AWS_PROFILE=default
```

#### Azure
```bash
AZURE_SUBSCRIPTION_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Configuración de Proxy
```bash
# Para entornos corporativos
HTTP_PROXY=http://proxy.empresa.com:8080
HTTPS_PROXY=http://proxy.empresa.com:8080
NO_PROXY=localhost,127.0.0.1
```

## 📚 Próximos Pasos

- [**API Reference**](../apis/provider-admin.md) - Documentación completa de endpoints
- [**Security Guide**](../security/providers.md) - Guía de seguridad
- [**Troubleshooting**](../troubleshooting/providers.md) - Solución de problemas
