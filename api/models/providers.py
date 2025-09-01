#!/usr/bin/env python3
"""
Provider Models - Gestión de providers externos
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    type = Column(String(50), index=True)  # github, azure, aws, gcp, openai
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Configuración específica del provider
    config = Column(JSON)  # Configuración flexible por provider
    
    # Metadatos
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'is_active': self.is_active,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }

class ProviderCredential(Base):
    __tablename__ = "provider_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, index=True)
    credential_type = Column(String(50))  # token, key, secret, etc.
    credential_name = Column(String(100))
    credential_value = Column(Text)  # Encriptado
    is_active = Column(Boolean, default=True)
    
    # Metadatos
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    def to_dict(self, include_value=False):
        result = {
            'id': self.id,
            'provider_id': self.provider_id,
            'credential_type': self.credential_type,
            'credential_name': self.credential_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
        
        if include_value:
            result['credential_value'] = self.credential_value
            
        return result
