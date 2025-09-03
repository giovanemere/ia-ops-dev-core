#!/usr/bin/env python3
"""
Módulo de configuración de base de datos para Service Layer
"""
import os
import psycopg2
from typing import Dict, Any, Optional

class ServiceConfigDB:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'iaops-postgres-main'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'postgres'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres_admin_2024')
        }
    
    def get_connection(self):
        """Obtener conexión a base de datos"""
        return psycopg2.connect(**self.db_config)
    
    def init_service_config_table(self) -> bool:
        """Inicializar tabla de configuración de servicios"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Crear tabla si no existe
            cur.execute("""
                CREATE TABLE IF NOT EXISTS service_configs (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(100) NOT NULL,
                    config_key VARCHAR(100) NOT NULL,
                    config_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(service_name, config_key)
                )
            """)
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error inicializando tabla de configuración: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_config(self, service: str, key: str = None) -> Optional[Dict[str, Any]]:
        """Obtener configuración de servicio"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            if key:
                cur.execute("SELECT config_value FROM service_configs WHERE service_name = %s AND config_key = %s", (service, key))
                result = cur.fetchone()
                return result[0] if result else None
            else:
                cur.execute("SELECT config_key, config_value FROM service_configs WHERE service_name = %s", (service,))
                results = cur.fetchall()
                return {row[0]: row[1] for row in results}
        except Exception as e:
            print(f"Error obteniendo configuración: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def set_config(self, service: str, key: str, value: str) -> bool:
        """Establecer configuración de servicio"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO service_configs (service_name, config_key, config_value)
                VALUES (%s, %s, %s)
                ON CONFLICT (service_name, config_key)
                DO UPDATE SET config_value = EXCLUDED.config_value, updated_at = CURRENT_TIMESTAMP
            """, (service, key, value))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error estableciendo configuración: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
