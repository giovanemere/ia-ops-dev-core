#!/usr/bin/env python3
"""
Repository Manager API with Swagger Documentation
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from sqlalchemy.orm import Session
from database import get_db, init_db, Repository, get_minio, get_redis
from swagger_config import create_swagger_config, get_common_models, get_repository_models
import os
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Swagger configuration
api = create_swagger_config(app, "Repository Manager", "2.0.0")
common_models = get_common_models(api)
repo_models = get_repository_models(api)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Namespaces
repositories_ns = api.namespace('repositories', description='Repository operations')
health_ns = api.namespace('health', description='Health check operations')

@health_ns.route('/')
class HealthCheck(Resource):
    @api.doc('health_check')
    @api.marshal_with(common_models['success_response'])
    def get(self):
        """Health check endpoint"""
        try:
            db = next(get_db())
            db.execute("SELECT 1")
            return {
                'success': True,
                'data': {'status': 'healthy', 'service': 'Repository Manager'},
                'message': 'Service is healthy'
            }
        except Exception as e:
            return {
                'success': False,
                'error': {'code': 'HEALTH_CHECK_FAILED', 'message': str(e)}
            }, 500

@repositories_ns.route('/')
class RepositoryList(Resource):
    @api.doc('list_repositories')
    @api.marshal_with(common_models['success_response'])
    def get(self):
        """Get all repositories"""
        try:
            db = next(get_db())
            repositories = db.query(Repository).all()
            
            repo_list = []
            for repo in repositories:
                repo_list.append({
                    'id': repo.id,
                    'name': repo.name,
                    'url': repo.url,
                    'branch': repo.branch,
                    'description': repo.description,
                    'status': repo.status,
                    'created_at': repo.created_at.isoformat() if repo.created_at else None,
                    'last_sync': repo.last_sync.isoformat() if repo.last_sync else None
                })
            
            return {
                'success': True,
                'data': repo_list,
                'message': f'Found {len(repo_list)} repositories'
            }
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return {
                'success': False,
                'error': {'code': 'LIST_FAILED', 'message': str(e)}
            }, 500

    @api.doc('create_repository')
    @api.expect(repo_models['repository_create'])
    @api.marshal_with(common_models['success_response'])
    def post(self):
        """Create a new repository"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'url', 'branch']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'error': {'code': 'MISSING_FIELD', 'message': f'Missing required field: {field}'}
                    }, 400
            
            db = next(get_db())
            
            # Check if repository already exists
            existing = db.query(Repository).filter(Repository.name == data['name']).first()
            if existing:
                return {
                    'success': False,
                    'error': {'code': 'REPOSITORY_EXISTS', 'message': 'Repository already exists'}
                }, 409
            
            # Create new repository
            new_repo = Repository(
                name=data['name'],
                url=data['url'],
                branch=data['branch'],
                description=data.get('description', ''),
                status='active',
                created_at=datetime.utcnow()
            )
            
            db.add(new_repo)
            db.commit()
            db.refresh(new_repo)
            
            return {
                'success': True,
                'data': {
                    'id': new_repo.id,
                    'name': new_repo.name,
                    'url': new_repo.url,
                    'branch': new_repo.branch,
                    'description': new_repo.description,
                    'status': new_repo.status,
                    'created_at': new_repo.created_at.isoformat()
                },
                'message': 'Repository created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating repository: {e}")
            return {
                'success': False,
                'error': {'code': 'CREATE_FAILED', 'message': str(e)}
            }, 500

@repositories_ns.route('/<int:repo_id>')
class RepositoryDetail(Resource):
    @api.doc('get_repository')
    @api.marshal_with(common_models['success_response'])
    def get(self, repo_id):
        """Get repository by ID"""
        try:
            db = next(get_db())
            repo = db.query(Repository).filter(Repository.id == repo_id).first()
            
            if not repo:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Repository not found'}
                }, 404
            
            return {
                'success': True,
                'data': {
                    'id': repo.id,
                    'name': repo.name,
                    'url': repo.url,
                    'branch': repo.branch,
                    'description': repo.description,
                    'status': repo.status,
                    'created_at': repo.created_at.isoformat() if repo.created_at else None,
                    'last_sync': repo.last_sync.isoformat() if repo.last_sync else None
                },
                'message': 'Repository retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Error getting repository: {e}")
            return {
                'success': False,
                'error': {'code': 'GET_FAILED', 'message': str(e)}
            }, 500

    @api.doc('update_repository')
    @api.expect(repo_models['repository_create'])
    @api.marshal_with(common_models['success_response'])
    def put(self, repo_id):
        """Update repository"""
        try:
            data = request.get_json()
            db = next(get_db())
            
            repo = db.query(Repository).filter(Repository.id == repo_id).first()
            if not repo:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Repository not found'}
                }, 404
            
            # Update fields
            if 'name' in data:
                repo.name = data['name']
            if 'url' in data:
                repo.url = data['url']
            if 'branch' in data:
                repo.branch = data['branch']
            if 'description' in data:
                repo.description = data['description']
            
            db.commit()
            
            return {
                'success': True,
                'data': {
                    'id': repo.id,
                    'name': repo.name,
                    'url': repo.url,
                    'branch': repo.branch,
                    'description': repo.description,
                    'status': repo.status
                },
                'message': 'Repository updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating repository: {e}")
            return {
                'success': False,
                'error': {'code': 'UPDATE_FAILED', 'message': str(e)}
            }, 500

    @api.doc('delete_repository')
    @api.marshal_with(common_models['success_response'])
    def delete(self, repo_id):
        """Delete repository"""
        try:
            db = next(get_db())
            repo = db.query(Repository).filter(Repository.id == repo_id).first()
            
            if not repo:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Repository not found'}
                }, 404
            
            db.delete(repo)
            db.commit()
            
            return {
                'success': True,
                'data': {'id': repo_id},
                'message': 'Repository deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting repository: {e}")
            return {
                'success': False,
                'error': {'code': 'DELETE_FAILED', 'message': str(e)}
            }, 500

@repositories_ns.route('/<int:repo_id>/sync')
class RepositorySync(Resource):
    @api.doc('sync_repository')
    @api.marshal_with(common_models['success_response'])
    def post(self, repo_id):
        """Sync repository with remote"""
        try:
            db = next(get_db())
            repo = db.query(Repository).filter(Repository.id == repo_id).first()
            
            if not repo:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Repository not found'}
                }, 404
            
            # Update sync status
            repo.status = 'syncing'
            repo.last_sync = datetime.utcnow()
            db.commit()
            
            # Here you would implement actual sync logic
            # For now, just simulate success
            repo.status = 'active'
            db.commit()
            
            return {
                'success': True,
                'data': {
                    'id': repo.id,
                    'status': repo.status,
                    'last_sync': repo.last_sync.isoformat()
                },
                'message': 'Repository synced successfully'
            }
            
        except Exception as e:
            logger.error(f"Error syncing repository: {e}")
            return {
                'success': False,
                'error': {'code': 'SYNC_FAILED', 'message': str(e)}
            }, 500

# Legacy endpoints for backward compatibility
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'Repository Manager',
        'version': '2.0.0',
        'status': 'active',
        'docs': '/docs/',
        'endpoints': {
            'repositories': '/api/v1/repositories',
            'health': '/api/v1/health'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return HealthCheck().get()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8850))
    app.run(host='0.0.0.0', port=port, debug=True)
