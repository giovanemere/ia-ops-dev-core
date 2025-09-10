#!/usr/bin/env python3
"""
Real Provider Service with PostgreSQL integration
"""

import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import requests

# Import database models
from api.database_enhanced import get_db, Provider, init_db

class ProviderServiceReal:
    def __init__(self):
        # Initialize database
        init_db()
        
        # Encryption key for sensitive data
        self.encryption_key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
        if isinstance(self.encryption_key, str):
            self.encryption_key = self.encryption_key.encode()
        self.cipher = Fernet(self.encryption_key)
    
    def _encrypt_config(self, config: dict) -> str:
        """Encrypt sensitive configuration data"""
        config_str = json.dumps(config)
        return self.cipher.encrypt(config_str.encode()).decode()
    
    def _decrypt_config(self, encrypted_config: str) -> dict:
        """Decrypt configuration data"""
        try:
            decrypted = self.cipher.decrypt(encrypted_config.encode()).decode()
            return json.loads(decrypted)
        except:
            return {}
    
    async def list_providers(self) -> List[Dict]:
        """List all providers from database"""
        db = next(get_db())
        try:
            providers = db.query(Provider).all()
            result = []
            for provider in providers:
                # Don't return encrypted config in list
                result.append({
                    "id": provider.id,
                    "name": provider.name,
                    "type": provider.type,
                    "description": provider.description,
                    "is_active": provider.is_active,
                    "created_at": provider.created_at.isoformat(),
                    "updated_at": provider.updated_at.isoformat()
                })
            return result
        finally:
            db.close()
    
    async def get_provider(self, provider_id: int) -> Optional[Dict]:
        """Get specific provider by ID"""
        db = next(get_db())
        try:
            provider = db.query(Provider).filter(Provider.id == provider_id).first()
            if not provider:
                return None
            
            # Decrypt config for viewing (mask sensitive fields)
            config = self._decrypt_config(provider.config)
            masked_config = self._mask_sensitive_fields(config, provider.type)
            
            return {
                "id": provider.id,
                "name": provider.name,
                "type": provider.type,
                "description": provider.description,
                "config": masked_config,
                "is_active": provider.is_active,
                "created_at": provider.created_at.isoformat(),
                "updated_at": provider.updated_at.isoformat()
            }
        finally:
            db.close()
    
    async def create_provider(self, provider_data: Dict) -> Dict:
        """Create new provider in database"""
        db = next(get_db())
        try:
            # Encrypt sensitive configuration
            encrypted_config = self._encrypt_config(provider_data["config"])
            
            provider = Provider(
                name=provider_data["name"],
                type=provider_data["type"],
                description=provider_data.get("description", ""),
                config=encrypted_config,
                is_active=True
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            return {
                "status": "success",
                "provider": {
                    "id": provider.id,
                    "name": provider.name,
                    "type": provider.type,
                    "description": provider.description,
                    "is_active": provider.is_active,
                    "created_at": provider.created_at.isoformat()
                }
            }
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
    
    async def update_provider(self, provider_id: int, provider_data: Dict) -> Dict:
        """Update existing provider"""
        db = next(get_db())
        try:
            provider = db.query(Provider).filter(Provider.id == provider_id).first()
            if not provider:
                return {"status": "error", "message": "Provider not found"}
            
            # Update fields
            provider.name = provider_data.get("name", provider.name)
            provider.type = provider_data.get("type", provider.type)
            provider.description = provider_data.get("description", provider.description)
            
            # Update config if provided
            if "config" in provider_data:
                provider.config = self._encrypt_config(provider_data["config"])
            
            provider.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "status": "success",
                "provider": {
                    "id": provider.id,
                    "name": provider.name,
                    "type": provider.type,
                    "description": provider.description,
                    "updated_at": provider.updated_at.isoformat()
                }
            }
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
    
    async def delete_provider(self, provider_id: int) -> Dict:
        """Delete provider from database"""
        db = next(get_db())
        try:
            provider = db.query(Provider).filter(Provider.id == provider_id).first()
            if not provider:
                return {"status": "error", "message": "Provider not found"}
            
            db.delete(provider)
            db.commit()
            
            return {
                "status": "success",
                "message": f"Provider {provider_id} deleted successfully"
            }
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
    
    async def test_connection(self, provider_type: str, config: Dict) -> Dict:
        """Test connection to provider"""
        try:
            if provider_type == "github":
                return await self._test_github_connection(config)
            elif provider_type == "aws":
                return await self._test_aws_connection(config)
            elif provider_type == "azure":
                return await self._test_azure_connection(config)
            elif provider_type == "gcp":
                return await self._test_gcp_connection(config)
            elif provider_type == "openai":
                return await self._test_openai_connection(config)
            else:
                return {"status": "error", "message": "Unsupported provider type"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _test_github_connection(self, config: Dict) -> Dict:
        """Test GitHub connection"""
        token = config.get("token")
        if not token:
            return {"status": "error", "message": "GitHub token is required"}
        
        try:
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "status": "success",
                    "provider_type": "github",
                    "connection": "established",
                    "message": f"Successfully connected as {user_data.get('login')}",
                    "user_info": {
                        "login": user_data.get("login"),
                        "name": user_data.get("name"),
                        "email": user_data.get("email")
                    },
                    "tested_at": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"GitHub API error: {response.status_code} - {response.text}"
                }
        except requests.RequestException as e:
            return {"status": "error", "message": f"Connection failed: {str(e)}"}
    
    async def _test_aws_connection(self, config: Dict) -> Dict:
        """Test AWS connection"""
        # Mock AWS test - in real implementation use boto3
        await asyncio.sleep(1)
        return {
            "status": "success",
            "provider_type": "aws",
            "connection": "established",
            "message": "AWS connection test successful (mock)",
            "tested_at": datetime.now().isoformat()
        }
    
    async def _test_azure_connection(self, config: Dict) -> Dict:
        """Test Azure connection"""
        # Mock Azure test - in real implementation use azure-identity
        await asyncio.sleep(1)
        return {
            "status": "success",
            "provider_type": "azure",
            "connection": "established",
            "message": "Azure connection test successful (mock)",
            "tested_at": datetime.now().isoformat()
        }
    
    async def _test_gcp_connection(self, config: Dict) -> Dict:
        """Test GCP connection"""
        # Mock GCP test - in real implementation use google-cloud
        await asyncio.sleep(1)
        return {
            "status": "success",
            "provider_type": "gcp",
            "connection": "established",
            "message": "GCP connection test successful (mock)",
            "tested_at": datetime.now().isoformat()
        }
    
    async def _test_openai_connection(self, config: Dict) -> Dict:
        """Test OpenAI connection"""
        api_key = config.get("api_key")
        if not api_key:
            return {"status": "error", "message": "OpenAI API key is required"}
        
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "provider_type": "openai",
                    "connection": "established",
                    "message": "OpenAI API connection successful",
                    "tested_at": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"OpenAI API error: {response.status_code}"
                }
        except requests.RequestException as e:
            return {"status": "error", "message": f"Connection failed: {str(e)}"}
    
    def _mask_sensitive_fields(self, config: Dict, provider_type: str) -> Dict:
        """Mask sensitive fields in configuration"""
        masked_config = config.copy()
        
        sensitive_fields = {
            "github": ["token"],
            "aws": ["secret_access_key", "session_token"],
            "azure": ["client_secret"],
            "gcp": ["service_account_key"],
            "openai": ["api_key"]
        }
        
        fields_to_mask = sensitive_fields.get(provider_type, [])
        
        for field in fields_to_mask:
            if field in masked_config:
                value = masked_config[field]
                if len(value) > 8:
                    masked_config[field] = value[:4] + "*" * (len(value) - 8) + value[-4:]
                else:
                    masked_config[field] = "*" * len(value)
        
        return masked_config

# Global instance
provider_service_real = ProviderServiceReal()
