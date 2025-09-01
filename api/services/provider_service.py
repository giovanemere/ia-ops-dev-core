#!/usr/bin/env python3
"""
Provider Service - Integración con múltiples providers
"""

import os
import requests
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from google.cloud import storage as gcp_storage
import openai
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ProviderService:
    def __init__(self):
        self.providers = {
            'github': GitHubProvider(),
            'azure': AzureProvider(),
            'aws': AWSProvider(),
            'gcp': GCPProvider(),
            'openai': OpenAIProvider()
        }
    
    def get_provider(self, provider_type: str):
        return self.providers.get(provider_type)
    
    def test_connection(self, provider_type: str, config: Dict) -> Dict:
        provider = self.get_provider(provider_type)
        if not provider:
            return {'success': False, 'error': 'Provider not supported'}
        
        return provider.test_connection(config)

class GitHubProvider:
    def __init__(self):
        self.base_url = 'https://api.github.com'
    
    def get_required_config(self) -> Dict:
        return {
            'token': {'type': 'string', 'required': True, 'description': 'GitHub Personal Access Token'},
            'username': {'type': 'string', 'required': False, 'description': 'GitHub Username'},
            'organization': {'type': 'string', 'required': False, 'description': 'GitHub Organization'}
        }
    
    def test_connection(self, config: Dict) -> Dict:
        try:
            headers = {'Authorization': f"token {config['token']}"}
            response = requests.get(f"{self.base_url}/user", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'data': {
                        'username': user_data.get('login'),
                        'name': user_data.get('name'),
                        'email': user_data.get('email')
                    }
                }
            else:
                return {'success': False, 'error': 'Invalid token or insufficient permissions'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_repositories(self, config: Dict, username: str = None, org: str = None) -> List[Dict]:
        headers = {'Authorization': f"token {config['token']}"}
        
        if org:
            url = f"{self.base_url}/orgs/{org}/repos"
        elif username:
            url = f"{self.base_url}/users/{username}/repos"
        else:
            url = f"{self.base_url}/user/repos"
        
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else []

class AzureProvider:
    def get_required_config(self) -> Dict:
        return {
            'subscription_id': {'type': 'string', 'required': True, 'description': 'Azure Subscription ID'},
            'client_id': {'type': 'string', 'required': True, 'description': 'Azure Client ID'},
            'client_secret': {'type': 'string', 'required': True, 'description': 'Azure Client Secret'},
            'tenant_id': {'type': 'string', 'required': True, 'description': 'Azure Tenant ID'}
        }
    
    def test_connection(self, config: Dict) -> Dict:
        try:
            os.environ['AZURE_CLIENT_ID'] = config['client_id']
            os.environ['AZURE_CLIENT_SECRET'] = config['client_secret']
            os.environ['AZURE_TENANT_ID'] = config['tenant_id']
            
            credential = DefaultAzureCredential()
            resource_client = ResourceManagementClient(credential, config['subscription_id'])
            
            # Test listing resource groups
            resource_groups = list(resource_client.resource_groups.list())
            
            return {
                'success': True,
                'data': {
                    'subscription_id': config['subscription_id'],
                    'resource_groups_count': len(resource_groups)
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_resource_groups(self, config: Dict) -> List[Dict]:
        try:
            os.environ['AZURE_CLIENT_ID'] = config['client_id']
            os.environ['AZURE_CLIENT_SECRET'] = config['client_secret']
            os.environ['AZURE_TENANT_ID'] = config['tenant_id']
            
            credential = DefaultAzureCredential()
            resource_client = ResourceManagementClient(credential, config['subscription_id'])
            
            return [
                {
                    'name': rg.name,
                    'location': rg.location,
                    'id': rg.id
                }
                for rg in resource_client.resource_groups.list()
            ]
        except Exception as e:
            logger.error(f"Error listing Azure resource groups: {e}")
            return []

class AWSProvider:
    def get_required_config(self) -> Dict:
        return {
            'access_key_id': {'type': 'string', 'required': True, 'description': 'AWS Access Key ID'},
            'secret_access_key': {'type': 'string', 'required': True, 'description': 'AWS Secret Access Key'},
            'region': {'type': 'string', 'required': True, 'description': 'AWS Region', 'default': 'us-east-1'}
        }
    
    def test_connection(self, config: Dict) -> Dict:
        try:
            session = boto3.Session(
                aws_access_key_id=config['access_key_id'],
                aws_secret_access_key=config['secret_access_key'],
                region_name=config['region']
            )
            
            # Test with STS to get caller identity
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            
            return {
                'success': True,
                'data': {
                    'account_id': identity.get('Account'),
                    'user_id': identity.get('UserId'),
                    'arn': identity.get('Arn'),
                    'region': config['region']
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_s3_buckets(self, config: Dict) -> List[Dict]:
        try:
            session = boto3.Session(
                aws_access_key_id=config['access_key_id'],
                aws_secret_access_key=config['secret_access_key'],
                region_name=config['region']
            )
            
            s3 = session.client('s3')
            response = s3.list_buckets()
            
            return [
                {
                    'name': bucket['Name'],
                    'creation_date': bucket['CreationDate'].isoformat()
                }
                for bucket in response['Buckets']
            ]
        except Exception as e:
            logger.error(f"Error listing S3 buckets: {e}")
            return []

class GCPProvider:
    def get_required_config(self) -> Dict:
        return {
            'project_id': {'type': 'string', 'required': True, 'description': 'GCP Project ID'},
            'service_account_key': {'type': 'json', 'required': True, 'description': 'Service Account Key JSON'}
        }
    
    def test_connection(self, config: Dict) -> Dict:
        try:
            # Set up credentials
            import json
            import tempfile
            
            key_data = json.loads(config['service_account_key'])
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(key_data, f)
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
            
            # Test with Storage client
            client = gcp_storage.Client(project=config['project_id'])
            buckets = list(client.list_buckets())
            
            return {
                'success': True,
                'data': {
                    'project_id': config['project_id'],
                    'buckets_count': len(buckets)
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_storage_buckets(self, config: Dict) -> List[Dict]:
        try:
            import json
            import tempfile
            
            key_data = json.loads(config['service_account_key'])
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(key_data, f)
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
            
            client = gcp_storage.Client(project=config['project_id'])
            
            return [
                {
                    'name': bucket.name,
                    'location': bucket.location,
                    'storage_class': bucket.storage_class
                }
                for bucket in client.list_buckets()
            ]
        except Exception as e:
            logger.error(f"Error listing GCP buckets: {e}")
            return []

class OpenAIProvider:
    def get_required_config(self) -> Dict:
        return {
            'api_key': {'type': 'string', 'required': True, 'description': 'OpenAI API Key'},
            'organization': {'type': 'string', 'required': False, 'description': 'OpenAI Organization ID'}
        }
    
    def test_connection(self, config: Dict) -> Dict:
        try:
            openai.api_key = config['api_key']
            if config.get('organization'):
                openai.organization = config['organization']
            
            # Test with a simple completion
            response = openai.Model.list()
            
            return {
                'success': True,
                'data': {
                    'models_count': len(response['data']),
                    'organization': config.get('organization')
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_models(self, config: Dict) -> List[Dict]:
        try:
            openai.api_key = config['api_key']
            if config.get('organization'):
                openai.organization = config['organization']
            
            response = openai.Model.list()
            
            return [
                {
                    'id': model['id'],
                    'object': model['object'],
                    'created': model['created']
                }
                for model in response['data']
            ]
        except Exception as e:
            logger.error(f"Error listing OpenAI models: {e}")
            return []
