#!/usr/bin/env python3
"""
Repository Manager API
Gestión centralizada de repositorios para IA-Ops con PostgreSQL
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.orm import Session
from database import get_db, init_db, Repository, get_minio, get_redis
import os
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

@app.route('/', methods=['GET'])
def index():
    """Información del servicio"""
    return jsonify({
        'service': 'Repository Manager',
        'version': '2.0.0',
        'description': 'Gestión centralizada de repositorios para IA-Ops con PostgreSQL',
        'database': 'PostgreSQL',
        'storage': 'MinIO',
        'cache': 'Redis',
        'endpoints': {
            '/health': 'Health check',
            '/repositories': 'GET: Listar repositorios, POST: Crear repositorio',
            '/repositories/<id>': 'GET: Obtener repositorio, PUT: Actualizar, DELETE: Eliminar',
            '/repositories/<id>/sync': 'POST: Sincronizar repositorio'
        },
        'status': 'running'
    })

@app.route('/health', methods=['GET'])
def health():
    try:
        # Test database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    try:
        # Test Redis connection
        redis_client = get_redis()
        redis_client.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    try:
        # Test MinIO connection
        minio_client = get_minio()
        minio_client.list_buckets()
        minio_status = "connected"
    except Exception as e:
        minio_status = f"error: {str(e)}"
    
    return jsonify({
        'status': 'healthy',
        'service': 'repository-manager',
        'database': db_status,
        'redis': redis_status,
        'minio': minio_status
    })

@app.route('/repositories', methods=['GET'])
def list_repositories():
    """Listar todos los repositorios"""
    try:
        db = next(get_db())
        
        # Filtros opcionales
        status = request.args.get('status')
        search = request.args.get('search')
        
        query = db.query(Repository)
        
        if status:
            query = query.filter(Repository.status == status)
        if search:
            query = query.filter(Repository.name.contains(search))
        
        repositories = query.all()
        
        # Cache result in Redis
        redis_client = get_redis()
        redis_client.setex('repositories:list', 300, str(len(repositories)))
        
        return jsonify({
            'success': True,
            'data': [{
                'id': repo.id,
                'name': repo.name,
                'url': repo.url,
                'branch': repo.branch,
                'description': repo.description,
                'status': repo.status,
                'created_at': repo.created_at.isoformat() if repo.created_at else None,
                'last_sync': repo.last_sync.isoformat() if repo.last_sync else None,
                'metadata': repo.metadata
            } for repo in repositories],
            'count': len(repositories)
        })
        
    except Exception as e:
        logger.error(f"Error listing repositories: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'code': 'DATABASE_ERROR', 'message': str(e)}
        }), 500

@app.route('/repositories', methods=['POST'])
def create_repository():
    """Crear nuevo repositorio"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'url', 'branch']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': {'code': 'MISSING_FIELDS', 'message': 'Missing required fields'}
            }), 400
        
        db = next(get_db())
        
        # Verificar si ya existe
        existing = db.query(Repository).filter(Repository.name == data['name']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': {'code': 'REPOSITORY_EXISTS', 'message': 'Repository already exists'}
            }), 409
        
        # Crear repositorio
        new_repo = Repository(
            name=data['name'],
            url=data['url'],
            branch=data.get('branch', 'main'),
            description=data.get('description', ''),
            status='active',
            metadata=data.get('metadata', {})
        )
        
        db.add(new_repo)
        db.commit()
        db.refresh(new_repo)
        
        # Invalidate cache
        redis_client = get_redis()
        redis_client.delete('repositories:list')
        
        return jsonify({
            'success': True,
            'data': {
                'id': new_repo.id,
                'name': new_repo.name,
                'url': new_repo.url,
                'branch': new_repo.branch,
                'description': new_repo.description,
                'status': new_repo.status,
                'created_at': new_repo.created_at.isoformat(),
                'last_sync': None,
                'metadata': new_repo.metadata
            },
            'message': 'Repository created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating repository: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'code': 'DATABASE_ERROR', 'message': str(e)}
        }), 500

@app.route('/repositories/<int:repo_id>', methods=['GET'])
def get_repository(repo_id):
    """Obtener repositorio por ID"""
    try:
        db = next(get_db())
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        
        if not repo:
            return jsonify({
                'success': False,
                'error': {'code': 'REPOSITORY_NOT_FOUND', 'message': 'Repository not found'}
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': repo.id,
                'name': repo.name,
                'url': repo.url,
                'branch': repo.branch,
                'description': repo.description,
                'status': repo.status,
                'created_at': repo.created_at.isoformat() if repo.created_at else None,
                'last_sync': repo.last_sync.isoformat() if repo.last_sync else None,
                'metadata': repo.metadata
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting repository: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'code': 'DATABASE_ERROR', 'message': str(e)}
        }), 500

@app.route('/repositories/<int:repo_id>', methods=['PUT'])
def update_repository(repo_id):
    """Actualizar repositorio"""
    try:
        data = request.get_json()
        db = next(get_db())
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        
        if not repo:
            return jsonify({
                'success': False,
                'error': {'code': 'REPOSITORY_NOT_FOUND', 'message': 'Repository not found'}
            }), 404
        
        # Actualizar campos permitidos
        updatable_fields = ['name', 'url', 'branch', 'description', 'status', 'metadata']
        for field in updatable_fields:
            if field in data:
                setattr(repo, field, data[field])
        
        db.commit()
        db.refresh(repo)
        
        # Invalidate cache
        redis_client = get_redis()
        redis_client.delete('repositories:list')
        
        return jsonify({
            'success': True,
            'data': {
                'id': repo.id,
                'name': repo.name,
                'url': repo.url,
                'branch': repo.branch,
                'description': repo.description,
                'status': repo.status,
                'created_at': repo.created_at.isoformat() if repo.created_at else None,
                'last_sync': repo.last_sync.isoformat() if repo.last_sync else None,
                'metadata': repo.metadata
            },
            'message': 'Repository updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating repository: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'code': 'DATABASE_ERROR', 'message': str(e)}
        }), 500

@app.route('/repositories/<int:repo_id>', methods=['DELETE'])
def delete_repository(repo_id):
    """Eliminar repositorio"""
    try:
        db = next(get_db())
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        
        if not repo:
            return jsonify({
                'success': False,
                'error': {'code': 'REPOSITORY_NOT_FOUND', 'message': 'Repository not found'}
            }), 404
        
        db.delete(repo)
        db.commit()
        
        # Invalidate cache
        redis_client = get_redis()
        redis_client.delete('repositories:list')
        
        return jsonify({
            'success': True,
            'message': 'Repository deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting repository: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'code': 'DATABASE_ERROR', 'message': str(e)}
        }), 500

@app.route('/repositories/<int:repo_id>/sync', methods=['POST'])
def sync_repository(repo_id):
    """Sincronizar repositorio"""
    try:
        db = next(get_db())
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        
        if not repo:
            return jsonify({
                'success': False,
                'error': {'code': 'REPOSITORY_NOT_FOUND', 'message': 'Repository not found'}
            }), 404
        
        # Actualizar timestamp de sincronización
        repo.last_sync = datetime.utcnow()
        db.commit()
        
        # Aquí iría la lógica de sincronización real
        # Por ahora solo simulamos
        
        return jsonify({
            'success': True,
            'message': 'Repository sync started',
            'data': {
                'repository_id': repo_id,
                'last_sync': repo.last_sync.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error syncing repository: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'code': 'DATABASE_ERROR', 'message': str(e)}
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8850, debug=True)
