#!/usr/bin/env python3
"""
Repository Manager API Enhanced - Con funcionalidades GitHub completas
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from sqlalchemy.orm import Session
from database import get_db, init_db, Repository, get_minio, get_redis
from swagger_config import create_swagger_config, get_common_models, get_repository_models
from github_service import GitHubService
from mkdocs_service import MkDocsService
import os
import logging
import tempfile
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Swagger configuration
api = create_swagger_config(app, "Repository Manager Enhanced", "2.0.0")
common_models = get_common_models(api)
repo_models = get_repository_models(api)

# Services
github_service = GitHubService()
mkdocs_service = MkDocsService(get_minio())

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Namespaces
repositories_ns = api.namespace('repositories', description='Repository operations')
github_ns = api.namespace('github', description='GitHub integration')
docs_ns = api.namespace('docs', description='Documentation operations')
health_ns = api.namespace('health', description='Health check operations')

# Models
github_repo_model = api.model('GitHubRepository', {
    'id': fields.Integer(description='GitHub repository ID'),
    'name': fields.String(description='Repository name'),
    'full_name': fields.String(description='Full repository name'),
    'description': fields.String(description='Repository description'),
    'clone_url': fields.String(description='Clone URL'),
    'default_branch': fields.String(description='Default branch'),
    'private': fields.Boolean(description='Is private repository'),
    'language': fields.String(description='Primary language')
})

project_create_model = api.model('ProjectCreate', {
    'project_name': fields.String(required=True, description='Nombre del Proyecto'),
    'project_description': fields.String(description='Descripción del Proyecto'),
    'github_url': fields.String(required=True, description='URL del repositorio GitHub'),
    'branch': fields.String(default='main', description='Branch a usar')
})

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
                'data': {'status': 'healthy', 'service': 'Repository Manager Enhanced'},
                'message': 'Service is healthy'
            }
        except Exception as e:
            return {
                'success': False,
                'error': {'code': 'HEALTH_CHECK_FAILED', 'message': str(e)}
            }, 500

@github_ns.route('/repositories')
class GitHubRepositories(Resource):
    @api.doc('list_github_repositories')
    @api.param('username', 'GitHub username')
    @api.param('org', 'GitHub organization')
    @api.marshal_with(common_models['success_response'])
    def get(self):
        """Listar repositorios de GitHub"""
        try:
            username = request.args.get('username')
            org = request.args.get('org')
            
            repos = github_service.list_repositories(username=username, org=org)
            
            return {
                'success': True,
                'data': repos,
                'message': f'Found {len(repos)} repositories'
            }
        except Exception as e:
            logger.error(f"Error listing GitHub repositories: {e}")
            return {
                'success': False,
                'error': {'code': 'GITHUB_LIST_FAILED', 'message': str(e)}
            }, 500

@repositories_ns.route('/projects')
class ProjectManager(Resource):
    @api.doc('create_project')
    @api.expect(project_create_model)
    @api.marshal_with(common_models['success_response'])
    def post(self):
        """Crear proyecto con estructura completa (Nombre, Descripción, GitHub)"""
        try:
            data = request.get_json()
            
            # Validar campos requeridos
            if not data.get('project_name') or not data.get('github_url'):
                return {
                    'success': False,
                    'error': {'code': 'MISSING_FIELDS', 'message': 'project_name and github_url are required'}
                }, 400
            
            db = next(get_db())
            
            # Verificar si ya existe
            existing = db.query(Repository).filter(Repository.name == data['project_name']).first()
            if existing:
                return {
                    'success': False,
                    'error': {'code': 'PROJECT_EXISTS', 'message': 'Project already exists'}
                }, 409
            
            # Crear directorio temporal para clonación
            with tempfile.TemporaryDirectory() as temp_dir:
                clone_path = os.path.join(temp_dir, data['project_name'])
                
                # Clonar repositorio
                if not github_service.clone_repository(
                    data['github_url'], 
                    clone_path, 
                    data.get('branch', 'main')
                ):
                    return {
                        'success': False,
                        'error': {'code': 'CLONE_FAILED', 'message': 'Failed to clone repository'}
                    }, 500
                
                # Crear configuración MkDocs si no existe
                if not mkdocs_service.has_mkdocs_config(clone_path):
                    mkdocs_service.create_mkdocs_config(
                        clone_path,
                        data['project_name'],
                        data.get('project_description', '')
                    )
                
                # Construir documentación
                docs_output = os.path.join(temp_dir, 'docs_output')
                build_result = mkdocs_service.build_docs(clone_path, docs_output)
                
                if not build_result['success']:
                    return {
                        'success': False,
                        'error': {'code': 'BUILD_FAILED', 'message': build_result['error']}
                    }, 500
                
                # Subir a MinIO
                upload_result = mkdocs_service.upload_to_minio(docs_output, data['project_name'])
                
                if not upload_result['success']:
                    return {
                        'success': False,
                        'error': {'code': 'UPLOAD_FAILED', 'message': upload_result['error']}
                    }, 500
            
            # Guardar en base de datos
            new_repo = Repository(
                name=data['project_name'],
                url=data['github_url'],
                branch=data.get('branch', 'main'),
                description=data.get('project_description', ''),
                status='active',
                created_at=datetime.utcnow(),
                last_sync=datetime.utcnow(),
                repo_metadata={
                    'docs_url': upload_result['url'],
                    'files_uploaded': upload_result['files_uploaded']
                }
            )
            
            db.add(new_repo)
            db.commit()
            db.refresh(new_repo)
            
            return {
                'success': True,
                'data': {
                    'id': new_repo.id,
                    'project_name': new_repo.name,
                    'project_description': new_repo.description,
                    'github_url': new_repo.url,
                    'branch': new_repo.branch,
                    'docs_url': upload_result['url'],
                    'created_at': new_repo.created_at.isoformat()
                },
                'message': 'Project created successfully with documentation'
            }
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {
                'success': False,
                'error': {'code': 'CREATE_PROJECT_FAILED', 'message': str(e)}
            }, 500

@repositories_ns.route('/<int:repo_id>/clone')
class RepositoryClone(Resource):
    @api.doc('clone_repository')
    @api.marshal_with(common_models['success_response'])
    def post(self, repo_id):
        """Clonar repositorio específico"""
        try:
            db = next(get_db())
            repo = db.query(Repository).filter(Repository.id == repo_id).first()
            
            if not repo:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Repository not found'}
                }, 404
            
            with tempfile.TemporaryDirectory() as temp_dir:
                clone_path = os.path.join(temp_dir, repo.name)
                
                if github_service.clone_repository(repo.url, clone_path, repo.branch):
                    return {
                        'success': True,
                        'data': {'repository': repo.name, 'cloned': True},
                        'message': 'Repository cloned successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': {'code': 'CLONE_FAILED', 'message': 'Failed to clone repository'}
                    }, 500
                    
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            return {
                'success': False,
                'error': {'code': 'CLONE_ERROR', 'message': str(e)}
            }, 500

@docs_ns.route('/<int:repo_id>/build')
class DocumentationBuild(Resource):
    @api.doc('build_documentation')
    @api.marshal_with(common_models['success_response'])
    def post(self, repo_id):
        """Construir y subir documentación MkDocs"""
        try:
            db = next(get_db())
            repo = db.query(Repository).filter(Repository.id == repo_id).first()
            
            if not repo:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Repository not found'}
                }, 404
            
            with tempfile.TemporaryDirectory() as temp_dir:
                clone_path = os.path.join(temp_dir, repo.name)
                docs_output = os.path.join(temp_dir, 'docs_output')
                
                # Clonar
                if not github_service.clone_repository(repo.url, clone_path, repo.branch):
                    return {
                        'success': False,
                        'error': {'code': 'CLONE_FAILED', 'message': 'Failed to clone repository'}
                    }, 500
                
                # Crear config si no existe
                if not mkdocs_service.has_mkdocs_config(clone_path):
                    mkdocs_service.create_mkdocs_config(clone_path, repo.name, repo.description)
                
                # Construir
                build_result = mkdocs_service.build_docs(clone_path, docs_output)
                if not build_result['success']:
                    return {
                        'success': False,
                        'error': {'code': 'BUILD_FAILED', 'message': build_result['error']}
                    }, 500
                
                # Subir a MinIO
                upload_result = mkdocs_service.upload_to_minio(docs_output, repo.name)
                if not upload_result['success']:
                    return {
                        'success': False,
                        'error': {'code': 'UPLOAD_FAILED', 'message': upload_result['error']}
                    }, 500
                
                # Actualizar metadata
                repo.repo_metadata = {
                    'docs_url': upload_result['url'],
                    'files_uploaded': upload_result['files_uploaded'],
                    'last_build': datetime.utcnow().isoformat()
                }
                repo.last_sync = datetime.utcnow()
                db.commit()
                
                return {
                    'success': True,
                    'data': {
                        'repository': repo.name,
                        'docs_url': upload_result['url'],
                        'files_uploaded': upload_result['files_uploaded']
                    },
                    'message': 'Documentation built and uploaded successfully'
                }
                
        except Exception as e:
            logger.error(f"Error building documentation: {e}")
            return {
                'success': False,
                'error': {'code': 'BUILD_ERROR', 'message': str(e)}
            }, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8850))
    app.run(host='0.0.0.0', port=port, debug=True)
