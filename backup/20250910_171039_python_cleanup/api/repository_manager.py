from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Repository Manager", version="2.1.0")

class RepositoryRequest(BaseModel):
    url: str
    branch: str = "main"

@app.get("/health")
async def health():
    return {
        "service": "repository_manager", 
        "status": "healthy",
        "port": 8860,
        "bucket": "ia-ops-dev-core"
    }

@app.get("/repositories")
async def list_repositories():
    return {
        "repositories": [
            {"id": 1, "name": "ia-ops-core", "project": "ia-ops-core"},
            {"id": 2, "name": "ia-ops-docs", "project": "ia-ops-docs"}
        ]
    }

@app.post("/clone")
async def clone_repository(request: RepositoryRequest):
    return {
        "status": "success",
        "url": request.url,
        "branch": request.branch,
        "message": "Repository cloned successfully"
    }
