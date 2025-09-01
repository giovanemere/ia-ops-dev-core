#!/usr/bin/env python3
"""
Portal centralizado de documentación Swagger para IA-Ops Dev Core Services
"""

from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# Configuración de servicios
SERVICES = {
    'repository-manager': {
        'name': 'Repository Manager',
        'url': 'http://localhost:8860',
        'port': 8860,
        'description': 'Gestión de repositorios con PostgreSQL y MinIO'
    },
    'task-manager': {
        'name': 'Task Manager', 
        'url': 'http://localhost:8861',
        'port': 8861,
        'description': 'Gestión de tareas con PostgreSQL y Redis'
    },
    'log-manager': {
        'name': 'Log Manager',
        'url': 'http://localhost:8862', 
        'port': 8862,
        'description': 'Gestión de logs con PostgreSQL'
    },
    'datasync-manager': {
        'name': 'DataSync Manager',
        'url': 'http://localhost:8863',
        'port': 8863, 
        'description': 'Sincronización de datos con PostgreSQL y MinIO'
    },
    'github-runner-manager': {
        'name': 'GitHub Runner Manager',
        'url': 'http://localhost:8864',
        'port': 8864,
        'description': 'Gestión de runners de GitHub con PostgreSQL'
    },
    'techdocs-builder': {
        'name': 'TechDocs Builder',
        'url': 'http://localhost:8865',
        'port': 8865,
        'description': 'Constructor de documentación con PostgreSQL'
    }
}

PORTAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA-Ops Dev Core - API Documentation Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            padding: 40px 0;
        }
        .header h1 { font-size: 3rem; margin-bottom: 10px; }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        .service-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-left: 5px solid #667eea;
        }
        .service-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        .service-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .service-name {
            font-size: 1.4rem;
            font-weight: bold;
            color: #333;
        }
        .service-status {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .status-online { background: #d4edda; color: #155724; }
        .status-offline { background: #f8d7da; color: #721c24; }
        .service-description {
            color: #666;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        .service-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: #888;
        }
        .service-actions {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s ease;
            cursor: pointer;
            font-size: 0.9rem;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background: #5a6268;
            transform: translateY(-2px);
        }
        .stats-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .stat-item {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .footer {
            text-align: center;
            color: white;
            opacity: 0.8;
            margin-top: 40px;
        }
        .integration-badges {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: bold;
        }
        .badge-postgresql { background: #336791; color: white; }
        .badge-redis { background: #dc382d; color: white; }
        .badge-minio { background: #c72e29; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 IA-Ops Dev Core</h1>
            <p>Portal de Documentación de APIs - Servicios Integrados</p>
        </div>

        <div class="stats-section">
            <h2 style="margin-bottom: 20px; text-align: center;">📊 Estado del Sistema</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number" id="services-online">{{ services_online }}</div>
                    <div class="stat-label">Servicios Online</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ total_services }}</div>
                    <div class="stat-label">Total Servicios</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">3</div>
                    <div class="stat-label">Bases de Datos</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{{ uptime }}</div>
                    <div class="stat-label">Uptime</div>
                </div>
            </div>
        </div>

        <div class="services-grid">
            {% for service_id, service in services.items() %}
            <div class="service-card">
                <div class="service-header">
                    <div class="service-name">{{ service.name }}</div>
                    <div class="service-status {{ 'status-online' if service.status == 'online' else 'status-offline' }}">
                        {{ service.status.upper() }}
                    </div>
                </div>
                <div class="service-description">{{ service.description }}</div>
                <div class="service-info">
                    <span>Puerto: {{ service.port }}</span>
                    <span>Versión: 2.0.0</span>
                </div>
                <div class="integration-badges">
                    {% if 'postgresql' in service.integrations %}
                    <span class="badge badge-postgresql">PostgreSQL</span>
                    {% endif %}
                    {% if 'redis' in service.integrations %}
                    <span class="badge badge-redis">Redis</span>
                    {% endif %}
                    {% if 'minio' in service.integrations %}
                    <span class="badge badge-minio">MinIO</span>
                    {% endif %}
                </div>
                <div class="service-actions">
                    <a href="{{ service.url }}/docs/" class="btn btn-primary" target="_blank">
                        📚 Documentación
                    </a>
                    <a href="{{ service.url }}/health" class="btn btn-secondary" target="_blank">
                        ❤️ Health Check
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="footer">
            <p>🛠️ IA-Ops Dev Core Services - Integrado con PostgreSQL, Redis y MinIO</p>
            <p>Portal de pruebas: <a href="https://github.com/giovanemere/ia-ops-veritas" style="color: #fff;">ia-ops-veritas</a></p>
        </div>
    </div>

    <script>
        // Auto-refresh service status
        setInterval(async () => {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                document.getElementById('services-online').textContent = data.services_online;
            } catch (error) {
                console.error('Error updating status:', error);
            }
        }, 30000); // Update every 30 seconds
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Portal principal de documentación"""
    
    # Verificar estado de servicios
    services_status = {}
    services_online = 0
    
    for service_id, service in SERVICES.items():
        try:
            response = requests.get(f"{service['url']}/health", timeout=5)
            if response.status_code == 200:
                services_status[service_id] = {
                    **service,
                    'status': 'online',
                    'integrations': get_service_integrations(service_id)
                }
                services_online += 1
            else:
                services_status[service_id] = {
                    **service,
                    'status': 'offline',
                    'integrations': get_service_integrations(service_id)
                }
        except:
            services_status[service_id] = {
                **service,
                'status': 'offline',
                'integrations': get_service_integrations(service_id)
            }
    
    return render_template_string(PORTAL_TEMPLATE, 
                                services=services_status,
                                services_online=services_online,
                                total_services=len(SERVICES),
                                uptime="99.9%")

@app.route('/api/status')
def api_status():
    """API para obtener estado de servicios"""
    
    services_online = 0
    service_details = {}
    
    for service_id, service in SERVICES.items():
        try:
            response = requests.get(f"{service['url']}/health", timeout=5)
            if response.status_code == 200:
                services_online += 1
                service_details[service_id] = {
                    'status': 'online',
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                service_details[service_id] = {
                    'status': 'offline',
                    'response_time': None
                }
        except Exception as e:
            service_details[service_id] = {
                'status': 'offline',
                'error': str(e)
            }
    
    return jsonify({
        'services_online': services_online,
        'total_services': len(SERVICES),
        'services': service_details,
        'timestamp': '2025-09-01T22:31:45.829Z'
    })

@app.route('/api/services')
def api_services():
    """API para obtener información de servicios"""
    return jsonify(SERVICES)

@app.route('/api/openapi/<service_id>')
def get_openapi_spec(service_id):
    """Obtener especificación OpenAPI de un servicio"""
    if service_id not in SERVICES:
        return jsonify({'error': 'Service not found'}), 404
    
    try:
        service = SERVICES[service_id]
        response = requests.get(f"{service['url']}/swagger.json", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({'error': 'OpenAPI spec not available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_service_integrations(service_id):
    """Obtener integraciones de un servicio"""
    integrations_map = {
        'repository-manager': ['postgresql', 'minio'],
        'task-manager': ['postgresql', 'redis'],
        'log-manager': ['postgresql'],
        'datasync-manager': ['postgresql', 'minio'],
        'github-runner-manager': ['postgresql'],
        'techdocs-builder': ['postgresql']
    }
    return integrations_map.get(service_id, [])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8870))
    print(f"🚀 IA-Ops Swagger Portal starting on port {port}")
    print(f"📚 Access documentation at: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
