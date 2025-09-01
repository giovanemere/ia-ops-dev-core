#!/usr/bin/env python3
"""
Authentication Service - JWT Token Management para IA-Ops Portals
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import hashlib
import secrets

class AuthService:
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or os.environ.get('JWT_SECRET_KEY', 'ia-ops-dev-core-secret-2024')
        self.algorithm = 'HS256'
        self.token_expiry = timedelta(hours=24)
    
    def generate_token(self, user_data: dict) -> str:
        """Generar JWT token"""
        payload = {
            'user_id': user_data.get('user_id'),
            'username': user_data.get('username'),
            'role': user_data.get('role', 'user'),
            'permissions': user_data.get('permissions', []),
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow(),
            'iss': 'ia-ops-dev-core'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Verificar JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return {'valid': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
    
    def generate_api_key(self, service_name: str) -> str:
        """Generar API Key para servicios"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        random_part = secrets.token_hex(16)
        raw_key = f"{service_name}:{timestamp}:{random_part}"
        
        # Hash para crear API key
        api_key = hashlib.sha256(raw_key.encode()).hexdigest()
        return f"iaops_{api_key[:32]}"

# Decorador para proteger endpoints
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_service = AuthService()
        
        # Verificar header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        
        try:
            # Formato: "Bearer <token>" o "ApiKey <key>"
            auth_type, token = auth_header.split(' ', 1)
            
            if auth_type.lower() == 'bearer':
                # JWT Token
                result = auth_service.verify_token(token)
                if not result['valid']:
                    return jsonify({'error': result['error']}), 401
                
                request.user = result['payload']
                
            elif auth_type.lower() == 'apikey':
                # API Key validation
                if not token.startswith('iaops_'):
                    return jsonify({'error': 'Invalid API key format'}), 401
                
                # Aquí validarías contra base de datos
                request.user = {'user_id': 'service', 'role': 'service'}
                
            else:
                return jsonify({'error': 'Invalid authorization type'}), 401
                
        except ValueError:
            return jsonify({'error': 'Invalid authorization format'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

# Configuración de tokens por portal
PORTAL_CONFIGS = {
    'swagger-portal': {
        'port': 8870,
        'auth_required': False,  # Portal público de documentación
        'api_key': None
    },
    'provider-admin': {
        'port': 8866,
        'auth_required': True,   # Requiere autenticación
        'permissions': ['admin', 'provider_management'],
        'api_key': 'iaops_provider_admin_2024'
    },
    'testing-portal': {
        'port': 18860,
        'auth_required': False,  # Para desarrollo y testing
        'api_key': 'iaops_testing_portal_2024'
    },
    'repository-manager': {
        'port': 8860,
        'auth_required': True,
        'permissions': ['user', 'repository_management'],
        'api_key': 'iaops_repo_manager_2024'
    }
}

def get_portal_config(portal_name: str) -> dict:
    """Obtener configuración de autenticación por portal"""
    return PORTAL_CONFIGS.get(portal_name, {})

def create_service_tokens():
    """Crear tokens para servicios internos"""
    auth_service = AuthService()
    
    tokens = {}
    for service, config in PORTAL_CONFIGS.items():
        if config.get('api_key'):
            tokens[service] = {
                'api_key': config['api_key'],
                'jwt_token': auth_service.generate_token({
                    'user_id': f'service_{service}',
                    'username': service,
                    'role': 'service',
                    'permissions': config.get('permissions', [])
                })
            }
    
    return tokens
