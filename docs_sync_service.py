#!/usr/bin/env python3
"""
Servicio de sincronización de documentación
Maneja el flujo completo: clone -> detect mkdocs -> build -> upload to minio
"""
import os
import uuid
import json
import shutil
import subprocess
import psycopg2
import boto3
from datetime import datetime
from botocore.client import Config
import tempfile
import threading
import time

class DocsyncService:
    def __init__(self):
        self.db_config = {
            'host': 'iaops-postgres-main',
            'port': '5432',
            'database': 'postgres',
            'user': 'postgres',
            'password': 'postgres_admin_2024'
        }
        
        self.minio_config = {
            'endpoint_url': 'http://ia-ops-minio-portal:9000',
            'aws_access_key_id': 'minioadmin',
            'aws_secret_access_key': 'minioadmin123',
            'region_name': 'us-east-1'
        }
        
        self.bucket = 'repositories'
        self.running_jobs = {}
    
    def start_sync_job(self, repo_name, repo_url, branch='main'):
        """Iniciar trabajo de sincronización"""
        # Verificar si ya hay un trabajo corriendo para este repo
        if self.is_job_running(repo_name):
            existing_job = self.get_running_job(repo_name)
            return {
                'success': False,
                'error': f'Job already running for {repo_name}',
                'existing_job_id': existing_job['job_id'],
                'status_url': f'/tasks/{existing_job["job_id"]}'
            }
        
        # Crear nuevo trabajo
        job_id = f"docs-sync-{uuid.uuid4().hex[:8]}"
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO sync_jobs (job_id, repository_name, repository_url, status, started_at)
                VALUES (%s, %s, %s, 'running', %s)
            """, (job_id, repo_name, repo_url, datetime.now()))
            
            conn.commit()
            cur.close()
            conn.close()
            
            # Iniciar trabajo en hilo separado
            thread = threading.Thread(
                target=self._process_sync_job,
                args=(job_id, repo_name, repo_url, branch)
            )
            thread.daemon = True
            thread.start()
            
            self.running_jobs[repo_name] = {
                'job_id': job_id,
                'started_at': datetime.now(),
                'thread': thread
            }
            
            return {
                'success': True,
                'job_id': job_id,
                'status_url': f'/tasks/{job_id}',
                'message': f'Documentation sync started for {repo_name}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_sync_job(self, job_id, repo_name, repo_url, branch):
        """Procesar trabajo de sincronización"""
        temp_dir = None
        try:
            self._update_job_status(job_id, 'running', 10, 'Cloning repository...')
            
            # 1. Clonar repositorio
            temp_dir = tempfile.mkdtemp(prefix=f'docs-sync-{repo_name}-')
            clone_path = os.path.join(temp_dir, repo_name)
            
            subprocess.run([
                'git', 'clone', '--depth', '1', '--branch', branch, repo_url, clone_path
            ], check=True, capture_output=True)
            
            self._update_job_status(job_id, 'running', 30, 'Analyzing repository structure...')
            
            # 2. Detectar/crear estructura MkDocs
            mkdocs_path = os.path.join(clone_path, 'mkdocs.yml')
            docs_path = os.path.join(clone_path, 'docs')
            
            if not os.path.exists(mkdocs_path):
                self._update_job_status(job_id, 'running', 40, 'Creating MkDocs structure...')
                self._create_mkdocs_structure(clone_path, repo_name)
            
            self._update_job_status(job_id, 'running', 60, 'Building documentation...')
            
            # 3. Construir documentación
            site_path = self._build_mkdocs(clone_path)
            
            self._update_job_status(job_id, 'running', 80, 'Uploading to MinIO...')
            
            # 4. Subir a MinIO
            self._upload_to_minio(repo_name, clone_path, site_path)
            
            self._update_job_status(job_id, 'completed', 100, 'Documentation sync completed')
            
            # Limpiar trabajos corriendo
            if repo_name in self.running_jobs:
                del self.running_jobs[repo_name]
                
        except Exception as e:
            self._update_job_status(job_id, 'failed', 0, f'Error: {str(e)}')
            if repo_name in self.running_jobs:
                del self.running_jobs[repo_name]
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def _create_mkdocs_structure(self, repo_path, repo_name):
        """Crear estructura MkDocs básica"""
        mkdocs_config = f"""site_name: {repo_name} Documentation
site_description: Documentation for {repo_name}
site_url: http://localhost:8845/techdocs/{repo_name}

nav:
  - Home: index.md
  - API: api.md
  - Setup: setup.md

theme:
  name: material
  palette:
    primary: blue
    accent: blue

markdown_extensions:
  - codehilite
  - admonition
  - toc:
      permalink: true
"""
        
        # Crear mkdocs.yml
        with open(os.path.join(repo_path, 'mkdocs.yml'), 'w') as f:
            f.write(mkdocs_config)
        
        # Crear carpeta docs si no existe
        docs_path = os.path.join(repo_path, 'docs')
        os.makedirs(docs_path, exist_ok=True)
        
        # Crear index.md básico
        readme_path = os.path.join(repo_path, 'README.md')
        index_content = f"# {repo_name} Documentation\n\nWelcome to {repo_name} documentation.\n"
        
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                index_content = f.read()
        
        with open(os.path.join(docs_path, 'index.md'), 'w') as f:
            f.write(index_content)
        
        # Crear páginas básicas
        with open(os.path.join(docs_path, 'api.md'), 'w') as f:
            f.write(f"# API Documentation\n\nAPI documentation for {repo_name}.\n")
        
        with open(os.path.join(docs_path, 'setup.md'), 'w') as f:
            f.write(f"# Setup Guide\n\nSetup instructions for {repo_name}.\n")
    
    def _build_mkdocs(self, repo_path):
        """Construir documentación con MkDocs"""
        site_path = os.path.join(repo_path, 'site')
        
        # Instalar mkdocs si no está disponible
        subprocess.run(['pip', 'install', 'mkdocs', 'mkdocs-material'], 
                      capture_output=True, check=False)
        
        # Construir sitio
        result = subprocess.run(['mkdocs', 'build'], 
                               cwd=repo_path, 
                               capture_output=True, 
                               text=True)
        
        if result.returncode != 0:
            raise Exception(f"MkDocs build failed: {result.stderr}")
        
        return site_path
    
    def _upload_to_minio(self, repo_name, repo_path, site_path):
        """Subir documentación a MinIO"""
        s3_client = boto3.client('s3', **self.minio_config, 
                                config=Config(signature_version='s3v4'))
        
        # Subir archivos del sitio construido
        for root, dirs, files in os.walk(site_path):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, site_path)
                s3_key = f"docs/{repo_name}/site/{relative_path}"
                
                with open(local_path, 'rb') as f:
                    s3_client.put_object(
                        Bucket=self.bucket,
                        Key=s3_key,
                        Body=f.read(),
                        ContentType=self._get_content_type(file)
                    )
        
        # Subir archivos fuente
        docs_source = os.path.join(repo_path, 'docs')
        if os.path.exists(docs_source):
            for root, dirs, files in os.walk(docs_source):
                for file in files:
                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, docs_source)
                    s3_key = f"docs/{repo_name}/source/{relative_path}"
                    
                    with open(local_path, 'rb') as f:
                        s3_client.put_object(
                            Bucket=self.bucket,
                            Key=s3_key,
                            Body=f.read()
                        )
        
        # Subir mkdocs.yml
        mkdocs_file = os.path.join(repo_path, 'mkdocs.yml')
        if os.path.exists(mkdocs_file):
            with open(mkdocs_file, 'rb') as f:
                s3_client.put_object(
                    Bucket=self.bucket,
                    Key=f"docs/{repo_name}/mkdocs.yml",
                    Body=f.read()
                )
    
    def _get_content_type(self, filename):
        """Obtener content type por extensión"""
        ext = os.path.splitext(filename)[1].lower()
        types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.svg': 'image/svg+xml'
        }
        return types.get(ext, 'application/octet-stream')
    
    def _update_job_status(self, job_id, status, progress, message):
        """Actualizar estado del trabajo"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            update_data = {
                'status': status,
                'progress': progress,
                'error_message': message if status == 'failed' else None,
                'completed_at': datetime.now() if status in ['completed', 'failed'] else None
            }
            
            cur.execute("""
                UPDATE sync_jobs 
                SET status = %s, progress = %s, error_message = %s, completed_at = %s
                WHERE job_id = %s
            """, (status, progress, update_data['error_message'], 
                  update_data['completed_at'], job_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Error updating job status: {e}")
    
    def is_job_running(self, repo_name):
        """Verificar si hay trabajo corriendo para el repositorio"""
        return repo_name in self.running_jobs
    
    def get_running_job(self, repo_name):
        """Obtener trabajo corriendo para el repositorio"""
        return self.running_jobs.get(repo_name)
    
    def get_job_status(self, job_id):
        """Obtener estado de trabajo"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT job_id, repository_name, status, progress, 
                       started_at, completed_at, error_message
                FROM sync_jobs WHERE job_id = %s
            """, (job_id,))
            
            result = cur.fetchone()
            cur.close()
            conn.close()
            
            if result:
                return {
                    'job_id': result[0],
                    'repository_name': result[1],
                    'status': result[2],
                    'progress': result[3],
                    'started_at': result[4].isoformat() if result[4] else None,
                    'completed_at': result[5].isoformat() if result[5] else None,
                    'error_message': result[6],
                    'docs_url': f'/techdocs/{result[1]}' if result[2] == 'completed' else None
                }
            
            return None
            
        except Exception as e:
            return {'error': str(e)}

# Instancia global del servicio
docs_sync_service = DocsyncService()
