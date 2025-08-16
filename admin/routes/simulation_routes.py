from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from admin.controllers.simulation_controller import SimulationController
# Learning controller removed - Learning Paths feature disabled
from admin.services.assignment_service import assignment_service
from socket_events import emit_new_simulation_available, emit_assignment_created
import json

# Create blueprint with unique name to avoid conflicts
admin_simulation_bp = Blueprint('admin_simulation', __name__, url_prefix='/admin/simulation')

# Initialize controllers
simulation_controller = SimulationController()
# learning_controller removed - Learning Paths feature disabled

@admin_simulation_bp.route('/dashboard')
@login_required
def simulation_dashboard():
    """Enhanced simulation management dashboard"""
    try:
        # Get dashboard data
        dashboard_data = simulation_controller.get_dashboard_data()
        # Learning data removed - Learning Paths feature disabled
        learning_data = {'recent_paths': [], 'total_paths': 0, 'published_paths': 0}
        
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

# Learning Path Integration Routes - DISABLED (Feature Removed)

@admin_simulation_bp.route('/api/learning-paths', methods=['GET'])
@login_required
def get_learning_paths_api():
    """Get all learning paths - DISABLED"""
    return jsonify({'learning_paths': [], 'message': 'Learning Paths feature has been removed'})

@admin_simulation_bp.route('/api/learning-paths', methods=['POST'])
@login_required
def create_learning_path_api():
    """Create a new learning path - DISABLED"""
    return jsonify({'error': 'Learning Paths feature has been removed'}), 410

@admin_simulation_bp.route('/api/learning-paths/<int:path_id>/simulations', methods=['POST'])
@login_required
def add_simulation_to_path_api(path_id):
    """Add simulation to learning path - DISABLED"""
    return jsonify({'error': 'Learning Paths feature has been removed'}), 410

# Error Handlers
@admin_simulation_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@admin_simulation_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ===== WEEK 2 ENHANCEMENT: ASSIGNMENT API ENDPOINTS =====

@admin_simulation_bp.route('/api/assignments/lesson', methods=['POST'])
@login_required
def create_lesson_assignment():
    """Create a lesson-based assignment"""
    try:
        data = request.get_json()
        
        assignment = assignment_service.create_lesson_assignment(
            simulation_id=data['simulation_id'],
            class_id=data['class_id'],
            lesson_name=data['lesson_name'],
            due_date=data.get('due_date'),
            max_attempts=data.get('max_attempts', 3)
        )
        
        return jsonify({
            'success': True,
            'assignment_id': assignment.id,
            'message': 'Lesson assignment created successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to create lesson assignment: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/category', methods=['POST'])
@login_required
def create_category_auto_assignment():
    """Create automatic assignments for all simulations in a category"""
    try:
        data = request.get_json()
        
        assignments = assignment_service.create_category_auto_assignment(
            category=data['category'],
            class_ids=data['class_ids']
        )
        
        return jsonify({
            'success': True,
            'assignments_created': len(assignments),
            'message': f'Created {len(assignments)} auto-assignments for {data["category"]} category'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to create category assignments: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/explicit', methods=['POST'])
@login_required
def create_explicit_assignment():
    """Create an explicit assignment with custom settings"""
    try:
        data = request.get_json()
        
        assignment = assignment_service.create_explicit_assignment(
            simulation_id=data['simulation_id'],
            class_id=data['class_id'],
            title=data['title'],
            description=data.get('description', ''),
            due_date=data.get('due_date'),
            max_attempts=data.get('max_attempts', 3)
        )
        
        return jsonify({
            'success': True,
            'assignment_id': assignment.id,
            'message': 'Explicit assignment created successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to create explicit assignment: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/auto-assign/<int:simulation_id>', methods=['POST'])
@login_required
def auto_assign_simulation(simulation_id):
    """Automatically assign a simulation to relevant classes"""
    try:
        assignments = assignment_service.auto_assign_new_simulation(simulation_id)
        
        return jsonify({
            'success': True,
            'assignments_created': len(assignments),
            'class_ids': [a.class_id for a in assignments],
            'message': f'Auto-assigned simulation to {len(assignments)} classes'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to auto-assign simulation: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/class/<int:class_id>')
@login_required
def get_class_assignments(class_id):
    """Get all assignments for a specific class"""
    try:
        assignment_type = request.args.get('type')
        assignments = assignment_service.get_assignments_for_class(class_id, assignment_type)
        
        return jsonify({
            'success': True,
            'class_id': class_id,
            'assignments': assignments,
            'total': len(assignments)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get class assignments: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/enable-auto/<int:class_id>', methods=['POST'])
@login_required
def enable_category_auto_assignment(class_id):
    """Enable automatic assignment for a category in a class"""
    try:
        data = request.get_json()
        category = data['category']
        
        success = assignment_service.enable_category_auto_assignment(class_id, category)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Auto-assignment enabled for {category} in class {class_id}'
            })
        else:
            return jsonify({'error': 'Failed to enable auto-assignment'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to enable auto-assignment: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/statistics/<int:class_id>')
@login_required
def get_assignment_statistics(class_id):
    """Get comprehensive assignment statistics for a class"""
    try:
        stats = assignment_service.get_assignment_statistics(class_id)
        
        return jsonify({
            'success': True,
            'class_id': class_id,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get assignment statistics: {str(e)}'}), 500

# Enhanced simulation creation with auto-assignment
@admin_simulation_bp.route('/api/create-with-auto-assign', methods=['POST'])
@login_required
def create_simulation_with_auto_assign():
    """Create simulation and automatically assign to relevant classes"""
    try:
        data = request.get_json()
        
        # Create the simulation first
        result = simulation_controller.create_simulation(data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        simulation_id = result['simulation_id']
        
        # Auto-assign to relevant classes
        assignments = assignment_service.auto_assign_new_simulation(simulation_id)
        
        # Send real-time notification
        emit_new_simulation_available(
            simulation_id, 
            data.get('category', 'general'),
            [a.class_id for a in assignments]
        )
        
        return jsonify({
            'success': True,
            'simulation_id': simulation_id,
            'assignments_created': len(assignments),
            'message': f'Simulation created and assigned to {len(assignments)} classes'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to create simulation with auto-assignment: {str(e)}'}), 500
