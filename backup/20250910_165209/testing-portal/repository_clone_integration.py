#!/usr/bin/env python3
"""
Repository Clone Integration - Integración del servicio de clonación con portal de pruebas
"""

import requests
import json
import os
from typing import Dict, Optional

class RepositoryCloneClient:
    def __init__(self, clone_service_url: str = "http://localhost:8867"):
        self.base_url = clone_service_url
        self.api_base = f"{self.base_url}/api/v1"
    
    def clone_repository(self, repo_url: str, branch: str = "main", 
                        token: Optional[str] = None, shallow: bool = True) -> Dict:
        """Clone a repository using the cloning service"""
        try:
            payload = {
                "repo_url": repo_url,
                "branch": branch,
                "shallow": shallow
            }
            
            if token:
                payload["token"] = token
            
            response = requests.post(
                f"{self.api_base}/clone/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300  # 5 minutes timeout
            )
            
            return response.json()
            
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Clone operation timed out"}
        except Exception as e:
            return {"success": False, "message": f"Clone error: {str(e)}"}
    
    def list_clones(self) -> Dict:
        """List all active clones"""
        try:
            response = requests.get(f"{self.api_base}/clone/list")
            return response.json()
        except Exception as e:
            return {"success": False, "message": f"List error: {str(e)}"}
    
    def get_clone_info(self, clone_id: str) -> Dict:
        """Get information about a specific clone"""
        try:
            response = requests.get(f"{self.api_base}/clone/{clone_id}")
            return response.json()
        except Exception as e:
            return {"success": False, "message": f"Get info error: {str(e)}"}
    
    def delete_clone(self, clone_id: str) -> Dict:
        """Delete a cloned repository"""
        try:
            response = requests.delete(f"{self.api_base}/clone/{clone_id}")
            return response.json()
        except Exception as e:
            return {"success": False, "message": f"Delete error: {str(e)}"}
    
    def list_clone_files(self, clone_id: str) -> Dict:
        """List files in a cloned repository"""
        try:
            response = requests.get(f"{self.api_base}/clone/{clone_id}/files")
            return response.json()
        except Exception as e:
            return {"success": False, "message": f"List files error: {str(e)}"}
    
    def cleanup_all_clones(self) -> Dict:
        """Cleanup all clones"""
        try:
            response = requests.post(f"{self.api_base}/clone/cleanup")
            return response.json()
        except Exception as e:
            return {"success": False, "message": f"Cleanup error: {str(e)}"}

# Testing functions for integration
def test_clone_integration():
    """Test the repository cloning integration"""
    print("🧪 Testing Repository Clone Integration")
    print("=" * 50)
    
    client = RepositoryCloneClient()
    
    # Test repositories
    test_repos = [
        {
            "url": "https://github.com/octocat/Hello-World.git",
            "branch": "master",
            "description": "Simple test repository"
        },
        {
            "url": "https://github.com/microsoft/vscode.git",
            "branch": "main",
            "description": "Large repository (shallow clone)"
        }
    ]
    
    cloned_ids = []
    
    for repo in test_repos:
        print(f"\n📁 Cloning: {repo['description']}")
        print(f"   URL: {repo['url']}")
        print(f"   Branch: {repo['branch']}")
        
        result = client.clone_repository(
            repo_url=repo['url'],
            branch=repo['branch'],
            shallow=True
        )
        
        if result.get('success'):
            clone_id = result['clone_id']
            cloned_ids.append(clone_id)
            print(f"✅ Clone successful: {clone_id}")
            print(f"   Local path: {result['local_path']}")
            
            # Get repository info
            repo_info = result.get('repo_info', {})
            if 'last_commit' in repo_info:
                commit = repo_info['last_commit']
                print(f"   Last commit: {commit.get('hash', 'unknown')[:8]}")
                print(f"   Author: {commit.get('author', 'unknown')}")
        else:
            print(f"❌ Clone failed: {result.get('message', 'Unknown error')}")
    
    # List all clones
    print(f"\n📊 Listing all clones...")
    clones_list = client.list_clones()
    if clones_list.get('success'):
        print(f"✅ Found {clones_list['total']} active clones")
        for clone_data in clones_list['data']:
            print(f"   - {clone_data['clone_id']}: {clone_data['repo_url']}")
    
    # Test file listing for first clone
    if cloned_ids:
        first_clone = cloned_ids[0]
        print(f"\n📄 Listing files in clone: {first_clone}")
        files_result = client.list_clone_files(first_clone)
        if files_result.get('success'):
            files = files_result['data']['files']
            print(f"✅ Found {len(files)} files")
            for file_info in files[:5]:  # Show first 5 files
                print(f"   - {file_info['path']} ({file_info['size']} bytes)")
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")
    
    # Cleanup
    print(f"\n🧹 Cleaning up clones...")
    cleanup_result = client.cleanup_all_clones()
    if cleanup_result.get('success'):
        print(f"✅ {cleanup_result['message']}")
    else:
        print(f"❌ Cleanup failed: {cleanup_result.get('message', 'Unknown error')}")
    
    print("\n✨ Integration test completed")

# Mock service integration for testing portal
class MockRepositoryCloneService:
    """Mock repository clone service for testing when real service is not available"""
    
    def __init__(self):
        self.clones = {}
        self.clone_counter = 0
    
    def clone_repository(self, repo_url: str, branch: str = "main", **kwargs) -> Dict:
        """Mock clone operation"""
        self.clone_counter += 1
        clone_id = f"mock_clone_{self.clone_counter}"
        
        # Simulate clone data
        clone_data = {
            "clone_id": clone_id,
            "repo_url": repo_url,
            "branch": branch,
            "local_path": f"/tmp/mock_clones/{clone_id}",
            "repo_info": {
                "remote_url": repo_url,
                "current_branch": branch,
                "last_commit": {
                    "hash": "abc123def456",
                    "message": "Mock commit message",
                    "author": "Mock Author",
                    "date": "2024-01-01 12:00:00"
                }
            }
        }
        
        self.clones[clone_id] = clone_data
        
        return {
            "success": True,
            "clone_id": clone_id,
            "local_path": clone_data["local_path"],
            "repo_info": clone_data["repo_info"],
            "message": "Repository cloned successfully (mock)"
        }
    
    def list_clones(self) -> Dict:
        """Mock list clones"""
        return {
            "success": True,
            "data": list(self.clones.values()),
            "total": len(self.clones)
        }
    
    def delete_clone(self, clone_id: str) -> Dict:
        """Mock delete clone"""
        if clone_id in self.clones:
            del self.clones[clone_id]
            return {"success": True, "message": "Clone deleted successfully (mock)"}
        else:
            return {"success": False, "message": "Clone not found"}

if __name__ == "__main__":
    # Run integration test
    test_clone_integration()
