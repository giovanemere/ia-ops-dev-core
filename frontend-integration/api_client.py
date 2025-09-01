#!/usr/bin/env python3
"""
API Client for IA-Ops Frontend Integration
To be copied to ia-ops-docs/web-interface/
"""

import requests
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class IAOpsApiClient:
    """Client for integrating with IA-Ops Dev Core backend services"""
    
    def __init__(self):
        self.base_urls = {
            'swagger_portal': os.getenv('SWAGGER_PORTAL_URL', 'http://localhost:8870'),
            'repository': os.getenv('REPOSITORY_MANAGER_URL', 'http://localhost:8860'),
            'task': os.getenv('TASK_MANAGER_URL', 'http://localhost:8861'),
            'log': os.getenv('LOG_MANAGER_URL', 'http://localhost:8862'),
            'datasync': os.getenv('DATASYNC_MANAGER_URL', 'http://localhost:8863'),
            'github_runner': os.getenv('GITHUB_RUNNER_MANAGER_URL', 'http://localhost:8864'),
            'techdocs': os.getenv('TECHDOCS_BUILDER_URL', 'http://localhost:8865')
        }
        self.timeout = 10
    
    def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'error': None
            }
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout', 'status_code': 408}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection error', 'status_code': 503}
        except Exception as e:
            return {'success': False, 'error': str(e), 'status_code': 500}
    
    # System Status
    def get_services_status(self) -> Dict[str, Any]:
        """Get status of all backend services"""
        result = self._make_request('GET', f"{self.base_urls['swagger_portal']}/api/status")
        if result['success']:
            return result['data']
        return {'error': result['error'], 'services_online': 0, 'total_services': 6}
    
    def health_check_all(self) -> Dict[str, Any]:
        """Check health of all services"""
        health_status = {}
        for service, url in self.base_urls.items():
            if service == 'swagger_portal':
                endpoint = f"{url}/api/status"
            else:
                endpoint = f"{url}/health"
            
            result = self._make_request('GET', endpoint)
            health_status[service] = {
                'status': 'online' if result['success'] else 'offline',
                'response_time': result.get('response_time', 0),
                'error': result.get('error')
            }
        
        return health_status
    
    # Repository Management
    def get_repositories(self) -> Dict[str, Any]:
        """Get all repositories"""
        return self._make_request('GET', f"{self.base_urls['repository']}/api/v1/repositories")
    
    def get_repository(self, repo_id: int) -> Dict[str, Any]:
        """Get repository by ID"""
        return self._make_request('GET', f"{self.base_urls['repository']}/api/v1/repositories/{repo_id}")
    
    def create_repository(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new repository"""
        return self._make_request('POST', f"{self.base_urls['repository']}/api/v1/repositories", json=data)
    
    def update_repository(self, repo_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update repository"""
        return self._make_request('PUT', f"{self.base_urls['repository']}/api/v1/repositories/{repo_id}", json=data)
    
    def delete_repository(self, repo_id: int) -> Dict[str, Any]:
        """Delete repository"""
        return self._make_request('DELETE', f"{self.base_urls['repository']}/api/v1/repositories/{repo_id}")
    
    def sync_repository(self, repo_id: int) -> Dict[str, Any]:
        """Sync repository with remote"""
        return self._make_request('POST', f"{self.base_urls['repository']}/api/v1/repositories/{repo_id}/sync")
    
    # Task Management
    def get_tasks(self) -> Dict[str, Any]:
        """Get all tasks"""
        return self._make_request('GET', f"{self.base_urls['task']}/api/v1/tasks")
    
    def get_task(self, task_id: int) -> Dict[str, Any]:
        """Get task by ID"""
        return self._make_request('GET', f"{self.base_urls['task']}/api/v1/tasks/{task_id}")
    
    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new task"""
        return self._make_request('POST', f"{self.base_urls['task']}/api/v1/tasks", json=data)
    
    def execute_task(self, task_id: int) -> Dict[str, Any]:
        """Execute task"""
        return self._make_request('POST', f"{self.base_urls['task']}/api/v1/tasks/{task_id}/execute")
    
    def get_task_logs(self, task_id: int) -> Dict[str, Any]:
        """Get task logs"""
        return self._make_request('GET', f"{self.base_urls['task']}/api/v1/tasks/{task_id}/logs")
    
    # Log Management
    def get_logs(self, service: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Get logs"""
        url = f"{self.base_urls['log']}/api/v1/logs"
        if service:
            url += f"/{service}"
        
        params = {'limit': limit}
        return self._make_request('GET', url, params=params)
    
    def search_logs(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Search logs"""
        params = {'q': query, 'limit': limit}
        return self._make_request('GET', f"{self.base_urls['log']}/api/v1/logs/search", params=params)
    
    def create_log(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create log entry"""
        return self._make_request('POST', f"{self.base_urls['log']}/api/v1/logs", json=data)
    
    # DataSync Management
    def get_sync_jobs(self) -> Dict[str, Any]:
        """Get sync jobs"""
        return self._make_request('GET', f"{self.base_urls['datasync']}/api/v1/sync-jobs")
    
    def create_sync_job(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create sync job"""
        return self._make_request('POST', f"{self.base_urls['datasync']}/api/v1/sync-jobs", json=data)
    
    def execute_sync(self, job_id: int) -> Dict[str, Any]:
        """Execute sync job"""
        return self._make_request('POST', f"{self.base_urls['datasync']}/api/v1/sync-jobs/{job_id}/execute")
    
    def get_backups(self) -> Dict[str, Any]:
        """Get backups"""
        return self._make_request('GET', f"{self.base_urls['datasync']}/api/v1/backups")
    
    def create_backup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create backup"""
        return self._make_request('POST', f"{self.base_urls['datasync']}/api/v1/backups", json=data)
    
    # GitHub Runner Management
    def get_runners(self) -> Dict[str, Any]:
        """Get GitHub runners"""
        return self._make_request('GET', f"{self.base_urls['github_runner']}/api/v1/runners")
    
    def create_runner(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create GitHub runner"""
        return self._make_request('POST', f"{self.base_urls['github_runner']}/api/v1/runners", json=data)
    
    def get_workflows(self) -> Dict[str, Any]:
        """Get workflows"""
        return self._make_request('GET', f"{self.base_urls['github_runner']}/api/v1/workflows")
    
    def trigger_workflow(self, workflow_id: int) -> Dict[str, Any]:
        """Trigger workflow"""
        return self._make_request('POST', f"{self.base_urls['github_runner']}/api/v1/workflows/{workflow_id}/trigger")
    
    # TechDocs Management
    def get_docs(self) -> Dict[str, Any]:
        """Get documentation sites"""
        return self._make_request('GET', f"{self.base_urls['techdocs']}/api/v1/docs")
    
    def build_docs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build documentation"""
        return self._make_request('POST', f"{self.base_urls['techdocs']}/api/v1/docs/build", json=data)
    
    def rebuild_docs(self, doc_id: int) -> Dict[str, Any]:
        """Rebuild documentation"""
        return self._make_request('POST', f"{self.base_urls['techdocs']}/api/v1/docs/{doc_id}/rebuild")
    
    # Dashboard Data
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # Get services status
            services_status = self.get_services_status()
            
            # Get repositories
            repositories = self.get_repositories()
            repo_count = len(repositories.get('data', [])) if repositories.get('success') else 0
            
            # Get tasks
            tasks = self.get_tasks()
            task_count = len(tasks.get('data', [])) if tasks.get('success') else 0
            running_tasks = len([t for t in tasks.get('data', []) if t.get('status') == 'running']) if tasks.get('success') else 0
            
            # Get recent logs
            recent_logs = self.get_logs(limit=10)
            log_count = len(recent_logs.get('data', [])) if recent_logs.get('success') else 0
            
            # Get sync jobs
            sync_jobs = self.get_sync_jobs()
            sync_count = len(sync_jobs.get('data', [])) if sync_jobs.get('success') else 0
            
            return {
                'success': True,
                'data': {
                    'services': services_status,
                    'counters': {
                        'repositories': repo_count,
                        'tasks': task_count,
                        'running_tasks': running_tasks,
                        'logs': log_count,
                        'sync_jobs': sync_count
                    },
                    'health': self.health_check_all(),
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Dashboard data error: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {
                    'services': {'services_online': 0, 'total_services': 6},
                    'counters': {'repositories': 0, 'tasks': 0, 'running_tasks': 0, 'logs': 0, 'sync_jobs': 0},
                    'timestamp': datetime.now().isoformat()
                }
            }

# Singleton instance
api_client = IAOpsApiClient()
