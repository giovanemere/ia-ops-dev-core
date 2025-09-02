#!/usr/bin/env python3
"""
Frontend Configuration API - Almacenamiento de configuración del frontend
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from database import get_db, init_db, Base
from datetime import datetime
import json
import os
import logging

app = Flask(__name__)
CORS(app)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelo para configuración del frontend
class FrontendConfig(Base):
    __tablename__ = "frontend_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, index=True)
    config_value = Column(Text)
    config_type = Column(String(50))  # 'user_settings', 'app_config', 'provider_config'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), default='system')

# Swagger configuration
api = Api(app, version='1.0.0', title='Frontend Configuration API',
          description='API para almacenar configuración del frontend')

# Initialize database
init_db()

# Namespaces
config_ns = api.namespace('config', description='Frontend configuration operations')
health_ns = api.namespace('health', description='Health check operations')

# Models
config_model = api.model('FrontendConfig', {
    'config_key': fields.String(required=True, description='Configuration key'),
    'config_value': fields.Raw(required=True, description='Configuration value (JSON)'),
    'config_type': fields.String(description='Configuration type', enum=['user_settings', 'app_config', 'provider_config']),
    'created_by': fields.String(description='Created by user')
})

@health_ns.route('/')
class HealthCheck(Resource):
    def get(self):
        """Health check endpoint"""
        return {'status': 'healthy', 'service': 'Frontend Configuration API'}

@config_ns.route('/')
class ConfigList(Resource):
    @api.doc('list_configs')
    def get(self):
        """Get all frontend configurations"""
        try:
            db = next(get_db())
            configs = db.query(FrontendConfig).filter(FrontendConfig.is_active == True).all()
            
            result = {}
            for config in configs:
                try:
                    result[config.config_key] = json.loads(config.config_value)
                except json.JSONDecodeError:
                    result[config.config_key] = config.config_value
            
            return {
                'success': True,
                'data': result,
                'message': f'Found {len(result)} configurations'
            }
        except Exception as e:
            logger.error(f"Error listing configs: {e}")
            return {'success': False, 'error': str(e)}, 500

    @api.doc('create_or_update_config')
    @api.expect(config_model)
    def post(self):
        """Create or update frontend configuration"""
        try:
            data = request.get_json()
            
            if not data.get('config_key'):
                return {'success': False, 'error': 'config_key is required'}, 400
            
            db = next(get_db())
            
            # Check if config exists
            existing = db.query(FrontendConfig).filter(
                FrontendConfig.config_key == data['config_key']
            ).first()
            
            config_value = json.dumps(data['config_value']) if isinstance(data['config_value'], (dict, list)) else str(data['config_value'])
            
            if existing:
                # Update existing
                existing.config_value = config_value
                existing.config_type = data.get('config_type', existing.config_type)
                existing.updated_at = datetime.utcnow()
                existing.created_by = data.get('created_by', existing.created_by)
                db.commit()
                
                return {
                    'success': True,
                    'data': {
                        'id': existing.id,
                        'config_key': existing.config_key,
                        'config_type': existing.config_type,
                        'updated_at': existing.updated_at.isoformat()
                    },
                    'message': 'Configuration updated successfully'
                }
            else:
                # Create new
                new_config = FrontendConfig(
                    config_key=data['config_key'],
                    config_value=config_value,
                    config_type=data.get('config_type', 'app_config'),
                    created_by=data.get('created_by', 'system')
                )
                
                db.add(new_config)
                db.commit()
                db.refresh(new_config)
                
                return {
                    'success': True,
                    'data': {
                        'id': new_config.id,
                        'config_key': new_config.config_key,
                        'config_type': new_config.config_type,
                        'created_at': new_config.created_at.isoformat()
                    },
                    'message': 'Configuration created successfully'
                }
                
        except Exception as e:
            logger.error(f"Error creating/updating config: {e}")
            return {'success': False, 'error': str(e)}, 500

@config_ns.route('/<string:config_key>')
class ConfigDetail(Resource):
    @api.doc('get_config')
    def get(self, config_key):
        """Get specific configuration by key"""
        try:
            db = next(get_db())
            config = db.query(FrontendConfig).filter(
                FrontendConfig.config_key == config_key,
                FrontendConfig.is_active == True
            ).first()
            
            if not config:
                return {'success': False, 'error': 'Configuration not found'}, 404
            
            try:
                config_value = json.loads(config.config_value)
            except json.JSONDecodeError:
                config_value = config.config_value
            
            return {
                'success': True,
                'data': {
                    'config_key': config.config_key,
                    'config_value': config_value,
                    'config_type': config.config_type,
                    'created_at': config.created_at.isoformat(),
                    'updated_at': config.updated_at.isoformat()
                },
                'message': 'Configuration retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return {'success': False, 'error': str(e)}, 500

    @api.doc('delete_config')
    def delete(self, config_key):
        """Delete configuration (soft delete)"""
        try:
            db = next(get_db())
            config = db.query(FrontendConfig).filter(
                FrontendConfig.config_key == config_key
            ).first()
            
            if not config:
                return {'success': False, 'error': 'Configuration not found'}, 404
            
            config.is_active = False
            config.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                'success': True,
                'data': {'config_key': config_key},
                'message': 'Configuration deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting config: {e}")
            return {'success': False, 'error': str(e)}, 500

# Endpoints específicos para configuraciones comunes
@config_ns.route('/user-settings')
class UserSettings(Resource):
    @api.doc('get_user_settings')
    def get(self):
        """Get user settings configuration"""
        try:
            db = next(get_db())
            configs = db.query(FrontendConfig).filter(
                FrontendConfig.config_type == 'user_settings',
                FrontendConfig.is_active == True
            ).all()
            
            settings = {}
            for config in configs:
                try:
                    settings[config.config_key] = json.loads(config.config_value)
                except json.JSONDecodeError:
                    settings[config.config_key] = config.config_value
            
            return {
                'success': True,
                'data': settings,
                'message': 'User settings retrieved successfully'
            }
        except Exception as e:
            logger.error(f"Error getting user settings: {e}")
            return {'success': False, 'error': str(e)}, 500

@config_ns.route('/provider-configs')
class ProviderConfigs(Resource):
    @api.doc('get_provider_configs')
    def get(self):
        """Get provider configurations"""
        try:
            db = next(get_db())
            configs = db.query(FrontendConfig).filter(
                FrontendConfig.config_type == 'provider_config',
                FrontendConfig.is_active == True
            ).all()
            
            provider_configs = {}
            for config in configs:
                try:
                    provider_configs[config.config_key] = json.loads(config.config_value)
                except json.JSONDecodeError:
                    provider_configs[config.config_key] = config.config_value
            
            return {
                'success': True,
                'data': provider_configs,
                'message': 'Provider configurations retrieved successfully'
            }
        except Exception as e:
            logger.error(f"Error getting provider configs: {e}")
            return {'success': False, 'error': str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8868))
    app.run(host='0.0.0.0', port=port, debug=True)
