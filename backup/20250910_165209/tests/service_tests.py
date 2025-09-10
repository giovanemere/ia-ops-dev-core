#!/usr/bin/env python3
"""
Pruebas específicas por servicio para IA-Ops Dev Core
Incluye validación de integración con PostgreSQL, Redis y MinIO
"""

import asyncio
import json
from test_api_methods import IAOpsTestClient, SAMPLE_REPOSITORY, SAMPLE_TASK, SAMPLE_LOG

class ServiceTester:
    def __init__(self):
        self.client = IAOpsTestClient()
        self.test_results = {}
    
    def run_repository_tests(self):
        """Pruebas completas del Repository Manager"""
        print("\n📁 Testing Repository Manager...")
        
        tests = {
            'health': self.client.test_repository_health(),
            'list_repos': self.client.test_get_repositories(),
            'create_repo': self.client.test_create_repository(SAMPLE_REPOSITORY)
        }
        
        # Si se creó el repo, probar operaciones adicionales
        if tests['create_repo']['success']:
            repo_data = tests['create_repo']['data'].get('data', {})
            repo_id = repo_data.get('id')
            
            if repo_id:
                tests['get_repo'] = self.client.test_get_repository(repo_id)
                tests['sync_repo'] = self.client.test_sync_repository(repo_id)
                
                # Update repo
                updated_data = SAMPLE_REPOSITORY.copy()
                updated_data['description'] = 'Updated description'
                tests['update_repo'] = self.client.test_update_repository(repo_id, updated_data)
        
        self.test_results['repository'] = tests
        return tests
    
    def run_task_tests(self):
        """Pruebas completas del Task Manager"""
        print("\n📋 Testing Task Manager...")
        
        tests = {
            'health': self.client.test_task_health(),
            'list_tasks': self.client.test_get_tasks(),
            'create_task': self.client.test_create_task(SAMPLE_TASK)
        }
        
        # Si se creó la tarea, probar ejecución
        if tests['create_task']['success']:
            task_data = tests['create_task']['data'].get('data', {})
            task_id = task_data.get('id')
            
            if task_id:
                tests['get_task'] = self.client.test_get_task(task_id)
                tests['execute_task'] = self.client.test_execute_task(task_id)
                tests['get_logs'] = self.client.test_get_task_logs(task_id)
        
        self.test_results['task'] = tests
        return tests
    
    def run_log_tests(self):
        """Pruebas completas del Log Manager"""
        print("\n📊 Testing Log Manager...")
        
        tests = {
            'health': self.client.test_log_health(),
            'list_logs': self.client.test_get_logs(),
            'create_log': self.client.test_create_log(SAMPLE_LOG),
            'search_logs': self.client.test_search_logs('test'),
            'service_logs': self.client.test_get_logs_by_service('test-service')
        }
        
        self.test_results['log'] = tests
        return tests
    
    def run_datasync_tests(self):
        """Pruebas completas del DataSync Manager"""
        print("\n🔄 Testing DataSync Manager...")
        
        sync_job_data = {
            "name": "test-sync",
            "source": "postgresql://test",
            "destination": "minio://backup/test"
        }
        
        backup_data = {
            "name": "test-backup",
            "source": "repositories",
            "destination": "minio://backups/"
        }
        
        tests = {
            'health': self.client.test_datasync_health(),
            'list_jobs': self.client.test_get_sync_jobs(),
            'create_job': self.client.test_create_sync_job(sync_job_data),
            'list_backups': self.client.test_get_backups(),
            'create_backup': self.client.test_create_backup(backup_data)
        }
        
        # Si se creó el job, probar ejecución
        if tests['create_job']['success']:
            job_data = tests['create_job']['data'].get('data', {})
            job_id = job_data.get('id')
            
            if job_id:
                tests['execute_sync'] = self.client.test_execute_sync(job_id)
        
        self.test_results['datasync'] = tests
        return tests
    
    def run_github_runner_tests(self):
        """Pruebas completas del GitHub Runner Manager"""
        print("\n🏃 Testing GitHub Runner Manager...")
        
        runner_data = {
            "name": "test-runner",
            "labels": ["linux", "docker", "test"],
            "repository": "giovanemere/ia-ops"
        }
        
        tests = {
            'health': self.client.test_github_runner_health(),
            'list_runners': self.client.test_get_runners(),
            'create_runner': self.client.test_create_runner(runner_data),
            'list_workflows': self.client.test_get_workflows()
        }
        
        self.test_results['github_runner'] = tests
        return tests
    
    def run_techdocs_tests(self):
        """Pruebas completas del TechDocs Builder"""
        print("\n📚 Testing TechDocs Builder...")
        
        build_data = {
            "repository_id": 1,
            "source_path": "docs/",
            "output_path": "site/",
            "config": {
                "theme": "material",
                "plugins": ["search", "mermaid"]
            }
        }
        
        tests = {
            'health': self.client.test_techdocs_health(),
            'list_docs': self.client.test_get_docs(),
            'build_docs': self.client.test_build_docs(build_data)
        }
        
        # Si se construyó la doc, probar rebuild
        if tests['build_docs']['success']:
            doc_data = tests['build_docs']['data'].get('data', {})
            doc_id = doc_data.get('id')
            
            if doc_id:
                tests['rebuild_docs'] = self.client.test_rebuild_docs(doc_id)
        
        self.test_results['techdocs'] = tests
        return tests
    
    def run_integration_tests(self):
        """Pruebas de integración entre servicios"""
        print("\n🔗 Testing Service Integration...")
        
        # Test completo de workflow
        workflow_result = self.client.test_full_workflow()
        
        # Test de conectividad de bases de datos
        db_tests = {
            'postgresql': self._test_postgresql_connection(),
            'redis': self._test_redis_connection(),
            'minio': self._test_minio_connection()
        }
        
        integration_tests = {
            'workflow': workflow_result,
            'databases': db_tests,
            'cross_service': self._test_cross_service_communication()
        }
        
        self.test_results['integration'] = integration_tests
        return integration_tests
    
    def _test_postgresql_connection(self):
        """Test conexión PostgreSQL a través de los servicios"""
        # Usar el repository manager para probar PostgreSQL
        result = self.client.test_get_repositories()
        return {
            'success': result['success'],
            'message': 'PostgreSQL connection via Repository Manager',
            'status_code': result['status_code']
        }
    
    def _test_redis_connection(self):
        """Test conexión Redis a través de los servicios"""
        # Usar el task manager para probar Redis (cache de tareas)
        result = self.client.test_get_tasks()
        return {
            'success': result['success'],
            'message': 'Redis connection via Task Manager',
            'status_code': result['status_code']
        }
    
    def _test_minio_connection(self):
        """Test conexión MinIO a través de los servicios"""
        # Usar el datasync manager para probar MinIO
        result = self.client.test_get_backups()
        return {
            'success': result['success'],
            'message': 'MinIO connection via DataSync Manager',
            'status_code': result['status_code']
        }
    
    def _test_cross_service_communication(self):
        """Test comunicación entre servicios"""
        # Crear repo -> crear tarea -> crear log -> crear backup
        results = {}
        
        # 1. Crear repositorio
        repo_result = self.client.test_create_repository({
            "name": "integration-test",
            "url": "https://github.com/test/integration.git",
            "branch": "main"
        })
        results['step1_repo'] = repo_result
        
        if repo_result['success']:
            repo_id = repo_result['data'].get('data', {}).get('id')
            
            # 2. Crear tarea para el repo
            task_result = self.client.test_create_task({
                "name": "integration-build",
                "type": "build",
                "repository_id": repo_id,
                "command": "echo 'Integration test'"
            })
            results['step2_task'] = task_result
            
            # 3. Crear log del proceso
            log_result = self.client.test_create_log({
                "service": "integration-test",
                "level": "info",
                "message": f"Created task for repo {repo_id}"
            })
            results['step3_log'] = log_result
            
            # 4. Crear backup del repo
            backup_result = self.client.test_create_backup({
                "name": f"backup-repo-{repo_id}",
                "source": f"repository-{repo_id}",
                "destination": "minio://integration-backups/"
            })
            results['step4_backup'] = backup_result
        
        return results
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🧪 Iniciando pruebas completas de IA-Ops Dev Core Services...")
        
        # Pruebas por servicio
        self.run_repository_tests()
        self.run_task_tests()
        self.run_log_tests()
        self.run_datasync_tests()
        self.run_github_runner_tests()
        self.run_techdocs_tests()
        
        # Pruebas de integración
        self.run_integration_tests()
        
        return self.test_results
    
    def generate_report(self):
        """Generar reporte de pruebas"""
        if not self.test_results:
            return "No hay resultados de pruebas disponibles"
        
        report = []
        report.append("📊 REPORTE DE PRUEBAS IA-OPS DEV CORE")
        report.append("=" * 50)
        
        total_tests = 0
        passed_tests = 0
        
        for service, tests in self.test_results.items():
            report.append(f"\n🔧 {service.upper()}")
            report.append("-" * 30)
            
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    total_tests += 1
                    if isinstance(result, dict) and result.get('success'):
                        passed_tests += 1
                        status = "✅ PASS"
                    else:
                        status = "❌ FAIL"
                    
                    report.append(f"  {status} {test_name}")
        
        # Resumen
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        report.append(f"\n📈 RESUMEN")
        report.append("-" * 20)
        report.append(f"Total de pruebas: {total_tests}")
        report.append(f"Pruebas exitosas: {passed_tests}")
        report.append(f"Tasa de éxito: {success_rate:.1f}%")
        
        return "\n".join(report)

if __name__ == "__main__":
    tester = ServiceTester()
    
    # Ejecutar todas las pruebas
    results = tester.run_all_tests()
    
    # Generar y mostrar reporte
    report = tester.generate_report()
    print(report)
    
    # Guardar resultados en archivo
    with open('/home/giovanemere/ia-ops/ia-ops-dev-core/tests/test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en: test_results.json")
