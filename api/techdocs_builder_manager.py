#!/usr/bin/env python3
"""
TechDocs Builder Manager API
Gestión de construcción de documentación para IA-Ops
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
BUILDS_FILE = '/app/data/builds.json'
DOCS_OUTPUT_DIR = '/app/data/docs_output'

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuildStatus(Enum):
    QUEUED = "queued"
    BUILDING = "building"
    COMPLETED = "completed"
    FAILED = "failed"

def load_builds():
    """Cargar historial de builds"""
    if os.path.exists(BUILDS_FILE):
        with open(BUILDS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_builds(builds):
    """Guardar historial de builds"""
    os.makedirs(os.path.dirname(BUILDS_FILE), exist_ok=True)
    with open(BUILDS_FILE, 'w') as f:
        json.dump(builds, f, indent=2)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'techdocs-builder-manager'})

@app.route('/builds', methods=['GET'])
def list_builds():
    """Listar builds de documentación"""
    builds = load_builds()
    status_filter = request.args.get('status')
    
    if status_filter:
        builds = [b for b in builds if b['status'] == status_filter]
    
    return jsonify({
        'builds': builds,
        'count': len(builds)
    })

@app.route('/builds', methods=['POST'])
def create_build():
    """Crear nuevo build de documentación"""
    data = request.get_json()
    
    required_fields = ['repository', 'branch']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    builds = load_builds()
    
    new_build = {
        'id': len(builds) + 1,
        'repository': data['repository'],
        'branch': data.get('branch', 'main'),
        'commit_sha': data.get('commit_sha', ''),
        'status': BuildStatus.QUEUED.value,
        'created_at': datetime.now().isoformat(),
        'started_at': None,
        'completed_at': None,
        'duration': None,
        'output_path': None,
        'error_message': None,
        'pages_built': 0,
        'assets_processed': 0
    }
    
    builds.append(new_build)
    save_builds(builds)
    
    logger.info(f"Build created: {new_build['repository']} - {new_build['id']}")
    return jsonify(new_build), 201

@app.route('/builds/<int:build_id>', methods=['GET'])
def get_build(build_id):
    """Obtener build específico"""
    builds = load_builds()
    build = next((b for b in builds if b['id'] == build_id), None)
    
    if not build:
        return jsonify({'error': 'Build not found'}), 404
    
    return jsonify(build)

@app.route('/builds/<int:build_id>/start', methods=['POST'])
def start_build(build_id):
    """Iniciar build de documentación"""
    builds = load_builds()
    build = next((b for b in builds if b['id'] == build_id), None)
    
    if not build:
        return jsonify({'error': 'Build not found'}), 404
    
    if build['status'] != BuildStatus.QUEUED.value:
        return jsonify({'error': 'Build is not in queued status'}), 400
    
    build['status'] = BuildStatus.BUILDING.value
    build['started_at'] = datetime.now().isoformat()
    save_builds(builds)
    
    # Aquí iría la lógica real de construcción
    # Por ahora simulamos el proceso
    
    logger.info(f"Build started: {build_id}")
    return jsonify({'message': 'Build started', 'build': build})

@app.route('/builds/<int:build_id>/cancel', methods=['POST'])
def cancel_build(build_id):
    """Cancelar build"""
    builds = load_builds()
    build = next((b for b in builds if b['id'] == build_id), None)
    
    if not build:
        return jsonify({'error': 'Build not found'}), 404
    
    if build['status'] not in [BuildStatus.QUEUED.value, BuildStatus.BUILDING.value]:
        return jsonify({'error': 'Build cannot be cancelled'}), 400
    
    build['status'] = BuildStatus.FAILED.value
    build['completed_at'] = datetime.now().isoformat()
    build['error_message'] = 'Build cancelled by user'
    save_builds(builds)
    
    logger.info(f"Build cancelled: {build_id}")
    return jsonify({'message': 'Build cancelled', 'build': build})

@app.route('/builds/stats', methods=['GET'])
def build_stats():
    """Estadísticas de builds"""
    builds = load_builds()
    
    stats = {
        'total': len(builds),
        'queued': len([b for b in builds if b['status'] == BuildStatus.QUEUED.value]),
        'building': len([b for b in builds if b['status'] == BuildStatus.BUILDING.value]),
        'completed': len([b for b in builds if b['status'] == BuildStatus.COMPLETED.value]),
        'failed': len([b for b in builds if b['status'] == BuildStatus.FAILED.value])
    }
    
    return jsonify(stats)

@app.route('/templates', methods=['GET'])
def list_templates():
    """Listar plantillas de documentación disponibles"""
    templates = [
        {
            'name': 'mkdocs-material',
            'description': 'Material Design theme for MkDocs',
            'version': '9.4.0',
            'features': ['search', 'navigation', 'dark_mode']
        },
        {
            'name': 'mkdocs-basic',
            'description': 'Basic MkDocs template',
            'version': '1.5.0',
            'features': ['search', 'navigation']
        }
    ]
    
    return jsonify({
        'templates': templates,
        'count': len(templates)
    })

@app.route('/sites', methods=['GET'])
def list_sites():
    """Listar sitios de documentación generados"""
    # Simulación - en producción escanearia el directorio de salida
    sites = [
        {
            'name': 'ia-ops-main',
            'repository': 'ia-ops',
            'branch': 'main',
            'last_build': '2025-09-01T10:00:00Z',
            'url': '/docs/ia-ops-main',
            'status': 'active'
        },
        {
            'name': 'ia-ops-dev',
            'repository': 'ia-ops',
            'branch': 'develop',
            'last_build': '2025-09-01T09:30:00Z',
            'url': '/docs/ia-ops-dev',
            'status': 'active'
        }
    ]
    
    return jsonify({
        'sites': sites,
        'count': len(sites)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8865, debug=False)
