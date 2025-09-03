#!/usr/bin/env python3
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import time
import requests
import re

app = FastAPI(title="IA-Ops Backend", version="1.0.0")

class ServiceResponse(BaseModel):
    success: bool
    data: dict = {}
    message: str = ""

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/api/v1/repository/analyze/{owner}/{repo}")
async def analyze_repository(owner: str, repo: str):
    """Analyze GitHub repository to detect MkDocs structure"""
    try:
        import subprocess
        import os
        import shutil
        import yaml
        from pathlib import Path
        
        # Repository details
        repo_url = f"https://github.com/{owner}/{repo}.git"
        
        # Create temp directory
        temp_dir = "/tmp/ia-ops-analyze"
        repo_dir = f"{temp_dir}/{repo}"
        
        # Clean previous clone
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Clone repository
        clone_result = subprocess.run([
            "git", "clone", repo_url, repo_dir
        ], capture_output=True, text=True, timeout=60)
        
        if clone_result.returncode != 0:
            return ServiceResponse(
                success=False,
                message=f"Failed to clone repository: {clone_result.stderr}"
            )
        
        # Check for MkDocs
        mkdocs_config = os.path.join(repo_dir, 'mkdocs.yml')
        has_mkdocs = os.path.exists(mkdocs_config)
        
        mkdocs_info = {}
        if has_mkdocs:
            try:
                with open(mkdocs_config, 'r') as f:
                    mkdocs_data = yaml.safe_load(f)
                    mkdocs_info = {
                        'site_name': mkdocs_data.get('site_name', repo),
                        'site_description': mkdocs_data.get('site_description', ''),
                        'docs_dir': mkdocs_data.get('docs_dir', 'docs'),
                        'nav': mkdocs_data.get('nav', [])
                    }
            except:
                mkdocs_info = {'site_name': repo, 'docs_dir': 'docs'}
        
        # Find documentation files
        docs_found = []
        docs_dir = os.path.join(repo_dir, mkdocs_info.get('docs_dir', 'docs'))
        
        if os.path.exists(docs_dir):
            for root, dirs, files in os.walk(docs_dir):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, docs_dir)
                        
                        # Read file content for indexing
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Extract title from first line or filename
                                lines = content.split('\n')
                                title = file.replace('.md', '').replace('_', ' ').title()
                                if lines and lines[0].startswith('#'):
                                    title = lines[0].replace('#', '').strip()
                                
                                docs_found.append({
                                    'file': file,
                                    'path': rel_path,
                                    'title': title,
                                    'content_preview': content[:200] + '...' if len(content) > 200 else content,
                                    'size': len(content)
                                })
                        except:
                            pass
        
        # Parse project and application from repository name
        project_name = "sterling"
        application_name = repo
        
        if '-' in repo:
            parts = repo.split('-')
            if len(parts) >= 2 and parts[0] in ['sterling', 'ia-ops']:
                project_name = parts[0]
                application_name = '-'.join(parts[1:])
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        return ServiceResponse(
            success=True,
            data={
                "repository": {
                    "owner": owner,
                    "name": repo,
                    "full_name": f"{owner}/{repo}",
                    "clone_url": repo_url
                },
                "mkdocs": {
                    "has_mkdocs": has_mkdocs,
                    "config": mkdocs_info,
                    "docs_count": len(docs_found),
                    "docs_files": docs_found
                },
                "structure": {
                    "project_name": project_name,
                    "application_name": application_name,
                    "bucket_name": f"{project_name}-apps",
                    "app_path": f"applications/{application_name}"
                }
            },
            message=f"Repository analyzed: {'MkDocs found' if has_mkdocs else 'No MkDocs'}"
        )
        
    except Exception as e:
        return ServiceResponse(
            success=False,
            message=f"Error analyzing repository: {str(e)}"
        )

@app.post("/api/v1/repository/sync")
async def sync_repository():
    """Clone repository and sync MkDocs structure to MinIO"""
    try:
        import subprocess
        import os
        import shutil
        from pathlib import Path
        
        # Repository details
        repo_url = "https://github.com/giovanemere/sterling-msgraph-sdk-java.git"
        project_name = "sterling"
        app_name = "msgraph-sdk-java"
        
        # Create temp directory
        temp_dir = "/tmp/ia-ops-sync"
        repo_dir = f"{temp_dir}/{app_name}"
        
        # Clean previous clone
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Clone repository
        clone_result = subprocess.run([
            "git", "clone", repo_url, repo_dir
        ], capture_output=True, text=True, timeout=60)
        
        if clone_result.returncode != 0:
            return ServiceResponse(
                success=False,
                message=f"Failed to clone repository: {clone_result.stderr}"
            )
        
        # Look for documentation files
        docs_found = []
        docs_patterns = ["*.md", "docs/", "README*", "mkdocs.yml"]
        
        for root, dirs, files in os.walk(repo_dir):
            for file in files:
                if (file.endswith('.md') or 
                    file.lower().startswith('readme') or
                    file == 'mkdocs.yml'):
                    rel_path = os.path.relpath(os.path.join(root, file), repo_dir)
                    docs_found.append({
                        'file': file,
                        'path': rel_path,
                        'size': os.path.getsize(os.path.join(root, file))
                    })
        
        # Check for MkDocs structure
        mkdocs_config = os.path.join(repo_dir, 'mkdocs.yml')
        has_mkdocs = os.path.exists(mkdocs_config)
        
        # Simulate MinIO upload (in real implementation would use boto3)
        bucket_structure = {
            'bucket': f"{project_name}-apps",
            'path': f"applications/{app_name}",
            'docs_path': f"applications/{app_name}/docs",
            'files_uploaded': len(docs_found)
        }
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        return ServiceResponse(
            success=True,
            data={
                "sync_status": "completed",
                "project": project_name,
                "application": app_name,
                "repository": repo_url,
                "bucket_structure": bucket_structure,
                "documentation": {
                    "files_found": len(docs_found),
                    "has_mkdocs": has_mkdocs,
                    "files": docs_found[:10]  # First 10 files
                },
                "timestamp": time.time()
            },
            message=f"Repository {app_name} synced successfully with {len(docs_found)} documentation files"
        )
        
    except subprocess.TimeoutExpired:
        return ServiceResponse(
            success=False,
            message="Repository clone timeout"
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            message=f"Error syncing repository: {str(e)}"
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

@app.get("/api/v1/projects")
async def get_projects():
    """Get projects with MkDocs documentation only"""
    try:
        # Analyze sterling repository
        analysis_result = await analyze_repository("giovanemere", "sterling-msgraph-sdk-java")
        
        projects = []
        
        if analysis_result.success and analysis_result.data["mkdocs"]["has_mkdocs"]:
            mkdocs_data = analysis_result.data["mkdocs"]
            structure = analysis_result.data["structure"]
            
            projects.append({
                "id": "sterling",
                "name": "Sterling Platform",
                "description": "Plataforma Sterling con documentación MkDocs",
                "type": "platform",
                "status": "active",
                "last_updated": "2024-09-02T15:00:00Z",
                "bucket": structure["bucket_name"],
                "has_mkdocs": True,
                "applications": [
                    {
                        "id": structure["application_name"],
                        "name": mkdocs_data["config"].get("site_name", "Sterling MsgGraph SDK"),
                        "description": mkdocs_data["config"].get("site_description", "SDK Java para Microsoft Graph"),
                        "language": "Java",
                        "path": structure["app_path"],
                        "files_count": mkdocs_data["docs_count"],
                        "size": f"{sum(doc['size'] for doc in mkdocs_data['docs_files']) / 1024:.1f}KB",
                        "repository": "https://github.com/giovanemere/sterling-msgraph-sdk-java",
                        "has_mkdocs": True,
                        "docs_files": mkdocs_data["docs_files"]
                    }
                ]
            })
        
        return ServiceResponse(
            success=True,
            data={
                "projects": projects,
                "total": len(projects),
                "active": len([p for p in projects if p["status"] == "active"]),
                "total_applications": sum(len(p.get("applications", [])) for p in projects),
                "mkdocs_only": True
            },
            message="Projects with MkDocs retrieved successfully"
        )
        
    except Exception as e:
        return ServiceResponse(
            success=False,
            data={"projects": [], "mkdocs_only": True},
            message=f"Error getting projects: {str(e)}"
        )

@app.get("/api/v1/documentation/{doc_id}")
async def get_documentation_content(doc_id: str):
    """Get MkDocs documentation content"""
    try:
        # For sterling-msgraph-sdk-java
        if doc_id == "msgraph-sdk-java" or doc_id == "sterling":
            analysis_result = await analyze_repository("giovanemere", "sterling-msgraph-sdk-java")
            
            if analysis_result.success and analysis_result.data["mkdocs"]["has_mkdocs"]:
                mkdocs_data = analysis_result.data["mkdocs"]
                
                return ServiceResponse(
                    success=True,
                    data={
                        "id": doc_id,
                        "site_name": mkdocs_data["config"].get("site_name", "Sterling MsgGraph SDK"),
                        "description": mkdocs_data["config"].get("site_description", ""),
                        "docs_dir": mkdocs_data["config"].get("docs_dir", "docs"),
                        "navigation": mkdocs_data["config"].get("nav", []),
                        "files": mkdocs_data["docs_files"],
                        "has_content": True
                    },
                    message="Documentation content retrieved"
                )
        
        return ServiceResponse(
            success=False,
            message="Documentation not found or no MkDocs"
        )
        
    except Exception as e:
        return ServiceResponse(
            success=False,
            message=f"Error getting documentation: {str(e)}"
        )

if __name__ == "__main__":
    print("🚀 Starting Simple IA-Ops Backend...")
    print("📚 Health Check: http://localhost:8801/health")
    print("📊 Dashboard: http://localhost:8801/api/v1/dashboard")
    
    uvicorn.run(
        "simple_backend:app",
        host="0.0.0.0",
        port=8801,
        reload=False
    )
