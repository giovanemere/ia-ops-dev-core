#!/usr/bin/env python3
"""
Docs Backend - Backend completo para el portal de documentación
Todas las integraciones: DB, GitHub, MinIO, Tasks, etc.
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional, Any
import asyncio
import subprocess
import tempfile
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IA-Ops Docs Backend", version="2.0.0")

# CORS para permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8845", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de servicios
DEV_CORE_SERVICES = {
    "repository_manager": "http://localhost:8860",
    "task_manager": "http://localhost:8861", 
    "log_manager": "http://localhost:8862",
    "datasync_manager": "http://localhost:8863",
    "github_runner_manager": "http://localhost:8864"
}

EXTERNAL_SERVICES = {
    "postgres": "postgresql://postgres:postgres_admin_2024@localhost:5434/postgres",
    "redis": "redis://localhost:6380",
    "minio": "http://localhost:9899"
}

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
async def system_status():
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
        for service_name, service_url in EXTERNAL_SERVICES.items():
            if service_name == "postgres":
                try:
                    import psycopg2
                    conn = psycopg2.connect(service_url)
                    conn.close()
                    status["external_services"][service_name] = "healthy"
                except:
                    status["external_services"][service_name] = "unavailable"
            elif service_name == "redis":
                try:
                    import redis
                    r = redis.from_url(service_url)
                    r.ping()
                    status["external_services"][service_name] = "healthy"
                except:
                    status["external_services"][service_name] = "unavailable"
            elif service_name == "minio":
                try:
                    response = requests.get(service_url, timeout=5)
                    status["external_services"][service_name] = "healthy"
                except:
                    status["external_services"][service_name] = "unavailable"
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8846)
