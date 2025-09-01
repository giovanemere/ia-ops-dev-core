#!/usr/bin/env python3
"""
Task Manager API
Gestión de tareas y builds para IA-Ops
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import subprocess
import logging
import threading
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración
TASKS_FILE = '/app/data/tasks.json'
LOGS_DIR = '/app/logs'

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_tasks():
    """Cargar tareas desde archivo JSON"""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """Guardar tareas en archivo JSON"""
    os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def execute_task_async(task_id):
    """Ejecutar tarea de forma asíncrona"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return
    
    # Actualizar estado a running
    task['status'] = 'running'
    task['started_at'] = datetime.now().isoformat()
    save_tasks(tasks)
    
    try:
        # Simular ejecución de tarea
        time.sleep(2)  # Simular trabajo
        
        # Actualizar estado a completed
        task['status'] = 'completed'
        task['completed_at'] = datetime.now().isoformat()
        task['logs'] += f"\n[{datetime.now()}] Task completed successfully"
        
    except Exception as e:
        task['status'] = 'failed'
        task['completed_at'] = datetime.now().isoformat()
        task['logs'] += f"\n[{datetime.now()}] Task failed: {str(e)}"
    
    save_tasks(tasks)

@app.route('/', methods=['GET'])
def index():
    """Información del servicio"""
    return jsonify({
        'service': 'Task Manager',
        'version': '1.0.0',
        'description': 'Gestión de tareas y builds para IA-Ops',
        'endpoints': {
            '/health': 'Health check',
            '/tasks': 'GET: Listar tareas, POST: Crear tarea',
            '/tasks/<id>': 'GET: Obtener tarea, PUT: Actualizar, DELETE: Eliminar',
            '/tasks/<id>/execute': 'POST: Ejecutar tarea',
            '/tasks/<id>/logs': 'GET: Obtener logs de tarea'
        },
        'status': 'running'
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'task-manager'})

@app.route('/tasks', methods=['GET'])
def list_tasks():
    """Listar todas las tareas"""
    tasks = load_tasks()
    
    # Filtros opcionales
    status = request.args.get('status')
    task_type = request.args.get('type')
    
    if status:
        tasks = [t for t in tasks if t['status'] == status]
    if task_type:
        tasks = [t for t in tasks if t['type'] == task_type]
    
    return jsonify({
        'success': True,
        'data': tasks,
        'count': len(tasks)
    })

@app.route('/tasks', methods=['POST'])
def create_task():
    """Crear nueva tarea"""
    data = request.get_json()
    
    required_fields = ['name', 'type', 'command']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'error': {'code': 'MISSING_FIELDS', 'message': 'Missing required fields'}
        }), 400
    
    tasks = load_tasks()
    
    new_task = {
        'id': len(tasks) + 1,
        'name': data['name'],
        'type': data['type'],
        'status': 'pending',
        'repository_id': data.get('repository_id'),
        'command': data['command'],
        'environment': data.get('environment', {}),
        'created_at': datetime.now().isoformat(),
        'started_at': None,
        'completed_at': None,
        'logs': f"[{datetime.now()}] Task created"
    }
    
    tasks.append(new_task)
    save_tasks(tasks)
    
    return jsonify({
        'success': True,
        'data': new_task,
        'message': 'Task created successfully'
    }), 201

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Obtener tarea por ID"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({
            'success': False,
            'error': {'code': 'TASK_NOT_FOUND', 'message': 'Task not found'}
        }), 404
    
    return jsonify({
        'success': True,
        'data': task
    })

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Actualizar tarea"""
    data = request.get_json()
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({
            'success': False,
            'error': {'code': 'TASK_NOT_FOUND', 'message': 'Task not found'}
        }), 404
    
    # Actualizar campos permitidos
    updatable_fields = ['name', 'type', 'command', 'environment']
    for field in updatable_fields:
        if field in data:
            task[field] = data[field]
    
    save_tasks(tasks)
    
    return jsonify({
        'success': True,
        'data': task,
        'message': 'Task updated successfully'
    })

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Eliminar tarea"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({
            'success': False,
            'error': {'code': 'TASK_NOT_FOUND', 'message': 'Task not found'}
        }), 404
    
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    
    return jsonify({
        'success': True,
        'message': 'Task deleted successfully'
    })

@app.route('/tasks/<int:task_id>/execute', methods=['POST'])
def execute_task(task_id):
    """Ejecutar tarea"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({
            'success': False,
            'error': {'code': 'TASK_NOT_FOUND', 'message': 'Task not found'}
        }), 404
    
    if task['status'] == 'running':
        return jsonify({
            'success': False,
            'error': {'code': 'TASK_RUNNING', 'message': 'Task is already running'}
        }), 400
    
    # Ejecutar tarea en hilo separado
    thread = threading.Thread(target=execute_task_async, args=(task_id,))
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Task execution started'
    })

@app.route('/tasks/<int:task_id>/logs', methods=['GET'])
def get_task_logs(task_id):
    """Obtener logs de tarea"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({
            'success': False,
            'error': {'code': 'TASK_NOT_FOUND', 'message': 'Task not found'}
        }), 404
    
    return jsonify({
        'success': True,
        'data': {
            'task_id': task_id,
            'logs': task['logs'],
            'status': task['status']
        }
    })

if __name__ == '__main__':
    os.makedirs('/app/data', exist_ok=True)
    os.makedirs('/app/logs', exist_ok=True)
    app.run(host='0.0.0.0', port=8851, debug=True)
