#!/usr/bin/env python3
"""
Log Manager API
Gestión centralizada de logs para IA-Ops
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime, timedelta
import glob

app = Flask(__name__)
CORS(app)

# Configuración
LOGS_DIR = '/app/logs'
LOG_SOURCES = {
    'web-interface': '/app/logs/web-interface',
    'github-runner': '/app/logs/github-runner',
    'techdocs-builder': '/app/logs/techdocs-builder',
    'datasync': '/app/logs/datasync',
    'testing-portal': '/app/logs/testing-portal',
    'minio': '/app/logs/minio'
}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'log-manager'})

@app.route('/logs/sources', methods=['GET'])
def list_log_sources():
    """Listar fuentes de logs disponibles"""
    available_sources = {}
    
    for source, path in LOG_SOURCES.items():
        if os.path.exists(path):
            files = glob.glob(f"{path}/*.log")
            available_sources[source] = {
                'path': path,
                'files': [os.path.basename(f) for f in files],
                'count': len(files)
            }
    
    return jsonify({
        'sources': available_sources,
        'total_sources': len(available_sources)
    })

@app.route('/logs/<source>', methods=['GET'])
def get_logs(source):
    """Obtener logs de una fuente específica"""
    if source not in LOG_SOURCES:
        return jsonify({'error': 'Invalid log source'}), 400
    
    log_path = LOG_SOURCES[source]
    if not os.path.exists(log_path):
        return jsonify({'error': 'Log source not found'}), 404
    
    # Parámetros de consulta
    lines = request.args.get('lines', 100, type=int)
    level = request.args.get('level', '').upper()
    since = request.args.get('since')  # ISO format
    
    log_files = glob.glob(f"{log_path}/*.log")
    if not log_files:
        return jsonify({'logs': [], 'count': 0})
    
    # Usar el archivo más reciente
    latest_log = max(log_files, key=os.path.getmtime)
    
    try:
        with open(latest_log, 'r') as f:
            log_lines = f.readlines()
        
        # Filtrar por nivel si se especifica
        if level:
            log_lines = [line for line in log_lines if level in line.upper()]
        
        # Filtrar por fecha si se especifica
        if since:
            try:
                since_date = datetime.fromisoformat(since.replace('Z', '+00:00'))
                # Aquí se podría implementar filtrado por fecha
                # Por simplicidad, se omite la implementación completa
            except ValueError:
                pass
        
        # Tomar las últimas N líneas
        recent_lines = log_lines[-lines:] if lines > 0 else log_lines
        
        logs = []
        for i, line in enumerate(recent_lines):
            logs.append({
                'line_number': len(log_lines) - len(recent_lines) + i + 1,
                'content': line.strip(),
                'timestamp': datetime.now().isoformat()  # Simplificado
            })
        
        return jsonify({
            'source': source,
            'file': os.path.basename(latest_log),
            'logs': logs,
            'count': len(logs),
            'total_lines': len(log_lines)
        })
    
    except Exception as e:
        logger.error(f"Error reading logs from {source}: {str(e)}")
        return jsonify({'error': f'Failed to read logs: {str(e)}'}), 500

@app.route('/logs/<source>/files', methods=['GET'])
def list_log_files(source):
    """Listar archivos de log de una fuente"""
    if source not in LOG_SOURCES:
        return jsonify({'error': 'Invalid log source'}), 400
    
    log_path = LOG_SOURCES[source]
    if not os.path.exists(log_path):
        return jsonify({'error': 'Log source not found'}), 404
    
    log_files = glob.glob(f"{log_path}/*.log")
    files_info = []
    
    for file_path in log_files:
        stat = os.stat(file_path)
        files_info.append({
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'path': file_path
        })
    
    # Ordenar por fecha de modificación (más reciente primero)
    files_info.sort(key=lambda x: x['modified'], reverse=True)
    
    return jsonify({
        'source': source,
        'files': files_info,
        'count': len(files_info)
    })

@app.route('/logs/<source>/search', methods=['GET'])
def search_logs(source):
    """Buscar en logs de una fuente"""
    if source not in LOG_SOURCES:
        return jsonify({'error': 'Invalid log source'}), 400
    
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    log_path = LOG_SOURCES[source]
    if not os.path.exists(log_path):
        return jsonify({'error': 'Log source not found'}), 404
    
    log_files = glob.glob(f"{log_path}/*.log")
    matches = []
    
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if query.lower() in line.lower():
                        matches.append({
                            'file': os.path.basename(log_file),
                            'line_number': line_num,
                            'content': line.strip(),
                            'timestamp': datetime.now().isoformat()
                        })
        except Exception as e:
            logger.error(f"Error searching in {log_file}: {str(e)}")
    
    return jsonify({
        'source': source,
        'query': query,
        'matches': matches,
        'count': len(matches)
    })

@app.route('/logs/stats', methods=['GET'])
def get_log_stats():
    """Obtener estadísticas de logs"""
    stats = {}
    total_size = 0
    total_files = 0
    
    for source, path in LOG_SOURCES.items():
        if os.path.exists(path):
            files = glob.glob(f"{path}/*.log")
            size = sum(os.path.getsize(f) for f in files)
            
            stats[source] = {
                'files': len(files),
                'size_bytes': size,
                'size_mb': round(size / (1024 * 1024), 2)
            }
            
            total_size += size
            total_files += len(files)
    
    stats['total'] = {
        'sources': len(stats),
        'files': total_files,
        'size_bytes': total_size,
        'size_mb': round(total_size / (1024 * 1024), 2)
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8852, debug=False)
