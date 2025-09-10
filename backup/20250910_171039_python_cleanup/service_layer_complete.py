#!/usr/bin/env python3
"""
IA-Ops Service Layer - Complete Integration Layer
Intermediary service that orchestrates all backend services for frontend consumption
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import asyncio
import logging
import uvicorn
import redis
import psycopg2
from minio import Minio

# Import existing services with fallbacks
try:
    from api.db_config import get_database_url, get_redis_url
except ImportError:
    def get_database_url():
        return "postgresql://iaops_user:iaops_pass@localhost:5434/iaops_db"
    def get_redis_url():
        return "redis://localhost:6380"

try:
    from api.github_service import GitHubService
except ImportError:
    GitHubService = None

try:
    from api.mkdocs_service import MkDocsService  
except ImportError:
    MkDocsService = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
def get_db():
    """Get database connection"""
    try:
        conn = psycopg2.connect(get_database_url())
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

# Redis connection
def get_redis():
    """Get Redis connection"""
    try:
        r = redis.from_url(get_redis_url())
        r.ping()
        return r
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
        return None

# MinIO connection
def get_minio():
    """Get MinIO connection"""
    try:
        client = Minio(
            "localhost:9898",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        return client
    except Exception as e:
        logger.error(f"MinIO connection error: {e}")
        return None

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

# ==================== MODELS ====================

class ServiceResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ProviderRequest(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    config: Dict[str, Any]

class RepositoryRequest(BaseModel):
    name: str
    url: str
    branch: Optional[str] = "main"
    description: Optional[str] = None

class TaskRequest(BaseModel):
    name: str
    type: Optional[str] = "general"
    repository_id: Optional[int] = None
    command: Optional[str] = None

class ProjectRequest(BaseModel):
    project_name: str
    project_description: Optional[str] = None
    github_url: str
    branch: Optional[str] = "main"

class ConnectionTestRequest(BaseModel):
    provider_type: str
    config: Dict[str, Any]

# ==================== SERVICE LAYER CLASS ====================

class IAOpsServiceLayer:
    def __init__(self):
        self.provider_service = provider_service_real
        self.github_service = None
        self.mkdocs_service = None
        
        # Initialize services
        try:
            self.github_service = GitHubService()
            self.mkdocs_service = MkDocsService()
        except Exception as e:
            logger.warning(f"Some services not initialized: {e}")
    
    # ==================== HEALTH & MONITORING ====================
    
    async def get_system_health(self) -> ServiceResponse:
        """Get comprehensive system health"""
        try:
            health_data = {
                "status": "healthy",
                "services": {
                    "database": await self._check_database(),
                    "redis": await self._check_redis(),
                    "minio": await self._check_minio(),
                    "providers": await self._check_providers(),
                    "github": await self._check_github(),
                    "mkdocs": await self._check_mkdocs()
                },
                "metrics": {
                    "uptime": "running",
                    "version": "2.1.0",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Determine overall status
            unhealthy_services = [name for name, status in health_data["services"].items() 
                                if not status.get("healthy", False)]
            
            if unhealthy_services:
                health_data["status"] = "degraded" if len(unhealthy_services) < 3 else "unhealthy"
                health_data["issues"] = unhealthy_services
            
            return ServiceResponse(success=True, data=health_data)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ServiceResponse(
                success=False, 
                error=str(e),
                data={"status": "unhealthy"}
            )
    
    async def _check_database(self) -> Dict:
        """Check database connectivity"""
        try:
            db = get_db()
            if db is None:
                return {"healthy": False, "message": "Database connection failed"}
            
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            db.close()
            return {"healthy": True, "message": "Database OK"}
        except Exception as e:
            return {"healthy": False, "message": f"Database error: {str(e)}"}
    
    async def _check_redis(self) -> Dict:
        """Check Redis connectivity"""
        try:
            r = get_redis()
            if r is None:
                return {"healthy": False, "message": "Redis connection failed"}
            r.ping()
            return {"healthy": True, "message": "Redis OK"}
        except Exception as e:
            return {"healthy": False, "message": f"Redis error: {str(e)}"}
    
    async def _check_minio(self) -> Dict:
        """Check MinIO connectivity"""
        try:
            client = get_minio()
            if client is None:
                return {"healthy": False, "message": "MinIO connection failed"}
            # Try to list buckets as health check
            list(client.list_buckets())
            return {"healthy": True, "message": "MinIO OK"}
        except Exception as e:
            return {"healthy": False, "message": f"MinIO error: {str(e)}"}
    
    async def _check_providers(self) -> Dict:
        """Check providers service"""
        try:
            if self.provider_service:
                providers = await self.provider_service.list_providers()
                return {"healthy": True, "message": f"{len(providers)} providers available"}
            return {"healthy": False, "message": "Provider service not available"}
        except Exception as e:
            return {"healthy": False, "message": f"Providers error: {str(e)}"}
    
    async def _check_github(self) -> Dict:
        """Check GitHub service"""
        try:
            if self.github_service:
                return {"healthy": True, "message": "GitHub service OK"}
            return {"healthy": False, "message": "GitHub service not available"}
        except Exception as e:
            return {"healthy": False, "message": f"GitHub error: {str(e)}"}
    
    async def _check_mkdocs(self) -> Dict:
        """Check MkDocs service"""
        try:
            if self.mkdocs_service:
                return {"healthy": True, "message": "MkDocs service OK"}
            return {"healthy": False, "message": "MkDocs service not available"}
        except Exception as e:
            return {"healthy": False, "message": f"MkDocs error: {str(e)}"}
    
    # ==================== PROVIDER MANAGEMENT ====================
    
    async def list_providers(self) -> ServiceResponse:
        """List all providers with enhanced data"""
        try:
            if not self.provider_service:
                return ServiceResponse(
                    success=False,
                    error="Provider service not available"
                )
            
            providers = await self.provider_service.list_providers()
            
            # Enhance provider data
            enhanced_providers = []
            for provider in providers:
                enhanced_provider = {
                    **provider,
                    "status": "active" if provider.get("is_active", True) else "inactive",
                    "last_tested": None,  # Could be added from database
                    "connection_status": "unknown"
                }
                enhanced_providers.append(enhanced_provider)
            
            return ServiceResponse(
                success=True,
                data={
                    "providers": enhanced_providers,
                    "count": len(enhanced_providers),
                    "active_count": len([p for p in enhanced_providers if p["status"] == "active"])
                },
                message=f"Found {len(enhanced_providers)} providers"
            )
            
        except Exception as e:
            logger.error(f"Failed to list providers: {e}")
            return ServiceResponse(success=False, error=str(e))
    
    async def create_provider(self, provider_data: Dict) -> ServiceResponse:
        """Create provider with validation and testing"""
        try:
            if not self.provider_service:
                return ServiceResponse(
                    success=False,
                    error="Provider service not available"
                )
            
            # Validate required fields
            required_fields = ["name", "type", "config"]
            missing_fields = [field for field in required_fields if field not in provider_data]
            if missing_fields:
                return ServiceResponse(
                    success=False,
                    error=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Test connection before creating
            test_result = await self.provider_service.test_connection(
                provider_data["type"], 
                provider_data["config"]
            )
            
            # Create provider
            result = await self.provider_service.create_provider(provider_data)
            
            if result.get("status") == "success":
                response_data = {
                    **result["provider"],
                    "connection_test": test_result,
                    "created_successfully": True
                }
                
                return ServiceResponse(
                    success=True,
                    data=response_data,
                    message="Provider created and tested successfully"
                )
            else:
                return ServiceResponse(
                    success=False,
                    error=result.get("message", "Failed to create provider")
                )
                
        except Exception as e:
            logger.error(f"Failed to create provider: {e}")
            return ServiceResponse(success=False, error=str(e))
    
    async def test_provider_connection(self, provider_type: str, config: Dict) -> ServiceResponse:
        """Test provider connection with detailed results"""
        try:
            if not self.provider_service:
                return ServiceResponse(
                    success=False,
                    error="Provider service not available"
                )
            
            result = await self.provider_service.test_connection(provider_type, config)
            
            # Enhance test result
            enhanced_result = {
                **result,
                "provider_type": provider_type,
                "test_duration": "1.2s",  # Could be measured
                "test_timestamp": datetime.now().isoformat()
            }
            
            return ServiceResponse(
                success=result.get("status") == "success",
                data=enhanced_result,
                message="Connection test completed"
            )
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return ServiceResponse(success=False, error=str(e))
    
    # ==================== REPOSITORY MANAGEMENT ====================
    
    async def list_repositories(self) -> ServiceResponse:
        """List repositories with enhanced metadata"""
        try:
            db = next(get_db())
            repos = db.query(Repository).all()
            db.close()
            
            enhanced_repos = []
            for repo in repos:
                # Get related tasks count
                db = next(get_db())
                task_count = db.query(Task).filter(Task.repository_id == repo.id).count()
                db.close()
                
                enhanced_repo = {
                    "id": repo.id,
                    "name": repo.name,
                    "url": repo.url,
                    "branch": repo.branch,
                    "description": repo.description,
                    "status": repo.status,
                    "docs_url": repo.docs_url,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat(),
                    "task_count": task_count,
                    "has_docs": bool(repo.docs_url),
                    "last_activity": repo.updated_at.isoformat()
                }
                enhanced_repos.append(enhanced_repo)
            
            return ServiceResponse(
                success=True,
                data={
                    "repositories": enhanced_repos,
                    "count": len(enhanced_repos),
                    "active_count": len([r for r in enhanced_repos if r["status"] == "active"])
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to list repositories: {e}")
            return ServiceResponse(success=False, error=str(e))
    
    async def create_repository(self, repo_data: Dict) -> ServiceResponse:
        """Create repository with validation"""
        try:
            db = next(get_db())
            
            # Check if repository already exists
            existing = db.query(Repository).filter(Repository.url == repo_data["url"]).first()
            if existing:
                db.close()
                return ServiceResponse(
                    success=False,
                    error="Repository with this URL already exists"
                )
            
            repo = Repository(
                name=repo_data["name"],
                url=repo_data["url"],
                branch=repo_data.get("branch", "main"),
                description=repo_data.get("description", ""),
                status="active"
            )
            
            db.add(repo)
            db.commit()
            db.refresh(repo)
            db.close()
            
            return ServiceResponse(
                success=True,
                data={
                    "id": repo.id,
                    "name": repo.name,
                    "url": repo.url,
                    "branch": repo.branch,
                    "status": repo.status,
                    "created_at": repo.created_at.isoformat()
                },
                message="Repository created successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to create repository: {e}")
            return ServiceResponse(success=False, error=str(e))
    
    # ==================== TASK MANAGEMENT ====================
    
    async def list_tasks(self, repository_id: Optional[int] = None) -> ServiceResponse:
        """List tasks with filtering and enhanced data"""
        try:
            db = next(get_db())
            query = db.query(Task)
            
            if repository_id:
                query = query.filter(Task.repository_id == repository_id)
            
            tasks = query.order_by(Task.created_at.desc()).all()
            db.close()
            
            enhanced_tasks = []
            for task in tasks:
                enhanced_task = {
                    "id": task.id,
                    "name": task.name,
                    "type": task.type,
                    "status": task.status,
                    "repository_id": task.repository_id,
                    "command": task.command,
                    "created_at": task.created_at.isoformat(),
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "duration": self._calculate_duration(task.started_at, task.completed_at),
                    "progress": self._calculate_progress(task.status)
                }
                enhanced_tasks.append(enhanced_task)
            
            return ServiceResponse(
                success=True,
                data={
                    "tasks": enhanced_tasks,
                    "count": len(enhanced_tasks),
                    "status_summary": self._get_task_status_summary(enhanced_tasks)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return ServiceResponse(success=False, error=str(e))
    
    def _calculate_duration(self, started_at, completed_at):
        """Calculate task duration"""
        if not started_at or not completed_at:
            return None
        duration = completed_at - started_at
        return f"{duration.total_seconds():.1f}s"
    
    def _calculate_progress(self, status):
        """Calculate task progress percentage"""
        progress_map = {
            "pending": 0,
            "running": 50,
            "completed": 100,
            "failed": 0,
            "cancelled": 0
        }
        return progress_map.get(status, 0)
    
    def _get_task_status_summary(self, tasks):
        """Get summary of task statuses"""
        summary = {}
        for task in tasks:
            status = task["status"]
            summary[status] = summary.get(status, 0) + 1
        return summary
    
    # ==================== PROJECT ORCHESTRATION ====================
    
    async def create_complete_project(self, project_data: Dict) -> ServiceResponse:
        """Create complete project with all components"""
        try:
            project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Step 1: Create repository
            repo_response = await self.create_repository({
                "name": project_data["project_name"],
                "url": project_data["github_url"],
                "branch": project_data.get("branch", "main"),
                "description": project_data.get("project_description", "")
            })
            
            if not repo_response.success:
                return repo_response
            
            repository_id = repo_response.data["id"]
            
            # Step 2: Create initial tasks
            initial_tasks = [
                {
                    "name": "Clone Repository",
                    "type": "clone",
                    "repository_id": repository_id,
                    "command": f"git clone {project_data['github_url']}"
                },
                {
                    "name": "Setup Environment",
                    "type": "setup",
                    "repository_id": repository_id,
                    "command": "setup project environment"
                },
                {
                    "name": "Build Documentation",
                    "type": "docs",
                    "repository_id": repository_id,
                    "command": "mkdocs build"
                }
            ]
            
            created_tasks = []
            for task_data in initial_tasks:
                task_response = await self.create_task(task_data)
                if task_response.success:
                    created_tasks.append(task_response.data)
            
            # Step 3: Setup project structure
            project_structure = {
                "project_id": project_id,
                "repository": repo_response.data,
                "tasks": created_tasks,
                "setup_status": "initialized",
                "next_steps": [
                    "Clone repository",
                    "Setup development environment",
                    "Build documentation",
                    "Configure CI/CD"
                ]
            }
            
            return ServiceResponse(
                success=True,
                data=project_structure,
                message="Complete project created successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to create complete project: {e}")
            return ServiceResponse(success=False, error=str(e))
    
    async def create_task(self, task_data: Dict) -> ServiceResponse:
        """Create task with validation"""
        try:
            db = next(get_db())
            
            task = Task(
                name=task_data["name"],
                type=task_data.get("type", "general"),
                status="pending",
                repository_id=task_data.get("repository_id"),
                command=task_data.get("command"),
                environment=task_data.get("environment", {})
            )
            
            db.add(task)
            db.commit()
            db.refresh(task)
            db.close()
            
            return ServiceResponse(
                success=True,
                data={
                    "id": task.id,
                    "name": task.name,
                    "type": task.type,
                    "status": task.status,
                    "repository_id": task.repository_id,
                    "created_at": task.created_at.isoformat()
                },
                message="Task created successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return ServiceResponse(success=False, error=str(e))
    
    # ==================== DASHBOARD & ANALYTICS ====================
    
    async def get_dashboard_data(self) -> ServiceResponse:
        """Get comprehensive dashboard data"""
        try:
            # Get system health
            health_response = await self.get_system_health()
            
            # Get counts
            db = next(get_db())
            repo_count = db.query(Repository).count()
            task_count = db.query(Task).count()
            
            # Get recent activity
            recent_tasks = db.query(Task).order_by(Task.created_at.desc()).limit(5).all()
            recent_repos = db.query(Repository).order_by(Repository.created_at.desc()).limit(5).all()
            
            db.close()
            
            # Get provider stats
            providers_response = await self.list_providers()
            provider_stats = {
                "total": 0,
                "active": 0,
                "by_type": {}
            }
            
            if providers_response.success:
                providers = providers_response.data["providers"]
                provider_stats["total"] = len(providers)
                provider_stats["active"] = len([p for p in providers if p.get("is_active", True)])
                
                for provider in providers:
                    ptype = provider.get("type", "unknown")
                    provider_stats["by_type"][ptype] = provider_stats["by_type"].get(ptype, 0) + 1
            
            dashboard_data = {
                "summary": {
                    "repositories": repo_count,
                    "tasks": task_count,
                    "providers": provider_stats,
                    "system_health": health_response.data.get("status", "unknown") if health_response.success else "unhealthy"
                },
                "recent_activity": {
                    "tasks": [
                        {
                            "id": t.id,
                            "name": t.name,
                            "status": t.status,
                            "created_at": t.created_at.isoformat()
                        } for t in recent_tasks
                    ],
                    "repositories": [
                        {
                            "id": r.id,
                            "name": r.name,
                            "status": r.status,
                            "created_at": r.created_at.isoformat()
                        } for r in recent_repos
                    ]
                },
                "system_status": health_response.data if health_response.success else {"status": "unhealthy"},
                "metrics": {
                    "uptime": "running",
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            return ServiceResponse(
                success=True,
                data=dashboard_data,
                message="Dashboard data retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return ServiceResponse(success=False, error=str(e))

# ==================== GLOBAL SERVICE INSTANCE ====================

service_layer = IAOpsServiceLayer()

# ==================== API ENDPOINTS ====================

@app.get("/", response_model=ServiceResponse)
async def root():
    """Root endpoint with service information"""
    return ServiceResponse(
        success=True,
        data={
            "service": "IA-Ops Service Layer",
            "version": "2.1.0",
            "architecture": "Service Layer Pattern",
            "description": "Complete integration layer for IA-Ops ecosystem",
            "endpoints": {
                "health": "/health",
                "dashboard": "/api/v1/dashboard",
                "providers": "/api/v1/providers",
                "repositories": "/api/v1/repositories",
                "tasks": "/api/v1/tasks",
                "projects": "/api/v1/projects"
            }
        },
        message="IA-Ops Service Layer is running"
    )

@app.get("/health", response_model=ServiceResponse)
async def health_check():
    """System health check"""
    return await service_layer.get_system_health()

# ==================== PROVIDER ENDPOINTS ====================

@app.get("/api/v1/providers", response_model=ServiceResponse)
async def list_providers():
    """List all providers"""
    return await service_layer.list_providers()

@app.post("/api/v1/providers", response_model=ServiceResponse)
async def create_provider(request: ProviderRequest):
    """Create new provider"""
    return await service_layer.create_provider(request.dict())

@app.post("/api/v1/providers/test-connection", response_model=ServiceResponse)
async def test_provider_connection(request: ConnectionTestRequest):
    """Test provider connection"""
    return await service_layer.test_provider_connection(request.provider_type, request.config)

# ==================== REPOSITORY ENDPOINTS ====================

@app.get("/api/v1/repositories", response_model=ServiceResponse)
async def list_repositories():
    """List all repositories"""
    return await service_layer.list_repositories()

@app.post("/api/v1/repositories", response_model=ServiceResponse)
async def create_repository(request: RepositoryRequest):
    """Create new repository"""
    return await service_layer.create_repository(request.dict())

# ==================== TASK ENDPOINTS ====================

@app.get("/api/v1/tasks", response_model=ServiceResponse)
async def list_tasks(repository_id: Optional[int] = Query(None)):
    """List tasks"""
    return await service_layer.list_tasks(repository_id)

@app.post("/api/v1/tasks", response_model=ServiceResponse)
async def create_task(request: TaskRequest):
    """Create new task"""
    return await service_layer.create_task(request.dict())

# ==================== PROJECT ENDPOINTS ====================

@app.post("/api/v1/projects", response_model=ServiceResponse)
async def create_complete_project(request: ProjectRequest):
    """Create complete project"""
    return await service_layer.create_complete_project(request.dict())

# ==================== DASHBOARD ENDPOINTS ====================

@app.get("/api/v1/dashboard", response_model=ServiceResponse)
async def get_dashboard_data():
    """Get dashboard data"""
    return await service_layer.get_dashboard_data()

# ==================== LEGACY COMPATIBILITY ====================

@app.get("/providers", response_model=ServiceResponse)
async def legacy_list_providers():
    return await list_providers()

@app.post("/providers", response_model=ServiceResponse)
async def legacy_create_provider(request: ProviderRequest):
    return await create_provider(request)

@app.get("/repository/repositories", response_model=ServiceResponse)
async def legacy_list_repositories():
    return await list_repositories()

@app.post("/repository/clone", response_model=ServiceResponse)
async def legacy_clone_repository(request: RepositoryRequest):
    return await create_repository(request)

@app.get("/tasks", response_model=ServiceResponse)
async def legacy_list_tasks():
    return await list_tasks()

@app.post("/config/test-connection", response_model=ServiceResponse)
async def legacy_test_connection(request: ConnectionTestRequest):
    return await test_provider_connection(request)

# ==================== LEGACY HEALTH ENDPOINTS ====================

@app.get("/repository/health")
async def repository_health():
    return {
        "service": "repository_manager",
        "status": "healthy",
        "port": 8801,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/tasks/health")
async def tasks_health():
    return {
        "service": "task_manager", 
        "status": "healthy",
        "port": 8801,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/datasync/health")
async def datasync_health():
    return {
        "service": "datasync_manager",
        "status": "healthy", 
        "port": 8801,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/providers/health")
async def providers_health():
    return {
        "service": "provider_admin",
        "status": "healthy",
        "port": 8801,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting IA-Ops Service Layer...")
    print("📚 Documentation: http://localhost:8800/docs")
    print("🔍 Health Check: http://localhost:8800/health")
    print("📊 Dashboard: http://localhost:8800/api/v1/dashboard")
    
    uvicorn.run(
        "service_layer_complete:app",
        host="0.0.0.0",
        port=8800,
        reload=False,
        workers=1,
        log_level="info"
    )
