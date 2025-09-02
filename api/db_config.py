#!/usr/bin/env python3
"""
REUTILIZAR servicios existentes:
PostgreSQL: veritas-postgres (puerto 5432) - veritas_user/veritas_pass/veritas_db
Redis: veritas-redis (puerto 6379)
MinIO: ia-ops-minio-portal (puertos 9898, 9899)
UN BUCKET: ia-ops-storage
"""
import subprocess

class DBConfig:
    def __init__(self):
        self._cache = {}
    
    def get_config(self, key, default=None):
        if key in self._cache:
            return self._cache[key]
        
        try:
            cmd = f'PGPASSWORD=veritas_pass psql -h localhost -p 5432 -U veritas_user -d veritas_db -t -c "SELECT config_value FROM system_config WHERE config_key = \'{key}\';"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                value = result.stdout.strip()
                self._cache[key] = value
                return value
        except:
            pass
        return default
    
    def get_redis_client(self):
        import redis
        return redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    def get_minio_client(self):
        from minio import Minio
        return Minio('localhost:9898', access_key='minioadmin', secret_key='minioadmin123', secure=False)
    
    def get_storage_bucket(self):
        return self.get_config('storage_bucket', 'ia-ops-storage')
    
    def get_service_port(self, service_name):
        return int(self.get_config(f'port_{service_name}', '8000'))

db_config = DBConfig()
