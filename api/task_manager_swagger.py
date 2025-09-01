#!/usr/bin/env python3
"""
Task Manager API with Swagger Documentation
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restx import Api, Resource
from sqlalchemy.orm import Session
from database import get_db, init_db, Task, get_redis
from swagger_config import create_swagger_config, get_common_models, get_task_models
import os
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Swagger configuration
api = create_swagger_config(app, "Task Manager", "2.0.0")
common_models = get_common_models(api)
task_models = get_task_models(api)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Namespaces
tasks_ns = api.namespace('tasks', description='Task operations')
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
            redis_client = get_redis()
            redis_client.ping()
            return {
                'success': True,
                'data': {'status': 'healthy', 'service': 'Task Manager'},
                'message': 'Service is healthy'
            }
        except Exception as e:
            return {
                'success': False,
                'error': {'code': 'HEALTH_CHECK_FAILED', 'message': str(e)}
            }, 500

@tasks_ns.route('/')
class TaskList(Resource):
    @api.doc('list_tasks')
    @api.marshal_with(common_models['success_response'])
    def get(self):
        """Get all tasks"""
        try:
            db = next(get_db())
            tasks = db.query(Task).all()
            
            task_list = []
            for task in tasks:
                task_list.append({
                    'id': task.id,
                    'name': task.name,
                    'type': task.type,
                    'status': task.status,
                    'repository_id': task.repository_id,
                    'command': task.command,
                    'environment': task.environment,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'started_at': task.started_at.isoformat() if task.started_at else None,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                    'logs': task.logs
                })
            
            return {
                'success': True,
                'data': task_list,
                'message': f'Found {len(task_list)} tasks'
            }
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return {
                'success': False,
                'error': {'code': 'LIST_FAILED', 'message': str(e)}
            }, 500

    @api.doc('create_task')
    @api.expect(task_models['task_create'])
    @api.marshal_with(common_models['success_response'])
    def post(self):
        """Create a new task"""
        try:
            data = request.get_json()
            
            required_fields = ['name', 'type']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'error': {'code': 'MISSING_FIELD', 'message': f'Missing required field: {field}'}
                    }, 400
            
            db = next(get_db())
            
            new_task = Task(
                name=data['name'],
                type=data['type'],
                status='pending',
                repository_id=data.get('repository_id'),
                command=data.get('command', ''),
                environment=data.get('environment', {}),
                created_at=datetime.utcnow()
            )
            
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
            
            # Add to Redis queue
            redis_client = get_redis()
            redis_client.lpush('task_queue', new_task.id)
            
            return {
                'success': True,
                'data': {
                    'id': new_task.id,
                    'name': new_task.name,
                    'type': new_task.type,
                    'status': new_task.status,
                    'repository_id': new_task.repository_id,
                    'command': new_task.command,
                    'environment': new_task.environment,
                    'created_at': new_task.created_at.isoformat()
                },
                'message': 'Task created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return {
                'success': False,
                'error': {'code': 'CREATE_FAILED', 'message': str(e)}
            }, 500

@tasks_ns.route('/<int:task_id>')
class TaskDetail(Resource):
    @api.doc('get_task')
    @api.marshal_with(common_models['success_response'])
    def get(self, task_id):
        """Get task by ID"""
        try:
            db = next(get_db())
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Task not found'}
                }, 404
            
            return {
                'success': True,
                'data': {
                    'id': task.id,
                    'name': task.name,
                    'type': task.type,
                    'status': task.status,
                    'repository_id': task.repository_id,
                    'command': task.command,
                    'environment': task.environment,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'started_at': task.started_at.isoformat() if task.started_at else None,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                    'logs': task.logs
                },
                'message': 'Task retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return {
                'success': False,
                'error': {'code': 'GET_FAILED', 'message': str(e)}
            }, 500

@tasks_ns.route('/<int:task_id>/execute')
class TaskExecution(Resource):
    @api.doc('execute_task')
    @api.marshal_with(common_models['success_response'])
    def post(self, task_id):
        """Execute a task"""
        try:
            db = next(get_db())
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Task not found'}
                }, 404
            
            if task.status == 'running':
                return {
                    'success': False,
                    'error': {'code': 'TASK_RUNNING', 'message': 'Task is already running'}
                }, 409
            
            # Update task status
            task.status = 'running'
            task.started_at = datetime.utcnow()
            task.logs = f"Task {task.name} started at {task.started_at}\n"
            db.commit()
            
            # Simulate task execution
            import time
            time.sleep(1)  # Simulate work
            
            task.status = 'completed'
            task.completed_at = datetime.utcnow()
            task.logs += f"Task completed at {task.completed_at}\n"
            db.commit()
            
            return {
                'success': True,
                'data': {
                    'id': task.id,
                    'status': task.status,
                    'started_at': task.started_at.isoformat(),
                    'completed_at': task.completed_at.isoformat()
                },
                'message': 'Task executed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            return {
                'success': False,
                'error': {'code': 'EXECUTION_FAILED', 'message': str(e)}
            }, 500

@tasks_ns.route('/<int:task_id>/logs')
class TaskLogs(Resource):
    @api.doc('get_task_logs')
    @api.marshal_with(common_models['success_response'])
    def get(self, task_id):
        """Get task logs"""
        try:
            db = next(get_db())
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Task not found'}
                }, 404
            
            return {
                'success': True,
                'data': {
                    'task_id': task.id,
                    'logs': task.logs or 'No logs available'
                },
                'message': 'Task logs retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Error getting task logs: {e}")
            return {
                'success': False,
                'error': {'code': 'LOGS_FAILED', 'message': str(e)}
            }, 500

# Legacy endpoints
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'service': 'Task Manager',
        'version': '2.0.0',
        'status': 'active',
        'docs': '/docs/',
        'endpoints': {
            'tasks': '/api/v1/tasks',
            'health': '/api/v1/health'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return HealthCheck().get()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8851))
    app.run(host='0.0.0.0', port=port, debug=True)
