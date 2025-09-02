#!/usr/bin/env python3
"""
Enhanced Database Configuration for IA-Ops Solution
PostgreSQL for all data storage, Redis for caching, MinIO single bucket
"""

import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import redis
from minio import Minio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cache_service import cache_service
from storage_config import get_bucket_name

# Environment variables with defaults
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://iaops_user:iaops_password@localhost:5434/iaops_db')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6380/0')
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9898')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin123')

# PostgreSQL setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.from_url(REDIS_URL)

# MinIO setup (single bucket)
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Database Models
class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(255), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    branch = Column(String(100), default="main")
    description = Column(Text)
    status = Column(String(50), default="active")
    docs_url = Column(String(500))
    storage_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")
    repository_id = Column(Integer)
    command = Column(Text)
    environment = Column(JSON)
    logs = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    description = Column(Text)
    config = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Build(Base):
    __tablename__ = "builds"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer)
    branch = Column(String(100))
    commit_sha = Column(String(100))
    status = Column(String(50), default="queued")
    output_path = Column(String(500))
    storage_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration = Column(Integer)
    error_message = Column(Text)

class CacheStats(Base):
    __tablename__ = "cache_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(100), nullable=False)
    cache_hits = Column(Integer, default=0)
    cache_misses = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

# Database functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

def get_redis():
    """Get Redis client"""
    return redis_client

def get_minio():
    """Get MinIO client"""
    return minio_client

def get_cache():
    """Get cache service"""
    return cache_service

def get_storage_bucket():
    """Get single storage bucket name"""
    return get_bucket_name()

def get_config_value(key: str, default: str = None):
    """Get configuration value from database with Redis cache"""
    cache_key = f"config:{key}"
    
    # Try cache first
    cached_value = cache_service.get("system", cache_key)
    if cached_value:
        return cached_value
    
    # Get from database
    db = next(get_db())
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        if config:
            # Cache the result
            cache_service.set("system", cache_key, config.config_value, ttl=3600)
            return config.config_value
        return default
    finally:
        db.close()

def set_config_value(key: str, value: str, config_type: str = "system"):
    """Set configuration value in database and clear cache"""
    db = next(get_db())
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        if config:
            config.config_value = value
            config.updated_at = datetime.utcnow()
        else:
            config = SystemConfig(
                config_key=key,
                config_value=value,
                config_type=config_type
            )
            db.add(config)
        
        db.commit()
        
        # Clear cache
        cache_service.delete("system", f"config:{key}")
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()
