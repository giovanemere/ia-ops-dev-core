#!/usr/bin/env python3
"""
MkDocs Service - Construcción de documentación y subida a MinIO
"""

import os
import subprocess
import shutil
import yaml
from typing import Dict, Optional
import logging
from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)

class MkDocsService:
    def __init__(self, minio_client: Optional[Minio] = None):
        self.minio_client = minio_client
        self.bucket_name = 'docs'
    
    def has_mkdocs_config(self, repo_path: str) -> bool:
        """Verificar si el repositorio tiene configuración MkDocs"""
        config_files = ['mkdocs.yml', 'mkdocs.yaml']
        return any(os.path.exists(os.path.join(repo_path, config)) for config in config_files)
    
    def create_mkdocs_config(self, repo_path: str, project_name: str, description: str = '') -> bool:
        """Crear configuración MkDocs básica"""
        try:
            config = {
                'site_name': project_name,
                'site_description': description,
                'theme': {
                    'name': 'material',
                    'features': [
                        'navigation.tabs',
                        'navigation.sections',
                        'toc.integrate',
                        'navigation.top'
                    ]
                },
                'markdown_extensions': [
                    'codehilite',
                    'admonition',
                    'toc',
                    'pymdownx.superfences',
                    'pymdownx.tabbed'
                ],
                'nav': [
                    {'Home': 'index.md'},
                    {'Documentation': 'docs/'}
                ]
            }
            
            config_path = os.path.join(repo_path, 'mkdocs.yml')
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            # Crear estructura básica de docs
            docs_dir = os.path.join(repo_path, 'docs')
            os.makedirs(docs_dir, exist_ok=True)
            
            # Crear index.md si no existe
            index_path = os.path.join(repo_path, 'docs', 'index.md')
            if not os.path.exists(index_path):
                with open(index_path, 'w') as f:
                    f.write(f"# {project_name}\n\n{description}\n\n## Documentación\n\nBienvenido a la documentación del proyecto {project_name}.\n")
            
            return True
        except Exception as e:
            logger.error(f"Error creating MkDocs config: {e}")
            return False
    
    def build_docs(self, repo_path: str, output_dir: str) -> Dict:
        """Construir documentación MkDocs"""
        try:
            if not self.has_mkdocs_config(repo_path):
                return {'success': False, 'error': 'No MkDocs configuration found'}
            
            # Limpiar directorio de salida
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            
            # Construir documentación
            cmd = ['mkdocs', 'build', '--site-dir', output_dir]
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output_dir': output_dir,
                    'message': 'Documentation built successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'message': 'Build failed'
                }
                
        except Exception as e:
            logger.error(f"Error building docs: {e}")
            return {'success': False, 'error': str(e)}
    
    def upload_to_minio(self, local_path: str, project_name: str) -> Dict:
        """Subir documentación construida a MinIO"""
        try:
            if not self.minio_client:
                return {'success': False, 'error': 'MinIO client not configured'}
            
            # Crear bucket si no existe
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
            
            uploaded_files = []
            
            # Subir todos los archivos
            for root, dirs, files in os.walk(local_path):
                for file in files:
                    local_file = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file, local_path)
                    object_name = f"{project_name}/{relative_path}".replace('\\', '/')
                    
                    self.minio_client.fput_object(
                        self.bucket_name,
                        object_name,
                        local_file
                    )
                    uploaded_files.append(object_name)
            
            return {
                'success': True,
                'bucket': self.bucket_name,
                'project': project_name,
                'files_uploaded': len(uploaded_files),
                'url': f"http://localhost:9898/{self.bucket_name}/{project_name}/index.html"
            }
            
        except S3Error as e:
            logger.error(f"MinIO error: {e}")
            return {'success': False, 'error': f'MinIO error: {e}'}
        except Exception as e:
            logger.error(f"Error uploading to MinIO: {e}")
            return {'success': False, 'error': str(e)}
