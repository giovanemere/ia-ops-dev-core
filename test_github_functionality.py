#!/usr/bin/env python3
"""
Script de prueba para funcionalidades GitHub
"""

import requests
import json

BASE_URL = "http://localhost:8860"

def test_github_repositories():
    """Probar listado de repositorios GitHub"""
    print("🔍 Probando listado de repositorios GitHub...")
    
    # Probar con usuario público
    response = requests.get(f"{BASE_URL}/api/v1/github/repositories?username=octocat")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Encontrados {len(data.get('data', []))} repositorios")
        if data.get('data'):
            print(f"   Ejemplo: {data['data'][0]['name']}")
    else:
        print(f"❌ Error: {response.status_code}")

def test_create_project():
    """Probar creación de proyecto completo"""
    print("\n📁 Probando creación de proyecto...")
    
    project_data = {
        "project_name": "Test Project",
        "project_description": "Proyecto de prueba para IA-Ops",
        "github_url": "https://github.com/octocat/Hello-World.git",
        "branch": "master"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/repositories/projects",
        json=project_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Proyecto creado exitosamente")
        print(f"   Nombre: {data['data']['project_name']}")
        print(f"   Docs URL: {data['data']['docs_url']}")
        return data['data']['id']
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def test_build_docs(repo_id):
    """Probar construcción de documentación"""
    if not repo_id:
        return
        
    print(f"\n📚 Probando construcción de docs para repo {repo_id}...")
    
    response = requests.post(f"{BASE_URL}/api/v1/docs/{repo_id}/build")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Documentación construida exitosamente")
        print(f"   URL: {data['data']['docs_url']}")
        print(f"   Archivos: {data['data']['files_uploaded']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def test_health():
    """Probar health check"""
    print("\n❤️ Probando health check...")
    
    response = requests.get(f"{BASE_URL}/api/v1/health/")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Servicio saludable: {data['data']['service']}")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de funcionalidades GitHub")
    print("=" * 50)
    
    # Probar health
    test_health()
    
    # Probar GitHub
    test_github_repositories()
    
    # Probar creación de proyecto
    repo_id = test_create_project()
    
    # Probar construcción de docs
    test_build_docs(repo_id)
    
    print("\n✨ Pruebas completadas")
