#!/usr/bin/env python3
"""
Métodos de prueba para IA-Ops Dev Core Services
Integrado con PostgreSQL, Redis y MinIO
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class IAOpsTestClient:
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.services = {
            'repository': 8860,
            'task': 8861,
            'log': 8862,
            'datasync': 8863,
            'github_runner': 8864,
            'techdocs': 8865
        }
    
    def _request(self, method: str, service: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Método base para hacer requests"""
        port = self.services[service]
        url = f"{self.base_url}:{port}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data)
            elif method == 'PUT':
                response = requests.put(url, json=data)
            elif method == 'DELETE':
                response = requests.delete(url)
            
            return {
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'success': response.status_code < 400
            }
        except Exception as e:
            return {
                'status_code': 500,
                'data': {'error': str(e)},
                'success': False
            }

    # ========== REPOSITORY MANAGER TESTS ==========
    
    def test_repository_health(self) -> Dict[str, Any]:
        """Test health check del Repository Manager"""
        return self._request('GET', 'repository', '/health')
    
    def test_get_repositories(self) -> Dict[str, Any]:
        """Test obtener lista de repositorios"""
        return self._request('GET', 'repository', '/repositories')
    
    def test_create_repository(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test crear repositorio"""
        return self._request('POST', 'repository', '/repositories', repo_data)
    
    def test_get_repository(self, repo_id: int) -> Dict[str, Any]:
        """Test obtener repositorio por ID"""
        return self._request('GET', 'repository', f'/repositories/{repo_id}')
    
    def test_update_repository(self, repo_id: int, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test actualizar repositorio"""
        return self._request('PUT', 'repository', f'/repositories/{repo_id}', repo_data)
    
    def test_sync_repository(self, repo_id: int) -> Dict[str, Any]:
        """Test sincronizar repositorio"""
        return self._request('POST', 'repository', f'/repositories/{repo_id}/sync')
    
    def test_delete_repository(self, repo_id: int) -> Dict[str, Any]:
        """Test eliminar repositorio"""
        return self._request('DELETE', 'repository', f'/repositories/{repo_id}')

    # ========== TASK MANAGER TESTS ==========
    
    def test_task_health(self) -> Dict[str, Any]:
        """Test health check del Task Manager"""
        return self._request('GET', 'task', '/health')
    
    def test_get_tasks(self) -> Dict[str, Any]:
        """Test obtener lista de tareas"""
        return self._request('GET', 'task', '/tasks')
    
    def test_create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test crear tarea"""
        return self._request('POST', 'task', '/tasks', task_data)
    
    def test_get_task(self, task_id: int) -> Dict[str, Any]:
        """Test obtener tarea por ID"""
        return self._request('GET', 'task', f'/tasks/{task_id}')
    
    def test_execute_task(self, task_id: int) -> Dict[str, Any]:
        """Test ejecutar tarea"""
        return self._request('POST', 'task', f'/tasks/{task_id}/execute')
    
    def test_get_task_logs(self, task_id: int) -> Dict[str, Any]:
        """Test obtener logs de tarea"""
        return self._request('GET', 'task', f'/tasks/{task_id}/logs')

    # ========== LOG MANAGER TESTS ==========
    
    def test_log_health(self) -> Dict[str, Any]:
        """Test health check del Log Manager"""
        return self._request('GET', 'log', '/health')
    
    def test_get_logs(self) -> Dict[str, Any]:
        """Test obtener logs"""
        return self._request('GET', 'log', '/logs')
    
    def test_search_logs(self, query: str) -> Dict[str, Any]:
        """Test buscar logs"""
        return self._request('GET', 'log', f'/logs/search?q={query}')
    
    def test_get_logs_by_service(self, service: str) -> Dict[str, Any]:
        """Test obtener logs por servicio"""
        return self._request('GET', 'log', f'/logs/{service}')
    
    def test_create_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test crear entrada de log"""
        return self._request('POST', 'log', '/logs', log_data)

    # ========== DATASYNC MANAGER TESTS ==========
    
    def test_datasync_health(self) -> Dict[str, Any]:
        """Test health check del DataSync Manager"""
        return self._request('GET', 'datasync', '/health')
    
    def test_get_sync_jobs(self) -> Dict[str, Any]:
        """Test obtener trabajos de sincronización"""
        return self._request('GET', 'datasync', '/sync-jobs')
    
    def test_create_sync_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test crear trabajo de sincronización"""
        return self._request('POST', 'datasync', '/sync-jobs', job_data)
    
    def test_execute_sync(self, job_id: int) -> Dict[str, Any]:
        """Test ejecutar sincronización"""
        return self._request('POST', 'datasync', f'/sync-jobs/{job_id}/execute')
    
    def test_get_backups(self) -> Dict[str, Any]:
        """Test obtener backups"""
        return self._request('GET', 'datasync', '/backups')
    
    def test_create_backup(self, backup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test crear backup"""
        return self._request('POST', 'datasync', '/backups', backup_data)

    # ========== GITHUB RUNNER TESTS ==========
    
    def test_github_runner_health(self) -> Dict[str, Any]:
        """Test health check del GitHub Runner Manager"""
        return self._request('GET', 'github_runner', '/health')
    
    def test_get_runners(self) -> Dict[str, Any]:
        """Test obtener runners"""
        return self._request('GET', 'github_runner', '/runners')
    
    def test_create_runner(self, runner_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test crear runner"""
        return self._request('POST', 'github_runner', '/runners', runner_data)
    
    def test_get_workflows(self) -> Dict[str, Any]:
        """Test obtener workflows"""
        return self._request('GET', 'github_runner', '/workflows')
    
    def test_trigger_workflow(self, workflow_id: int) -> Dict[str, Any]:
        """Test disparar workflow"""
        return self._request('POST', 'github_runner', f'/workflows/{workflow_id}/trigger')

    # ========== TECHDOCS BUILDER TESTS ==========
    
    def test_techdocs_health(self) -> Dict[str, Any]:
        """Test health check del TechDocs Builder"""
        return self._request('GET', 'techdocs', '/health')
    
    def test_get_docs(self) -> Dict[str, Any]:
        """Test obtener sitios de documentación"""
        return self._request('GET', 'techdocs', '/docs')
    
    def test_build_docs(self, build_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test construir documentación"""
        return self._request('POST', 'techdocs', '/docs/build', build_data)
    
    def test_rebuild_docs(self, doc_id: int) -> Dict[str, Any]:
        """Test reconstruir documentación"""
        return self._request('POST', 'techdocs', f'/docs/{doc_id}/rebuild')

    # ========== INTEGRATION TESTS ==========
    
    def test_full_workflow(self) -> Dict[str, Any]:
        """Test completo de workflow integrado"""
        results = {}
        
        # 1. Crear repositorio
        repo_data = {
            "name": "test-repo",
            "url": "https://github.com/test/repo.git",
            "branch": "main",
            "description": "Test repository"
        }
        results['create_repo'] = self.test_create_repository(repo_data)
        
        if results['create_repo']['success']:
            repo_id = results['create_repo']['data'].get('data', {}).get('id')
            
            # 2. Crear tarea de build
            task_data = {
                "name": "build-test",
                "type": "build",
                "repository_id": repo_id,
                "command": "npm install && npm run build"
            }
            results['create_task'] = self.test_create_task(task_data)
            
            # 3. Crear trabajo de sincronización
            sync_data = {
                "name": "sync-test",
                "source": f"repo-{repo_id}",
                "destination": "minio://backup/"
            }
            results['create_sync'] = self.test_create_sync_job(sync_data)
        
        return results
    
    def test_all_health_checks(self) -> Dict[str, Any]:
        """Test de health check de todos los servicios"""
        return {
            'repository': self.test_repository_health(),
            'task': self.test_task_health(),
            'log': self.test_log_health(),
            'datasync': self.test_datasync_health(),
            'github_runner': self.test_github_runner_health(),
            'techdocs': self.test_techdocs_health()
        }

# ========== SAMPLE DATA FOR TESTING ==========

SAMPLE_REPOSITORY = {
    "name": "ia-ops-sample",
    "url": "https://github.com/giovanemere/ia-ops-sample.git",
    "branch": "main",
    "description": "Sample repository for testing"
}

SAMPLE_TASK = {
    "name": "build-sample",
    "type": "build",
    "repository_id": 1,
    "command": "echo 'Building project...' && sleep 5 && echo 'Build completed'",
    "environment": {
        "NODE_ENV": "production",
        "BUILD_TARGET": "dist"
    }
}

SAMPLE_LOG = {
    "service": "test-service",
    "level": "info",
    "message": "Test log message",
    "metadata": {
        "user": "test-user",
        "action": "test-action"
    }
}

SAMPLE_SYNC_JOB = {
    "name": "backup-repos",
    "source": "postgresql://repos",
    "destination": "minio://backups/repos"
}

SAMPLE_RUNNER = {
    "name": "test-runner",
    "labels": ["linux", "docker"],
    "repository": "giovanemere/ia-ops"
}

SAMPLE_DOC_BUILD = {
    "repository_id": 1,
    "source_path": "docs/",
    "output_path": "site/"
}

if __name__ == "__main__":
    # Ejemplo de uso
    client = IAOpsTestClient()
    
    print("🧪 Ejecutando pruebas de IA-Ops Dev Core Services...")
    
    # Test health checks
    health_results = client.test_all_health_checks()
    print("\n📊 Health Checks:")
    for service, result in health_results.items():
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {service}: {result['status_code']}")
    
    # Test workflow completo
    print("\n🔄 Test de workflow completo:")
    workflow_result = client.test_full_workflow()
    for step, result in workflow_result.items():
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {step}: {result['status_code']}")
