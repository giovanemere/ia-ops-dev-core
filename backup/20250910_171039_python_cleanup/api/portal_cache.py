#!/usr/bin/env python3
"""
Portal Cache Integration for all IA-Ops Services
Standardized caching for Repository Manager, Task Manager, Log Manager, etc.
"""

from functools import wraps
from flask import request, jsonify
import hashlib
import json
from cache_service import cache_service

def cache_response(service_name: str, ttl: int = 300):
    """Decorator to cache API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key from request
            cache_key = _generate_request_key(request)
            
            # Try to get from cache
            cached_result = cache_service.get(service_name, cache_key)
            if cached_result:
                return jsonify(cached_result)
            
            # Execute function
            result = f(*args, **kwargs)
            
            # Cache the result if it's successful
            if hasattr(result, 'status_code') and result.status_code == 200:
                cache_service.set(service_name, cache_key, result.get_json(), ttl)
            elif isinstance(result, dict):
                cache_service.set(service_name, cache_key, result, ttl)
            
            return result
        return decorated_function
    return decorator

def cache_data(service_name: str, key: str, data: any, ttl: int = 300):
    """Cache arbitrary data"""
    return cache_service.set(service_name, key, data, ttl)

def get_cached_data(service_name: str, key: str):
    """Get cached data"""
    return cache_service.get(service_name, key)

def invalidate_cache(service_name: str, pattern: str = None):
    """Invalidate cache for service or specific pattern"""
    if pattern:
        # For specific patterns, we'd need to implement pattern matching
        # For now, clear entire service cache
        return cache_service.clear_service(service_name)
    else:
        return cache_service.clear_service(service_name)

def get_cache_stats():
    """Get cache statistics for all services"""
    return cache_service.get_stats()

def _generate_request_key(request):
    """Generate cache key from request"""
    key_data = {
        'path': request.path,
        'method': request.method,
        'args': dict(request.args),
        'json': request.get_json() if request.is_json else None
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()

# Service-specific cache helpers
class RepositoryCache:
    SERVICE_NAME = "repository_manager"
    
    @staticmethod
    def get_repositories():
        return get_cached_data(RepositoryCache.SERVICE_NAME, "repositories_list")
    
    @staticmethod
    def cache_repositories(repos, ttl=300):
        return cache_data(RepositoryCache.SERVICE_NAME, "repositories_list", repos, ttl)
    
    @staticmethod
    def invalidate_repositories():
        return invalidate_cache(RepositoryCache.SERVICE_NAME, "repositories")

class TaskCache:
    SERVICE_NAME = "task_manager"
    
    @staticmethod
    def get_tasks():
        return get_cached_data(TaskCache.SERVICE_NAME, "tasks_list")
    
    @staticmethod
    def cache_tasks(tasks, ttl=300):
        return cache_data(TaskCache.SERVICE_NAME, "tasks_list", tasks, ttl)
    
    @staticmethod
    def invalidate_tasks():
        return invalidate_cache(TaskCache.SERVICE_NAME, "tasks")

class LogCache:
    SERVICE_NAME = "log_manager"
    
    @staticmethod
    def get_logs(source):
        return get_cached_data(LogCache.SERVICE_NAME, f"logs_{source}")
    
    @staticmethod
    def cache_logs(source, logs, ttl=60):  # Shorter TTL for logs
        return cache_data(LogCache.SERVICE_NAME, f"logs_{source}", logs, ttl)

class ProviderCache:
    SERVICE_NAME = "provider_admin"
    
    @staticmethod
    def get_providers():
        return get_cached_data(ProviderCache.SERVICE_NAME, "providers_list")
    
    @staticmethod
    def cache_providers(providers, ttl=600):  # Longer TTL for providers
        return cache_data(ProviderCache.SERVICE_NAME, "providers_list", providers, ttl)
