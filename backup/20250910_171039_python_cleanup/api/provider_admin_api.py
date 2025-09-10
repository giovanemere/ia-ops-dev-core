#!/usr/bin/env python3
"""
Provider Administration API - CRUD para gestión de providers
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from sqlalchemy.orm import Session
from database import get_db, init_db
from models.providers import Provider, ProviderCredential
from services.provider_service import ProviderService
from swagger_config import create_swagger_config, get_common_models
import os
import logging
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Swagger configuration
api = create_swagger_config(app, "Provider Administration", "1.0.0")
common_models = get_common_models(api)
provider_service = ProviderService()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Namespaces
providers_ns = api.namespace('providers', description='Provider management operations')
config_ns = api.namespace('config', description='Provider configuration operations')
health_ns = api.namespace('health', description='Health check operations')

# Models
provider_model = api.model('Provider', {
    'name': fields.String(required=True, description='Provider name'),
    'type': fields.String(required=True, description='Provider type', enum=['github', 'azure', 'aws', 'gcp', 'openai']),
    'description': fields.String(description='Provider description'),
    'is_active': fields.Boolean(default=True, description='Is provider active'),
    'config': fields.Raw(description='Provider configuration')
})

provider_response_model = api.model('ProviderResponse', {
    'id': fields.Integer(description='Provider ID'),
    'name': fields.String(description='Provider name'),
    'type': fields.String(description='Provider type'),
    'description': fields.String(description='Provider description'),
    'is_active': fields.Boolean(description='Is provider active'),
    'config': fields.Raw(description='Provider configuration'),
    'created_at': fields.String(description='Creation date'),
    'updated_at': fields.String(description='Update date')
})

credential_model = api.model('ProviderCredential', {
    'provider_id': fields.Integer(required=True, description='Provider ID'),
    'credential_type': fields.String(required=True, description='Credential type'),
    'credential_name': fields.String(required=True, description='Credential name'),
    'credential_value': fields.String(required=True, description='Credential value'),
    'expires_at': fields.String(description='Expiration date (ISO format)')
})

test_connection_model = api.model('TestConnection', {
    'provider_type': fields.String(required=True, description='Provider type'),
    'config': fields.Raw(required=True, description='Provider configuration')
})

@health_ns.route('/')
class HealthCheck(Resource):
    @api.doc('health_check')
    @api.marshal_with(common_models['success_response'])
    def get(self):
        """Health check endpoint"""
        return {
            'success': True,
            'data': {'status': 'healthy', 'service': 'Provider Administration'},
            'message': 'Service is healthy'
        }

@providers_ns.route('/')
class ProviderList(Resource):
    @api.doc('list_providers')
    @api.marshal_with(common_models['success_response'])
    def get(self):
        """Get all providers"""
        try:
            db = next(get_db())
            providers = db.query(Provider).all()
            
            provider_list = [provider.to_dict() for provider in providers]
            
            return {
                'success': True,
                'data': provider_list,
                'message': f'Found {len(provider_list)} providers'
            }
        except Exception as e:
            logger.error(f"Error listing providers: {e}")
            return {
                'success': False,
                'error': {'code': 'LIST_FAILED', 'message': str(e)}
            }, 500

    @api.doc('create_provider')
    @api.expect(provider_model)
    @api.marshal_with(common_models['success_response'])
    def post(self):
        """Create a new provider"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('name') or not data.get('type'):
                return {
                    'success': False,
                    'error': {'code': 'MISSING_FIELDS', 'message': 'name and type are required'}
                }, 400
            
            # Validate provider type
            if data['type'] not in ['github', 'azure', 'aws', 'gcp', 'openai']:
                return {
                    'success': False,
                    'error': {'code': 'INVALID_TYPE', 'message': 'Invalid provider type'}
                }, 400
            
            db = next(get_db())
            
            # Check if provider already exists
            existing = db.query(Provider).filter(Provider.name == data['name']).first()
            if existing:
                return {
                    'success': False,
                    'error': {'code': 'PROVIDER_EXISTS', 'message': 'Provider already exists'}
                }, 409
            
            # Create new provider
            new_provider = Provider(
                name=data['name'],
                type=data['type'],
                description=data.get('description', ''),
                is_active=data.get('is_active', True),
                config=data.get('config', {}),
                created_by=data.get('created_by', 'system')
            )
            
            db.add(new_provider)
            db.commit()
            db.refresh(new_provider)
            
            return {
                'success': True,
                'data': new_provider.to_dict(),
                'message': 'Provider created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating provider: {e}")
            return {
                'success': False,
                'error': {'code': 'CREATE_FAILED', 'message': str(e)}
            }, 500

@providers_ns.route('/<int:provider_id>')
class ProviderDetail(Resource):
    @api.doc('get_provider')
    @api.marshal_with(common_models['success_response'])
    def get(self, provider_id):
        """Get provider by ID"""
        try:
            db = next(get_db())
            provider = db.query(Provider).filter(Provider.id == provider_id).first()
            
            if not provider:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Provider not found'}
                }, 404
            
            return {
                'success': True,
                'data': provider.to_dict(),
                'message': 'Provider retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Error getting provider: {e}")
            return {
                'success': False,
                'error': {'code': 'GET_FAILED', 'message': str(e)}
            }, 500

    @api.doc('update_provider')
    @api.expect(provider_model)
    @api.marshal_with(common_models['success_response'])
    def put(self, provider_id):
        """Update provider"""
        try:
            data = request.get_json()
            db = next(get_db())
            
            provider = db.query(Provider).filter(Provider.id == provider_id).first()
            if not provider:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Provider not found'}
                }, 404
            
            # Update fields
            if 'name' in data:
                provider.name = data['name']
            if 'type' in data:
                provider.type = data['type']
            if 'description' in data:
                provider.description = data['description']
            if 'is_active' in data:
                provider.is_active = data['is_active']
            if 'config' in data:
                provider.config = data['config']
            
            provider.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                'success': True,
                'data': provider.to_dict(),
                'message': 'Provider updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating provider: {e}")
            return {
                'success': False,
                'error': {'code': 'UPDATE_FAILED', 'message': str(e)}
            }, 500

    @api.doc('delete_provider')
    @api.marshal_with(common_models['success_response'])
    def delete(self, provider_id):
        """Delete provider"""
        try:
            db = next(get_db())
            provider = db.query(Provider).filter(Provider.id == provider_id).first()
            
            if not provider:
                return {
                    'success': False,
                    'error': {'code': 'NOT_FOUND', 'message': 'Provider not found'}
                }, 404
            
            # Delete associated credentials
            db.query(ProviderCredential).filter(ProviderCredential.provider_id == provider_id).delete()
            
            db.delete(provider)
            db.commit()
            
            return {
                'success': True,
                'data': {'id': provider_id},
                'message': 'Provider deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting provider: {e}")
            return {
                'success': False,
                'error': {'code': 'DELETE_FAILED', 'message': str(e)}
            }, 500

@config_ns.route('/requirements/<string:provider_type>')
class ProviderRequirements(Resource):
    @api.doc('get_provider_requirements')
    @api.marshal_with(common_models['success_response'])
    def get(self, provider_type):
        """Get configuration requirements for provider type"""
        try:
            provider = provider_service.get_provider(provider_type)
            if not provider:
                return {
                    'success': False,
                    'error': {'code': 'INVALID_TYPE', 'message': 'Invalid provider type'}
                }, 400
            
            requirements = provider.get_required_config()
            
            return {
                'success': True,
                'data': {
                    'provider_type': provider_type,
                    'requirements': requirements
                },
                'message': f'Requirements for {provider_type} provider'
            }
            
        except Exception as e:
            logger.error(f"Error getting provider requirements: {e}")
            return {
                'success': False,
                'error': {'code': 'GET_REQUIREMENTS_FAILED', 'message': str(e)}
            }, 500

@config_ns.route('/test-connection')
class TestConnection(Resource):
    @api.doc('test_provider_connection')
    @api.expect(test_connection_model)
    @api.marshal_with(common_models['success_response'])
    def post(self):
        """Test connection to provider"""
        try:
            data = request.get_json()
            
            if not data.get('provider_type') or not data.get('config'):
                return {
                    'success': False,
                    'error': {'code': 'MISSING_FIELDS', 'message': 'provider_type and config are required'}
                }, 400
            
            result = provider_service.test_connection(data['provider_type'], data['config'])
            
            return {
                'success': result['success'],
                'data': result.get('data', {}),
                'message': 'Connection test completed',
                'error': result.get('error') if not result['success'] else None
            }
            
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return {
                'success': False,
                'error': {'code': 'TEST_FAILED', 'message': str(e)}
            }, 500

@providers_ns.route('/<int:provider_id>/credentials')
class ProviderCredentials(Resource):
    @api.doc('list_provider_credentials')
    @api.marshal_with(common_models['success_response'])
    def get(self, provider_id):
        """Get credentials for provider (without values)"""
        try:
            db = next(get_db())
            credentials = db.query(ProviderCredential).filter(
                ProviderCredential.provider_id == provider_id
            ).all()
            
            credential_list = [cred.to_dict(include_value=False) for cred in credentials]
            
            return {
                'success': True,
                'data': credential_list,
                'message': f'Found {len(credential_list)} credentials'
            }
            
        except Exception as e:
            logger.error(f"Error listing credentials: {e}")
            return {
                'success': False,
                'error': {'code': 'LIST_CREDENTIALS_FAILED', 'message': str(e)}
            }, 500

    @api.doc('create_provider_credential')
    @api.expect(credential_model)
    @api.marshal_with(common_models['success_response'])
    def post(self, provider_id):
        """Create credential for provider"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['credential_type', 'credential_name', 'credential_value']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'error': {'code': 'MISSING_FIELD', 'message': f'Missing required field: {field}'}
                    }, 400
            
            db = next(get_db())
            
            # Verify provider exists
            provider = db.query(Provider).filter(Provider.id == provider_id).first()
            if not provider:
                return {
                    'success': False,
                    'error': {'code': 'PROVIDER_NOT_FOUND', 'message': 'Provider not found'}
                }, 404
            
            # Create new credential
            new_credential = ProviderCredential(
                provider_id=provider_id,
                credential_type=data['credential_type'],
                credential_name=data['credential_name'],
                credential_value=data['credential_value'],  # TODO: Encrypt this
                expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
            )
            
            db.add(new_credential)
            db.commit()
            db.refresh(new_credential)
            
            return {
                'success': True,
                'data': new_credential.to_dict(include_value=False),
                'message': 'Credential created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating credential: {e}")
            return {
                'success': False,
                'error': {'code': 'CREATE_CREDENTIAL_FAILED', 'message': str(e)}
            }, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8866))
    app.run(host='0.0.0.0', port=port, debug=True)
