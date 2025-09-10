#!/usr/bin/env python3
"""
Quick Test Runner - Versión simplificada para pruebas rápidas
"""

import json
import requests
import time
import threading
from mock_services import MockServiceManager, MOCK_SERVICES_CONFIG

def test_mock_services():
    """Probar servicios mock"""
    print("🎭 Testing Mock Services")
    print("=" * 30)
    
    # Crear manager
    manager = MockServiceManager()
    
    # Crear servicios mock
    for service_name, config in MOCK_SERVICES_CONFIG.items():
        manager.create_mock_service(service_name, config['port'], config['endpoints'])
    
    # Iniciar servicios en threads
    threads = []
    for service_name in MOCK_SERVICES_CONFIG:
        service = manager.services[service_name]
        thread = threading.Thread(
            target=lambda: service['app'].run(
                host='0.0.0.0', 
                port=service['port'], 
                debug=False, 
                use_reloader=False
            ),
            daemon=True
        )
        thread.start()
        threads.append(thread)
    
    print("⏳ Waiting for services to start...")
    time.sleep(3)
    
    # Probar cada servicio
    results = {}
    for service_name, config in MOCK_SERVICES_CONFIG.items():
        port = config['port']
        try:
            # Health check
            response = requests.get(f'http://localhost:{port}/health', timeout=5)
            results[service_name] = {
                'health': response.status_code == 200,
                'response': response.json() if response.content else {}
            }
            
            status = "✅" if results[service_name]['health'] else "❌"
            print(f"  {status} {service_name} (:{port})")
            
        except Exception as e:
            results[service_name] = {'health': False, 'error': str(e)}
            print(f"  ❌ {service_name} (:{port}) - {e}")
    
    return results

def test_api_endpoints():
    """Probar endpoints específicos"""
    print("\n🧪 Testing API Endpoints")
    print("=" * 30)
    
    tests = [
        {
            'name': 'Repository Health Check',
            'url': 'http://localhost:18860/health',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Create Repository',
            'url': 'http://localhost:18860/api/v1/repositories',
            'method': 'POST',
            'data': {
                'name': 'quick-test-repo',
                'url': 'https://github.com/test/quick.git',
                'branch': 'main',
                'description': 'Quick test repository'
            },
            'expected_status': 200
        },
        {
            'name': 'List Repositories',
            'url': 'http://localhost:18860/api/v1/repositories',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Task Manager Health',
            'url': 'http://localhost:18861/health',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Create Task',
            'url': 'http://localhost:18861/api/v1/tasks',
            'method': 'POST',
            'data': {
                'name': 'quick-test-task',
                'type': 'test',
                'repository_id': 1,
                'command': 'echo "Quick test"'
            },
            'expected_status': 200
        }
    ]
    
    results = []
    for test in tests:
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=5)
            elif test['method'] == 'POST':
                response = requests.post(test['url'], json=test.get('data', {}), timeout=5)
            
            passed = response.status_code == test['expected_status']
            status = "✅ PASS" if passed else "❌ FAIL"
            
            result = {
                'name': test['name'],
                'passed': passed,
                'status_code': response.status_code,
                'expected': test['expected_status']
            }
            
            results.append(result)
            print(f"  {status} {test['name']} ({response.status_code})")
            
        except Exception as e:
            results.append({
                'name': test['name'],
                'passed': False,
                'error': str(e)
            })
            print(f"  ❌ FAIL {test['name']} - {e}")
    
    return results

def test_integration_workflow():
    """Probar workflow de integración"""
    print("\n🔗 Testing Integration Workflow")
    print("=" * 35)
    
    try:
        # 1. Crear repositorio
        print("  Step 1: Creating repository...")
        repo_response = requests.post(
            'http://localhost:18860/api/v1/repositories',
            json={
                'name': 'integration-test-repo',
                'url': 'https://github.com/test/integration.git',
                'branch': 'main',
                'description': 'Integration test repository'
            },
            timeout=5
        )
        
        if repo_response.status_code != 200:
            raise Exception(f"Failed to create repository: {repo_response.status_code}")
        
        repo_data = repo_response.json()
        repo_id = repo_data['data']['id']
        print(f"    ✅ Repository created with ID: {repo_id}")
        
        # 2. Crear tarea
        print("  Step 2: Creating task...")
        task_response = requests.post(
            'http://localhost:18861/api/v1/tasks',
            json={
                'name': 'integration-test-task',
                'type': 'build',
                'repository_id': int(repo_id),
                'command': 'echo "Integration test"'
            },
            timeout=5
        )
        
        if task_response.status_code != 200:
            raise Exception(f"Failed to create task: {task_response.status_code}")
        
        task_data = task_response.json()
        task_id = task_data['data']['id']
        print(f"    ✅ Task created with ID: {task_id}")
        
        # 3. Ejecutar tarea
        print("  Step 3: Executing task...")
        execute_response = requests.post(
            f'http://localhost:18861/api/v1/tasks/{task_id}/execute',
            timeout=10
        )
        
        if execute_response.status_code != 200:
            raise Exception(f"Failed to execute task: {execute_response.status_code}")
        
        print("    ✅ Task executed successfully")
        
        # 4. Obtener logs
        print("  Step 4: Getting task logs...")
        logs_response = requests.get(
            f'http://localhost:18861/api/v1/tasks/{task_id}/logs',
            timeout=5
        )
        
        if logs_response.status_code != 200:
            raise Exception(f"Failed to get logs: {logs_response.status_code}")
        
        print("    ✅ Task logs retrieved")
        
        print("\n  🎉 Integration workflow completed successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Integration workflow failed: {e}")
        return False

def generate_report(mock_results, api_results, integration_result):
    """Generar reporte simple"""
    print("\n📊 Test Report")
    print("=" * 20)
    
    # Mock services
    mock_healthy = sum(1 for r in mock_results.values() if r.get('health', False))
    print(f"Mock Services: {mock_healthy}/{len(mock_results)} healthy")
    
    # API tests
    api_passed = sum(1 for r in api_results if r.get('passed', False))
    print(f"API Tests: {api_passed}/{len(api_results)} passed")
    
    # Integration
    integration_status = "✅ PASS" if integration_result else "❌ FAIL"
    print(f"Integration Test: {integration_status}")
    
    # Overall
    total_tests = len(api_results) + 1  # +1 for integration
    total_passed = api_passed + (1 if integration_result else 0)
    success_rate = (total_passed / total_tests) * 100
    
    print(f"\nOverall Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed")
    
    return success_rate

def main():
    """Función principal"""
    print("🚀 IA-Ops Quick Test Suite")
    print("=" * 40)
    
    # 1. Probar servicios mock
    mock_results = test_mock_services()
    
    # 2. Probar endpoints API
    api_results = test_api_endpoints()
    
    # 3. Probar integración
    integration_result = test_integration_workflow()
    
    # 4. Generar reporte
    success_rate = generate_report(mock_results, api_results, integration_result)
    
    # Exit code
    return 0 if success_rate == 100 else 1

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
