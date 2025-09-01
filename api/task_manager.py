#!/usr/bin/env python3
"""
Task Manager API
Gestión centralizada de tareas y builds para IA-Ops
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from enum import Enum

app = Flask(__name__)
CORS(app)

# Configuración
TASKS_FILE = '/app/data/tasks.json'

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

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

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'task-manager'})

@app.route('/tasks', methods=['GET'])
def list_tasks():
    """Listar todas las tareas"""
    tasks = load_tasks()
    status_filter = request.args.get('status')
    
    if status_filter:
        tasks = [t for t in tasks if t['status'] == status_filter]
    
    return jsonify({
        'tasks': tasks,
        'count': len(tasks)
    })

@app.route('/tasks', methods=['POST'])
def create_task():
    """Crear nueva tarea"""
    data = request.get_json()
    
    required_fields = ['name', 'type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    tasks = load_tasks()
    
    new_task = {
        'id': len(tasks) + 1,
        'name': data['name'],
        'type': data['type'],
        'description': data.get('description', ''),
        'repository': data.get('repository'),
        'status': TaskStatus.PENDING.value,
        'progress': 0,
        'created_at': datetime.now().isoformat(),
        'started_at': None,
        'completed_at': None,
        'logs': [],
        'metadata': data.get('metadata', {})
    }
    
    tasks.append(new_task)
    save_tasks(tasks)
    
    logger.info(f"Task created: {new_task['name']}")
    return jsonify(new_task), 201

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Obtener tarea específica"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task)

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Actualizar tarea"""
    data = request.get_json()
    tasks = load_tasks()
    
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Actualizar campos permitidos
    for field in ['status', 'progress', 'description']:
        if field in data:
            task[field] = data[field]
    
    # Actualizar timestamps según el estado
    if data.get('status') == TaskStatus.RUNNING.value and not task['started_at']:
        task['started_at'] = datetime.now().isoformat()
    elif data.get('status') in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
        task['completed_at'] = datetime.now().isoformat()
    
    task['updated_at'] = datetime.now().isoformat()
    save_tasks(tasks)
    
    logger.info(f"Task updated: {task['name']} - Status: {task['status']}")
    return jsonify(task)

@app.route('/tasks/<int:task_id>/logs', methods=['POST'])
def add_task_log(task_id):
    """Agregar log a tarea"""
    data = request.get_json()
    tasks = load_tasks()
    
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': data.get('level', 'INFO'),
        'message': data.get('message', ''),
        'source': data.get('source', 'system')
    }
    
    task['logs'].append(log_entry)
    save_tasks(tasks)
    
    return jsonify(log_entry), 201

@app.route('/tasks/<int:task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Cancelar tarea"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if task['status'] in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
        return jsonify({'error': 'Cannot cancel completed task'}), 400
    
    task['status'] = TaskStatus.CANCELLED.value
    task['completed_at'] = datetime.now().isoformat()
    save_tasks(tasks)
    
    logger.info(f"Task cancelled: {task['name']}")
    return jsonify({'message': 'Task cancelled successfully', 'task': task})

@app.route('/tasks/stats', methods=['GET'])
def get_task_stats():
    """Obtener estadísticas de tareas"""
    tasks = load_tasks()
    
    stats = {
        'total': len(tasks),
        'pending': len([t for t in tasks if t['status'] == TaskStatus.PENDING.value]),
        'running': len([t for t in tasks if t['status'] == TaskStatus.RUNNING.value]),
        'completed': len([t for t in tasks if t['status'] == TaskStatus.COMPLETED.value]),
        'failed': len([t for t in tasks if t['status'] == TaskStatus.FAILED.value]),
        'cancelled': len([t for t in tasks if t['status'] == TaskStatus.CANCELLED.value])
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8851, debug=False)
