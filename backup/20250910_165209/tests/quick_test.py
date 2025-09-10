#!/usr/bin/env python3
"""
Script de pruebas rápidas para IA-Ops Dev Core
Ejecuta las pruebas más importantes para validar el funcionamiento
"""

import sys
import json
from test_api_methods import IAOpsTestClient

def quick_health_check():
    """Verificación rápida de salud de todos los servicios"""
    print("🏥 Verificación rápida de salud de servicios...")
    
    client = IAOpsTestClient()
    results = client.test_all_health_checks()
    
    all_healthy = True
    for service, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {service}: {result['status_code']}")
        if not result['success']:
            all_healthy = False
    
    return all_healthy, results

def quick_database_test():
    """Prueba rápida de conectividad de bases de datos"""
    print("\n🗄️ Verificación de bases de datos...")
    
    client = IAOpsTestClient()
    
    # Test PostgreSQL via Repository Manager
    pg_result = client.test_get_repositories()
    pg_status = "✅" if pg_result['success'] else "❌"
    print(f"  {pg_status} PostgreSQL (via Repository Manager): {pg_result['status_code']}")
    
    # Test Redis via Task Manager
    redis_result = client.test_get_tasks()
    redis_status = "✅" if redis_result['success'] else "❌"
    print(f"  {redis_status} Redis (via Task Manager): {redis_result['status_code']}")
    
    # Test MinIO via DataSync Manager
    minio_result = client.test_get_backups()
    minio_status = "✅" if minio_result['success'] else "❌"
    print(f"  {minio_status} MinIO (via DataSync Manager): {minio_result['status_code']}")
    
    return {
        'postgresql': pg_result['success'],
        'redis': redis_result['success'],
        'minio': minio_result['success']
    }

def quick_crud_test():
    """Prueba rápida de operaciones CRUD"""
    print("\n🔄 Prueba de operaciones CRUD...")
    
    client = IAOpsTestClient()
    
    # Test Repository CRUD
    repo_data = {
        "name": "quick-test-repo",
        "url": "https://github.com/test/quick.git",
        "branch": "main",
        "description": "Quick test repository"
    }
    
    create_result = client.test_create_repository(repo_data)
    create_status = "✅" if create_result['success'] else "❌"
    print(f"  {create_status} Crear repositorio: {create_result['status_code']}")
    
    if create_result['success']:
        repo_id = create_result['data'].get('data', {}).get('id')
        if repo_id:
            # Test Read
            read_result = client.test_get_repository(repo_id)
            read_status = "✅" if read_result['success'] else "❌"
            print(f"  {read_status} Leer repositorio: {read_result['status_code']}")
            
            # Test Update
            updated_data = repo_data.copy()
            updated_data['description'] = 'Updated description'
            update_result = client.test_update_repository(repo_id, updated_data)
            update_status = "✅" if update_result['success'] else "❌"
            print(f"  {update_status} Actualizar repositorio: {update_result['status_code']}")
            
            # Test Delete
            delete_result = client.test_delete_repository(repo_id)
            delete_status = "✅" if delete_result['success'] else "❌"
            print(f"  {delete_status} Eliminar repositorio: {delete_result['status_code']}")
    
    return create_result['success']

def quick_integration_test():
    """Prueba rápida de integración entre servicios"""
    print("\n🔗 Prueba de integración de servicios...")
    
    client = IAOpsTestClient()
    
    # Crear repositorio
    repo_result = client.test_create_repository({
        "name": "integration-quick-test",
        "url": "https://github.com/test/integration.git",
        "branch": "main"
    })
    
    if not repo_result['success']:
        print("  ❌ Falló creación de repositorio")
        return False
    
    repo_id = repo_result['data'].get('data', {}).get('id')
    
    # Crear tarea para el repositorio
    task_result = client.test_create_task({
        "name": "quick-integration-task",
        "type": "test",
        "repository_id": repo_id,
        "command": "echo 'Quick integration test'"
    })
    
    task_status = "✅" if task_result['success'] else "❌"
    print(f"  {task_status} Crear tarea para repositorio: {task_result['status_code']}")
    
    # Crear log del proceso
    log_result = client.test_create_log({
        "service": "quick-test",
        "level": "info",
        "message": f"Quick test completed for repo {repo_id}"
    })
    
    log_status = "✅" if log_result['success'] else "❌"
    print(f"  {log_status} Crear log de proceso: {log_result['status_code']}")
    
    # Limpiar - eliminar repositorio creado
    if repo_id:
        client.test_delete_repository(repo_id)
    
    return repo_result['success'] and task_result['success'] and log_result['success']

def main():
    """Función principal de pruebas rápidas"""
    print("🚀 IA-Ops Dev Core - Pruebas Rápidas")
    print("=" * 50)
    
    # 1. Health Check
    healthy, health_results = quick_health_check()
    
    if not healthy:
        print("\n❌ Algunos servicios no están disponibles. Verifica la configuración.")
        sys.exit(1)
    
    # 2. Database Test
    db_results = quick_database_test()
    
    # 3. CRUD Test
    crud_success = quick_crud_test()
    
    # 4. Integration Test
    integration_success = quick_integration_test()
    
    # Resumen
    print("\n📊 RESUMEN DE PRUEBAS RÁPIDAS")
    print("-" * 35)
    
    health_status = "✅" if healthy else "❌"
    print(f"  {health_status} Health Checks: {'PASS' if healthy else 'FAIL'}")
    
    db_all_ok = all(db_results.values())
    db_status = "✅" if db_all_ok else "❌"
    print(f"  {db_status} Bases de Datos: {'PASS' if db_all_ok else 'FAIL'}")
    
    crud_status = "✅" if crud_success else "❌"
    print(f"  {crud_status} Operaciones CRUD: {'PASS' if crud_success else 'FAIL'}")
    
    integration_status = "✅" if integration_success else "❌"
    print(f"  {integration_status} Integración: {'PASS' if integration_success else 'FAIL'}")
    
    # Resultado final
    all_passed = healthy and db_all_ok and crud_success and integration_success
    
    if all_passed:
        print(f"\n🎉 TODAS LAS PRUEBAS PASARON - Sistema listo para desarrollo")
        return 0
    else:
        print(f"\n⚠️ ALGUNAS PRUEBAS FALLARON - Revisar configuración")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
