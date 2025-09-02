from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Task Manager", version="2.1.0")

class Task(BaseModel):
    id: Optional[int] = None
    name: str
    status: str = "pending"
    description: Optional[str] = None

@app.get("/health")
async def health():
    return {
        "service": "task_manager",
        "status": "healthy", 
        "port": 8861,
        "bucket": "ia-ops-dev-core"
    }

@app.get("/tasks")
async def list_tasks():
    return {
        "tasks": [
            {"id": 1, "name": "Build Documentation", "status": "completed"},
            {"id": 2, "name": "Deploy Services", "status": "running"}
        ]
    }

@app.post("/tasks")
async def create_task(task: Task):
    return {
        "status": "success",
        "task": {
            "id": 123,
            "name": task.name,
            "status": task.status,
            "description": task.description
        }
    }
