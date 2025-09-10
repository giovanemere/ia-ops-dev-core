from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import requests
import hashlib
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la aplicación
app = FastAPI(title="IA-Ops Docs Backend", version="2.0.0")
security = HTTPBearer()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento en memoria (temporal)
CONFIG_STORE = {}

# Token válido para pruebas
VALID_API_KEY = "iaops-api-key-2024"
VALID_TOKEN = None

def verify_bearer_token(credentials: HTTPAuthorizationCredentials):
    """Verificar token Bearer"""
    global VALID_TOKEN
    if not VALID_TOKEN:
        raise HTTPException(status_code=401, detail="No authenticated")
    
    if credentials.credentials != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "docs-backend-minimal",
        "version": "2.0.0",
        "storage": "memory"
    }

@app.post("/api/auth/login")
async def login(request: Request):
    """Login con API key"""
    global VALID_TOKEN
    try:
        data = await request.json()
        api_key = data.get("api_key")
        
        if api_key == VALID_API_KEY:
            # Generar token simple
            VALID_TOKEN = hashlib.sha256(f"{api_key}{datetime.now()}".encode()).hexdigest()
            
            return {
                "success": True,
                "access_token": VALID_TOKEN,
                "token_type": "bearer",
                "expires_in": 3600
            }
        else:
            return {"success": False, "error": "Invalid API key"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/auth/verify")
async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token válido"""
    try:
        verify_bearer_token(credentials)
        return {
            "success": True,
            "user": "iaops-portal",
            "authenticated": True
        }
    except HTTPException:
        return {
            "success": False,
            "authenticated": False
        }

@app.get("/api/providers/{provider}")
async def get_provider_config(provider: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtener configuración de provider desde memoria"""
    verify_bearer_token(credentials)
    
    try:
        if provider in CONFIG_STORE:
            return CONFIG_STORE[provider]
        else:
            # Configuración por defecto
            default_config = {
                "success": True,
                "config": {"configured": False},
                "type": "provider"
            }
            return default_config
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/providers/{provider}")
async def save_provider_config(provider: str, request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Guardar configuración de provider en memoria"""
    verify_bearer_token(credentials)
    
    try:
        data = await request.json()
        
        # Determinar tipo
        config_type = "provider"
        if provider in ["openai", "google_ai", "bedrock", "anthropic", "azure_ai"]:
            config_type = "api_provider"
        elif provider in ["postgres", "redis", "minio"]:
            config_type = "system"
        
        # Preparar configuración
        config_value = {"configured": True}
        config_value.update(data)
        
        # Guardar en memoria
        CONFIG_STORE[provider] = {
            "success": True,
            "config": config_value,
            "type": config_type
        }
        
        return {"success": True, "message": "Configuration saved"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/github/test")
async def test_github_connection(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Probar conexión con GitHub"""
    verify_bearer_token(credentials)
    
    try:
        # Obtener config de GitHub desde memoria
        if "github" not in CONFIG_STORE:
            return {"success": False, "error": "GitHub no configurado"}
        
        config_data = CONFIG_STORE["github"]
        github_config = config_data.get("config", {})
        
        if not github_config.get("token"):
            return {"success": False, "error": "GitHub token no configurado"}
        
        # Probar conexión con GitHub API
        headers = {
            'Authorization': f"token {github_config['token']}",
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                "success": True,
                "user": {"login": user_data["login"], "name": user_data.get("name", "")},
                "message": "Conexión exitosa"
            }
        else:
            return {"success": False, "error": f"Error GitHub API: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/github/repositories")
async def get_github_repositories(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtener repositorios de GitHub"""
    verify_bearer_token(credentials)
    
    try:
        # Obtener config de GitHub desde memoria
        if "github" not in CONFIG_STORE:
            return {"success": False, "error": "Configura GitHub en Settings > Providers > GitHub primero"}
        
        config_data = CONFIG_STORE["github"]
        github_config = config_data.get("config", {})
        
        if not github_config.get("token"):
            return {"success": False, "error": "GitHub token no configurado"}
        
        # Obtener repositorios
        headers = {
            'Authorization': f"token {github_config['token']}",
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = 'https://api.github.com/user/repos?per_page=100&sort=updated'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            repositories = response.json()
            return {
                "success": True,
                "repositories": repositories,
                "count": len(repositories)
            }
        else:
            return {"success": False, "error": f"Error GitHub API: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/config/status")
async def get_config_status():
    """Ver configuraciones en memoria"""
    return {
        "success": True,
        "stored_configs": list(CONFIG_STORE.keys()),
        "total_configs": len(CONFIG_STORE),
        "storage_type": "memory"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8846)
