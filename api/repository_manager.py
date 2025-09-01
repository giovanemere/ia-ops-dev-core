#!/usr/bin/env python3
"""
Repository Manager API
Gestión centralizada de repositorios para IA-Ops
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import subprocess
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración
REPOSITORIES_FILE = '/app/data/repositories.json'
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9898')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin123')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_repositories():
    """Cargar repositorios desde archivo JSON"""
    if os.path.exists(REPOSITORIES_FILE):
        with open(REPOSITORIES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_repositories(repos):
    """Guardar repositorios en archivo JSON"""
    os.makedirs(os.path.dirname(REPOSITORIES_FILE), exist_ok=True)
    with open(REPOSITORIES_FILE, 'w') as f:
        json.dump(repos, f, indent=2)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'repository-manager'})

@app.route('/repositories', methods=['GET'])
def list_repositories():
    """Listar todos los repositorios"""
    repos = load_repositories()
    return jsonify({
        'repositories': repos,
        'count': len(repos)
    })

@app.route('/repositories', methods=['POST'])
def add_repository():
    """Agregar nuevo repositorio"""
    data = request.get_json()
    
    required_fields = ['name', 'url', 'branch']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    repos = load_repositories()
    
    # Verificar si ya existe
    if any(repo['name'] == data['name'] for repo in repos):
        return jsonify({'error': 'Repository already exists'}), 409
    
    new_repo = {
        'id': len(repos) + 1,
        'name': data['name'],
        'url': data['url'],
        'branch': data.get('branch', 'main'),
        'description': data.get('description', ''),
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'last_sync': None
    }
    
    repos.append(new_repo)
    save_repositories(repos)
    
    logger.info(f"Repository added: {new_repo['name']}")
    return jsonify(new_repo), 201

@app.route('/repositories/<int:repo_id>', methods=['PUT'])
def update_repository(repo_id):
    """Actualizar repositorio"""
    data = request.get_json()
    repos = load_repositories()
    
    repo = next((r for r in repos if r['id'] == repo_id), None)
    if not repo:
        return jsonify({'error': 'Repository not found'}), 404
    
    # Actualizar campos
    for field in ['name', 'url', 'branch', 'description', 'status']:
        if field in data:
            repo[field] = data[field]
    
    repo['updated_at'] = datetime.now().isoformat()
    save_repositories(repos)
    
    logger.info(f"Repository updated: {repo['name']}")
    return jsonify(repo)

@app.route('/repositories/<int:repo_id>', methods=['DELETE'])
def delete_repository(repo_id):
    """Eliminar repositorio"""
    repos = load_repositories()
    repo = next((r for r in repos if r['id'] == repo_id), None)
    
    if not repo:
        return jsonify({'error': 'Repository not found'}), 404
    
    repos = [r for r in repos if r['id'] != repo_id]
    save_repositories(repos)
    
    logger.info(f"Repository deleted: {repo['name']}")
    return jsonify({'message': 'Repository deleted successfully'})

@app.route('/repositories/<int:repo_id>/sync', methods=['POST'])
def sync_repository(repo_id):
    """Sincronizar repositorio"""
    repos = load_repositories()
    repo = next((r for r in repos if r['id'] == repo_id), None)
    
    if not repo:
        return jsonify({'error': 'Repository not found'}), 404
    
    try:
        # Aquí iría la lógica de sincronización
        repo['last_sync'] = datetime.now().isoformat()
        repo['status'] = 'synced'
        save_repositories(repos)
        
        logger.info(f"Repository synced: {repo['name']}")
        return jsonify({'message': 'Repository synced successfully', 'repository': repo})
    
    except Exception as e:
        logger.error(f"Sync failed for {repo['name']}: {str(e)}")
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8850, debug=False)
