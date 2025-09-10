import os
import subprocess
import tempfile
from typing import Dict, Optional
from pathlib import Path

class RepositoryCloner:
    def __init__(self, base_path: str = "/tmp/ia-ops-repos"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def clone_repository(self, repo_url: str, branch: str = "main", token: Optional[str] = None) -> Dict:
        """Clone repository for testing purposes"""
        try:
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            clone_path = self.base_path / repo_name
            
            # Remove existing directory
            if clone_path.exists():
                subprocess.run(["rm", "-rf", str(clone_path)], check=True)
            
            # Build clone command
            if token:
                auth_url = repo_url.replace("https://", f"https://{token}@")
                cmd = ["git", "clone", "-b", branch, auth_url, str(clone_path)]
            else:
                cmd = ["git", "clone", "-b", branch, repo_url, str(clone_path)]
            
            # Execute clone
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "path": str(clone_path),
                    "repo_name": repo_name,
                    "branch": branch,
                    "files_count": len(list(clone_path.rglob("*")))
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "repo_name": repo_name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "repo_name": repo_url.split("/")[-1]
            }
    
    def cleanup_repository(self, repo_name: str) -> bool:
        """Remove cloned repository"""
        try:
            repo_path = self.base_path / repo_name
            if repo_path.exists():
                subprocess.run(["rm", "-rf", str(repo_path)], check=True)
            return True
        except:
            return False
