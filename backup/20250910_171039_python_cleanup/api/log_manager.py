from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Log Manager", version="2.1.0")

class LogEntry(BaseModel):
    level: str
    message: str
    timestamp: Optional[str] = None

@app.get("/health")
async def health():
    return {
        "service": "log_manager",
        "status": "healthy",
        "port": 8862, 
        "bucket": "ia-ops-dev-core"
    }

@app.get("/logs")
async def get_logs():
    return {
        "logs": [
            {"level": "INFO", "message": "Service started", "timestamp": "2024-01-01T00:00:00Z"},
            {"level": "DEBUG", "message": "Processing request", "timestamp": "2024-01-01T00:01:00Z"}
        ]
    }

@app.post("/logs")
async def add_log(log: LogEntry):
    return {
        "status": "success",
        "log": {
            "level": log.level,
            "message": log.message,
            "timestamp": log.timestamp or "2024-01-01T00:00:00Z"
        }
    }
