#!/usr/bin/env python3
import boto3
from botocore.client import Config

# Configuración MinIO
MINIO_CONFIG = {
    'endpoint_url': 'http://ia-ops-minio-portal:9000',
    'aws_access_key_id': 'minioadmin',
    'aws_secret_access_key': 'minioadmin123',
    'region_name': 'us-east-1'
}

def setup_minio_structure():
    try:
        s3_client = boto3.client('s3', **MINIO_CONFIG, config=Config(signature_version='s3v4'))
        
        bucket = 'repositories'
        folders = {
  "docs": "docs/",
  "builds": "builds/",
  "temp": "temp/",
  "logs": "logs/"
}
        
        # Crear estructura de carpetas
        for folder_name, folder_path in folders.items():
            key = folder_path + '.gitkeep'
            s3_client.put_object(Bucket=bucket, Key=key, Body=b'')
            print(f"✅ Creada carpeta: {folder_path}")
        
        print("✅ Estructura de MinIO configurada")
        
    except Exception as e:
        print(f"❌ Error configurando MinIO: {e}")

if __name__ == "__main__":
    setup_minio_structure()
