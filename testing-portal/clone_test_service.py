from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.services.repository_cloner import RepositoryCloner

app = FastAPI(title="Repository Clone Test Service", version="1.0.0")
cloner = RepositoryCloner()

class CloneRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    token: Optional[str] = None

@app.post("/clone")
async def clone_repository(request: CloneRequest):
    """Clone repository for testing"""
    result = cloner.clone_repository(
        repo_url=request.repo_url,
        branch=request.branch,
        token=request.token
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.delete("/cleanup/{repo_name}")
async def cleanup_repository(repo_name: str):
    """Remove cloned repository"""
    success = cloner.cleanup_repository(repo_name)
    return {"success": success, "repo_name": repo_name}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "clone-test"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18863)
