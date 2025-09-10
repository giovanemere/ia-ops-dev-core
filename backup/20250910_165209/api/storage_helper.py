#!/usr/bin/env python3
"""
Helper para organización de almacenamiento por proyectos
Bucket: ia-ops-dev-core (nombre del proyecto)
"""

def get_project_path(project_name, folder_type, file_name=""):
    """
    Generar ruta organizada por proyecto
    Estructura: proyecto/tipo/archivo
    """
    if file_name:
        return f"{project_name}/{folder_type}/{file_name}"
    else:
        return f"{project_name}/{folder_type}/"

def get_storage_url(bucket_name, project_name, folder_type, file_name=""):
    """
    Generar URL completa para acceso a archivos
    Bucket: ia-ops-dev-core
    """
    path = get_project_path(project_name, folder_type, file_name)
    return f"http://localhost:9898/{bucket_name}/{path}"

def get_project_structure():
    """
    Estructura estándar por proyecto
    """
    return {
        "bucket": "ia-ops-dev-core",
        "folders": ["docs", "repositories", "builds", "logs", "backups"],
        "projects": ["ia-ops-core", "ia-ops-docs", "ia-ops-minio", "ia-ops-veritas"]
    }

# Ejemplos de uso:
# get_project_path("ia-ops-core", "docs", "index.html") 
# -> "ia-ops-core/docs/index.html"
#
# get_storage_url("ia-ops-dev-core", "ia-ops-core", "docs", "index.html")
# -> "http://localhost:9898/ia-ops-dev-core/ia-ops-core/docs/index.html"
