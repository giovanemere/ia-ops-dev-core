from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import logging
import requests
import hashlib
from datetime import datetime, timedelta
import redis

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

# Configuración de Redis
REDIS_CONFIG = {
    "host": "iaops-redis",
    "port": 6379,
    "password": "redis",
    "db": 0,
    "decode_responses": True
}

# Cache TTL
CACHE_TTL = 300

def get_redis_connection():
    """Obtener conexión a Redis"""
    try:
        return redis.Redis(**REDIS_CONFIG)
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")
        return None

def get_cache_key(config_key: str):
    """Generar key de cache"""
    return f"config:{config_key}"

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
        "service": "docs-backend-simple",
        "version": "2.0.0"
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

@app.get("/api/providers/{provider}")
async def get_provider_config(provider: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtener configuración de provider desde Redis"""
    verify_bearer_token(credentials)
    
    try:
        redis_client = get_redis_connection()
        if not redis_client:
            return {"success": False, "error": "Redis not available"}
        
        cache_key = get_cache_key(provider)
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
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
    """Guardar configuración de provider en Redis"""
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
        
        # Guardar en Redis
        redis_client = get_redis_connection()
        if redis_client:
            cache_key = get_cache_key(provider)
            result_data = {
                "success": True,
                "config": config_value,
                "type": config_type
            }
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(result_data))
            
            return {"success": True, "message": "Configuration saved"}
        else:
            return {"success": False, "error": "Redis not available"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/github/test")
async def test_github_connection(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Probar conexión con GitHub"""
    verify_bearer_token(credentials)
    
    try:
        # Obtener config de GitHub desde Redis
        redis_client = get_redis_connection()
        if not redis_client:
            return {"success": False, "error": "Redis not available"}
        
        cache_key = get_cache_key("github")
        cached_data = redis_client.get(cache_key)
        
        if not cached_data:
            return {"success": False, "error": "GitHub no configurado"}
        
        config_data = json.loads(cached_data)
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
        # Obtener config de GitHub desde Redis
        redis_client = get_redis_connection()
        if not redis_client:
            return {"success": False, "error": "Redis not available"}
        
        cache_key = get_cache_key("github")
        cached_data = redis_client.get(cache_key)
        
        if not cached_data:
            return {"success": False, "error": "Configura GitHub en Settings > Providers > GitHub primero"}
        
        config_data = json.loads(cached_data)
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

@app.get("/api/cache/test")
async def test_redis_cache():
    """Probar Redis cache"""
    try:
        redis_client = get_redis_connection()
        if not redis_client:
            return {"success": False, "error": "No se pudo conectar a Redis"}
        
        # Test básico
        redis_client.ping()
        
        # Test de escritura/lectura
        test_key = "test:connection"
        test_data = {"timestamp": datetime.now().isoformat(), "test": True}
        
        redis_client.setex(test_key, 60, json.dumps(test_data))
        retrieved_data = redis_client.get(test_key)
        
        if retrieved_data:
            parsed_data = json.loads(retrieved_data)
            return {
                "success": True,
                "message": "Redis cache funcionando correctamente",
                "test_data": parsed_data,
                "redis_info": {
                    "host": REDIS_CONFIG["host"],
                    "port": REDIS_CONFIG["port"],
                    "connected": True
                }
            }
        else:
            return {"success": False, "error": "No se pudo leer datos de Redis"}
            
    except Exception as e:
        return {"success": False, "error": f"Error Redis: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8846)
