#!/usr/bin/env python3
"""
Simple Mock Services - Versión simplificada y funcional
"""

from flask import Flask, jsonify, request
import time
import threading
from datetime import datetime

# Contadores globales
counters = {'repo': 0, 'task': 0, 'log': 0}

def create_repository_mock():
    """Crear mock del Repository Manager"""
    app = Flask('repository-mock')
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
    
    @app.route('/health')
    def health():
        return jsonify({
            'success': True,
            'data': {
                'status': 'healthy',
                'service': 'Repository Manager Mock'
            }
        })
    
    @app.route('/api/v1/repositories', methods=['GET'])
    def list_repositories():
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': 1,
                    'name': 'mock-repo-1',
                    'url': 'https://github.com/mock/repo1.git',
                    'branch': 'main',
                    'status': 'active'
                }
            ]
        })
    
    @app.route('/api/v1/repositories', methods=['POST'])
    def create_repository():
        data = request.get_json() or {}
        counters['repo'] += 1
        
        return jsonify({
            'success': True,
            'data': {
                'id': counters['repo'],
                'name': data.get('name', 'unnamed'),
                'url': data.get('url', ''),
                'branch': data.get('branch', 'main'),
                'description': data.get('description', ''),
                'status': 'active',
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }
        })
    
    @app.route('/api/v1/repositories/<int:repo_id>')
    def get_repository(repo_id):
        return jsonify({
            'success': True,
            'data': {
                'id': repo_id,
                'name': f'mock-repo-{repo_id}',
                'url': f'https://github.com/mock/repo{repo_id}.git',
                'branch': 'main',
                'status': 'active'
            }
        })
    
    return app

def create_task_mock():
    """Crear mock del Task Manager"""
    app = Flask('task-mock')
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
    
    @app.route('/health')
    def health():
        return jsonify({
            'success': True,
            'data': {
                'status': 'healthy',
                'service': 'Task Manager Mock'
            }
        })
    
    @app.route('/api/v1/tasks', methods=['GET'])
    def list_tasks():
        return jsonify({
            'success': True,
            'data': []
        })
    
    @app.route('/api/v1/tasks', methods=['POST'])
    def create_task():
        data = request.get_json() or {}
        counters['task'] += 1
        
        return jsonify({
            'success': True,
            'data': {
                'id': counters['task'],
                'name': data.get('name', 'unnamed-task'),
                'type': data.get('type', 'unknown'),
                'status': 'pending',
                'repository_id': data.get('repository_id'),
                'command': data.get('command', ''),
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }
        })
    
    @app.route('/api/v1/tasks/<int:task_id>/execute', methods=['POST'])
    def execute_task(task_id):
        # Simular delay de ejecución
        time.sleep(1)
        
        return jsonify({
            'success': True,
            'data': {
                'id': task_id,
                'status': 'completed',
                'started_at': datetime.utcnow().isoformat() + 'Z',
                'completed_at': datetime.utcnow().isoformat() + 'Z'
            }
        })
    
    @app.route('/api/v1/tasks/<int:task_id>/logs')
    def get_task_logs(task_id):
        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'logs': f'Mock task {task_id} execution started\\nMock task completed successfully\\n'
            }
        })
    
    return app

def create_log_mock():
    """Crear mock del Log Manager"""
    app = Flask('log-mock')
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response
    
    @app.route('/health')
    def health():
        return jsonify({
            'success': True,
            'data': {
                'status': 'healthy',
                'service': 'Log Manager Mock'
            }
        })
    
    @app.route('/api/v1/logs', methods=['GET'])
    def list_logs():
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': 1,
                    'service': 'mock-service',
                    'level': 'info',
                    'message': 'Mock log entry',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            ]
        })
    
    @app.route('/api/v1/logs', methods=['POST'])
    def create_log():
        data = request.get_json() or {}
        counters['log'] += 1
        
        return jsonify({
            'success': True,
            'data': {
                'id': counters['log'],
                'service': data.get('service', 'unknown'),
                'level': data.get('level', 'info'),
                'message': data.get('message', ''),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        })
    
    return app

def start_all_mocks():
    """Iniciar todos los servicios mock"""
    print("🎭 Starting Simple Mock Services...")
    
    # Crear apps
    repo_app = create_repository_mock()
    task_app = create_task_mock()
    log_app = create_log_mock()
    
    # Iniciar en threads
    def run_repo():
        repo_app.run(host='0.0.0.0', port=18860, debug=False, use_reloader=False)
    
    def run_task():
        task_app.run(host='0.0.0.0', port=18861, debug=False, use_reloader=False)
    
    def run_log():
        log_app.run(host='0.0.0.0', port=18862, debug=False, use_reloader=False)
    
    threads = [
        threading.Thread(target=run_repo, daemon=True),
        threading.Thread(target=run_task, daemon=True),
        threading.Thread(target=run_log, daemon=True)
    ]
    
    for thread in threads:
        thread.start()
    
    print("✅ Mock services started:")
    print("  📁 Repository Manager: http://localhost:18860")
    print("  📋 Task Manager: http://localhost:18861")
    print("  📊 Log Manager: http://localhost:18862")
    
    return threads

if __name__ == '__main__':
    threads = start_all_mocks()
    
    print("\n🧪 Mock services ready for testing!")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping mock services...")
