from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from admin.controllers.simulation_controller import SimulationController
from admin.controllers.learning_controller import LearningPathController
import json

# Create blueprint with unique name to avoid conflicts
admin_simulation_bp = Blueprint('admin_simulation', __name__, url_prefix='/admin/simulation')

# Initialize controllers
simulation_controller = SimulationController()
learning_controller = LearningPathController()

@admin_simulation_bp.route('/dashboard')
@login_required
def simulation_dashboard():
    """Enhanced simulation management dashboard"""
    try:
        # Get dashboard data
        dashboard_data = simulation_controller.get_dashboard_data()
        learning_data = learning_controller.get_dashboard_data()
        
        return render_template(
            'admin/simulation_dashboard.html',
            simulation_data=dashboard_data,
            learning_data=learning_data
        )
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

@admin_simulation_bp.route('/builder')
@login_required
def simulation_builder():
    """Enhanced simulation builder interface"""
    return render_template('admin/simulation_builder.html')

@admin_simulation_bp.route('/list')
@login_required
def simulation_list():
    """List all simulations with management options"""
    try:
        simulations_data = simulation_controller.get_all_simulations()
        return render_template(
            'admin/simulation_list.html',
            simulations=simulations_data.get('simulations', []),
            total_count=simulations_data.get('total_count', 0)
        )
    except Exception as e:
        flash(f'Error loading simulations: {str(e)}', 'error')
        return redirect(url_for('admin_simulation.simulation_dashboard'))

@admin_simulation_bp.route('/edit/<int:simulation_id>')
@login_required
def edit_simulation(simulation_id):
    """Edit existing simulation"""
    try:
        simulation_data = simulation_controller.get_simulation_by_id(simulation_id, include_steps=True)
        if 'error' in simulation_data:
            flash(simulation_data['error'], 'error')
            return redirect(url_for('admin_simulation.simulation_list'))
        
        return render_template(
            'admin/simulation_editor.html',
            simulation=simulation_data['simulation']
        )
    except Exception as e:
        flash(f'Error loading simulation: {str(e)}', 'error')
        return redirect(url_for('admin_simulation.simulation_list'))

@admin_simulation_bp.route('/analytics/<int:simulation_id>')
@login_required
def simulation_analytics(simulation_id):
    """Detailed analytics for a specific simulation"""
    try:
        analytics_data = simulation_controller.get_simulation_analytics(simulation_id)
        if 'error' in analytics_data:
            flash(analytics_data['error'], 'error')
            return redirect(url_for('admin_simulation.simulation_list'))
        
        return render_template(
            'admin/simulation_analytics.html',
            analytics=analytics_data
        )
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'error')
        return redirect(url_for('admin_simulation.simulation_list'))

# API Routes for AJAX/Frontend Integration

@admin_simulation_bp.route('/api/create', methods=['POST'])
@login_required
def create_simulation_api():
    """Create simulation from builder interface"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = simulation_controller.create_simulation_from_builder(data, current_user.id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_simulation_bp.route('/api/templates/<simulation_type>')
@login_required
def get_simulation_templates(simulation_type):
    """Get templates for specific simulation type"""
    try:
        templates = simulation_controller.get_simulation_templates(simulation_type)
        return jsonify(templates)
    except Exception as e:
        return jsonify({'error': f'Failed to load templates: {str(e)}'}), 500

@admin_simulation_bp.route('/api/validate-step', methods=['POST'])
@login_required
def validate_simulation_step():
    """Real-time validation for simulation steps during creation"""
    try:
        data = request.get_json()
        
        # Mock validation for builder interface
        validation_result = {
            'isValid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        step_type = data.get('type')
        step_content = data.get('content', {})
        
        # Validate based on step type
        if step_type == 'configuration':
            if not step_content.get('device_type'):
                validation_result['errors'].append('Device type is required for configuration steps')
                validation_result['isValid'] = False
            
            if not step_content.get('commands'):
                validation_result['errors'].append('Configuration commands are required')
                validation_result['isValid'] = False
        
        elif step_type == 'question':
            if not step_content.get('question_text'):
                validation_result['errors'].append('Question text is required')
                validation_result['isValid'] = False
            
            if step_content.get('question_type') == 'multiple_choice' and not step_content.get('options'):
                validation_result['warnings'].append('Multiple choice questions should have options')
        
        return jsonify(validation_result)
        
    except Exception as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 500

@admin_simulation_bp.route('/api/list', methods=['GET'])
@login_required
def get_simulations_api():
    """Get simulations list for API consumption"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        result = simulation_controller.get_all_simulations(include_inactive=include_inactive)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get simulations: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>', methods=['GET'])
@login_required
def get_simulation_api(simulation_id):
    """Get simulation by ID"""
    try:
        include_steps = request.args.get('include_steps', 'true').lower() == 'true'
        result = simulation_controller.get_simulation_by_id(simulation_id, include_steps=include_steps)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get simulation: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>', methods=['PUT'])
@login_required
def update_simulation_api(simulation_id):
    """Update simulation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = simulation_controller.update_simulation(simulation_id, data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to update simulation: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>', methods=['DELETE'])
@login_required
def delete_simulation_api(simulation_id):
    """Delete simulation"""
    try:
        result = simulation_controller.delete_simulation(simulation_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to delete simulation: {str(e)}'}), 500

@admin_simulation_bp.route('/api/search', methods=['GET'])
@login_required
def search_simulations_api():
    """Search simulations with filters"""
    try:
        query_params = {
            'query': request.args.get('query', ''),
            'type': request.args.get('type'),
            'difficulty': request.args.get('difficulty'),
            'category': request.args.get('category')
        }
        
        result = simulation_controller.search_simulations(query_params)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>/analytics', methods=['GET'])
@login_required
def get_simulation_analytics_api(simulation_id):
    """Get simulation analytics"""
    try:
        result = simulation_controller.get_simulation_analytics(simulation_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get analytics: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>/validate/<int:step_index>', methods=['POST'])
@login_required
def validate_step_response(simulation_id, step_index):
    """Validate a specific step response (for testing simulations)"""
    try:
        data = request.get_json()
        if not data or 'response' not in data:
            return jsonify({'valid': False, 'message': 'No response provided'}), 400
        
        result = simulation_controller.validate_simulation_step(
            simulation_id, 
            step_index, 
            data['response']
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500

# Learning Path Integration Routes

@admin_simulation_bp.route('/api/learning-paths', methods=['GET'])
@login_required
def get_learning_paths_api():
    """Get all learning paths"""
    try:
        result = learning_controller.get_all_learning_paths()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get learning paths: {str(e)}'}), 500

@admin_simulation_bp.route('/api/learning-paths', methods=['POST'])
@login_required
def create_learning_path_api():
    """Create a new learning path"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        simulation_ids = data.pop('simulation_ids', [])
        result = learning_controller.create_learning_path_with_simulations(
            data, simulation_ids, current_user.id
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': f'Failed to create learning path: {str(e)}'}), 500

@admin_simulation_bp.route('/api/learning-paths/<int:path_id>/simulations', methods=['POST'])
@login_required
def add_simulation_to_path_api(path_id):
    """Add simulation to learning path"""
    try:
        data = request.get_json()
        if not data or 'simulation_id' not in data:
            return jsonify({'error': 'Simulation ID required'}), 400
        
        result = learning_controller.add_simulation_to_path(
            path_id,
            data['simulation_id'],
            data.get('order_index'),
            data.get('is_required', True),
            data.get('unlock_criteria')
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to add simulation: {str(e)}'}), 500

# Error Handlers
@admin_simulation_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@admin_simulation_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
