#!/usr/bin/env python3
"""
Docs Manager - Servicio de documentación integrado en Dev-Core
Gestión de documentación sin dependencia de MinIO
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
import os
import json
import logging
from datetime import datetime
from pathlib import Path
import markdown
from typing import List, Dict, Optional
import glob
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Docs Manager", version="1.0.0")

class DocsManager:
    def __init__(self):
        self.docs_base_path = Path("/app/docs")
        self.docs_base_path.mkdir(exist_ok=True)
        self.setup_default_docs()
    
    def setup_default_docs(self):
        """Setup default documentation structure"""
        default_docs = {
            "README.md": """# IA-Ops Documentation Portal

## Servicios Disponibles

### 🚀 Dev-Core Services
- **Repository Manager**: Gestión de repositorios
- **Task Manager**: Gestión de tareas
- **Log Manager**: Gestión de logs
- **DataSync Manager**: Sincronización de datos
- **GitHub Runner Manager**: Gestión de runners
- **Docs Manager**: Este servicio de documentación

### 🗄️ Infrastructure
- **PostgreSQL**: Base de datos principal
- **Redis**: Cache y sesiones
- **MinIO**: Almacenamiento de objetos

### 🎭 Frontend
- **Backstage**: Portal principal
- **Veritas**: Testing y calidad

## APIs Disponibles

### Health Check
```
GET /health
```

### Documentación
```
GET /docs/list - Lista todos los documentos
GET /docs/content/{path} - Obtiene contenido de un documento
GET /docs/search?q={query} - Busca en la documentación
```
""",
            "services/dev-core.md": """# Dev-Core Services

## Repository Manager (Puerto 8860)
Gestión centralizada de repositorios Git.

### Endpoints principales:
- `GET /repositories` - Lista repositorios
- `POST /repositories` - Crear repositorio
- `GET /repositories/{id}` - Obtener repositorio

## Task Manager (Puerto 8861)
Gestión de tareas y procesos.

### Endpoints principales:
- `GET /tasks` - Lista tareas
- `POST /tasks` - Crear tarea
- `GET /tasks/{id}/status` - Estado de tarea

## Log Manager (Puerto 8862)
Centralización y análisis de logs.

### Endpoints principales:
- `GET /logs` - Obtener logs
- `POST /logs/search` - Buscar en logs
- `GET /logs/stats` - Estadísticas de logs
""",
            "infrastructure/database.md": """# Database Configuration

## PostgreSQL (Puerto 5434)
Base de datos principal del sistema.

### Configuración:
- **Host**: localhost
- **Puerto**: 5434
- **Usuario**: postgres
- **Base de datos**: postgres

### Esquemas por servicio:
- `backstage` - Datos de Backstage
- `openai_service` - Datos del servicio OpenAI
- `veritas` - Datos de testing y calidad

## Redis (Puerto 6380)
Cache y gestión de sesiones.

### Configuración:
- **Host**: localhost
- **Puerto**: 6380
- **Password**: redis_admin_2024

### Bases de datos por servicio:
- DB 0: Backstage
- DB 1: OpenAI Service
- DB 2: Frontend App
- DB 3: Framework Docs
"""
        }
        
        for file_path, content in default_docs.items():
            full_path = self.docs_base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if not full_path.exists():
                full_path.write_text(content)
    
    def list_documents(self) -> List[Dict]:
        """Lista todos los documentos disponibles"""
        docs = []
        for md_file in self.docs_base_path.rglob("*.md"):
            relative_path = md_file.relative_to(self.docs_base_path)
            docs.append({
                "path": str(relative_path),
                "name": md_file.stem,
                "size": md_file.stat().st_size,
                "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
            })
        return docs
    
    def get_document_content(self, doc_path: str) -> Dict:
        """Obtiene el contenido de un documento"""
        try:
            full_path = self.docs_base_path / doc_path
            if not full_path.exists() or not full_path.is_file():
                return None
            
            content = full_path.read_text(encoding='utf-8')
            
            if doc_path.endswith('.md'):
                html_content = markdown.markdown(content, extensions=['codehilite', 'toc'])
                return {
                    "type": "markdown",
                    "raw_content": content,
                    "html_content": html_content,
                    "path": doc_path
                }
            else:
                return {
                    "type": "text",
                    "raw_content": content,
                    "html_content": f"<pre>{content}</pre>",
                    "path": doc_path
                }
        except Exception as e:
            logger.error(f"Error reading document {doc_path}: {e}")
            return None
    
    def search_documents(self, query: str) -> List[Dict]:
        """Busca en todos los documentos"""
        results = []
        query_lower = query.lower()
        
        for md_file in self.docs_base_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                if query_lower in content.lower():
                    # Encontrar contexto alrededor de la coincidencia
                    lines = content.split('\n')
                    matching_lines = []
                    
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            context = '\n'.join(lines[start:end])
                            matching_lines.append({
                                "line_number": i + 1,
                                "context": context
                            })
                    
                    relative_path = md_file.relative_to(self.docs_base_path)
                    results.append({
                        "path": str(relative_path),
                        "name": md_file.stem,
                        "matches": matching_lines[:3]  # Limitar a 3 coincidencias por archivo
                    })
            except Exception as e:
                logger.error(f"Error searching in {md_file}: {e}")
        
        return results

# Instancia global del manager
docs_manager = DocsManager()

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "docs-manager"}

@app.get("/docs/list")
async def list_documents():
    """Lista todos los documentos disponibles"""
    docs = docs_manager.list_documents()
    return {"documents": docs, "count": len(docs)}

@app.get("/docs/content/{path:path}")
async def get_document_content(path: str):
    """Obtiene el contenido de un documento específico"""
    content = docs_manager.get_document_content(path)
    if content is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return content

@app.get("/docs/search")
async def search_documents(q: str = Query(..., description="Query to search for")):
    """Busca en todos los documentos"""
    if len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    results = docs_manager.search_documents(q)
    return {"query": q, "results": results, "count": len(results)}

@app.get("/", response_class=HTMLResponse)
async def docs_portal():
    """Portal principal de documentación"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>IA-Ops Documentation Portal</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
            .docs-list { margin-top: 20px; }
            .doc-item { padding: 10px; border-bottom: 1px solid #eee; }
            .search-box { margin: 20px 0; }
            .search-box input { padding: 10px; width: 300px; }
            .search-box button { padding: 10px 20px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 IA-Ops Documentation Portal</h1>
            <p>Documentación integrada en Dev-Core</p>
        </div>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Buscar en documentación...">
            <button onclick="searchDocs()">Buscar</button>
        </div>
        
        <div class="docs-list" id="docsList">
            <h2>📚 Documentos Disponibles</h2>
            <p>Cargando documentos...</p>
        </div>
        
        <script>
            async function loadDocs() {
                try {
                    const response = await fetch('/docs/list');
                    const data = await response.json();
                    const docsList = document.getElementById('docsList');
                    
                    let html = '<h2>📚 Documentos Disponibles</h2>';
                    data.documents.forEach(doc => {
                        html += `
                            <div class="doc-item">
                                <strong>${doc.name}</strong> - ${doc.path}
                                <br><small>Modificado: ${new Date(doc.modified).toLocaleString()}</small>
                                <br><a href="/docs/content/${doc.path}" target="_blank">Ver contenido</a>
                            </div>
                        `;
                    });
                    
                    docsList.innerHTML = html;
                } catch (error) {
                    console.error('Error loading docs:', error);
                }
            }
            
            async function searchDocs() {
                const query = document.getElementById('searchInput').value;
                if (query.length < 2) return;
                
                try {
                    const response = await fetch(`/docs/search?q=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    const docsList = document.getElementById('docsList');
                    
                    let html = `<h2>🔍 Resultados de búsqueda para "${query}"</h2>`;
                    if (data.results.length === 0) {
                        html += '<p>No se encontraron resultados.</p>';
                    } else {
                        data.results.forEach(result => {
                            html += `
                                <div class="doc-item">
                                    <strong>${result.name}</strong> - ${result.path}
                                    <br><a href="/docs/content/${result.path}" target="_blank">Ver documento</a>
                                </div>
                            `;
                        });
                    }
                    
                    docsList.innerHTML = html;
                } catch (error) {
                    console.error('Error searching docs:', error);
                }
            }
            
            // Cargar documentos al inicio
            loadDocs();
            
            // Buscar con Enter
            document.getElementById('searchInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchDocs();
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8845)
