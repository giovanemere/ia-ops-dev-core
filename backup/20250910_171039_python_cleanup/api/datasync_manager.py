from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="DataSync Manager", version="2.1.0")

class SyncRequest(BaseModel):
    source: str
    destination: str
    sync_type: str = "full"

@app.get("/health")
async def health():
    return {
        "service": "datasync_manager",
        "status": "healthy",
        "port": 8863,
        "bucket": "ia-ops-dev-core"
    }

@app.get("/sync/status")
async def sync_status():
    return {
        "syncs": [
            {"id": 1, "source": "github", "destination": "minio", "status": "completed"},
            {"id": 2, "source": "docs", "destination": "storage", "status": "running"}
        ]
    }

@app.post("/sync")
async def start_sync(request: SyncRequest):
    return {
        "status": "success",
        "sync_id": 456,
        "source": request.source,
        "destination": request.destination,
        "type": request.sync_type
    }
