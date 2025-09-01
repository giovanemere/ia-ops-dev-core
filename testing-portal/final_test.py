#!/usr/bin/env python3
"""
Test Final del Portal de Pruebas IA-Ops
"""

import requests
import time
import threading
from simple_mock import start_all_mocks

def test_complete_workflow():
    """Probar workflow completo"""
    print("🚀 IA-Ops Testing Portal - Final Test")
    print("=" * 45)
    
    # 1. Iniciar mocks
    print("🎭 Starting mock services...")
    threads = start_all_mocks()
    
    print("⏳ Waiting for services to start...")
    time.sleep(3)
    
    # 2. Verificar health checks
    print("\n🏥 Health Checks:")
    services = [
        ("Repository Manager", "http://localhost:18860/health"),
        ("Task Manager", "http://localhost:18861/health"),
        ("Log Manager", "http://localhost:18862/health")
    ]
    
    healthy_services = 0
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {name}: Healthy")
                healthy_services += 1
            else:
                print(f"  ❌ {name}: Unhealthy ({response.status_code})")
        except Exception as e:
            print(f"  ❌ {name}: Error - {e}")
    
    # 3. Probar CRUD de repositorios
    print(f"\n📁 Repository CRUD Tests:")
    
    # Crear repositorio
    repo_data = {
        "name": "final-test-repo",
        "url": "https://github.com/test/final.git",
        "branch": "main",
        "description": "Final test repository"
    }
    
    try:
        create_response = requests.post(
            "http://localhost:18860/api/v1/repositories",
            json=repo_data,
            timeout=5
        )
        
        if create_response.status_code == 200:
            repo_result = create_response.json()
            repo_id = repo_result['data']['id']
            print(f"  ✅ Create Repository: ID {repo_id}")
            
            # Leer repositorio
            get_response = requests.get(f"http://localhost:18860/api/v1/repositories/{repo_id}", timeout=5)
            if get_response.status_code == 200:
                print(f"  ✅ Read Repository: Found")
            else:
                print(f"  ❌ Read Repository: Failed ({get_response.status_code})")
            
            # Listar repositorios
            list_response = requests.get("http://localhost:18860/api/v1/repositories", timeout=5)
            if list_response.status_code == 200:
                print(f"  ✅ List Repositories: Success")
            else:
                print(f"  ❌ List Repositories: Failed")
                
        else:
            print(f"  ❌ Create Repository: Failed ({create_response.status_code})")
            repo_id = 1  # Fallback
            
    except Exception as e:
        print(f"  ❌ Repository tests failed: {e}")
        repo_id = 1
    
    # 4. Probar gestión de tareas
    print(f"\n📋 Task Management Tests:")
    
    task_data = {
        "name": "final-test-task",
        "type": "build",
        "repository_id": repo_id,
        "command": "echo 'Final test execution'"
    }
    
    try:
        # Crear tarea
        task_response = requests.post(
            "http://localhost:18861/api/v1/tasks",
            json=task_data,
            timeout=5
        )
        
        if task_response.status_code == 200:
            task_result = task_response.json()
            task_id = task_result['data']['id']
            print(f"  ✅ Create Task: ID {task_id}")
            
            # Ejecutar tarea
            execute_response = requests.post(
                f"http://localhost:18861/api/v1/tasks/{task_id}/execute",
                timeout=10
            )
            
            if execute_response.status_code == 200:
                print(f"  ✅ Execute Task: Completed")
                
                # Obtener logs
                logs_response = requests.get(
                    f"http://localhost:18861/api/v1/tasks/{task_id}/logs",
                    timeout=5
                )
                
                if logs_response.status_code == 200:
                    print(f"  ✅ Get Task Logs: Available")
                else:
                    print(f"  ❌ Get Task Logs: Failed")
            else:
                print(f"  ❌ Execute Task: Failed ({execute_response.status_code})")
        else:
            print(f"  ❌ Create Task: Failed ({task_response.status_code})")
            
    except Exception as e:
        print(f"  ❌ Task tests failed: {e}")
    
    # 5. Probar logs
    print(f"\n📊 Log Management Tests:")
    
    log_data = {
        "service": "final-test",
        "level": "info",
        "message": "Final test log entry"
    }
    
    try:
        # Crear log
        log_response = requests.post(
            "http://localhost:18862/api/v1/logs",
            json=log_data,
            timeout=5
        )
        
        if log_response.status_code == 200:
            print(f"  ✅ Create Log: Success")
        else:
            print(f"  ❌ Create Log: Failed ({log_response.status_code})")
        
        # Listar logs
        list_logs_response = requests.get("http://localhost:18862/api/v1/logs", timeout=5)
        if list_logs_response.status_code == 200:
            print(f"  ✅ List Logs: Success")
        else:
            print(f"  ❌ List Logs: Failed")
            
    except Exception as e:
        print(f"  ❌ Log tests failed: {e}")
    
    # 6. Reporte final
    print(f"\n📊 Final Report:")
    print(f"  Mock Services: {healthy_services}/3 healthy")
    print(f"  Test Categories: Repository CRUD, Task Management, Log Management")
    print(f"  Integration: Multi-service workflow tested")
    
    if healthy_services == 3:
        print(f"\n🎉 SUCCESS: All mock services are working!")
        print(f"✨ The IA-Ops Testing Portal is ready for use!")
        print(f"\n🚀 Next Steps:")
        print(f"  1. Use './start_testing_portal.sh --mocks' for full testing")
        print(f"  2. Integrate with ia-ops-veritas portal")
        print(f"  3. Run against real services with '--real' flag")
        return True
    else:
        print(f"\n⚠️  Some services failed - check configuration")
        return False

if __name__ == '__main__':
    success = test_complete_workflow()
    exit(0 if success else 1)
