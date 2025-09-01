#!/usr/bin/env python3
"""
Database configuration and models for IA-Ops Dev Core
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import redis
from minio import Minio

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5434/iaops')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6380/0')
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9898')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin123')

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.from_url(REDIS_URL)

# MinIO setup
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Database Models
class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    url = Column(String)
    branch = Column(String, default="main")
    description = Column(Text)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sync = Column(DateTime)
    repo_metadata = Column(JSON)

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # build, test, deploy, sync
    status = Column(String, default="pending")  # pending, running, completed, failed
    repository_id = Column(Integer)
    command = Column(Text)
    environment = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    logs = Column(Text)

class LogEntry(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, index=True)
    level = Column(String)  # info, warning, error, debug
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    log_metadata = Column(JSON)

class SyncJob(Base):
    __tablename__ = "sync_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    source = Column(String)
    destination = Column(String)
    status = Column(String, default="pending")
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    config = Column(JSON)

class Runner(Base):
    __tablename__ = "runners"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String, default="offline")  # online, offline, busy
    labels = Column(JSON)
    repository = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime)

class DocSite(Base):
    __tablename__ = "doc_sites"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    repository_id = Column(Integer)
    status = Column(String, default="pending")  # building, ready, failed
    url = Column(String)
    last_build = Column(DateTime)
    config = Column(JSON)

# Database functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_redis():
    """Get Redis client"""
    return redis_client

def get_minio():
    """Get MinIO client"""
    return minio_client
