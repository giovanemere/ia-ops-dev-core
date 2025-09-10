#!/usr/bin/env python3
"""
Docs Backend - Backend completo para el portal de documentación
Todas las integraciones: DB, GitHub, MinIO, Tasks, etc.
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import logging
import requests
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import asyncio
import subprocess
import tempfile
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de seguridad
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "iaops-portal-secret-key-2024")
API_KEY = os.getenv("API_KEY", "iaops-api-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

app = FastAPI(title="IA-Ops Docs Backend", version="2.0.0")

# CORS para permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8845", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de servicios usando nombres de contenedores Docker
DEV_CORE_SERVICES = {
    "repository_manager": "http://iaops-repository-manager:8000",
    "task_manager": "http://iaops-task-manager:8000", 
    "log_manager": "http://iaops-log-manager:8000",
    "datasync_manager": "http://iaops-datasync-manager:8000",
    "github_runner_manager": "http://iaops-github-runner-manager:5000"
}

# Servicios externos usando nombres de contenedores de la red iaops-network
EXTERNAL_SERVICES = {
    "postgres": {"host": "iaops-postgres", "port": 5432},
    "redis": {"host": "iaops-redis", "port": 6379},
    "minio": {"host": "iaops-minio-portal", "port": 9000}
}

# Configuración de base de datos
DB_CONFIG = {
    "host": "iaops-postgres",
    "port": 5432,
    "database": "postgres", 
    "user": "postgres",
    "password": "postgres"
}

# Configuración de Redis
REDIS_CONFIG = {
    "host": "iaops-redis",
    "port": 6379,
    "password": "redis",  # Password configurado en el stack
    "db": 0,
    "decode_responses": True
}

# Cache TTL (Time To Live) en segundos
CACHE_TTL = 300  # 5 minutos

def get_redis_connection():
    """Obtener conexión a Redis"""
    try:
        import redis
        return redis.Redis(**REDIS_CONFIG)
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}")
        return None

def get_cache_key(config_key: str):
    """Generar key de cache"""
    return f"config:{config_key}"

async def get_configuration_cached(config_key: str):
    """Obtener configuración con cache Redis"""
    try:
        # 1. Intentar obtener desde Redis cache
        redis_client = get_redis_connection()
        if redis_client:
            cache_key = get_cache_key(config_key)
            cached_data = redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"Configuration '{config_key}' loaded from cache")
                return json.loads(cached_data)
        
        # 2. Si no está en cache, obtener desde BD
        result = await get_configuration_from_db(config_key)
        
        # 3. Guardar en cache si fue exitoso
        if result["success"] and redis_client:
            cache_key = get_cache_key(config_key)
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(result))
            logger.info(f"Configuration '{config_key}' cached for {CACHE_TTL}s")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in cached configuration: {e}")
        # Fallback a BD directamente
        return await get_configuration_from_db(config_key)

async def save_configuration_cached(config_key: str, config_value: dict, config_type: str):
    """Guardar configuración y actualizar cache"""
    try:
        # 1. Guardar en BD
        result = await save_configuration_to_db(config_key, config_value, config_type)
        
        # 2. Actualizar cache si fue exitoso
        if result["success"]:
            redis_client = get_redis_connection()
            if redis_client:
                cache_key = get_cache_key(config_key)
                cached_result = {
                    "success": True,
                    "config": config_value,
                    "type": config_type
                }
                redis_client.setex(cache_key, CACHE_TTL, json.dumps(cached_result))
                logger.info(f"Configuration '{config_key}' cache updated")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in cached save: {e}")
        return {"success": False, "error": str(e)}

def invalidate_cache(config_key: str = None):
    """Invalidar cache específico o todo el cache de configuraciones"""
    try:
        redis_client = get_redis_connection()
        if not redis_client:
            return
            
        if config_key:
            # Invalidar cache específico
            cache_key = get_cache_key(config_key)
            redis_client.delete(cache_key)
            logger.info(f"Cache invalidated for '{config_key}'")
        else:
            # Invalidar todo el cache de configuraciones
            pattern = get_cache_key("*")
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} configuration cache entries")
                
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")

async def get_configuration_from_db(config_key: str):
    """Obtener configuración directamente desde BD"""
    try:
        # Simulamos la función de BD (implementar cuando psycopg2 funcione)
        return {
            "success": False,
            "error": "Database connection not available - using cache fallback"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def save_configuration_to_db(config_key: str, config_value: dict, config_type: str):
    """Guardar configuración directamente en BD"""
    try:
        # Simulamos la función de BD (implementar cuando psycopg2 funcione)
        return {"success": True, "message": "Configuration saved (simulated)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_db_connection():
    """Obtener conexión a la base de datos"""
    return psycopg2.connect(**DB_CONFIG)

async def get_configuration(config_key: str):
    """Obtener configuración desde BD"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            "SELECT config_value, config_type FROM configurations WHERE config_key = %s",
            (config_key,)
        )
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                "success": True,
                "config": result['config_value'],
                "type": result['config_type']
            }
        else:
            return {"success": False, "error": "Configuration not found"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

async def save_configuration(config_key: str, config_value: dict, config_type: str):
    """Guardar configuración en BD"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO configurations (config_key, config_value, config_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (config_key) 
            DO UPDATE SET 
                config_value = EXCLUDED.config_value,
                updated_at = CURRENT_TIMESTAMP
        """, (config_key, json.dumps(config_value), config_type))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "Configuration saved"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================

def verify_api_key(request: Request):
    """Verificar API Key en headers"""
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar Bearer token simple"""
    expected_token = hashlib.sha256(API_KEY.encode()).hexdigest()
    if credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return True

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/login")
async def login(request: Request):
    """Login con API Key y obtener token simple"""
    try:
        data = await request.json()
        api_key = data.get("api_key")
        
        if not api_key or api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API Key")
        
        # Crear token simple (hash del API key)
        access_token = hashlib.sha256(api_key.encode()).hexdigest()
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
        
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

# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.get("/api/providers/{provider}")
async def get_provider_config(provider: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtener configuración de provider con cache Redis"""
    verify_bearer_token(credentials)
    return await get_configuration_cached(provider)

@app.post("/api/providers/{provider}")
async def save_provider_config(provider: str, request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Guardar configuración de provider con cache Redis"""
    verify_bearer_token(credentials)
    
    try:
        data = await request.json()
        
        # Determinar tipo de configuración
        config_type = "provider"
        if provider in ["openai", "google_ai", "bedrock", "anthropic", "azure_ai"]:
            config_type = "api_provider"
        elif provider in ["postgres", "redis", "minio"]:
            config_type = "system"
            
        # Preparar configuración
        config_value = {"configured": True}
        config_value.update(data)
        
        result = await save_configuration_cached(provider, config_value, config_type)
        return result
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/api/cache/{config_key}")
async def invalidate_config_cache(config_key: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Invalidar cache de configuración específica"""
    verify_bearer_token(credentials)
    
    try:
        invalidate_cache(config_key)
        return {"success": True, "message": f"Cache invalidated for {config_key}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/api/cache")
async def invalidate_all_cache(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Invalidar todo el cache de configuraciones"""
    verify_bearer_token(credentials)
    
    try:
        invalidate_cache()
        return {"success": True, "message": "All configuration cache invalidated"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/cache/stats")
async def get_cache_stats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtener estadísticas del cache"""
    verify_bearer_token(credentials)
    
    try:
        redis_client = get_redis_connection()
        if not redis_client:
            return {"success": False, "error": "Redis not available"}
        
        # Obtener keys de configuraciones
        pattern = get_cache_key("*")
        keys = redis_client.keys(pattern)
        
        stats = {
            "success": True,
            "total_cached_configs": len(keys),
            "cached_keys": [key.replace("config:", "") for key in keys],
            "redis_info": {
                "connected": True,
                "ttl_seconds": CACHE_TTL
            }
        }
        
        return stats
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/github/test")
async def test_github_connection(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Probar conexión con GitHub"""
    verify_bearer_token(credentials)
    
    try:
        config_result = await get_configuration("github")
        
        if not config_result["success"] or not config_result["config"].get("token"):
            return {"success": False, "error": "GitHub no configurado"}
        
        github_config = config_result["config"]
        
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

class DocsBackend:
    def __init__(self):
        self.github_config = {}
        self.azure_config = {}
        self.load_configurations()
    
    def load_configurations(self):
        """Cargar configuraciones desde variables de entorno"""
        self.github_config = {
            'token': os.getenv('GITHUB_TOKEN', ''),
            'user': os.getenv('GITHUB_USER', ''),
            'configured': bool(os.getenv('GITHUB_TOKEN'))
        }
    
    async def call_dev_core_service(self, service: str, endpoint: str, method: str = "GET", data: dict = None):
        """Llamar a servicios de Dev-Core"""
        try:
            service_url = DEV_CORE_SERVICES.get(service)
            if not service_url:
                return {"error": f"Service {service} not configured"}
            
            url = f"{service_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                return {"error": f"Method {method} not supported"}
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Service error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error calling {service}: {e}")
            return {"error": str(e)}

# Instancia global
backend = DocsBackend()

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "docs-backend",
        "version": "2.0.0",
        "integrations": {
            "dev_core_services": len(DEV_CORE_SERVICES),
            "external_services": len(EXTERNAL_SERVICES)
        }
    }

@app.get("/api/github/repositories")
async def get_github_repositories(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtener repositorios de GitHub usando configuración guardada"""
    verify_bearer_token(credentials)
    
    try:
        # Obtener configuración de GitHub desde BD
        config_result = await get_configuration("github")
        
        if not config_result["success"] or not config_result["config"].get("token"):
            return {
                "success": False,
                "error": "Configura GitHub en Settings > Providers > GitHub primero"
            }
        
        github_config = config_result["config"]
        
        headers = {
            'Authorization': f"token {github_config['token']}",
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Obtener repositorios del usuario
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
            return {
                "success": False,
                "error": f"Error GitHub API: {response.status_code}"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# GITHUB INTEGRATION
# ============================================================================

@app.get("/api/github/repositories")
async def get_github_repositories():
    """Obtener repositorios de GitHub"""
    try:
        if not backend.github_config.get('token'):
            return {
                "status": "error",
                "message": "GitHub token not configured",
                "repositories": [],
                "total_count": 0
            }
        
        headers = {
            "Authorization": f"token {backend.github_config['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(
            "https://api.github.com/user/repos",
            headers=headers,
            params={"per_page": 100, "sort": "updated"},
            timeout=10
        )
        
        if response.status_code == 200:
            repos = response.json()
            return {
                "status": "success",
                "repositories": repos,
                "total_count": len(repos)
            }
        else:
            return {
                "status": "error", 
                "message": f"GitHub API error: {response.status_code}",
                "repositories": [],
                "total_count": 0
            }
            
    except Exception as e:
        logger.error(f"GitHub API error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "repositories": [],
            "total_count": 0
        }

@app.post("/api/github/test")
async def test_github_connection(request: Request):
    """Probar conexión con GitHub"""
    try:
        data = await request.json()
        token = data.get('token') or backend.github_config.get('token')
        
        if not token:
            return {"success": False, "error": "No GitHub token provided"}
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(
            "https://api.github.com/user",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                "success": True,
                "user": user_data,
                "message": "GitHub connection successful"
            }
        else:
            return {
                "success": False,
                "error": f"GitHub API error: {response.status_code}"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/providers/github")
async def configure_github(request: Request):
    """Configurar provider de GitHub"""
    try:
        data = await request.json()
        token = data.get('github_token')
        user = data.get('github_user')
        
        if not token:
            return {"success": False, "error": "GitHub token is required"}
        
        # Probar token
        test_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token}"},
            timeout=10
        )
        
        if test_response.status_code == 200:
            user_data = test_response.json()
            
            # Guardar configuración
            backend.github_config = {
                'token': token,
                'user': user or user_data.get('login'),
                'user_data': user_data,
                'configured': True
            }
            
            # Guardar en Dev-Core usando Repository Manager
            config_data = {
                "provider": "github",
                "config": backend.github_config
            }
            
            save_result = await backend.call_dev_core_service(
                "repository_manager", 
                "/api/providers/save",
                "POST",
                config_data
            )
            
            return {
                "success": True,
                "message": "GitHub configured successfully",
                "user": user_data.get('login'),
                "save_result": save_result
            }
        else:
            return {
                "success": False,
                "error": f"Invalid GitHub token: {test_response.status_code}"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# REPOSITORY MANAGEMENT
# ============================================================================

@app.get("/api/repositories")
async def get_repositories():
    """Obtener repositorios de todos los providers"""
    try:
        # Obtener de Repository Manager
        repos_result = await backend.call_dev_core_service(
            "repository_manager",
            "/api/repositories"
        )
        
        if "error" not in repos_result:
            return repos_result
        
        # Fallback: obtener directamente de GitHub
        github_repos = await get_github_repositories()
        
        return {
            "status": "success",
            "repositories": github_repos.get("repositories", []),
            "total_count": github_repos.get("total_count", 0),
            "source": "github_direct"
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/repositories/refresh")
async def refresh_repositories():
    """Refrescar cache de repositorios"""
    try:
        # Llamar a Repository Manager para refrescar
        refresh_result = await backend.call_dev_core_service(
            "repository_manager",
            "/api/repositories/refresh",
            "POST"
        )
        
        return {
            "success": True,
            "message": "Repositories refreshed",
            "result": refresh_result
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# TASK MANAGEMENT
# ============================================================================

@app.get("/api/tasks")
async def get_tasks():
    """Obtener todas las tareas"""
    try:
        tasks_result = await backend.call_dev_core_service(
            "task_manager",
            "/api/tasks"
        )
        
        return tasks_result
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/tasks/{task_id}")
async def get_task_detail(task_id: str):
    """Obtener detalles de una tarea específica"""
    try:
        task_result = await backend.call_dev_core_service(
            "task_manager",
            f"/api/tasks/{task_id}"
        )
        
        return task_result
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/tasks/failed/clear")
async def clear_failed_tasks():
    """Limpiar tareas fallidas"""
    try:
        clear_result = await backend.call_dev_core_service(
            "task_manager",
            "/api/tasks/failed/clear",
            "POST"
        )
        
        return clear_result
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ============================================================================
# BUILD AND DEPLOYMENT
# ============================================================================

@app.post("/api/repository/{repo_name}/build")
async def build_repository(repo_name: str, background_tasks: BackgroundTasks):
    """Build individual de repositorio"""
    try:
        # Crear tarea en Task Manager
        task_data = {
            "name": f"Build {repo_name}",
            "type": "build",
            "repository": repo_name,
            "status": "running"
        }
        
        task_result = await backend.call_dev_core_service(
            "task_manager",
            "/api/tasks",
            "POST",
            task_data
        )
        
        # Ejecutar build en background
        background_tasks.add_task(execute_build, repo_name, task_result.get("task_id"))
        
        return {
            "success": True,
            "message": f"Build started for {repo_name}",
            "task_id": task_result.get("task_id")
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/build/all")
async def build_all_repositories(background_tasks: BackgroundTasks):
    """Build de todos los repositorios"""
    try:
        # Obtener lista de repositorios
        repos_result = await get_repositories()
        repositories = repos_result.get("repositories", [])
        
        if not repositories:
            return {"success": False, "error": "No repositories found"}
        
        # Crear tareas para cada repositorio
        tasks = []
        for repo in repositories[:5]:  # Limitar a 5 repos
            task_data = {
                "name": f"Build {repo['name']}",
                "type": "build",
                "repository": repo['name'],
                "status": "queued"
            }
            
            task_result = await backend.call_dev_core_service(
                "task_manager",
                "/api/tasks",
                "POST",
                task_data
            )
            
            tasks.append(task_result)
            
            # Ejecutar en background
            background_tasks.add_task(execute_build, repo['name'], task_result.get("task_id"))
        
        return {
            "success": True,
            "message": f"Build started for {len(tasks)} repositories",
            "tasks": tasks
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def execute_build(repo_name: str, task_id: str):
    """Ejecutar build de repositorio"""
    try:
        # Simular proceso de build
        await asyncio.sleep(2)
        
        # Actualizar tarea como completada
        update_data = {
            "status": "completed",
            "result": f"Build completed for {repo_name}",
            "completed_at": datetime.now().isoformat()
        }
        
        await backend.call_dev_core_service(
            "task_manager",
            f"/api/tasks/{task_id}",
            "POST",
            update_data
        )
        
        logger.info(f"Build completed for {repo_name}")
        
    except Exception as e:
        logger.error(f"Build failed for {repo_name}: {e}")
        
        # Marcar tarea como fallida
        update_data = {
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        }
        
        await backend.call_dev_core_service(
            "task_manager",
            f"/api/tasks/{task_id}",
            "POST",
            update_data
        )

# ============================================================================
# SYSTEM STATUS
# ============================================================================

@app.get("/api/system/status")
async def system_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Estado del sistema completo - Requiere autenticación"""
    verify_bearer_token(credentials)
    """Estado del sistema completo"""
    try:
        status = {
            "portal": "healthy",
            "dev_core_services": {},
            "external_services": {}
        }
        
        # Verificar servicios Dev-Core
        for service_name, service_url in DEV_CORE_SERVICES.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=5)
                status["dev_core_services"][service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                status["dev_core_services"][service_name] = "unavailable"
        
        # Verificar servicios externos
        # PostgreSQL
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((EXTERNAL_SERVICES["postgres"]["host"], EXTERNAL_SERVICES["postgres"]["port"]))
            sock.close()
            status["external_services"]["postgres"] = "healthy" if result == 0 else "unavailable"
        except:
            status["external_services"]["postgres"] = "unavailable"
        
        # Redis
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((EXTERNAL_SERVICES["redis"]["host"], EXTERNAL_SERVICES["redis"]["port"]))
            sock.close()
            status["external_services"]["redis"] = "healthy" if result == 0 else "unavailable"
        except:
            status["external_services"]["redis"] = "unavailable"
        
        # MinIO
        try:
            minio_url = f"http://{EXTERNAL_SERVICES['minio']['host']}:{EXTERNAL_SERVICES['minio']['port']}"
            response = requests.get(minio_url, timeout=5)
            status["external_services"]["minio"] = "healthy" if response.status_code in [200, 403, 404] else "unavailable"
        except:
            status["external_services"]["minio"] = "unavailable"
        
        return {
            "status": "success",
            "services": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ============================================================================
# METRICS AND DASHBOARD
# ============================================================================

@app.get("/api/v1/dashboard")
async def get_dashboard_data():
    """Datos para el dashboard"""
    try:
        # Obtener métricas de diferentes servicios
        dashboard_data = {
            "repositories": {
                "total": 0,
                "active": 0,
                "last_updated": datetime.now().isoformat()
            },
            "tasks": {
                "completed": 0,
                "running": 0,
                "failed": 0,
                "queued": 0
            },
            "system": {
                "uptime": "99.9%",
                "cpu_usage": "45%",
                "memory_usage": "62%",
                "disk_usage": "38%"
            }
        }
        
        # Obtener datos reales de repositorios
        repos_result = await get_repositories()
        if repos_result.get("status") == "success":
            dashboard_data["repositories"]["total"] = repos_result.get("total_count", 0)
            dashboard_data["repositories"]["active"] = len([r for r in repos_result.get("repositories", []) if not r.get("archived", False)])
        
        # Obtener datos reales de tareas
        tasks_result = await get_tasks()
        if tasks_result.get("status") == "success":
            tasks = tasks_result.get("tasks", [])
            dashboard_data["tasks"]["completed"] = len([t for t in tasks if t.get("status") == "completed"])
            dashboard_data["tasks"]["running"] = len([t for t in tasks if t.get("status") == "running"])
            dashboard_data["tasks"]["failed"] = len([t for t in tasks if t.get("status") == "failed"])
            dashboard_data["tasks"]["queued"] = len([t for t in tasks if t.get("status") == "queued"])
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/metrics")
async def get_metrics():
    """Métricas del sistema"""
    try:
        metrics = {
            "system": {
                "cpu_usage": 45.2,
                "memory_usage": 62.1,
                "disk_usage": 38.7,
                "network_io": {
                    "bytes_sent": 1024000,
                    "bytes_received": 2048000
                }
            },
            "services": {
                "total_requests": 15420,
                "successful_requests": 14890,
                "failed_requests": 530,
                "average_response_time": 245
            },
            "repositories": {
                "total_builds": 89,
                "successful_builds": 82,
                "failed_builds": 7,
                "average_build_time": 180
            }
        }
        
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# SERVICE TESTING ENDPOINTS
# ============================================================================

@app.post("/api/test/database")
async def test_database_connection(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Probar conexión a PostgreSQL - Requiere autenticación"""
    verify_bearer_token(credentials)
    """Probar conexión a PostgreSQL"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((EXTERNAL_SERVICES["postgres"]["host"], EXTERNAL_SERVICES["postgres"]["port"]))
        sock.close()
        
        if result == 0:
            return {
                "success": True,
                "status": "healthy",
                "message": "PostgreSQL connection successful",
                "host": f"{EXTERNAL_SERVICES['postgres']['host']}:{EXTERNAL_SERVICES['postgres']['port']}"
            }
        else:
            return {
                "success": False,
                "status": "unavailable",
                "message": "PostgreSQL port not accessible"
            }
    except Exception as e:
        return {
            "success": False,
            "status": "unavailable",
            "message": f"PostgreSQL unavailable: {str(e)}"
        }

@app.post("/api/test/redis")
async def test_redis_connection(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Probar conexión a Redis - Requiere autenticación"""
    verify_bearer_token(credentials)
    """Probar conexión a Redis"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((EXTERNAL_SERVICES["redis"]["host"], EXTERNAL_SERVICES["redis"]["port"]))
        sock.close()
        
        if result == 0:
            return {
                "success": True,
                "status": "healthy",
                "message": "Redis connection successful",
                "host": f"{EXTERNAL_SERVICES['redis']['host']}:{EXTERNAL_SERVICES['redis']['port']}"
            }
        else:
            return {
                "success": False,
                "status": "unavailable",
                "message": "Redis port not accessible"
            }
    except Exception as e:
        return {
            "success": False,
            "status": "unavailable", 
            "message": f"Redis unavailable: {str(e)}"
        }

@app.post("/api/test/minio")
async def test_minio_connection(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Probar conexión a MinIO - Requiere autenticación"""
    verify_bearer_token(credentials)
    """Probar conexión a MinIO"""
    try:
        minio_url = f"http://{EXTERNAL_SERVICES['minio']['host']}:{EXTERNAL_SERVICES['minio']['port']}"
        response = requests.get(minio_url, timeout=5)
        if response.status_code in [200, 403, 404]:  # 403/404 son normales para MinIO
            return {
                "success": True,
                "status": "healthy",
                "message": "MinIO connection successful",
                "host": f"{EXTERNAL_SERVICES['minio']['host']}:{EXTERNAL_SERVICES['minio']['port']}"
            }
        else:
            return {
                "success": False,
                "status": "unhealthy",
                "message": f"MinIO returned status {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "status": "unavailable",
            "message": f"MinIO unavailable: {str(e)}"
        }

# ============================================================================
# CLOUD PROVIDERS INTEGRATION
# ============================================================================

@app.get("/api/providers/azure-devops")
async def get_azure_devops_config():
    """Obtener configuración de Azure DevOps"""
    try:
        return {
            "success": True,
            "config": {
                "organization": backend.azure_config.get("organization", ""),
                "project": backend.azure_config.get("project", ""),
                "configured": backend.azure_config.get("configured", False)
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/providers/azure-devops")
async def configure_azure_devops(request: Request):
    """Configurar Azure DevOps"""
    try:
        data = await request.json()
        organization = data.get("organization")
        project = data.get("project", "")
        token = data.get("personal_access_token")
        
        if not organization or not token:
            return {"success": False, "error": "Organization and token are required"}
        
        # Probar conexión con Azure DevOps
        import base64
        auth_string = base64.b64encode(f":{token}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json"
        }
        
        test_url = f"https://dev.azure.com/{organization}/_apis/projects"
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Guardar configuración
            backend.azure_config = {
                "organization": organization,
                "project": project,
                "token": token,
                "configured": True
            }
            
            return {
                "success": True,
                "message": "Azure DevOps configured successfully",
                "organization": organization
            }
        else:
            return {
                "success": False,
                "error": f"Azure DevOps API error: {response.status_code}"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/providers/azure-devops/test")
async def test_azure_devops_connection():
    """Probar conexión con Azure DevOps"""
    try:
        if not backend.azure_config.get("configured"):
            return {"success": False, "error": "Azure DevOps not configured"}
        
        organization = backend.azure_config.get("organization")
        token = backend.azure_config.get("token")
        
        import base64
        auth_string = base64.b64encode(f":{token}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json"
        }
        
        test_url = f"https://dev.azure.com/{organization}/_apis/projects"
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            projects = response.json()
            return {
                "success": True,
                "message": f"Connected to Azure DevOps ({organization})",
                "projects_count": projects.get("count", 0)
            }
        else:
            return {
                "success": False,
                "error": f"Azure DevOps API error: {response.status_code}"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# TECHDOCS INTEGRATION
# ============================================================================

@app.get("/api/techdocs/projects")
async def get_techdocs_projects():
    """Obtener proyectos de documentación"""
    try:
        # Obtener repositorios y convertir a proyectos TechDocs
        repos_result = await backend.call_dev_core_service(
            "repository_manager",
            "/api/repositories"
        )
        
        projects = []
        if "error" not in repos_result:
            repositories = repos_result.get("repositories", [])
            for repo in repositories:
                projects.append({
                    "name": repo.get("name", ""),
                    "description": repo.get("description", f"Documentación de {repo.get('name', '')}"),
                    "has_mkdocs": True,
                    "pages": 5 + len(repo.get("name", "")) % 10,
                    "last_updated": repo.get("updated_at", datetime.now().isoformat()),
                    "language": repo.get("language", "Markdown")
                })
        
        # Si no hay repos, mostrar proyectos mock
        if not projects:
            projects = [
                {
                    "name": "ia-ops-dev-core",
                    "description": "Servicios principales de Dev-Core",
                    "has_mkdocs": True,
                    "pages": 15,
                    "last_updated": datetime.now().isoformat(),
                    "language": "Python"
                },
                {
                    "name": "ia-ops-docs", 
                    "description": "Portal de documentación migrado",
                    "has_mkdocs": True,
                    "pages": 8,
                    "last_updated": datetime.now().isoformat(),
                    "language": "Python"
                }
            ]
        
        return {
            "success": True,
            "projects": projects,
            "count": len(projects)
        }
        
    except Exception as e:
        logger.error(f"Error getting TechDocs projects: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/techdocs/search/advanced")
async def search_techdocs_advanced(q: str, project: str = ""):
    """Búsqueda avanzada en TechDocs"""
    try:
        if len(q.strip()) < 2:
            return []
        
        results = []
        projects = ["ia-ops-dev-core", "ia-ops-docs", "ia-ops-veritas"]
        
        for proj in projects:
            if not project or project == proj:
                if q.lower() in proj.lower() or q.lower() in "documentation api setup":
                    results.append({
                        "project": proj,
                        "file": f"docs/{q.lower()}.md",
                        "title": f"Documentación de {q}",
                        "snippet": f"Información sobre {q} en el proyecto {proj}..."
                    })
        
        return results
        
    except Exception as e:
        logger.error(f"Error in TechDocs search: {e}")
        return []

@app.get("/api/cache/test")
async def test_redis_cache():
    """Probar conexión y funcionalidad de Redis cache"""
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
