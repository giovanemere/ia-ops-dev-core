"""
Configuración de Swagger/OpenAPI para IA-Ops Dev Core Services
"""

from flask_restx import Api, Resource, fields
from flask import Blueprint

def create_swagger_config(app, service_name, version="1.0.0"):
    """Crear configuración de Swagger para un servicio"""
    
    blueprint = Blueprint('api', __name__)
    
    api = Api(
        blueprint,
        version=version,
        title=f'IA-Ops {service_name} API',
        description=f'API documentation for {service_name} service',
        doc='/docs/',
        prefix='/api/v1'
    )
    
    app.register_blueprint(blueprint)
    return api

# Modelos comunes
def get_common_models(api):
    """Modelos comunes para todas las APIs"""
    
    success_response = api.model('SuccessResponse', {
        'success': fields.Boolean(required=True, description='Operation success status'),
        'data': fields.Raw(description='Response data'),
        'message': fields.String(description='Success message')
    })
    
    error_response = api.model('ErrorResponse', {
        'success': fields.Boolean(required=True, description='Operation success status'),
        'error': fields.Nested(api.model('Error', {
            'code': fields.String(required=True, description='Error code'),
            'message': fields.String(required=True, description='Error message')
        }))
    })
    
    pagination = api.model('Pagination', {
        'page': fields.Integer(description='Current page'),
        'per_page': fields.Integer(description='Items per page'),
        'total': fields.Integer(description='Total items'),
        'pages': fields.Integer(description='Total pages')
    })
    
    return {
        'success_response': success_response,
        'error_response': error_response,
        'pagination': pagination
    }

# Modelos específicos por servicio
def get_repository_models(api):
    """Modelos para Repository Manager"""
    
    repository = api.model('Repository', {
        'id': fields.Integer(description='Repository ID'),
        'name': fields.String(required=True, description='Repository name'),
        'url': fields.String(required=True, description='Repository URL'),
        'branch': fields.String(required=True, description='Default branch'),
        'description': fields.String(description='Repository description'),
        'status': fields.String(description='Repository status', enum=['active', 'inactive', 'syncing']),
        'created_at': fields.DateTime(description='Creation timestamp'),
        'last_sync': fields.DateTime(description='Last sync timestamp')
    })
    
    repository_create = api.model('RepositoryCreate', {
        'name': fields.String(required=True, description='Repository name'),
        'url': fields.String(required=True, description='Repository URL'),
        'branch': fields.String(required=True, description='Default branch'),
        'description': fields.String(description='Repository description')
    })
    
    repository_clone_request = api.model('RepositoryCloneRequest', {
        'repo_url': fields.String(required=True, description='Repository URL to clone'),
        'branch': fields.String(description='Branch to clone', default='main'),
        'token': fields.String(description='GitHub token for private repos')
    })
    
    return {'repository': repository, 'repository_create': repository_create, 'repository_clone_request': repository_clone_request}

def get_task_models(api):
    """Modelos para Task Manager"""
    
    task = api.model('Task', {
        'id': fields.Integer(description='Task ID'),
        'name': fields.String(required=True, description='Task name'),
        'type': fields.String(required=True, description='Task type', enum=['build', 'test', 'deploy', 'sync']),
        'status': fields.String(description='Task status', enum=['pending', 'running', 'completed', 'failed']),
        'repository_id': fields.Integer(description='Associated repository ID'),
        'command': fields.String(description='Command to execute'),
        'environment': fields.Raw(description='Environment variables'),
        'created_at': fields.DateTime(description='Creation timestamp'),
        'started_at': fields.DateTime(description='Start timestamp'),
        'completed_at': fields.DateTime(description='Completion timestamp'),
        'logs': fields.String(description='Task logs')
    })
    
    task_create = api.model('TaskCreate', {
        'name': fields.String(required=True, description='Task name'),
        'type': fields.String(required=True, description='Task type'),
        'repository_id': fields.Integer(description='Associated repository ID'),
        'command': fields.String(description='Command to execute'),
        'environment': fields.Raw(description='Environment variables')
    })
    
    return {'task': task, 'task_create': task_create}

def get_log_models(api):
    """Modelos para Log Manager"""
    
    log = api.model('Log', {
        'id': fields.Integer(description='Log ID'),
        'service': fields.String(required=True, description='Service name'),
        'level': fields.String(required=True, description='Log level', enum=['info', 'warning', 'error', 'debug']),
        'message': fields.String(required=True, description='Log message'),
        'timestamp': fields.DateTime(description='Log timestamp'),
        'metadata': fields.Raw(description='Additional metadata')
    })
    
    log_create = api.model('LogCreate', {
        'service': fields.String(required=True, description='Service name'),
        'level': fields.String(required=True, description='Log level'),
        'message': fields.String(required=True, description='Log message'),
        'metadata': fields.Raw(description='Additional metadata')
    })
    
    return {'log': log, 'log_create': log_create}

def get_sync_models(api):
    """Modelos para DataSync Manager"""
    
    sync_job = api.model('SyncJob', {
        'id': fields.Integer(description='Sync job ID'),
        'name': fields.String(required=True, description='Job name'),
        'source': fields.String(required=True, description='Source location'),
        'destination': fields.String(required=True, description='Destination location'),
        'status': fields.String(description='Job status', enum=['pending', 'running', 'completed', 'failed']),
        'last_run': fields.DateTime(description='Last execution timestamp'),
        'next_run': fields.DateTime(description='Next scheduled execution')
    })
    
    backup = api.model('Backup', {
        'id': fields.Integer(description='Backup ID'),
        'name': fields.String(required=True, description='Backup name'),
        'source': fields.String(required=True, description='Source to backup'),
        'destination': fields.String(required=True, description='Backup destination'),
        'created_at': fields.DateTime(description='Creation timestamp'),
        'size': fields.Integer(description='Backup size in bytes')
    })
    
    return {'sync_job': sync_job, 'backup': backup}

def get_runner_models(api):
    """Modelos para GitHub Runner Manager"""
    
    runner = api.model('Runner', {
        'id': fields.Integer(description='Runner ID'),
        'name': fields.String(required=True, description='Runner name'),
        'status': fields.String(description='Runner status', enum=['online', 'offline', 'busy']),
        'labels': fields.List(fields.String, description='Runner labels'),
        'repository': fields.String(description='Associated repository'),
        'created_at': fields.DateTime(description='Creation timestamp')
    })
    
    workflow = api.model('Workflow', {
        'id': fields.Integer(description='Workflow ID'),
        'name': fields.String(description='Workflow name'),
        'status': fields.String(description='Workflow status'),
        'repository': fields.String(description='Repository name'),
        'branch': fields.String(description='Branch name')
    })
    
    return {'runner': runner, 'workflow': workflow}

def get_docs_models(api):
    """Modelos para TechDocs Builder"""
    
    doc_site = api.model('DocSite', {
        'id': fields.Integer(description='Documentation site ID'),
        'name': fields.String(required=True, description='Site name'),
        'repository_id': fields.Integer(description='Associated repository ID'),
        'status': fields.String(description='Build status', enum=['building', 'ready', 'failed']),
        'url': fields.String(description='Site URL'),
        'last_build': fields.DateTime(description='Last build timestamp')
    })
    
    build_request = api.model('BuildRequest', {
        'repository_id': fields.Integer(required=True, description='Repository ID'),
        'source_path': fields.String(description='Source documentation path'),
        'output_path': fields.String(description='Output path'),
        'config': fields.Raw(description='Build configuration')
    })
    
    return {'doc_site': doc_site, 'build_request': build_request}
