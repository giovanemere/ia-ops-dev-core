#!/usr/bin/env python3
"""
Docs Portal Manager - Migrated from ia-ops-docs
Gestión de portal de documentación integrado en Dev-Core
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import requests
import json
import logging
from datetime import datetime
from minio import Minio
from minio.error import S3Error
import yaml
import tempfile
from bs4 import BeautifulSoup
import markdown

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocsPortalManager:
    def __init__(self):
        self.minio_client = None
        self.bucket_name = "iaops-portal"
        self.setup_minio()
    
    def setup_minio(self):
        """Setup MinIO client"""
        try:
            self.minio_client = Minio(
                "localhost:9898",
                access_key="minioadmin",
                secret_key="minioadmin123",
                secure=False
            )
            logger.info("MinIO client initialized")
        except Exception as e:
            logger.error(f"Error initializing MinIO: {e}")
    
    def get_repositories(self):
        """Get list of repositories from MinIO"""
        try:
            objects = self.minio_client.list_objects(self.bucket_name, recursive=True)
            repos = set()
            for obj in objects:
                parts = obj.object_name.split('/')
                if len(parts) > 0:
                    repos.add(parts[0])
            return list(repos)
        except Exception as e:
            logger.error(f"Error getting repositories: {e}")
            return []
    
    def get_repository_files(self, repo_name):
        """Get files for a specific repository"""
        try:
            objects = self.minio_client.list_objects(
                self.bucket_name, 
                prefix=f"{repo_name}/",
                recursive=True
            )
            files = []
            for obj in objects:
                if obj.object_name.endswith(('.md', '.html')):
                    files.append({
                        'name': obj.object_name,
                        'size': obj.size,
                        'last_modified': obj.last_modified.isoformat()
                    })
            return files
        except Exception as e:
            logger.error(f"Error getting repository files: {e}")
            return []
    
    def get_file_content(self, file_path):
        """Get content of a specific file"""
        try:
            response = self.minio_client.get_object(self.bucket_name, file_path)
            content = response.read().decode('utf-8')
            
            if file_path.endswith('.md'):
                # Convert markdown to HTML
                html_content = markdown.markdown(content)
                return {'type': 'markdown', 'content': html_content, 'raw': content}
            else:
                return {'type': 'html', 'content': content, 'raw': content}
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return None
    
    def search_content(self, query):
        """Search content across all repositories"""
        try:
            results = []
            repos = self.get_repositories()
            
            for repo in repos:
                files = self.get_repository_files(repo)
                for file_info in files:
                    content = self.get_file_content(file_info['name'])
                    if content and query.lower() in content['raw'].lower():
                        results.append({
                            'repository': repo,
                            'file': file_info['name'],
                            'snippet': self._get_snippet(content['raw'], query)
                        })
            
            return results
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []
    
    def _get_snippet(self, content, query, context_length=100):
        """Get a snippet of content around the query"""
        lower_content = content.lower()
        lower_query = query.lower()
        
        index = lower_content.find(lower_query)
        if index == -1:
            return content[:context_length] + "..."
        
        start = max(0, index - context_length // 2)
        end = min(len(content), index + len(query) + context_length // 2)
        
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet

# Flask app setup
app = Flask(__name__)
CORS(app)
docs_manager = DocsPortalManager()

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'docs-portal-manager'})

@app.route('/api/repositories')
def get_repositories():
    repos = docs_manager.get_repositories()
    return jsonify({'repositories': repos})

@app.route('/api/repository/<repo_name>/files')
def get_repository_files(repo_name):
    files = docs_manager.get_repository_files(repo_name)
    return jsonify({'files': files})

@app.route('/api/file/<path:file_path>')
def get_file_content(file_path):
    content = docs_manager.get_file_content(file_path)
    if content:
        return jsonify(content)
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/search')
def search_content():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    results = docs_manager.search_content(query)
    return jsonify({'results': results, 'query': query})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8845, debug=False)
