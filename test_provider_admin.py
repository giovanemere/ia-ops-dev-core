#!/usr/bin/env python3
"""
Script de prueba para Provider Administration API
"""

import requests
import json

BASE_URL = "http://localhost:8866"

def test_health():
    """Probar health check"""
    print("🔍 Probando health check...")
    
    response = requests.get(f"{BASE_URL}/api/v1/health/")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Servicio saludable: {data['data']['service']}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False

def test_provider_requirements():
    """Probar obtención de requisitos por provider"""
    print("\n📋 Probando requisitos de providers...")
    
    providers = ['github', 'azure', 'aws', 'gcp', 'openai']
    
    for provider in providers:
        response = requests.get(f"{BASE_URL}/api/v1/config/requirements/{provider}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {provider.upper()}: {len(data['data']['requirements'])} campos requeridos")
        else:
            print(f"❌ Error con {provider}: {response.status_code}")

def test_create_github_provider():
    """Probar creación de provider GitHub"""
    print("\n📁 Probando creación de provider GitHub...")
    
    provider_data = {
        "name": "GitHub Test",
        "type": "github",
        "description": "Provider de prueba para GitHub",
        "is_active": True,
        "config": {
            "token": "ghp_test_token_example",
            "username": "test-user"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/providers/",
        json=provider_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Provider GitHub creado exitosamente")
        print(f"   ID: {data['data']['id']}")
        print(f"   Nombre: {data['data']['name']}")
        return data['data']['id']
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def test_list_providers():
    """Probar listado de providers"""
    print("\n📊 Probando listado de providers...")
    
    response = requests.get(f"{BASE_URL}/api/v1/providers/")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Encontrados {len(data['data'])} providers")
        for provider in data['data']:
            print(f"   - {provider['name']} ({provider['type']}) - {'Activo' if provider['is_active'] else 'Inactivo'}")
    else:
        print(f"❌ Error: {response.status_code}")

def test_connection_github():
    """Probar conexión con GitHub (simulada)"""
    print("\n🔗 Probando conexión GitHub...")
    
    test_data = {
        "provider_type": "github",
        "config": {
            "token": "ghp_test_token_example"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/config/test-connection",
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("✅ Conexión GitHub exitosa (simulada)")
        else:
            print(f"❌ Conexión falló: {data.get('error', 'Error desconocido')}")
    else:
        print(f"❌ Error: {response.status_code}")

def test_create_credential(provider_id):
    """Probar creación de credencial"""
    if not provider_id:
        return
        
    print(f"\n🔐 Probando creación de credencial para provider {provider_id}...")
    
    credential_data = {
        "credential_type": "token",
        "credential_name": "GitHub Token Principal",
        "credential_value": "ghp_real_token_would_be_here",
        "expires_at": "2024-12-31T23:59:59"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/providers/{provider_id}/credentials",
        json=credential_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Credencial creada exitosamente")
        print(f"   Tipo: {data['data']['credential_type']}")
        print(f"   Nombre: {data['data']['credential_name']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

def test_aws_requirements():
    """Probar requisitos específicos de AWS"""
    print("\n☁️ Probando requisitos específicos de AWS...")
    
    response = requests.get(f"{BASE_URL}/api/v1/config/requirements/aws")
    
    if response.status_code == 200:
        data = response.json()
        requirements = data['data']['requirements']
        print("✅ Requisitos AWS:")
        for field, config in requirements.items():
            required = "✅" if config['required'] else "❌"
            print(f"   {required} {field}: {config['description']}")
    else:
        print(f"❌ Error: {response.status_code}")

def main():
    print("🚀 Iniciando pruebas de Provider Administration API")
    print("=" * 60)
    
    # Probar health
    if not test_health():
        print("❌ Servicio no disponible, terminando pruebas")
        return
    
    # Probar requisitos
    test_provider_requirements()
    
    # Probar AWS específicamente
    test_aws_requirements()
    
    # Probar creación de provider
    provider_id = test_create_github_provider()
    
    # Probar listado
    test_list_providers()
    
    # Probar conexión
    test_connection_github()
    
    # Probar credenciales
    test_create_credential(provider_id)
    
    print("\n✨ Pruebas completadas")

if __name__ == "__main__":
    main()
