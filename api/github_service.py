#!/usr/bin/env python3
"""
GitHub Service - Funcionalidades de integración con GitHub
"""

import os
import requests
import subprocess
import shutil
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.headers = {'Authorization': f'token {self.token}'} if self.token else {}
        self.base_url = 'https://api.github.com'
    
    def list_repositories(self, username: str = None, org: str = None) -> List[Dict]:
        """Listar repositorios de GitHub"""
        try:
            if org:
                url = f"{self.base_url}/orgs/{org}/repos"
            elif username:
                url = f"{self.base_url}/users/{username}/repos"
            else:
                url = f"{self.base_url}/user/repos"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            repos = []
            for repo in response.json():
                repos.append({
                    'id': repo['id'],
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo['description'] or '',
                    'clone_url': repo['clone_url'],
                    'default_branch': repo['default_branch'],
                    'private': repo['private'],
                    'language': repo['language'],
                    'updated_at': repo['updated_at']
                })
            
            return repos
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            raise
    
    def clone_repository(self, repo_url: str, local_path: str, branch: str = 'main') -> bool:
        """Clonar repositorio"""
        try:
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            
            cmd = ['git', 'clone', '-b', branch, repo_url, local_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Repository cloned successfully: {repo_url}")
                return True
            else:
                logger.error(f"Clone failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            return False
    
    def delete_cloned_repository(self, local_path: str) -> bool:
        """Eliminar repositorio clonado"""
        try:
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
                logger.info(f"Deleted cloned repository: {local_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting repository: {e}")
            return False
