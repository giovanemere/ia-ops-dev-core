#!/usr/bin/env python3
"""
Pruebas de rendimiento y carga para IA-Ops Dev Core Services
"""

import asyncio
import aiohttp
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from test_api_methods import IAOpsTestClient

class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.client = IAOpsTestClient(base_url)
        self.results = {}
    
    async def measure_response_time(self, session, url):
        """Medir tiempo de respuesta de una URL"""
        start_time = time.time()
        try:
            async with session.get(url) as response:
                await response.text()
                end_time = time.time()
                return {
                    'success': True,
                    'response_time': end_time - start_time,
                    'status_code': response.status
                }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'response_time': end_time - start_time,
                'error': str(e)
            }
    
    async def load_test_service(self, service_port: int, endpoint: str = "/health", concurrent_requests: int = 10, total_requests: int = 100):
        """Test de carga para un servicio específico"""
        url = f"{self.base_url}:{service_port}{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Crear tareas concurrentes
            for _ in range(total_requests):
                task = asyncio.create_task(self.measure_response_time(session, url))
                tasks.append(task)
                
                # Limitar concurrencia
                if len(tasks) >= concurrent_requests:
                    results = await asyncio.gather(*tasks)
                    tasks = []
            
            # Procesar tareas restantes
            if tasks:
                results = await asyncio.gather(*tasks)
        
        return self.analyze_results(results)
    
    def analyze_results(self, results):
        """Analizar resultados de pruebas de rendimiento"""
        response_times = [r['response_time'] for r in results if r['success']]
        success_count = sum(1 for r in results if r['success'])
        
        if not response_times:
            return {
                'success_rate': 0,
                'avg_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'median_response_time': 0,
                'total_requests': len(results)
            }
        
        return {
            'success_rate': (success_count / len(results)) * 100,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'median_response_time': statistics.median(response_times),
            'std_deviation': statistics.stdev(response_times) if len(response_times) > 1 else 0,
            'total_requests': len(results),
            'successful_requests': success_count
        }
    
    async def test_all_services_performance(self):
        """Test de rendimiento para todos los servicios"""
        services = {
            'repository': 8860,
            'task': 8861,
            'log': 8862,
            'datasync': 8863,
            'github_runner': 8864,
            'techdocs': 8865
        }
        
        results = {}
        
        for service_name, port in services.items():
            print(f"🔄 Testing {service_name} performance...")
            results[service_name] = await self.load_test_service(port)
        
        return results
    
    def test_database_performance(self):
        """Test de rendimiento de operaciones de base de datos"""
        print("🗄️ Testing database performance...")
        
        # Test PostgreSQL via Repository Manager
        start_time = time.time()
        repo_results = []
        
        for i in range(10):
            result = self.client.test_get_repositories()
            repo_results.append({
                'success': result['success'],
                'response_time': time.time() - start_time
            })
            start_time = time.time()
        
        # Test Redis via Task Manager
        start_time = time.time()
        task_results = []
        
        for i in range(10):
            result = self.client.test_get_tasks()
            task_results.append({
                'success': result['success'],
                'response_time': time.time() - start_time
            })
            start_time = time.time()
        
        return {
            'postgresql': self.analyze_results(repo_results),
            'redis': self.analyze_results(task_results)
        }
    
    def test_concurrent_operations(self):
        """Test de operaciones concurrentes"""
        print("⚡ Testing concurrent operations...")
        
        def create_repository():
            return self.client.test_create_repository({
                "name": f"concurrent-test-{int(time.time() * 1000)}",
                "url": "https://github.com/test/concurrent.git",
                "branch": "main"
            })
        
        def create_task():
            return self.client.test_create_task({
                "name": f"concurrent-task-{int(time.time() * 1000)}",
                "type": "test",
                "repository_id": 1,
                "command": "echo 'concurrent test'"
            })
        
        # Ejecutar operaciones concurrentes
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Crear repositorios concurrentemente
            repo_futures = [executor.submit(create_repository) for _ in range(5)]
            task_futures = [executor.submit(create_task) for _ in range(5)]
            
            repo_results = [future.result() for future in repo_futures]
            task_results = [future.result() for future in task_futures]
        
        return {
            'concurrent_repositories': {
                'success_rate': sum(1 for r in repo_results if r['success']) / len(repo_results) * 100,
                'total_operations': len(repo_results)
            },
            'concurrent_tasks': {
                'success_rate': sum(1 for r in task_results if r['success']) / len(task_results) * 100,
                'total_operations': len(task_results)
            }
        }
    
    async def run_full_performance_suite(self):
        """Ejecutar suite completa de pruebas de rendimiento"""
        print("🚀 Iniciando suite de pruebas de rendimiento...")
        
        # Test de rendimiento de servicios
        service_performance = await self.test_all_services_performance()
        
        # Test de rendimiento de base de datos
        db_performance = self.test_database_performance()
        
        # Test de operaciones concurrentes
        concurrent_performance = self.test_concurrent_operations()
        
        self.results = {
            'services': service_performance,
            'databases': db_performance,
            'concurrent': concurrent_performance,
            'timestamp': time.time()
        }
        
        return self.results
    
    def generate_performance_report(self):
        """Generar reporte de rendimiento"""
        if not self.results:
            return "No hay resultados de rendimiento disponibles"
        
        report = []
        report.append("⚡ REPORTE DE RENDIMIENTO IA-OPS DEV CORE")
        report.append("=" * 55)
        
        # Rendimiento de servicios
        if 'services' in self.results:
            report.append("\n🔧 RENDIMIENTO DE SERVICIOS")
            report.append("-" * 35)
            
            for service, metrics in self.results['services'].items():
                report.append(f"\n📊 {service.upper()}")
                report.append(f"  Tasa de éxito: {metrics['success_rate']:.1f}%")
                report.append(f"  Tiempo promedio: {metrics['avg_response_time']*1000:.2f}ms")
                report.append(f"  Tiempo mínimo: {metrics['min_response_time']*1000:.2f}ms")
                report.append(f"  Tiempo máximo: {metrics['max_response_time']*1000:.2f}ms")
                report.append(f"  Mediana: {metrics['median_response_time']*1000:.2f}ms")
        
        # Rendimiento de bases de datos
        if 'databases' in self.results:
            report.append("\n🗄️ RENDIMIENTO DE BASES DE DATOS")
            report.append("-" * 40)
            
            for db, metrics in self.results['databases'].items():
                report.append(f"\n📈 {db.upper()}")
                report.append(f"  Tasa de éxito: {metrics['success_rate']:.1f}%")
                report.append(f"  Tiempo promedio: {metrics['avg_response_time']*1000:.2f}ms")
        
        # Operaciones concurrentes
        if 'concurrent' in self.results:
            report.append("\n⚡ OPERACIONES CONCURRENTES")
            report.append("-" * 35)
            
            concurrent = self.results['concurrent']
            report.append(f"\n🔄 Repositorios concurrentes:")
            report.append(f"  Tasa de éxito: {concurrent['concurrent_repositories']['success_rate']:.1f}%")
            report.append(f"  Total operaciones: {concurrent['concurrent_repositories']['total_operations']}")
            
            report.append(f"\n📋 Tareas concurrentes:")
            report.append(f"  Tasa de éxito: {concurrent['concurrent_tasks']['success_rate']:.1f}%")
            report.append(f"  Total operaciones: {concurrent['concurrent_tasks']['total_operations']}")
        
        return "\n".join(report)

async def main():
    tester = PerformanceTester()
    
    # Ejecutar suite de rendimiento
    results = await tester.run_full_performance_suite()
    
    # Generar reporte
    report = tester.generate_performance_report()
    print(report)
    
    # Guardar resultados
    import json
    with open('/home/giovanemere/ia-ops/ia-ops-dev-core/tests/performance_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en: performance_results.json")

if __name__ == "__main__":
    asyncio.run(main())
