# 📚 IA-Ops Dev Core - API Documentation

## 🌐 Base URLs
- **Repository Manager**: `http://localhost:8860`
- **Task Manager**: `http://localhost:8861`
- **Log Manager**: `http://localhost:8862`
- **DataSync Manager**: `http://localhost:8863`
- **GitHub Runner Manager**: `http://localhost:8864`
- **TechDocs Builder**: `http://localhost:8865`

---

## 📁 Repository Manager API (Port 8860)

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| GET | `/repositories` | List all repositories |
| POST | `/repositories` | Create new repository |
| GET | `/repositories/{id}` | Get repository by ID |
| PUT | `/repositories/{id}` | Update repository |
| DELETE | `/repositories/{id}` | Delete repository |
| POST | `/repositories/{id}/sync` | Sync repository |

### Data Models
```json
{
  "repository": {
    "id": "integer",
    "name": "string",
    "url": "string",
    "branch": "string",
    "description": "string",
    "status": "active|inactive|syncing",
    "created_at": "ISO datetime",
    "last_sync": "ISO datetime"
  }
}
```

---

## 📋 Task Manager API (Port 8861)

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create new task |
| GET | `/tasks/{id}` | Get task by ID |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| POST | `/tasks/{id}/execute` | Execute task |
| GET | `/tasks/{id}/logs` | Get task logs |

### Data Models
```json
{
  "task": {
    "id": "integer",
    "name": "string",
    "type": "build|test|deploy|sync",
    "status": "pending|running|completed|failed",
    "repository_id": "integer",
    "command": "string",
    "environment": "object",
    "created_at": "ISO datetime",
    "started_at": "ISO datetime",
    "completed_at": "ISO datetime",
    "logs": "string"
  }
}
```

---

## 📊 Log Manager API (Port 8862)

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| GET | `/logs` | List all logs |
| GET | `/logs/search` | Search logs |
| GET | `/logs/{service}` | Get logs by service |
| POST | `/logs` | Create log entry |
| DELETE | `/logs/{id}` | Delete log entry |

### Data Models
```json
{
  "log": {
    "id": "integer",
    "service": "string",
    "level": "info|warning|error|debug",
    "message": "string",
    "timestamp": "ISO datetime",
    "metadata": "object"
  }
}
```

---

## 🔄 DataSync Manager API (Port 8863)

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| GET | `/sync-jobs` | List sync jobs |
| POST | `/sync-jobs` | Create sync job |
| GET | `/sync-jobs/{id}` | Get sync job |
| POST | `/sync-jobs/{id}/execute` | Execute sync |
| GET | `/backups` | List backups |
| POST | `/backups` | Create backup |

### Data Models
```json
{
  "sync_job": {
    "id": "integer",
    "name": "string",
    "source": "string",
    "destination": "string",
    "status": "pending|running|completed|failed",
    "last_run": "ISO datetime",
    "next_run": "ISO datetime"
  }
}
```

---

## 🏃 GitHub Runner Manager API (Port 8864)

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| GET | `/runners` | List runners |
| POST | `/runners` | Create runner |
| GET | `/runners/{id}` | Get runner |
| DELETE | `/runners/{id}` | Remove runner |
| GET | `/workflows` | List workflows |
| POST | `/workflows/{id}/trigger` | Trigger workflow |

### Data Models
```json
{
  "runner": {
    "id": "integer",
    "name": "string",
    "status": "online|offline|busy",
    "labels": ["array"],
    "repository": "string",
    "created_at": "ISO datetime"
  }
}
```

---

## 📚 TechDocs Builder API (Port 8865)

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| GET | `/docs` | List documentation sites |
| POST | `/docs/build` | Build documentation |
| GET | `/docs/{id}` | Get doc site info |
| POST | `/docs/{id}/rebuild` | Rebuild docs |
| GET | `/docs/{id}/preview` | Preview docs |

### Data Models
```json
{
  "doc_site": {
    "id": "integer",
    "name": "string",
    "repository_id": "integer",
    "status": "building|ready|failed",
    "url": "string",
    "last_build": "ISO datetime"
  }
}
```

---

## 🔧 Common Response Format

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

### Pagination
```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```
