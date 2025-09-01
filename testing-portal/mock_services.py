#!/usr/bin/env python3
"""
Mock Services para IA-Ops Testing Portal
Simula todos los servicios del backend para pruebas aisladas
"""

from flask import Flask, jsonify, request
import time
import random
import threading
from datetime import datetime, timedelta
import json

class MockServiceManager:
    def __init__(self):
        self.services = {}
        self.auto_increment_counters = {}
        
    def create_mock_service(self, service_name, port, endpoints_config):
        """Crear un servicio mock"""
        app = Flask(f'mock-{service_name}')
        
        # Configurar CORS
        @app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        # Crear endpoints dinámicamente
        for endpoint_path, endpoint_config in endpoints_config.items():
            self._create_endpoint(app, endpoint_path, endpoint_config, service_name)
        
        self.services[service_name] = {
            'app': app,
            'port': port,
            'thread': None
        }
        
        return app
    
    def _create_endpoint(self, app, path, config, service_name):
        """Crear endpoint dinámico"""
        
        def endpoint_handler(**kwargs):
            # Simular delay si está configurado
            if 'delay' in config:
                delay_ms = self._parse_delay(config['delay'])
                time.sleep(delay_ms / 1000)
            
            # Obtener configuración del método HTTP
            method = request.method
            method_config = config.get(method, config)
            
            if 'response' not in method_config:
                return jsonify({'error': 'Method not allowed'}), 405
            
            # Procesar respuesta
            response_data = self._process_response(
                method_config['response'], 
                request, 
                kwargs, 
                service_name
            )
            
            # Simular errores aleatorios si está configurado
            if 'error_rate' in method_config:
                if random.random() < method_config['error_rate']:
                    return jsonify({'error': 'Simulated error'}), 500
            
            return jsonify(response_data)
        
        # Registrar endpoint con Flask
        endpoint_handler.__name__ = f"{service_name}_{path.replace('/', '_').replace('{', '').replace('}', '')}"
        
        # Manejar parámetros de ruta
        if '{' in path:
            # Convertir {id} a <int:id>
            flask_path = path.replace('{id}', '<int:id>').replace('{', '<').replace('}', '>')
        else:
            flask_path = path
        
        app.add_url_rule(
            flask_path,
            endpoint_handler.__name__,
            endpoint_handler,
            methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        )
    
    def _process_response(self, response_template, request_obj, path_params, service_name):
        """Procesar template de respuesta con datos dinámicos"""
        response_str = json.dumps(response_template)
        
        # Reemplazar placeholders
        replacements = {
            '{current_timestamp}': datetime.utcnow().isoformat() + 'Z',
            '{auto_increment}': str(self._get_auto_increment(service_name)),
            '{random}': str(random.randint(1000, 9999))
        }
        
        # Agregar datos del request
        if request_obj.is_json and request_obj.json:
            for key, value in request_obj.json.items():
                replacements[f'{{request.{key}}}'] = str(value)
        
        # Agregar parámetros de ruta
        for key, value in path_params.items():
            replacements[f'{{path.{key}}}'] = str(value)
        
        # Aplicar reemplazos
        for placeholder, value in replacements.items():
            response_str = response_str.replace(placeholder, value)
        
        return json.loads(response_str)
    
    def _get_auto_increment(self, service_name):
        """Obtener siguiente ID auto-incremental"""
        if service_name not in self.auto_increment_counters:
            self.auto_increment_counters[service_name] = 1
        else:
            self.auto_increment_counters[service_name] += 1
        return self.auto_increment_counters[service_name]
    
    def _parse_delay(self, delay_str):
        """Parsear string de delay a milisegundos"""
        if delay_str.endswith('ms'):
            return int(delay_str[:-2])
        elif delay_str.endswith('s'):
            return int(delay_str[:-1]) * 1000
        return int(delay_str)
    
    def start_service(self, service_name):
        """Iniciar servicio mock"""
        if service_name not in self.services:
            raise ValueError(f"Service {service_name} not found")
        
        service = self.services[service_name]
        
        def run_service():
            service['app'].run(
                host='0.0.0.0',
                port=service['port'],
                debug=False,
                use_reloader=False
            )
        
        service['thread'] = threading.Thread(target=run_service, daemon=True)
        service['thread'].start()
        
        print(f"✅ Mock service {service_name} started on port {service['port']}")
    
    def start_all_services(self):
        """Iniciar todos los servicios mock"""
        for service_name in self.services:
            self.start_service(service_name)
        
        print(f"🚀 Started {len(self.services)} mock services")

# Configuración de servicios mock
MOCK_SERVICES_CONFIG = {
    'repository-manager': {
        'port': 18860,
        'endpoints': {
            '/health': {
                'GET': {
                    'response': {
                        'success': True,
                        'data': {
                            'status': 'healthy',
                            'service': 'Repository Manager Mock'
                        }
                    },
                    'delay': '50ms'
                }
            },
            '/api/v1/repositories': {
                'GET': {
                    'response': {
                        'success': True,
                        'data': [
                            {
                                'id': 1,
                                'name': 'mock-repo-1',
                                'url': 'https://github.com/mock/repo1.git',
                                'branch': 'main',
                                'status': 'active',
                                'created_at': '2025-09-01T20:00:00Z'
                            },
                            {
                                'id': 2,
                                'name': 'mock-repo-2',
                                'url': 'https://github.com/mock/repo2.git',
                                'branch': 'develop',
                                'status': 'active',
                                'created_at': '2025-09-01T21:00:00Z'
                            }
                        ]
                    }
                },
                'POST': {
                    'response': {
                        'success': True,
                        'data': {
                            'id': '{auto_increment}',
                            'name': '{request.name}',
                            'url': '{request.url}',
                            'branch': '{request.branch}',
                            'description': '{request.description}',
                            'status': 'active',
                            'created_at': '{current_timestamp}'
                        }
                    }
                }
            },
            '/api/v1/repositories/<int:id>': {
                'GET': {
                    'response': {
                        'success': True,
                        'data': {
                            'id': '{path.id}',
                            'name': 'mock-repo-{path.id}',
                            'url': 'https://github.com/mock/repo{path.id}.git',
                            'branch': 'main',
                            'status': 'active'
                        }
                    }
                },
                'PUT': {
                    'response': {
                        'success': True,
                        'data': {
                            'id': '{path.id}',
                            'name': '{request.name}',
                            'description': '{request.description}',
                            'updated_at': '{current_timestamp}'
                        }
                    }
                },
                'DELETE': {
                    'response': {
                        'success': True,
                        'data': {
                            'id': '{path.id}'
                        }
                    }
                }
            },
            '/api/v1/repositories/<int:id>/sync': {
                'POST': {
                    'response': {
                        'success': True,
                        'data': {
                            'id': '{path.id}',
                            'status': 'active',
                            'last_sync': '{current_timestamp}'
                        }
                    },
                    'delay': '2s'
                }
            }
        }
    },
    'task-manager': {
        'port': 18861,
        'endpoints': {
            '/health': {
                'GET': {
                    'response': {
                        'success': True,
                        'data': {
                            'status': 'healthy',
                            'service': 'Task Manager Mock'
                        }
                    }
                }
            },
            '/api/v1/tasks': {
                'GET': {
                    'response': {
                        'success': True,
                        'data': [
                            {
                                'id': 1,
                                'name': 'mock-task-1',
                                'type': 'build',
                                'status': 'completed',
                                'repository_id': 1,
                                'created_at': '2025-09-01T20:00:00Z'
                            }
                        ]
                    }
                },
                'POST': {
                    'response': {
                        'success': True,
                        'data': {
                            'id': '{auto_increment}',
                            'name': '{request.name}',
                            'type': '{request.type}',
                            'status': 'pending',
                            'repository_id': '{request.repository_id}',
                            'command': '{request.command}',
                            'created_at': '{current_timestamp}'
                        }
                    }
                }
            },
            '/api/v1/tasks/<int:id>': {
                'GET': {
                    'response': {
                        'success': True,
                        'data': {
                            'id': '{path.id}',
                            'name': 'mock-task-{path.id}',
                            'type': 'build',
                            'status': 'pending',
                            'repository_id': 1
                        }
                    }
                }
            },
            '/api/v1/tasks/<int:id>/execute': {
                'POST': {
                    'response': {
                        'success': True,
                        'data': {
                            'id': '{path.id}',
                            'status': 'completed',
                            'started_at': '{current_timestamp}',
                            'completed_at': '{current_timestamp}'
                        }
                    },
                    'delay': '3s'
                }
            },
            '/api/v1/tasks/<int:id>/logs': {
                'GET': {
                    'response': {
                        'success': True,
                        'data': {
                            'task_id': '{path.id}',
                            'logs': 'Mock task execution started\\nMock task completed successfully\\n'
                        }
                    }
                }
            }
        }
    },
    'log-manager': {
        'port': 18862,
        'endpoints': {
            '/health': {
                'GET': {
                    'response': {
                        'success': True,
                        'data': {
                            'status': 'healthy',
                            'service': 'Log Manager Mock'
                        }
                    }
                }
            },
            '/api/v1/logs': {
                'GET': {
                    'response': {
                        'success': True,
                        'data': [
                            {
                                'id': 1,
                                'service': 'mock-service',
                                'level': 'info',
                                'message': 'Mock log entry',
                                'timestamp': '2025-09-01T20:00:00Z'
                            }
                        ]
                    }
                },
                'POST': {
                    'response': {
                        'success': True,
                        'data': {
                            'id': '{auto_increment}',
                            'service': '{request.service}',
                            'level': '{request.level}',
                            'message': '{request.message}',
                            'timestamp': '{current_timestamp}'
                        }
                    }
                }
            },
            '/api/v1/logs/search': {
                'GET': {
                    'response': {
                        'success': True,
                        'data': [
                            {
                                'id': 1,
                                'service': 'search-result',
                                'level': 'info',
                                'message': 'Mock search result',
                                'timestamp': '{current_timestamp}'
                            }
                        ]
                    }
                }
            }
        }
    }
}

def create_performance_mock():
    """Crear mock con respuestas de rendimiento variables"""
    
    class PerformanceMock:
        def __init__(self):
            self.request_count = 0
            self.error_rate = 0.01  # 1% error rate
        
        def get_response_delay(self):
            """Simular variación en tiempo de respuesta"""
            self.request_count += 1
            
            # Simular degradación con carga
            base_delay = 50  # 50ms base
            load_factor = min(self.request_count / 1000, 2.0)  # Max 2x slower
            
            return base_delay * load_factor + random.uniform(0, 100)
        
        def should_error(self):
            """Determinar si debe retornar error"""
            return random.random() < self.error_rate
    
    return PerformanceMock()

def main():
    """Iniciar todos los servicios mock"""
    manager = MockServiceManager()
    
    # Crear servicios mock
    for service_name, config in MOCK_SERVICES_CONFIG.items():
        manager.create_mock_service(
            service_name,
            config['port'],
            config['endpoints']
        )
    
    # Iniciar servicios
    manager.start_all_services()
    
    print("\n🎭 Mock Services Status:")
    print("=" * 40)
    for service_name, config in MOCK_SERVICES_CONFIG.items():
        print(f"✅ {service_name}: http://localhost:{config['port']}")
    
    print("\n🧪 Ready for testing!")
    print("Press Ctrl+C to stop all services")
    
    try:
        # Mantener servicios corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping mock services...")

if __name__ == '__main__':
    main()
