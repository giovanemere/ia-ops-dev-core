#!/usr/bin/env python3
"""
GitHub Runner Manager API
Gestión de GitHub Actions Runners para IA-Ops
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import logging
import subprocess
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración
RUNNERS_FILE = '/app/data/runners.json'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'giovanemere/ia-ops')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_runners():
    """Cargar información de runners"""
    if os.path.exists(RUNNERS_FILE):
        with open(RUNNERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_runners(runners):
    """Guardar información de runners"""
    os.makedirs(os.path.dirname(RUNNERS_FILE), exist_ok=True)
    with open(RUNNERS_FILE, 'w') as f:
        json.dump(runners, f, indent=2)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'github-runner-manager'})

@app.route('/runners', methods=['GET'])
def list_runners():
    """Listar runners registrados"""
    runners = load_runners()
    return jsonify({
        'runners': runners,
        'count': len(runners)
    })

@app.route('/runners', methods=['POST'])
def register_runner():
    """Registrar nuevo runner"""
    data = request.get_json()
    
    required_fields = ['name', 'labels']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    runners = load_runners()
    
    new_runner = {
        'id': len(runners) + 1,
        'name': data['name'],
        'labels': data['labels'],
        'status': 'offline',
        'registered_at': datetime.now().isoformat(),
        'last_seen': None,
        'jobs_completed': 0,
        'current_job': None
    }
    
    runners.append(new_runner)
    save_runners(runners)
    
    logger.info(f"Runner registered: {new_runner['name']}")
    return jsonify(new_runner), 201

@app.route('/runners/<int:runner_id>', methods=['PUT'])
def update_runner(runner_id):
    """Actualizar estado del runner"""
    data = request.get_json()
    runners = load_runners()
    
    runner = next((r for r in runners if r['id'] == runner_id), None)
    if not runner:
        return jsonify({'error': 'Runner not found'}), 404
    
    # Actualizar campos permitidos
    for field in ['status', 'last_seen', 'current_job', 'jobs_completed']:
        if field in data:
            runner[field] = data[field]
    
    save_runners(runners)
    
    logger.info(f"Runner updated: {runner['name']}")
    return jsonify(runner)

@app.route('/runners/<int:runner_id>/start', methods=['POST'])
def start_runner(runner_id):
    """Iniciar runner"""
    runners = load_runners()
    runner = next((r for r in runners if r['id'] == runner_id), None)
    
    if not runner:
        return jsonify({'error': 'Runner not found'}), 404
    
    try:
        # Aquí iría la lógica para iniciar el runner
        runner['status'] = 'starting'
        runner['last_seen'] = datetime.now().isoformat()
        save_runners(runners)
        
        logger.info(f"Runner starting: {runner['name']}")
        return jsonify({'message': 'Runner start initiated', 'runner': runner})
    
    except Exception as e:
        logger.error(f"Error starting runner: {str(e)}")
        return jsonify({'error': f'Failed to start runner: {str(e)}'}), 500

@app.route('/runners/<int:runner_id>/stop', methods=['POST'])
def stop_runner(runner_id):
    """Detener runner"""
    runners = load_runners()
    runner = next((r for r in runners if r['id'] == runner_id), None)
    
    if not runner:
        return jsonify({'error': 'Runner not found'}), 404
    
    try:
        runner['status'] = 'offline'
        runner['current_job'] = None
        save_runners(runners)
        
        logger.info(f"Runner stopped: {runner['name']}")
        return jsonify({'message': 'Runner stopped', 'runner': runner})
    
    except Exception as e:
        logger.error(f"Error stopping runner: {str(e)}")
        return jsonify({'error': f'Failed to stop runner: {str(e)}'}), 500

@app.route('/runners/stats', methods=['GET'])
def runner_stats():
    """Estadísticas de runners"""
    runners = load_runners()
    
    stats = {
        'total': len(runners),
        'online': len([r for r in runners if r['status'] == 'online']),
        'offline': len([r for r in runners if r['status'] == 'offline']),
        'busy': len([r for r in runners if r['status'] == 'busy']),
        'total_jobs_completed': sum(r.get('jobs_completed', 0) for r in runners)
    }
    
    return jsonify(stats)

@app.route('/jobs', methods=['GET'])
def list_jobs():
    """Listar trabajos de GitHub Actions"""
    # Simulación - en producción consultaría la API de GitHub
    jobs = [
        {
            'id': 1,
            'name': 'Build Documentation',
            'status': 'completed',
            'runner': 'iaops-runner-1',
            'started_at': '2025-09-01T10:00:00Z',
            'completed_at': '2025-09-01T10:05:00Z'
        },
        {
            'id': 2,
            'name': 'Deploy to Production',
            'status': 'running',
            'runner': 'iaops-runner-2',
            'started_at': '2025-09-01T10:10:00Z',
            'completed_at': None
        }
    ]
    
    return jsonify({
        'jobs': jobs,
        'count': len(jobs)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8864, debug=False)
