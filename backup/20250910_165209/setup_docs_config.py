#!/usr/bin/env python3
"""
Configuración para documentación centralizada en MinIO
"""
import psycopg2
import json
from datetime import datetime

# Configuración de base de datos
DB_CONFIG = {
    'host': 'iaops-postgres-main',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres_admin_2024'
}

# Configuración de MinIO para documentación
MINIO_DOCS_CONFIG = {
    'bucket': 'repositories',
    'paths': {
        'docs': 'docs/',           # Documentación procesada
        'builds': 'builds/',       # Builds versionados  
        'temp': 'temp/',           # Clones temporales
        'logs': 'logs/'            # Logs de procesamiento
    },
    'structure': {
        'repo_docs': '{repo_name}/',
        'repo_site': '{repo_name}/site/',
        'repo_source': '{repo_name}/docs/',
        'repo_config': '{repo_name}/mkdocs.yml',
        'build_version': 'builds/{repo_name}/{version}/',
        'build_latest': 'builds/{repo_name}/latest/',
        'temp_clone': 'temp/{repo_name}_{job_id}/'
    }
}

def setup_database_config():
    """Actualizar configuración en base de datos"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Crear tabla de configuración si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Configuraciones para documentación
        configs = [
            ('minio_docs_bucket', 'repositories', 'Bucket principal para documentación'),
            ('minio_docs_path', 'docs/', 'Ruta base para documentación procesada'),
            ('minio_builds_path', 'builds/', 'Ruta para builds versionados'),
            ('minio_temp_path', 'temp/', 'Ruta para clones temporales'),
            ('docs_base_url', 'http://localhost:8845/techdocs', 'URL base para documentación'),
            ('mkdocs_auto_create', 'true', 'Crear MkDocs automáticamente si no existe'),
            ('parallel_jobs_limit', '3', 'Límite de trabajos paralelos'),
            ('job_timeout_minutes', '30', 'Timeout para trabajos en minutos'),
            ('docs_sync_enabled', 'true', 'Habilitar sincronización de documentación')
        ]
        
        for key, value, description in configs:
            cur.execute("""
                INSERT INTO system_config (key, value, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    description = EXCLUDED.description,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value, description))
        
        # Crear tabla de trabajos si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sync_jobs (
                id SERIAL PRIMARY KEY,
                job_id VARCHAR(255) UNIQUE NOT NULL,
                repository_name VARCHAR(255) NOT NULL,
                repository_url VARCHAR(500) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                result_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear índices
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sync_jobs_status ON sync_jobs(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sync_jobs_repo ON sync_jobs(repository_name)")
        
        conn.commit()
        print("✅ Configuración de base de datos actualizada")
        
        # Mostrar configuración actual
        cur.execute("SELECT key, value, description FROM system_config WHERE key LIKE '%docs%' OR key LIKE '%minio%'")
        configs = cur.fetchall()
        
        print("\n📋 CONFIGURACIÓN ACTUAL:")
        for key, value, desc in configs:
            print(f"  {key}: {value}")
            print(f"    └─ {desc}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")

def create_minio_structure_script():
    """Crear script para estructura de MinIO"""
    script_content = f"""#!/usr/bin/env python3
import boto3
from botocore.client import Config

# Configuración MinIO
MINIO_CONFIG = {{
    'endpoint_url': 'http://ia-ops-minio-portal:9000',
    'aws_access_key_id': 'minioadmin',
    'aws_secret_access_key': 'minioadmin123',
    'region_name': 'us-east-1'
}}

def setup_minio_structure():
    try:
        s3_client = boto3.client('s3', **MINIO_CONFIG, config=Config(signature_version='s3v4'))
        
        bucket = 'repositories'
        folders = {json.dumps(MINIO_DOCS_CONFIG['paths'], indent=2)}
        
        # Crear estructura de carpetas
        for folder_name, folder_path in folders.items():
            key = folder_path + '.gitkeep'
            s3_client.put_object(Bucket=bucket, Key=key, Body=b'')
            print(f"✅ Creada carpeta: {{folder_path}}")
        
        print("✅ Estructura de MinIO configurada")
        
    except Exception as e:
        print(f"❌ Error configurando MinIO: {{e}}")

if __name__ == "__main__":
    setup_minio_structure()
"""
    
    with open('/home/giovanemere/ia-ops/ia-ops-dev-core/setup_minio_structure.py', 'w') as f:
        f.write(script_content)
    
    print("✅ Script de estructura MinIO creado")

if __name__ == "__main__":
    print("🚀 CONFIGURANDO DOCUMENTACIÓN CENTRALIZADA")
    print("=" * 50)
    
    setup_database_config()
    create_minio_structure_script()
    
    print("\n📁 ESTRUCTURA PROPUESTA:")
    print("repositories/")
    for path_name, path_value in MINIO_DOCS_CONFIG['paths'].items():
        print(f"├── {path_value:<15} # {path_name.title()}")
    
    print(f"\n🔗 URLs de acceso:")
    print(f"  - Repositorios: http://localhost:8845/repositories")
    print(f"  - TechDocs: http://localhost:8845/techdocs") 
    print(f"  - Tasks: http://localhost:8845/tasks")
    print(f"  - MinIO Files: http://localhost:8845/minio-files")
    
    print(f"\n✅ Configuración completada!")
