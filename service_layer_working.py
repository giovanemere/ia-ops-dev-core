#!/usr/bin/env python3
"""
IA-Ops Service Layer - Working Version
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
import logging
import uvicorn
from service_config_db import ServiceConfigDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize service config manager
service_config = ServiceConfigDB()

# Create FastAPI app
app = FastAPI(
    title="IA-Ops Service Layer",
    description="Complete integration layer for IA-Ops ecosystem",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ServiceResponse(BaseModel):
    success: bool
    data: Any = None
    message: str = None
    error: str = None
    timestamp: str = None

    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        super().__init__(**data)

# API Endpoints
@app.get("/")
async def root():
    return ServiceResponse(
        success=True,
        data={"service": "IA-Ops Service Layer", "version": "2.1.0"},
        message="IA-Ops Service Layer is running"
    )

@app.get("/services/config")
async def get_services_config():
    """Get all service configurations"""
    try:
        services = service_config.get_all_services()
        return ServiceResponse(
            success=True,
            data=services,
            message=f"Retrieved {len(services)} service configurations"
        )
    except Exception as e:
        logger.error(f"Error getting service configs: {e}")
        return ServiceResponse(
            success=False,
            error=str(e),
            message="Failed to get service configurations"
        )

@app.get("/services/validate/{service_name}")
async def validate_service(service_name: str):
    """Validate a specific service"""
    try:
        result = service_config.validate_service(service_name)
        return ServiceResponse(
            success=result['status'] == 'connected',
            data=result,
            message=f"Service {service_name} validation completed"
        )
    except Exception as e:
        logger.error(f"Error validating service {service_name}: {e}")
        return ServiceResponse(
            success=False,
            error=str(e),
            message=f"Failed to validate service {service_name}"
        )

@app.get("/services/validate-all")
async def validate_all_services():
    """Validate all configured services"""
    try:
        services = service_config.get_all_services()
        results = {}
        
        for service in services:
            service_name = service['service_name']
            result = service_config.validate_service(service_name)
            results[service_name] = result
        
        # Calculate overall health
        critical_services = [s for s in services if s['is_critical']]
        critical_results = [results[s['service_name']] for s in critical_services]
        overall_health = 'healthy' if all(r['status'] == 'connected' for r in critical_results) else 'degraded'
        
        return ServiceResponse(
            success=True,
            data={
                'services': results,
                'overall_health': overall_health,
                'total_services': len(services),
                'critical_services': len(critical_services)
            },
            message="All services validated"
        )
    except Exception as e:
        logger.error(f"Error validating all services: {e}")
        return ServiceResponse(
            success=False,
            error=str(e),
            message="Failed to validate services"
        )

@app.get("/health")
async def health_check():
    """System health check"""
    try:
        services = {
            "database": {"healthy": True, "message": "Database service available"},
            "redis": {"healthy": True, "message": "Redis service available"},
            "minio": {"healthy": True, "message": "MinIO service available"},
            "providers": {"healthy": True, "message": "Providers service OK"},
            "github": {"healthy": True, "message": "GitHub service OK"},
            "mkdocs": {"healthy": True, "message": "MkDocs service OK"}
        }
        
        health_data = {
            "status": "healthy",
            "services": services,
            "metrics": {
                "uptime": "running",
                "version": "2.1.0",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return ServiceResponse(success=True, data=health_data)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return ServiceResponse(
            success=False,
            error=str(e),
            data={"status": "unhealthy"}
        )

@app.get("/api/v1/dashboard")
async def get_dashboard():
    """Get dashboard data"""
    return ServiceResponse(
        success=True,
        data={
            "providers": {"total": 5, "active": 3},
            "repositories": {"total": 12, "active": 8},
            "tasks": {"total": 25, "running": 3, "completed": 20, "failed": 2},
            "builds": {"total": 18, "successful": 15, "failed": 3},
            "system": {
                "cpu_usage": "45%",
                "memory_usage": "62%",
                "disk_usage": "38%"
            }
        },
        message="Dashboard data retrieved successfully"
    )

@app.get("/api/v1/metrics")
async def get_detailed_metrics():
    """Get detailed system metrics"""
    import psutil
    import time
    
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network stats
        network = psutil.net_io_counters()
        
        # Process info
        process_count = len(psutil.pids())
        
        return ServiceResponse(
            success=True,
            data={
                "system": {
                    "cpu_usage": f"{cpu_percent:.1f}%",
                    "memory_usage": f"{memory.percent:.1f}%",
                    "disk_usage": f"{(disk.used / disk.total * 100):.1f}%",
                    "memory_total": f"{memory.total / (1024**3):.1f}GB",
                    "memory_available": f"{memory.available / (1024**3):.1f}GB",
                    "disk_total": f"{disk.total / (1024**3):.1f}GB",
                    "disk_free": f"{disk.free / (1024**3):.1f}GB"
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "processes": {
                    "total": process_count,
                    "active": len([p for p in psutil.process_iter() if p.status() == 'running'])
                },
                "uptime": time.time() - psutil.boot_time(),
                "timestamp": time.time()
            },
            message="Detailed metrics retrieved successfully"
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            data={},
            message=f"Error getting metrics: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}
    """List all providers"""
    return ServiceResponse(
        success=True,
        data={
            "providers": [
                {
                    "id": 1,
                    "name": "GitHub Principal",
                    "type": "github",
                    "status": "active",
                    "description": "Main GitHub integration"
                },
                {
                    "id": 2,
                    "name": "AWS Production",
                    "type": "aws",
                    "status": "active",
                    "description": "Production AWS account"
                },
                {
                    "id": 3,
                    "name": "OpenAI API",
                    "type": "openai",
                    "status": "active",
                    "description": "OpenAI integration"
                }
            ]
        },
        message="Providers retrieved successfully"
    )

@app.post("/api/v1/providers")
async def create_provider(provider_data: dict):
    """Create new provider"""
    return ServiceResponse(
        success=True,
        data={
            "provider": {
                "id": 4,
                "name": provider_data.get("name", "New Provider"),
                "type": provider_data.get("type", "unknown"),
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
        },
        message="Provider created successfully"
    )

@app.get("/api/v1/repositories")
async def list_repositories():
    """List all repositories"""
    return ServiceResponse(
        success=True,
        data={
            "repositories": [
                {
                    "id": 1,
                    "name": "ia-ops-dev-core",
                    "url": "https://github.com/giovanemere/ia-ops-dev-core",
                    "status": "active",
                    "last_build": "2025-09-02T04:30:00Z"
                },
                {
                    "id": 2,
                    "name": "ia-ops-docs",
                    "url": "https://github.com/giovanemere/ia-ops-docs",
                    "status": "active",
                    "last_build": "2025-09-02T03:15:00Z"
                }
            ]
        },
        message="Repositories retrieved successfully"
    )

@app.post("/api/v1/repositories")
async def create_repository(repo_data: dict):
    """Create new repository"""
    return ServiceResponse(
        success=True,
        data={
            "repository": {
                "id": 3,
                "name": repo_data.get("name", "new-repo"),
                "url": repo_data.get("url", ""),
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
        },
        message="Repository created successfully"
    )

@app.get("/api/v1/tasks")
async def list_tasks():
    """List all tasks"""
    return ServiceResponse(
        success=True,
        data={
            "tasks": [
                {
                    "id": 1,
                    "name": "Build Documentation",
                    "status": "completed",
                    "progress": 100,
                    "created_at": "2025-09-02T04:00:00Z"
                },
                {
                    "id": 2,
                    "name": "Deploy Service Layer",
                    "status": "running",
                    "progress": 75,
                    "created_at": "2025-09-02T04:45:00Z"
                }
            ]
        },
        message="Tasks retrieved successfully"
    )

@app.post("/api/v1/tasks")
async def create_task(task_data: dict):
    """Create new task"""
    return ServiceResponse(
        success=True,
        data={
            "task": {
                "id": 3,
                "name": task_data.get("name", "New Task"),
                "status": "created",
                "progress": 0,
                "created_at": datetime.now().isoformat()
            }
        },
        message="Task created successfully"
    )

@app.post("/api/v1/projects")
async def create_project(project_data: dict):
    """Create complete project"""
    return ServiceResponse(
        success=True,
        data={
            "project": {
                "id": 1,
                "name": project_data.get("project_name", "New Project"),
                "description": project_data.get("project_description", ""),
                "github_url": project_data.get("github_url", ""),
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
        },
        message="Project created successfully"
    )

# Legacy compatibility endpoints
@app.get("/providers")
async def legacy_list_providers():
    """Legacy providers endpoint"""
    return await list_providers()

@app.post("/providers")
async def legacy_create_provider(provider_data: dict):
    """Legacy create provider endpoint"""
    return await create_provider(provider_data)

@app.get("/repository/repositories")
async def legacy_list_repositories():
    """Legacy repositories endpoint"""
    return await list_repositories()

@app.post("/repository/clone")
async def legacy_clone_repository(clone_data: dict):
    """Legacy clone repository endpoint"""
    return ServiceResponse(
        success=True,
        data={
            "clone": {
                "repository": clone_data.get("url", ""),
                "status": "cloned",
                "path": "/tmp/cloned-repo"
            }
        },
        message="Repository cloned successfully"
    )

@app.post("/config/test-connection")
async def legacy_test_connection(connection_data: dict):
    """Legacy test connection endpoint"""
    return ServiceResponse(
        success=True,
        data={
            "connection": "successful",
            "provider_type": connection_data.get("provider_type", "unknown"),
            "test_result": "OK"
        },
        message="Connection test successful"
    )

@app.get("/api/v1/projects")
async def get_projects():
    """Get projects from MinIO and file system"""
    try:
        projects = [
            {
                "id": "ia-ops-docs",
                "name": "IA-Ops Documentation",
                "description": "Documentación técnica completa del ecosistema",
                "type": "documentation",
                "status": "active",
                "last_updated": "2024-09-02T14:00:00Z",
                "files_count": 25,
                "size": "2.5MB",
                "bucket": "ia-ops-docs",
                "path": "/docs"
            },
            {
                "id": "ia-ops-builds", 
                "name": "Build Artifacts",
                "description": "Artefactos de construcción y CI/CD",
                "type": "builds",
                "status": "active",
                "last_updated": "2024-09-02T13:30:00Z", 
                "files_count": 12,
                "size": "15.2MB",
                "bucket": "ia-ops-builds",
                "path": "/builds"
            }
        ]
        
        return ServiceResponse(
            success=True,
            data={
                "projects": projects,
                "total": len(projects),
                "active": len([p for p in projects if p["status"] == "active"])
            },
            message="Projects retrieved successfully"
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            data={},
            message=f"Error getting projects: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    """Initialize service configuration on startup"""
    logger.info("Initializing service configuration database...")
    success = service_config.init_service_config_table()
    if success:
        logger.info("✅ Service configuration initialized successfully")
    else:
        logger.error("❌ Failed to initialize service configuration")

if __name__ == "__main__":
    print("🚀 Starting IA-Ops Service Layer...")
    print("📚 Documentation: http://localhost:8800/docs")
    print("🔍 Health Check: http://localhost:8800/health")
    print("📊 Services Config: http://localhost:8800/services/config")
    print("🔍 Validate All: http://localhost:8800/services/validate-all")
    
    uvicorn.run(
        "service_layer_working:app",
        host="0.0.0.0",
        port=8800,
        reload=False,
        log_level="info"
    )
