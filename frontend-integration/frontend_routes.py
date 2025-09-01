#!/usr/bin/env python3
"""
Frontend Routes for IA-Ops Integration
To be added to ia-ops-docs/web-interface/app.py
"""

from flask import jsonify, request
from api_client import api_client
import logging

logger = logging.getLogger(__name__)

# Dashboard Routes
@app.route('/api/dashboard')
def dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        result = api_client.get_dashboard_data()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/services/status')
def services_status():
    """Get backend services status"""
    try:
        result = api_client.get_services_status()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        logger.error(f"Services status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/services/health')
def services_health():
    """Get health check of all services"""
    try:
        result = api_client.health_check_all()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Repository Routes
@app.route('/api/repositories')
def get_repositories():
    """Get all repositories"""
    try:
        result = api_client.get_repositories()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get repositories error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repositories', methods=['POST'])
def create_repository():
    """Create new repository"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        result = api_client.create_repository(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Create repository error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repositories/<int:repo_id>')
def get_repository(repo_id):
    """Get repository by ID"""
    try:
        result = api_client.get_repository(repo_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get repository error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repositories/<int:repo_id>', methods=['PUT'])
def update_repository(repo_id):
    """Update repository"""
    try:
        data = request.get_json()
        result = api_client.update_repository(repo_id, data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Update repository error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repositories/<int:repo_id>', methods=['DELETE'])
def delete_repository(repo_id):
    """Delete repository"""
    try:
        result = api_client.delete_repository(repo_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Delete repository error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/repositories/<int:repo_id>/sync', methods=['POST'])
def sync_repository(repo_id):
    """Sync repository"""
    try:
        result = api_client.sync_repository(repo_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Sync repository error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Task Routes
@app.route('/api/tasks')
def get_tasks():
    """Get all tasks"""
    try:
        result = api_client.get_tasks()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get tasks error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create new task"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        result = api_client.create_task(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Create task error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>')
def get_task(task_id):
    """Get task by ID"""
    try:
        result = api_client.get_task(task_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get task error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>/execute', methods=['POST'])
def execute_task(task_id):
    """Execute task"""
    try:
        result = api_client.execute_task(task_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Execute task error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>/logs')
def get_task_logs(task_id):
    """Get task logs"""
    try:
        result = api_client.get_task_logs(task_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get task logs error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Log Routes
@app.route('/api/logs')
@app.route('/api/logs/<service>')
def get_logs(service=None):
    """Get logs"""
    try:
        limit = request.args.get('limit', 100, type=int)
        result = api_client.get_logs(service, limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get logs error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs/search')
def search_logs():
    """Search logs"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 100, type=int)
        
        if not query:
            return jsonify({'success': False, 'error': 'Query parameter required'}), 400
        
        result = api_client.search_logs(query, limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Search logs error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs', methods=['POST'])
def create_log():
    """Create log entry"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        result = api_client.create_log(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Create log error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# DataSync Routes
@app.route('/api/sync-jobs')
def get_sync_jobs():
    """Get sync jobs"""
    try:
        result = api_client.get_sync_jobs()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get sync jobs error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sync-jobs', methods=['POST'])
def create_sync_job():
    """Create sync job"""
    try:
        data = request.get_json()
        result = api_client.create_sync_job(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Create sync job error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sync-jobs/<int:job_id>/execute', methods=['POST'])
def execute_sync(job_id):
    """Execute sync job"""
    try:
        result = api_client.execute_sync(job_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Execute sync error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backups')
def get_backups():
    """Get backups"""
    try:
        result = api_client.get_backups()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get backups error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backups', methods=['POST'])
def create_backup():
    """Create backup"""
    try:
        data = request.get_json()
        result = api_client.create_backup(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Create backup error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# GitHub Runner Routes
@app.route('/api/runners')
def get_runners():
    """Get GitHub runners"""
    try:
        result = api_client.get_runners()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get runners error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/runners', methods=['POST'])
def create_runner():
    """Create GitHub runner"""
    try:
        data = request.get_json()
        result = api_client.create_runner(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Create runner error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/workflows')
def get_workflows():
    """Get workflows"""
    try:
        result = api_client.get_workflows()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get workflows error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/workflows/<int:workflow_id>/trigger', methods=['POST'])
def trigger_workflow(workflow_id):
    """Trigger workflow"""
    try:
        result = api_client.trigger_workflow(workflow_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Trigger workflow error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# TechDocs Routes
@app.route('/api/docs')
def get_docs():
    """Get documentation sites"""
    try:
        result = api_client.get_docs()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get docs error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/docs/build', methods=['POST'])
def build_docs():
    """Build documentation"""
    try:
        data = request.get_json()
        result = api_client.build_docs(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Build docs error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/docs/<int:doc_id>/rebuild', methods=['POST'])
def rebuild_docs(doc_id):
    """Rebuild documentation"""
    try:
        result = api_client.rebuild_docs(doc_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Rebuild docs error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Utility Routes
@app.route('/api/swagger-portal')
def swagger_portal_redirect():
    """Redirect to Swagger portal"""
    swagger_url = api_client.base_urls['swagger_portal']
    return jsonify({
        'success': True,
        'data': {
            'swagger_portal_url': swagger_url,
            'message': 'Access Swagger documentation portal'
        }
    })

@app.route('/api/integration/test')
def test_integration():
    """Test backend integration"""
    try:
        health = api_client.health_check_all()
        services_online = sum(1 for service in health.values() if service['status'] == 'online')
        
        return jsonify({
            'success': True,
            'data': {
                'integration_status': 'healthy' if services_online > 0 else 'unhealthy',
                'services_online': services_online,
                'total_services': len(health),
                'health_details': health
            }
        })
    except Exception as e:
        logger.error(f"Integration test error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
