#!/usr/bin/env python3
"""
DataSync Manager API
Gestión de sincronización de datos para IA-Ops
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import logging
import subprocess
from datetime import datetime
from enum import Enum

app = Flask(__name__)
CORS(app)

# Configuración
SYNC_JOBS_FILE = '/app/data/sync_jobs.json'
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9898')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin123')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

def load_sync_jobs():
    """Cargar trabajos de sincronización"""
    if os.path.exists(SYNC_JOBS_FILE):
        with open(SYNC_JOBS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_sync_jobs(jobs):
    """Guardar trabajos de sincronización"""
    os.makedirs(os.path.dirname(SYNC_JOBS_FILE), exist_ok=True)
    with open(SYNC_JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'datasync-manager'})

@app.route('/sync/jobs', methods=['GET'])
def list_sync_jobs():
    """Listar trabajos de sincronización"""
    jobs = load_sync_jobs()
    status_filter = request.args.get('status')
    
    if status_filter:
        jobs = [j for j in jobs if j['status'] == status_filter]
    
    return jsonify({
        'jobs': jobs,
        'count': len(jobs)
    })

@app.route('/sync/jobs', methods=['POST'])
def create_sync_job():
    """Crear nuevo trabajo de sincronización"""
    data = request.get_json()
    
    required_fields = ['source', 'destination', 'type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    jobs = load_sync_jobs()
    
    new_job = {
        'id': len(jobs) + 1,
        'source': data['source'],
        'destination': data['destination'],
        'type': data['type'],  # 'upload', 'download', 'sync'
        'status': SyncStatus.PENDING.value,
        'progress': 0,
        'created_at': datetime.now().isoformat(),
        'started_at': None,
        'completed_at': None,
        'error_message': None,
        'files_processed': 0,
        'total_files': 0
    }
    
    jobs.append(new_job)
    save_sync_jobs(jobs)
    
    logger.info(f"Sync job created: {new_job['id']}")
    return jsonify(new_job), 201

@app.route('/sync/jobs/<int:job_id>', methods=['GET'])
def get_sync_job(job_id):
    """Obtener trabajo específico"""
    jobs = load_sync_jobs()
    job = next((j for j in jobs if j['id'] == job_id), None)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job)

@app.route('/sync/jobs/<int:job_id>/start', methods=['POST'])
def start_sync_job(job_id):
    """Iniciar trabajo de sincronización"""
    jobs = load_sync_jobs()
    job = next((j for j in jobs if j['id'] == job_id), None)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job['status'] != SyncStatus.PENDING.value:
        return jsonify({'error': 'Job is not in pending status'}), 400
    
    job['status'] = SyncStatus.RUNNING.value
    job['started_at'] = datetime.now().isoformat()
    save_sync_jobs(jobs)
    
    # Aquí iría la lógica real de sincronización
    # Por ahora simulamos el proceso
    
    logger.info(f"Sync job started: {job_id}")
    return jsonify({'message': 'Sync job started', 'job': job})

@app.route('/sync/buckets', methods=['GET'])
def list_buckets():
    """Listar buckets disponibles en MinIO"""
    try:
        # Simulación - en producción usaría minio client
        buckets = [
            {'name': 'repositories', 'objects': 150},
            {'name': 'documentation', 'objects': 45},
            {'name': 'builds', 'objects': 89},
            {'name': 'logs', 'objects': 234}
        ]
        return jsonify({
            'buckets': buckets,
            'count': len(buckets)
        })
    except Exception as e:
        logger.error(f"Error listing buckets: {str(e)}")
        return jsonify({'error': f'Failed to list buckets: {str(e)}'}), 500

@app.route('/sync/status', methods=['GET'])
def sync_status():
    """Estado general de sincronización"""
    jobs = load_sync_jobs()
    
    stats = {
        'total': len(jobs),
        'pending': len([j for j in jobs if j['status'] == SyncStatus.PENDING.value]),
        'running': len([j for j in jobs if j['status'] == SyncStatus.RUNNING.value]),
        'completed': len([j for j in jobs if j['status'] == SyncStatus.COMPLETED.value]),
        'failed': len([j for j in jobs if j['status'] == SyncStatus.FAILED.value])
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8863, debug=False)
