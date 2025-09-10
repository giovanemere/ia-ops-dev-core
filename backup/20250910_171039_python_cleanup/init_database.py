#!/usr/bin/env python3
"""
Inicializar base de datos con tabla sync_jobs
"""
import psycopg2
from datetime import datetime

DB_CONFIG = {
    'host': 'iaops-postgres-main',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres_admin_2024'
}

def init_database():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Crear tabla sync_jobs
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
        print("✅ Tabla sync_jobs creada exitosamente")
        
        # Verificar tabla
        cur.execute("SELECT COUNT(*) FROM sync_jobs")
        count = cur.fetchone()[0]
        print(f"📊 Registros en sync_jobs: {count}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")

if __name__ == "__main__":
    init_database()
