#!/usr/bin/env python3
"""
Portal de Pruebas Principal para IA-Ops
Ejecuta todos los tipos de pruebas: unitarias, integración, performance
"""

import asyncio
import json
import time
import sys
import argparse
from datetime import datetime
from pathlib import Path

from mock_services import MockServiceManager, MOCK_SERVICES_CONFIG
from performance_automation import PerformanceTestRunner
import requests

class TestPortalRunner:
    def __init__(self, config_file=None, use_mocks=False):
        self.config = self._load_config(config_file)
        self.use_mocks = use_mocks
        self.mock_manager = None
        self.performance_runner = None
        self.test_results = {}
        
    def _load_config(self, config_file):
        """Cargar configuración del portal"""
        default_config = {
            'test_suites': {
                'unit_tests': True,
                'integration_tests': True,
                'performance_tests': True,
                'security_tests': False
            },
            'services': {
                'repository-manager': 'http://localhost:8860',
                'task-manager': 'http://localhost:8861',
                'log-manager': 'http://localhost:8862',
                'datasync-manager': 'http://localhost:8863',
                'github-runner-manager': 'http://localhost:8864',
                'techdocs-builder': 'http://localhost:8865'
            },
            'mock_services': {
                'repository-manager': 'http://localhost:18860',
                'task-manager': 'http://localhost:18861',
                'log-manager': 'http://localhost:18862'
            },
            'reporting': {
                'formats': ['json', 'html'],
                'output_dir': './test-results'
            }
        }
        
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def initialize(self):
        """Inicializar el portal de pruebas"""
        print("🚀 Initializing IA-Ops Test Portal")
        print("=" * 50)
        
        # Crear directorio de resultados
        Path(self.config['reporting']['output_dir']).mkdir(exist_ok=True)
        
        if self.use_mocks:
            await self._start_mock_services()
        
        # Inicializar runner de performance
        self.performance_runner = PerformanceTestRunner()
        
        # Verificar servicios disponibles
        await self._check_services_availability()
    
    async def _start_mock_services(self):
        """Iniciar servicios mock"""
        print("🎭 Starting mock services...")
        
        self.mock_manager = MockServiceManager()
        
        for service_name, config in MOCK_SERVICES_CONFIG.items():
            self.mock_manager.create_mock_service(
                service_name,
                config['port'],
                config['endpoints']
            )
        
        self.mock_manager.start_all_services()
        
        # Esperar a que los servicios estén listos
        await asyncio.sleep(2)
        print("✅ Mock services started")
    
    async def _check_services_availability(self):
        """Verificar disponibilidad de servicios"""
        print("🔍 Checking services availability...")
        
        services_to_check = (
            self.config['mock_services'] if self.use_mocks 
            else self.config['services']
        )
        
        available_services = {}
        
        for service_name, service_url in services_to_check.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=5)
                if response.status_code == 200:
                    available_services[service_name] = service_url
                    print(f"  ✅ {service_name}: Available")
                else:
                    print(f"  ❌ {service_name}: Unhealthy (HTTP {response.status_code})")
            except Exception as e:
                print(f"  ❌ {service_name}: Unavailable ({str(e)})")
        
        self.available_services = available_services
        return available_services
    
    async def run_unit_tests(self):
        """Ejecutar pruebas unitarias"""
        print("\n🧪 Running Unit Tests")
        print("-" * 30)
        
        # Cargar casos de prueba unitarios
        test_cases = self._load_test_cases('unit_tests')
        results = []
        
        for test_case in test_cases:
            print(f"  Running: {test_case['name']}")
            
            result = await self._execute_test_case(test_case)
            results.append(result)
            
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"    {status} - {result.get('message', '')}")
        
        self.test_results['unit_tests'] = {
            'total': len(results),
            'passed': sum(1 for r in results if r['passed']),
            'failed': sum(1 for r in results if not r['passed']),
            'results': results
        }
        
        return self.test_results['unit_tests']
    
    async def run_integration_tests(self):
        """Ejecutar pruebas de integración"""
        print("\n🔗 Running Integration Tests")
        print("-" * 35)
        
        test_cases = self._load_test_cases('integration_tests')
        results = []
        
        for test_case in test_cases:
            print(f"  Running: {test_case['name']}")
            
            if test_case['type'] == 'integration':
                result = await self._execute_integration_test(test_case)
            else:
                result = await self._execute_test_case(test_case)
            
            results.append(result)
            
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"    {status} - {result.get('message', '')}")
        
        self.test_results['integration_tests'] = {
            'total': len(results),
            'passed': sum(1 for r in results if r['passed']),
            'failed': sum(1 for r in results if not r['passed']),
            'results': results
        }
        
        return self.test_results['integration_tests']
    
    async def run_performance_tests(self):
        """Ejecutar pruebas de performance"""
        print("\n⚡ Running Performance Tests")
        print("-" * 35)
        
        performance_results = {}
        
        # Pruebas de carga por servicio
        for service_name in self.available_services:
            if service_name in ['repository-manager', 'task-manager']:
                print(f"  Load testing: {service_name}")
                
                load_config = {
                    'concurrent_users': 10,
                    'duration': 30  # 30 seconds for quick test
                }
                
                result = await self.performance_runner.run_load_test(service_name, load_config)
                performance_results[service_name] = result
                
                # Verificar thresholds
                passed = result.get('thresholds_passed', {}).get('all_passed', False)
                status = "✅ PASS" if passed else "❌ FAIL"
                p95 = result.get('response_times', {}).get('p95', 0)
                error_rate = result.get('error_rate', 0)
                
                print(f"    {status} - P95: {p95:.2f}ms, Error Rate: {error_rate:.2%}")
        
        self.test_results['performance_tests'] = performance_results
        return performance_results
    
    async def _execute_test_case(self, test_case):
        """Ejecutar un caso de prueba individual"""
        try:
            service_name = test_case['service']
            
            # Determinar URL del servicio
            if service_name in self.available_services:
                base_url = self.available_services[service_name]
            else:
                return {
                    'test_id': test_case['id'],
                    'name': test_case['name'],
                    'passed': False,
                    'message': f'Service {service_name} not available'
                }
            
            # Construir URL completa
            url = f"{base_url}{test_case['endpoint']}"
            
            # Preparar request
            method = test_case['method']
            payload = test_case.get('payload', {})
            query_params = test_case.get('query_params', {})
            
            # Ejecutar request
            start_time = time.time()
            
            if method == 'GET':
                response = requests.get(url, params=query_params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=payload, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=payload, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            # Verificar respuesta esperada
            expected = test_case['expected_response']
            passed = True
            messages = []
            
            # Verificar status code
            if response.status_code != expected['status_code']:
                passed = False
                messages.append(f"Expected status {expected['status_code']}, got {response.status_code}")
            
            # Verificar body si está presente
            if 'body' in expected and response.content:
                try:
                    response_json = response.json()
                    if not self._compare_response_body(response_json, expected['body']):
                        passed = False
                        messages.append("Response body doesn't match expected")
                except:
                    passed = False
                    messages.append("Invalid JSON response")
            
            return {
                'test_id': test_case['id'],
                'name': test_case['name'],
                'passed': passed,
                'response_time': response_time,
                'status_code': response.status_code,
                'message': '; '.join(messages) if messages else 'Test passed'
            }
            
        except Exception as e:
            return {
                'test_id': test_case['id'],
                'name': test_case['name'],
                'passed': False,
                'message': f'Test execution failed: {str(e)}'
            }
    
    async def _execute_integration_test(self, test_case):
        """Ejecutar prueba de integración multi-step"""
        try:
            steps = test_case['steps']
            stored_values = {}
            
            for i, step in enumerate(steps):
                print(f"    Step {step['step']}: {step['action']}")
                
                # Reemplazar variables almacenadas en payload y URL
                endpoint = step['endpoint']
                payload = step.get('payload', {})
                
                # Reemplazar placeholders
                for key, value in stored_values.items():
                    endpoint = endpoint.replace(f'{{{key}}}', str(value))
                    if isinstance(payload, dict):
                        for p_key, p_value in payload.items():
                            if isinstance(p_value, str):
                                payload[p_key] = p_value.replace(f'{{{key}}}', str(value))
                
                # Ejecutar step
                service_name = step['service']
                if service_name not in self.available_services:
                    raise Exception(f"Service {service_name} not available")
                
                url = f"{self.available_services[service_name]}{endpoint}"
                method = step['method']
                
                if method == 'GET':
                    response = requests.get(url, timeout=10)
                elif method == 'POST':
                    response = requests.post(url, json=payload, timeout=10)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # Verificar respuesta
                if response.status_code >= 400:
                    raise Exception(f"Step {i+1} failed with status {response.status_code}")
                
                # Almacenar valores si es necesario
                if 'store_response' in step and response.content:
                    try:
                        response_json = response.json()
                        if response_json.get('success') and 'data' in response_json:
                            stored_key = step['store_response']
                            if 'id' in response_json['data']:
                                stored_values[stored_key] = response_json['data']['id']
                    except:
                        pass
            
            return {
                'test_id': test_case['id'],
                'name': test_case['name'],
                'passed': True,
                'message': f'All {len(steps)} steps completed successfully'
            }
            
        except Exception as e:
            return {
                'test_id': test_case['id'],
                'name': test_case['name'],
                'passed': False,
                'message': f'Integration test failed: {str(e)}'
            }
    
    def _compare_response_body(self, actual, expected):
        """Comparar cuerpo de respuesta"""
        if isinstance(expected, dict):
            if not isinstance(actual, dict):
                return False
            
            for key, value in expected.items():
                if key not in actual:
                    return False
                if not self._compare_response_body(actual[key], value):
                    return False
            return True
        
        elif isinstance(expected, list):
            return isinstance(actual, list)
        
        else:
            return actual == expected
    
    def _load_test_cases(self, test_type):
        """Cargar casos de prueba desde archivo JSON"""
        try:
            with open('test_cases_complete.json', 'r') as f:
                all_test_cases = json.load(f)
            
            return all_test_cases['test_suites'][test_type]['test_cases']
        except Exception as e:
            print(f"Warning: Could not load test cases for {test_type}: {e}")
            return []
    
    def generate_report(self):
        """Generar reporte completo de pruebas"""
        timestamp = datetime.utcnow().isoformat()
        
        # Calcular estadísticas generales
        total_tests = 0
        total_passed = 0
        
        for suite_name, suite_results in self.test_results.items():
            if isinstance(suite_results, dict) and 'total' in suite_results:
                total_tests += suite_results['total']
                total_passed += suite_results['passed']
        
        report = {
            'timestamp': timestamp,
            'summary': {
                'total_tests': total_tests,
                'total_passed': total_passed,
                'total_failed': total_tests - total_passed,
                'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
            },
            'test_suites': self.test_results,
            'configuration': {
                'use_mocks': self.use_mocks,
                'available_services': list(self.available_services.keys())
            }
        }
        
        # Guardar reporte JSON
        output_dir = Path(self.config['reporting']['output_dir'])
        json_file = output_dir / f"test_report_{timestamp.replace(':', '-')}.json"
        
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generar reporte HTML
        if 'html' in self.config['reporting']['formats']:
            html_file = output_dir / f"test_report_{timestamp.replace(':', '-')}.html"
            self._generate_html_report(report, html_file)
        
        print(f"\n📄 Test report generated:")
        print(f"  JSON: {json_file}")
        if 'html' in self.config['reporting']['formats']:
            print(f"  HTML: {html_file}")
        
        return report
    
    def _generate_html_report(self, report, output_file):
        """Generar reporte HTML"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>IA-Ops Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .test-suite {{ margin-bottom: 30px; }}
                .test-case {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }}
                .pass {{ border-left-color: #28a745; background: #d4edda; }}
                .fail {{ border-left-color: #dc3545; background: #f8d7da; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #e9ecef; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>🧪 IA-Ops Test Report</h1>
            <p>Generated: {timestamp}</p>
            
            <div class="summary">
                <h2>📊 Summary</h2>
                <div class="metric">Total Tests: {total_tests}</div>
                <div class="metric">Passed: {total_passed}</div>
                <div class="metric">Failed: {total_failed}</div>
                <div class="metric">Success Rate: {success_rate:.1f}%</div>
            </div>
            
            {test_suites_html}
        </body>
        </html>
        """
        
        # Generar HTML para cada suite de pruebas
        test_suites_html = ""
        for suite_name, suite_results in report['test_suites'].items():
            test_suites_html += f"<div class='test-suite'><h2>{suite_name.replace('_', ' ').title()}</h2>"
            
            if isinstance(suite_results, dict) and 'results' in suite_results:
                for test_result in suite_results['results']:
                    css_class = 'pass' if test_result['passed'] else 'fail'
                    test_suites_html += f"""
                    <div class='test-case {css_class}'>
                        <strong>{test_result['name']}</strong><br>
                        {test_result.get('message', '')}
                    </div>
                    """
            
            test_suites_html += "</div>"
        
        html_content = html_template.format(
            timestamp=report['timestamp'],
            total_tests=report['summary']['total_tests'],
            total_passed=report['summary']['total_passed'],
            total_failed=report['summary']['total_failed'],
            success_rate=report['summary']['success_rate'],
            test_suites_html=test_suites_html
        )
        
        with open(output_file, 'w') as f:
            f.write(html_content)

async def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='IA-Ops Test Portal Runner')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--mocks', action='store_true', help='Use mock services')
    parser.add_argument('--suite', choices=['unit', 'integration', 'performance', 'all'], 
                       default='all', help='Test suite to run')
    
    args = parser.parse_args()
    
    # Inicializar portal
    portal = TestPortalRunner(config_file=args.config, use_mocks=args.mocks)
    await portal.initialize()
    
    print(f"\n🎯 Running test suite: {args.suite}")
    
    # Ejecutar pruebas según selección
    if args.suite in ['unit', 'all']:
        await portal.run_unit_tests()
    
    if args.suite in ['integration', 'all']:
        await portal.run_integration_tests()
    
    if args.suite in ['performance', 'all']:
        await portal.run_performance_tests()
    
    # Generar reporte
    report = portal.generate_report()
    
    # Mostrar resumen
    print(f"\n🎉 Test execution completed!")
    print(f"📊 Results: {report['summary']['total_passed']}/{report['summary']['total_tests']} tests passed")
    print(f"✨ Success rate: {report['summary']['success_rate']:.1f}%")
    
    # Exit code basado en resultados
    sys.exit(0 if report['summary']['success_rate'] == 100 else 1)

if __name__ == '__main__':
    asyncio.run(main())
