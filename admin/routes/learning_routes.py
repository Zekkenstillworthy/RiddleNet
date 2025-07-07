from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from admin.controllers.learning_controller import LearningPathController
from admin.controllers.simulation_controller import SimulationController

# Create blueprint for learning path management
learning_path_bp = Blueprint('learning_path', __name__, url_prefix='/admin/learning')

# Initialize controllers
learning_controller = LearningPathController()
simulation_controller = SimulationController()

@learning_path_bp.route('/dashboard')
@login_required
def learning_dashboard():
    """Learning path management dashboard"""
    try:
        dashboard_data = learning_controller.get_dashboard_data()
        return render_template(
            'admin/learning_dashboard.html',
            dashboard_data=dashboard_data
        )
    except Exception as e:
        flash(f'Error loading learning dashboard: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

@learning_path_bp.route('/paths')
@login_required
def learning_paths_list():
    """List all learning paths"""
    try:
        paths_data = learning_controller.get_all_learning_paths()
        return render_template(
            'admin/learning_paths_list.html',
            learning_paths=paths_data.get('learning_paths', []),
            total_count=paths_data.get('total_count', 0)
        )
    except Exception as e:
        flash(f'Error loading learning paths: {str(e)}', 'error')
        return redirect(url_for('learning_path.learning_dashboard'))

@learning_path_bp.route('/builder')
@login_required
def learning_path_builder():
    """Learning path builder interface"""
    try:
        # Get available simulations for the builder
        simulations_data = simulation_controller.get_all_simulations()
        return render_template(
            'admin/learning_path_builder.html',
            available_simulations=simulations_data.get('simulations', []),
            active_page='learning_path_builder'
        )
    except Exception as e:
        flash(f'Error loading path builder: {str(e)}', 'error')
        return redirect(url_for('learning_path.learning_paths_list'))

@learning_path_bp.route('/edit/<int:path_id>')
@login_required
def edit_learning_path(path_id):
    """Edit existing learning path"""
    try:
        path_data = learning_controller.get_learning_path_by_id(path_id, include_simulations=True)
        if 'error' in path_data:
            flash(path_data['error'], 'error')
            return redirect(url_for('learning_path.learning_paths_list'))
        
        # Get available simulations for adding to path
        simulations_data = simulation_controller.get_all_simulations()
        
        return render_template(
            'admin/learning_path_editor.html',
            learning_path=path_data['learning_path'],
            available_simulations=simulations_data.get('simulations', [])
        )
    except Exception as e:
        flash(f'Error loading learning path: {str(e)}', 'error')
        return redirect(url_for('learning_path.learning_paths_list'))

@learning_path_bp.route('/analytics/<int:path_id>')
@login_required
def learning_path_analytics(path_id):
    """Detailed analytics for a learning path"""
    try:
        analytics_data = learning_controller.get_learning_path_analytics(path_id)
        if 'error' in analytics_data:
            flash(analytics_data['error'], 'error')
            return redirect(url_for('learning_path.learning_paths_list'))
        
        return render_template(
            'admin/learning_path_analytics.html',
            analytics=analytics_data
        )
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'error')
        return redirect(url_for('learning_path.learning_paths_list'))

# API Routes

@learning_path_bp.route('/api/paths', methods=['GET'])
@login_required
def get_learning_paths_api():
    """Get all learning paths"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        result = learning_controller.get_all_learning_paths(include_inactive=include_inactive)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get learning paths: {str(e)}'}), 500

@learning_path_bp.route('/api/paths', methods=['POST'])
@login_required
def create_learning_path_api():
    """Create a new learning path"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = learning_controller.create_learning_path(data, current_user.id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': f'Failed to create learning path: {str(e)}'}), 500

@learning_path_bp.route('/api/paths-with-simulations', methods=['POST'])
@login_required
def create_learning_path_with_simulations_api():
    """Create learning path with associated simulations"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        simulation_associations = data.pop('simulation_associations', [])
        result = learning_controller.create_learning_path_with_simulations(
            data, simulation_associations, current_user.id
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': f'Failed to create learning path: {str(e)}'}), 500

@learning_path_bp.route('/api/paths/<int:path_id>', methods=['GET'])
@login_required
def get_learning_path_api(path_id):
    """Get learning path by ID"""
    try:
        include_simulations = request.args.get('include_simulations', 'true').lower() == 'true'
        result = learning_controller.get_learning_path_by_id(path_id, include_simulations=include_simulations)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get learning path: {str(e)}'}), 500

@learning_path_bp.route('/api/paths/<int:path_id>', methods=['PUT'])
@login_required
def update_learning_path_api(path_id):
    """Update learning path"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = learning_controller.update_learning_path(path_id, data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to update learning path: {str(e)}'}), 500

@learning_path_bp.route('/api/paths/<int:path_id>', methods=['DELETE'])
@login_required
def delete_learning_path_api(path_id):
    """Delete learning path"""
    try:
        result = learning_controller.delete_learning_path(path_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to delete learning path: {str(e)}'}), 500

@learning_path_bp.route('/api/paths/<int:path_id>/simulations', methods=['POST'])
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

@learning_path_bp.route('/api/paths/<int:path_id>/simulations/<int:simulation_id>', methods=['DELETE'])
@login_required
def remove_simulation_from_path_api(path_id, simulation_id):
    """Remove simulation from learning path"""
    try:
        result = learning_controller.remove_simulation_from_path(path_id, simulation_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to remove simulation: {str(e)}'}), 500

@learning_path_bp.route('/api/paths/<int:path_id>/reorder', methods=['PUT'])
@login_required
def reorder_simulations_in_path_api(path_id):
    """Reorder simulations in learning path"""
    try:
        data = request.get_json()
        if not data or 'simulation_order' not in data:
            return jsonify({'error': 'Simulation order required'}), 400
        
        result = learning_controller.reorder_simulations_in_path(path_id, data['simulation_order'])
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to reorder simulations: {str(e)}'}), 500

@learning_path_bp.route('/api/paths/<int:path_id>/analytics', methods=['GET'])
@login_required
def get_learning_path_analytics_api(path_id):
    """Get learning path analytics"""
    try:
        result = learning_controller.get_learning_path_analytics(path_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get analytics: {str(e)}'}), 500

@learning_path_bp.route('/api/user/<int:user_id>/progress/<int:path_id>', methods=['GET'])
@login_required
def get_user_progress_in_path_api(user_id, path_id):
    """Get user progress in learning path"""
    try:
        result = learning_controller.get_user_progress_in_path(user_id, path_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get user progress: {str(e)}'}), 500

@learning_path_bp.route('/api/recommendations/<int:simulation_id>', methods=['GET'])
@login_required
def get_simulation_recommendations_api(simulation_id):
    """Get simulation recommendations for a user"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        recommendations = learning_controller.get_simulation_recommendations(
            int(user_id), simulation_id
        )
        
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': f'Failed to get recommendations: {str(e)}'}), 500

# Error Handlers
@learning_path_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@learning_path_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
