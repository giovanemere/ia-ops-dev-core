# Autenticación y Autorización

Este documento describe el sistema de autenticación y autorización implementado en IA-Ops Dev Core Services.

## 🔐 Tipos de Autenticación

### 1. **JWT Tokens (Usuarios)**
Para usuarios finales y aplicaciones frontend.

```bash
# Obtener token
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "iaops_admin_2024_secure"
}

# Usar token
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. **API Keys (Servicios)**
Para comunicación entre servicios y aplicaciones.

```bash
# Usar API Key
Authorization: ApiKey iaops_provider_admin_2024_secure
```

### 3. **Acceso Público**
Algunos portales no requieren autenticación.

## 🌐 Configuración por Portal

### **Swagger Portal** (Puerto 8870)
- **Autenticación**: No requerida (público)
- **Propósito**: Documentación de APIs
- **Acceso**: http://localhost:8870

```bash
# Acceso directo sin autenticación
curl http://localhost:8870/
```

### **Provider Admin** (Puerto 8866)
- **Autenticación**: Requerida
- **API Key**: `iaops_provider_admin_2024_secure`
- **Permisos**: admin, provider_management

```bash
# Acceso con API Key
curl -H "Authorization: ApiKey iaops_provider_admin_2024_secure" \
     http://localhost:8866/api/v1/providers/
```

### **Testing Portal** (Puerto 18860-18862)
- **Autenticación**: No requerida (desarrollo)
- **API Key**: `iaops_testing_portal_2024_dev` (opcional)
- **Propósito**: Mock services para desarrollo

```bash
# Acceso directo para desarrollo
curl http://localhost:18860/health
```

### **Repository Manager** (Puerto 8860)
- **Autenticación**: Requerida
- **API Key**: `iaops_repo_manager_2024_secure`
- **Permisos**: user, repository_management

```bash
# Acceso con API Key
curl -H "Authorization: ApiKey iaops_repo_manager_2024_secure" \
     http://localhost:8860/api/v1/repositories/
```

## 🔑 Tokens y Credenciales

### **Variables de Entorno**
```bash
# JWT Configuration
JWT_SECRET_KEY=ia-ops-dev-core-jwt-secret-2024-secure
JWT_EXPIRY_HOURS=24

# API Keys
PROVIDER_ADMIN_API_KEY=iaops_provider_admin_2024_secure
REPOSITORY_MANAGER_API_KEY=iaops_repo_manager_2024_secure
TESTING_PORTAL_API_KEY=iaops_testing_portal_2024_dev

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=iaops_admin_2024_secure
```

### **Configuración Docker**
```yaml
# En docker-compose.production.yml
environment:
  - JWT_SECRET_KEY=${JWT_SECRET_KEY}
  - PROVIDER_ADMIN_API_KEY=${PROVIDER_ADMIN_API_KEY}
  - ADMIN_USERNAME=${ADMIN_USERNAME}
  - ADMIN_PASSWORD=${ADMIN_PASSWORD}
```

## 🛡️ Niveles de Seguridad

### **Nivel 1: Público**
- Swagger Portal
- Testing Portal (desarrollo)
- Health checks

### **Nivel 2: API Key**
- Provider Administration
- Repository Manager
- Task Manager

### **Nivel 3: JWT + Permisos**
- Operaciones administrativas
- Gestión de usuarios
- Configuración del sistema

## 🔄 Flujo de Autenticación

### **Para Usuarios (JWT)**
```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant A as Auth Service
    participant S as Service

    U->>F: Login (username/password)
    F->>A: POST /auth/login
    A-->>F: JWT Token
    F->>S: Request + Bearer Token
    S->>A: Verify Token
    A-->>S: Token Valid
    S-->>F: Response
    F-->>U: Data
```

### **Para Servicios (API Key)**
```mermaid
sequenceDiagram
    participant S1 as Service A
    participant S2 as Service B
    participant A as Auth Service

    S1->>S2: Request + API Key
    S2->>A: Validate API Key
    A-->>S2: Key Valid
    S2-->>S1: Response
```

## 📊 Implementación

### **Middleware de Autenticación**
```python
from auth_service import require_auth, AuthService

@app.route('/api/v1/providers/')
@require_auth
def list_providers():
    # request.user contiene datos del usuario autenticado
    user_role = request.user.get('role')
    if user_role not in ['admin', 'service']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Lógica del endpoint
    return jsonify({'providers': []})
```

### **Configuración por Servicio**
```python
# En cada servicio
from auth_service import PORTAL_CONFIGS, get_portal_config

service_config = get_portal_config('provider-admin')
if service_config.get('auth_required'):
    # Aplicar middleware de autenticación
    app.before_request(check_authentication)
```

## 🔧 Configuración de Desarrollo

### **Variables Locales**
```bash
# Copiar configuración de autenticación
cp .env.auth.example .env.auth

# Cargar variables
source .env.auth

# O usar en docker-compose
docker-compose --env-file .env.auth up
```

### **Tokens de Desarrollo**
```bash
# API Keys para desarrollo (menos seguros)
PROVIDER_ADMIN_API_KEY=dev_provider_admin
REPOSITORY_MANAGER_API_KEY=dev_repo_manager
TESTING_PORTAL_API_KEY=dev_testing

# JWT Secret para desarrollo
JWT_SECRET_KEY=dev_jwt_secret_not_for_production
```

## 🚀 Producción

### **Tokens Seguros**
```bash
# Generar tokens seguros para producción
JWT_SECRET_KEY=$(openssl rand -hex 32)
PROVIDER_ADMIN_API_KEY=iaops_$(openssl rand -hex 16)
ADMIN_PASSWORD=$(openssl rand -base64 32)
```

### **Rotación de Tokens**
```bash
# Script de rotación (ejecutar periódicamente)
./scripts/rotate-tokens.sh

# Actualizar servicios con nuevos tokens
docker-compose restart
```

## 📈 Monitoreo

### **Logs de Autenticación**
```bash
# Ver intentos de autenticación
docker logs iaops-provider-admin | grep "auth"

# Monitorear tokens expirados
docker logs iaops-repository-manager | grep "expired"
```

### **Métricas de Seguridad**
- Intentos de login fallidos
- Tokens expirados
- Uso de API keys
- Accesos no autorizados

## 🔍 Troubleshooting

### **Token Expirado**
```json
{
  "error": "Token expired",
  "code": 401
}
```
**Solución**: Renovar token o usar refresh token.

### **API Key Inválida**
```json
{
  "error": "Invalid API key format",
  "code": 401
}
```
**Solución**: Verificar formato `iaops_` y configuración.

### **Permisos Insuficientes**
```json
{
  "error": "Insufficient permissions",
  "code": 403
}
```
**Solución**: Verificar rol y permisos del usuario.

## 🔗 Integración con Frontend

### **React/Vue.js**
```javascript
// Configurar interceptor para API calls
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

// O para servicios
axios.defaults.headers.common['Authorization'] = `ApiKey ${apiKey}`;
```

### **ia-ops-docs Frontend**
```javascript
// En el frontend principal
const API_BASE = 'http://localhost:8860';
const API_KEY = process.env.REACT_APP_REPO_MANAGER_API_KEY;

fetch(`${API_BASE}/api/v1/repositories/`, {
  headers: {
    'Authorization': `ApiKey ${API_KEY}`,
    'Content-Type': 'application/json'
  }
});
```
