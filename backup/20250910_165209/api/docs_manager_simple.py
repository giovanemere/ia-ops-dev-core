#!/usr/bin/env python3
"""
Simple Docs Manager - Servicio de documentación ultra-simplificado
Sin dependencias externas, solo FastAPI
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Docs Manager", version="1.0.0")

class SimpleDocsManager:
    def __init__(self):
        self.docs_base_path = Path("/app/docs")
        self.docs_base_path.mkdir(exist_ok=True)
        self.setup_default_docs()
    
    def setup_default_docs(self):
        """Setup default documentation structure"""
        default_docs = {
            "README.md": """# IA-Ops Documentation Portal

## Servicios Disponibles

### Dev-Core Services (Puerto 8801)
- Repository Manager (8860)
- Task Manager (8861) 
- Log Manager (8862)
- DataSync Manager (8863)
- GitHub Runner Manager (8864)
- Docs Manager (8845) - Este servicio

### Infrastructure
- PostgreSQL (5434)
- Redis (6380)
- MinIO (9899)

### Frontend
- Backstage (3000)
- Veritas (8869)

## Estado de Migración

✅ COMPLETADO: Docs Manager migrado de ia-ops-docs a ia-ops-dev-core
- Servicio independiente sin dependencia de MinIO
- Documentación local en sistema de archivos
- API REST para gestión de documentos
- Portal web integrado

## APIs Disponibles

GET /health - Health check
GET /docs/list - Lista documentos
GET /docs/content/{path} - Contenido de documento
GET /docs/search?q={query} - Búsqueda en documentos
GET / - Portal web
""",
            "migration-status.md": """# Estado de Migración ia-ops-docs → ia-ops-dev-core

## ✅ COMPLETADO

### Docs Manager (Puerto 8845)
- ✅ Migrado de ia-ops-docs a ia-ops-dev-core
- ✅ Eliminada dependencia de MinIO
- ✅ Sistema de archivos local para documentos
- ✅ API REST completa
- ✅ Portal web integrado
- ✅ Búsqueda en documentos
- ✅ Health checks configurados

## 🔄 PENDIENTE

### TechDocs Builder
- ⏳ Migrar techdocs_portal.py
- ⏳ Integrar con sistema de build de MkDocs
- ⏳ Configurar pipeline de documentación

### Amazon Q Integration
- ⏳ Evaluar migración de funcionalidades de Amazon Q
- ⏳ Integrar con búsqueda local

## 📋 BENEFICIOS DE LA MIGRACIÓN

1. **Simplicidad**: Sin dependencias externas complejas
2. **Integración**: Parte del ecosistema Dev-Core
3. **Mantenimiento**: Gestión centralizada
4. **Performance**: Acceso directo a archivos locales
5. **Escalabilidad**: Fácil extensión con nuevas funcionalidades
""",
            "dev-core-services.md": """# Dev-Core Services Overview

## Arquitectura de Microservicios

### Repository Manager (8860)
Gestión de repositorios Git y control de versiones.

Endpoints:
- GET /repositories - Lista repositorios
- POST /repositories - Crear repositorio
- GET /repositories/{id} - Detalles de repositorio

### Task Manager (8861)
Gestión de tareas asíncronas y procesos.

Endpoints:
- GET /tasks - Lista tareas
- POST /tasks - Crear tarea
- GET /tasks/{id}/status - Estado de tarea

### Log Manager (8862)
Centralización y análisis de logs del sistema.

Endpoints:
- GET /logs - Obtener logs
- POST /logs/search - Buscar en logs
- GET /logs/stats - Estadísticas

### DataSync Manager (8863)
Sincronización de datos entre servicios.

Endpoints:
- GET /sync/status - Estado de sincronización
- POST /sync/trigger - Disparar sincronización
- GET /sync/history - Historial de sincronizaciones

### GitHub Runner Manager (8864)
Gestión de runners de GitHub Actions.

Endpoints:
- GET /runners - Lista runners
- POST /runners/register - Registrar runner
- GET /runners/{id}/status - Estado de runner

### Docs Manager (8845)
Gestión de documentación (este servicio).

Endpoints:
- GET /docs/list - Lista documentos
- GET /docs/content/{path} - Contenido
- GET /docs/search - Búsqueda
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
            
            # Conversión simple de Markdown a HTML
            html_content = self.simple_markdown_to_html(content)
            
            return {
                "type": "markdown",
                "raw_content": content,
                "html_content": html_content,
                "path": doc_path
            }
        except Exception as e:
            logger.error(f"Error reading document {doc_path}: {e}")
            return None
    
    def simple_markdown_to_html(self, content: str) -> str:
        """Conversión simple de Markdown a HTML"""
        html = content
        
        # Headers
        html = re.sub(r'^### (.*$)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*$)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*$)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Code blocks
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Bold and italic
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Lists
        html = re.sub(r'^- (.*$)', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        
        # Line breaks
        html = html.replace('\n', '<br>\n')
        
        return html
    
    def search_documents(self, query: str) -> List[Dict]:
        """Busca en todos los documentos"""
        results = []
        query_lower = query.lower()
        
        for md_file in self.docs_base_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                if query_lower in content.lower():
                    lines = content.split('\n')
                    matching_lines = []
                    
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            start = max(0, i - 1)
                            end = min(len(lines), i + 2)
                            context = '\n'.join(lines[start:end])
                            matching_lines.append({
                                "line_number": i + 1,
                                "context": context
                            })
                    
                    relative_path = md_file.relative_to(self.docs_base_path)
                    results.append({
                        "path": str(relative_path),
                        "name": md_file.stem,
                        "matches": matching_lines[:2]
                    })
            except Exception as e:
                logger.error(f"Error searching in {md_file}: {e}")
        
        return results

# Instancia global del manager
docs_manager = SimpleDocsManager()

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "simple-docs-manager", "version": "1.0.0"}

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
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>IA-Ops Docs Manager</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
            .status { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .docs-list { margin-top: 20px; }
            .doc-item { padding: 15px; border-bottom: 1px solid #eee; transition: background 0.3s; }
            .doc-item:hover { background: #f8f9fa; }
            .search-box { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .search-box input { padding: 12px; width: 300px; border: 1px solid #ddd; border-radius: 5px; }
            .search-box button { padding: 12px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px; }
            .search-box button:hover { background: #0056b3; }
            .api-info { background: #e7f3ff; border: 1px solid #b3d7ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 IA-Ops Documentation Manager</h1>
                <p>Servicio de documentación migrado a Dev-Core</p>
            </div>
            
            <div class="status">
                ✅ <strong>Migración Completada:</strong> Servicio de documentación migrado exitosamente de ia-ops-docs a ia-ops-dev-core
            </div>
            
            <div class="api-info">
                <h3>📡 API Endpoints Disponibles</h3>
                <ul>
                    <li><code>GET /health</code> - Health check del servicio</li>
                    <li><code>GET /docs/list</code> - Lista todos los documentos</li>
                    <li><code>GET /docs/content/{path}</code> - Obtiene contenido de un documento</li>
                    <li><code>GET /docs/search?q={query}</code> - Busca en la documentación</li>
                </ul>
            </div>
            
            <div class="search-box">
                <h3>🔍 Buscar en Documentación</h3>
                <input type="text" id="searchInput" placeholder="Buscar en documentación...">
                <button onclick="searchDocs()">Buscar</button>
                <button onclick="loadDocs()" style="background: #28a745;">Ver Todos</button>
            </div>
            
            <div class="docs-list" id="docsList">
                <h2>📚 Documentos Disponibles</h2>
                <p>Cargando documentos...</p>
            </div>
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
                                <h4>${doc.name}</h4>
                                <p><strong>Ruta:</strong> ${doc.path}</p>
                                <p><strong>Tamaño:</strong> ${doc.size} bytes | <strong>Modificado:</strong> ${new Date(doc.modified).toLocaleString()}</p>
                                <a href="/docs/content/${doc.path}" target="_blank" style="color: #007bff; text-decoration: none;">📖 Ver contenido</a>
                            </div>
                        `;
                    });
                    
                    docsList.innerHTML = html;
                } catch (error) {
                    console.error('Error loading docs:', error);
                    document.getElementById('docsList').innerHTML = '<p style="color: red;">Error cargando documentos</p>';
                }
            }
            
            async function searchDocs() {
                const query = document.getElementById('searchInput').value;
                if (query.length < 2) {
                    alert('La búsqueda debe tener al menos 2 caracteres');
                    return;
                }
                
                try {
                    const response = await fetch(`/docs/search?q=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    const docsList = document.getElementById('docsList');
                    
                    let html = `<h2>🔍 Resultados de búsqueda para "${query}" (${data.count} resultados)</h2>`;
                    if (data.results.length === 0) {
                        html += '<p>No se encontraron resultados.</p>';
                    } else {
                        data.results.forEach(result => {
                            html += `
                                <div class="doc-item">
                                    <h4>${result.name}</h4>
                                    <p><strong>Archivo:</strong> ${result.path}</p>
                                    <a href="/docs/content/${result.path}" target="_blank" style="color: #007bff; text-decoration: none;">📖 Ver documento completo</a>
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8845)
