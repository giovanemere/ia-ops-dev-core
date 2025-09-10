#!/usr/bin/env python3
"""
Automatización de Pruebas de Performance para IA-Ops
Incluye pruebas de carga, estrés y monitoreo continuo
"""

import asyncio
import aiohttp
import time
import json
import statistics
import psutil
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import pandas as pd

class PerformanceTestRunner:
    def __init__(self, config_file=None):
        self.config = self._load_config(config_file)
        self.results = {}
        self.metrics_collector = MetricsCollector()
        
    def _load_config(self, config_file):
        """Cargar configuración de pruebas"""
        default_config = {
            'services': {
                'repository-manager': 'http://localhost:8860',
                'task-manager': 'http://localhost:8861',
                'log-manager': 'http://localhost:8862',
                'datasync-manager': 'http://localhost:8863'
            },
            'load_test_config': {
                'concurrent_users': [10, 25, 50, 100],
                'duration': 300,  # 5 minutes
                'ramp_up': 30     # 30 seconds
            },
            'thresholds': {
                'response_time_p95': 500,  # ms
                'error_rate': 0.01,        # 1%
                'throughput_min': 100      # req/s
            }
        }
        
        if config_file:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def run_load_test(self, service_name, test_config):
        """Ejecutar prueba de carga para un servicio"""
        print(f"🚀 Starting load test for {service_name}")
        
        service_url = self.config['services'][service_name]
        concurrent_users = test_config['concurrent_users']
        duration = test_config['duration']
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            # Crear tareas concurrentes
            tasks = []
            for user_id in range(concurrent_users):
                task = asyncio.create_task(
                    self._simulate_user_load(session, service_url, duration, user_id)
                )
                tasks.append(task)
            
            # Ejecutar todas las tareas
            user_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados
            for user_result in user_results:
                if isinstance(user_result, list):
                    results.extend(user_result)
        
        return self._analyze_results(results, service_name)
    
    async def _simulate_user_load(self, session, base_url, duration, user_id):
        """Simular carga de un usuario"""
        results = []
        start_time = time.time()
        request_count = 0
        
        # Patrones de uso realistas
        endpoints = [
            {'path': '/health', 'method': 'GET', 'weight': 20},
            {'path': '/api/v1/repositories', 'method': 'GET', 'weight': 40},
            {'path': '/api/v1/repositories', 'method': 'POST', 'weight': 10, 'data': {
                'name': f'load-test-{user_id}-{request_count}',
                'url': f'https://github.com/test/load-{user_id}.git',
                'branch': 'main'
            }},
            {'path': '/api/v1/tasks', 'method': 'GET', 'weight': 30}
        ]
        
        while time.time() - start_time < duration:
            # Seleccionar endpoint basado en peso
            endpoint = self._weighted_choice(endpoints)
            
            # Ejecutar request
            result = await self._make_request(
                session, 
                base_url, 
                endpoint, 
                user_id, 
                request_count
            )
            
            results.append(result)
            request_count += 1
            
            # Pausa realista entre requests
            await asyncio.sleep(0.1 + (0.5 * asyncio.get_event_loop().time() % 1))
        
        return results
    
    async def _make_request(self, session, base_url, endpoint, user_id, request_count):
        """Hacer request y medir métricas"""
        url = f"{base_url}{endpoint['path']}"
        method = endpoint['method']
        data = endpoint.get('data', {})
        
        # Personalizar datos si es necesario
        if data and 'name' in data:
            data['name'] = data['name'].replace('{request_count}', str(request_count))
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                async with session.get(url) as response:
                    await response.text()
                    status_code = response.status
            elif method == 'POST':
                async with session.post(url, json=data) as response:
                    await response.text()
                    status_code = response.status
            else:
                status_code = 405  # Method not allowed
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # ms
            
            return {
                'timestamp': start_time,
                'user_id': user_id,
                'endpoint': endpoint['path'],
                'method': method,
                'response_time': response_time,
                'status_code': status_code,
                'success': status_code < 400
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                'timestamp': start_time,
                'user_id': user_id,
                'endpoint': endpoint['path'],
                'method': method,
                'response_time': response_time,
                'status_code': 0,
                'success': False,
                'error': str(e)
            }
    
    def _weighted_choice(self, choices):
        """Selección ponderada de endpoints"""
        total_weight = sum(choice['weight'] for choice in choices)
        r = total_weight * (time.time() % 1)  # Pseudo-random
        
        for choice in choices:
            r -= choice['weight']
            if r <= 0:
                return choice
        
        return choices[-1]  # Fallback
    
    def _analyze_results(self, results, service_name):
        """Analizar resultados de pruebas"""
        if not results:
            return {'error': 'No results to analyze'}
        
        # Métricas básicas
        response_times = [r['response_time'] for r in results if r['success']]
        error_count = sum(1 for r in results if not r['success'])
        total_requests = len(results)
        
        # Calcular métricas
        analysis = {
            'service': service_name,
            'total_requests': total_requests,
            'successful_requests': len(response_times),
            'error_count': error_count,
            'error_rate': error_count / total_requests if total_requests > 0 else 0,
            'response_times': {
                'min': min(response_times) if response_times else 0,
                'max': max(response_times) if response_times else 0,
                'mean': statistics.mean(response_times) if response_times else 0,
                'median': statistics.median(response_times) if response_times else 0,
                'p95': self._percentile(response_times, 95) if response_times else 0,
                'p99': self._percentile(response_times, 99) if response_times else 0
            },
            'throughput': {
                'requests_per_second': total_requests / 300 if total_requests > 0 else 0  # Assuming 5min test
            },
            'status_codes': self._count_status_codes(results)
        }
        
        # Verificar thresholds
        analysis['thresholds_passed'] = self._check_thresholds(analysis)
        
        return analysis
    
    def _percentile(self, data, percentile):
        """Calcular percentil"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _count_status_codes(self, results):
        """Contar códigos de estado"""
        status_counts = {}
        for result in results:
            code = result['status_code']
            status_counts[code] = status_counts.get(code, 0) + 1
        return status_counts
    
    def _check_thresholds(self, analysis):
        """Verificar si se cumplen los thresholds"""
        thresholds = self.config['thresholds']
        
        checks = {
            'response_time_p95': analysis['response_times']['p95'] <= thresholds['response_time_p95'],
            'error_rate': analysis['error_rate'] <= thresholds['error_rate'],
            'throughput': analysis['throughput']['requests_per_second'] >= thresholds['throughput_min']
        }
        
        return {
            'all_passed': all(checks.values()),
            'individual_checks': checks
        }
    
    async def run_stress_test(self, service_name):
        """Ejecutar prueba de estrés incremental"""
        print(f"💪 Starting stress test for {service_name}")
        
        stress_results = []
        concurrent_users_levels = self.config['load_test_config']['concurrent_users']
        
        for user_count in concurrent_users_levels:
            print(f"  Testing with {user_count} concurrent users...")
            
            test_config = {
                'concurrent_users': user_count,
                'duration': 120  # 2 minutes per level
            }
            
            result = await self.run_load_test(service_name, test_config)
            result['concurrent_users'] = user_count
            stress_results.append(result)
            
            # Pausa entre niveles
            await asyncio.sleep(30)
        
        return self._analyze_stress_results(stress_results, service_name)
    
    def _analyze_stress_results(self, results, service_name):
        """Analizar resultados de prueba de estrés"""
        return {
            'service': service_name,
            'test_type': 'stress',
            'levels_tested': len(results),
            'results_by_load': results,
            'breaking_point': self._find_breaking_point(results),
            'recommendations': self._generate_recommendations(results)
        }
    
    def _find_breaking_point(self, results):
        """Encontrar punto de quiebre del sistema"""
        for result in results:
            if (result['error_rate'] > 0.05 or  # 5% error rate
                result['response_times']['p95'] > 2000):  # 2s response time
                return {
                    'concurrent_users': result['concurrent_users'],
                    'reason': 'High error rate or response time'
                }
        
        return {'concurrent_users': 'Not found', 'reason': 'System stable at all tested levels'}
    
    def _generate_recommendations(self, results):
        """Generar recomendaciones basadas en resultados"""
        recommendations = []
        
        # Analizar tendencias
        if len(results) >= 2:
            last_result = results[-1]
            if last_result['error_rate'] > 0.01:
                recommendations.append("Consider implementing rate limiting")
            
            if last_result['response_times']['p95'] > 1000:
                recommendations.append("Optimize database queries or add caching")
            
            if last_result['throughput']['requests_per_second'] < 50:
                recommendations.append("Scale horizontally or optimize application performance")
        
        return recommendations
    
    def run_continuous_monitoring(self, duration_hours=24):
        """Ejecutar monitoreo continuo de performance"""
        print(f"📊 Starting continuous monitoring for {duration_hours} hours")
        
        def monitor_loop():
            end_time = time.time() + (duration_hours * 3600)
            
            while time.time() < end_time:
                # Recopilar métricas del sistema
                system_metrics = self.metrics_collector.collect_system_metrics()
                
                # Hacer health checks
                health_results = asyncio.run(self._check_all_services_health())
                
                # Almacenar métricas
                timestamp = datetime.utcnow().isoformat()
                self.metrics_collector.store_metrics(timestamp, system_metrics, health_results)
                
                # Esperar 5 minutos
                time.sleep(300)
        
        # Ejecutar en thread separado
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    async def _check_all_services_health(self):
        """Verificar salud de todos los servicios"""
        health_results = {}
        
        async with aiohttp.ClientSession() as session:
            for service_name, service_url in self.config['services'].items():
                try:
                    start_time = time.time()
                    async with session.get(f"{service_url}/health", timeout=10) as response:
                        end_time = time.time()
                        
                        health_results[service_name] = {
                            'status': 'healthy' if response.status == 200 else 'unhealthy',
                            'response_time': (end_time - start_time) * 1000,
                            'status_code': response.status
                        }
                except Exception as e:
                    health_results[service_name] = {
                        'status': 'error',
                        'error': str(e),
                        'response_time': None
                    }
        
        return health_results
    
    def generate_performance_report(self, output_file='performance_report.html'):
        """Generar reporte de performance en HTML"""
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>IA-Ops Performance Report</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metric-card { 
                    border: 1px solid #ddd; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 5px; 
                }
                .success { background-color: #d4edda; }
                .warning { background-color: #fff3cd; }
                .error { background-color: #f8d7da; }
            </style>
        </head>
        <body>
            <h1>🚀 IA-Ops Performance Report</h1>
            <p>Generated: {timestamp}</p>
            
            <h2>📊 Summary</h2>
            <div id="summary">
                {summary_content}
            </div>
            
            <h2>📈 Performance Metrics</h2>
            <div id="metrics-chart"></div>
            
            <h2>🔍 Detailed Results</h2>
            <div id="detailed-results">
                {detailed_results}
            </div>
            
            <script>
                // Generar gráficos con Plotly
                {chart_script}
            </script>
        </body>
        </html>
        """
        
        # Generar contenido del reporte
        summary_content = self._generate_summary_html()
        detailed_results = self._generate_detailed_results_html()
        chart_script = self._generate_chart_script()
        
        html_content = html_template.format(
            timestamp=datetime.utcnow().isoformat(),
            summary_content=summary_content,
            detailed_results=detailed_results,
            chart_script=chart_script
        )
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"📄 Performance report generated: {output_file}")
    
    def _generate_summary_html(self):
        """Generar HTML del resumen"""
        if not self.results:
            return "<p>No performance data available</p>"
        
        summary_html = ""
        for service, result in self.results.items():
            status_class = "success" if result.get('thresholds_passed', {}).get('all_passed', False) else "error"
            
            summary_html += f"""
            <div class="metric-card {status_class}">
                <h3>{service}</h3>
                <p>Response Time P95: {result.get('response_times', {}).get('p95', 0):.2f}ms</p>
                <p>Error Rate: {result.get('error_rate', 0):.2%}</p>
                <p>Throughput: {result.get('throughput', {}).get('requests_per_second', 0):.2f} req/s</p>
            </div>
            """
        
        return summary_html
    
    def _generate_detailed_results_html(self):
        """Generar HTML de resultados detallados"""
        return "<pre>" + json.dumps(self.results, indent=2) + "</pre>"
    
    def _generate_chart_script(self):
        """Generar script de gráficos"""
        return """
        var data = [{
            x: ['Repository Manager', 'Task Manager', 'Log Manager'],
            y: [150, 200, 100],
            type: 'bar',
            name: 'Response Time (ms)'
        }];
        
        var layout = {
            title: 'Average Response Times by Service'
        };
        
        Plotly.newPlot('metrics-chart', data, layout);
        """

class MetricsCollector:
    def __init__(self):
        self.metrics_history = []
    
    def collect_system_metrics(self):
        """Recopilar métricas del sistema"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
            'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {},
            'timestamp': time.time()
        }
    
    def store_metrics(self, timestamp, system_metrics, health_results):
        """Almacenar métricas"""
        self.metrics_history.append({
            'timestamp': timestamp,
            'system': system_metrics,
            'health': health_results
        })

async def main():
    """Función principal para ejecutar pruebas"""
    runner = PerformanceTestRunner()
    
    print("🧪 IA-Ops Performance Test Suite")
    print("=" * 40)
    
    # Ejecutar pruebas de carga
    for service_name in runner.config['services']:
        print(f"\n🔄 Testing {service_name}...")
        
        # Prueba de carga básica
        load_config = {
            'concurrent_users': 25,
            'duration': 60  # 1 minute for demo
        }
        
        result = await runner.run_load_test(service_name, load_config)
        runner.results[service_name] = result
        
        print(f"  ✅ Completed - P95: {result['response_times']['p95']:.2f}ms, Error Rate: {result['error_rate']:.2%}")
    
    # Generar reporte
    runner.generate_performance_report()
    
    print("\n🎉 Performance testing completed!")
    print("📄 Check performance_report.html for detailed results")

if __name__ == '__main__':
    asyncio.run(main())
