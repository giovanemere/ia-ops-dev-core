#!/usr/bin/env python3
"""
Centralized Storage Configuration for IA-Ops
All services must use the same bucket for consistency
"""

# Single bucket configuration for all IA-Ops services
STORAGE_CONFIG = {
    "bucket_name": "ia-ops-storage",
    "folders": {
        "docs": "docs/",
        "repositories": "repositories/", 
        "builds": "builds/",
        "logs": "logs/",
        "backups": "backups/"
    }
}

def get_bucket_name():
    """Get the single bucket name for all services"""
    return STORAGE_CONFIG["bucket_name"]

def get_folder_path(folder_type):
    """Get folder path within the bucket"""
    return STORAGE_CONFIG["folders"].get(folder_type, "")

def get_object_path(folder_type, object_name):
    """Get full object path within the bucket"""
    folder = get_folder_path(folder_type)
    return f"{folder}{object_name}"
