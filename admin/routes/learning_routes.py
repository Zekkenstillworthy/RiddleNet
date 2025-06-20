from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from admin.controllers.learning_controller import LearningPathController

# Create admin learning path routes blueprint
admin_learning_bp = Blueprint('admin_learning', __name__, url_prefix='/admin/learning')

# Initialize controller
learning_controller = LearningPathController()

@admin_learning_bp.route('/dashboard')
@login_required
def learning_dashboard():
    """Admin learning path dashboard"""
    learning_paths = learning_controller.get_all_learning_paths()
    return render_template('admin/learning_dashboard.html', learning_paths=learning_paths)

@admin_learning_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_learning_path():
    """Create a new learning path"""
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        simulation_ids = data.pop('simulation_ids', [])
        result = learning_controller.create_learning_path_with_simulations(data, simulation_ids, current_user.id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
    
    return render_template('admin/learning_path_builder.html')

@admin_learning_bp.route('/edit/<int:path_id>', methods=['GET', 'PUT'])
@login_required
def edit_learning_path(path_id):
    """Edit an existing learning path"""
    if request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = learning_controller.update_learning_path(path_id, data, current_user.id)
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    # GET request - show edit form with learning path data
    learning_path = learning_controller.get_learning_path_by_id(path_id)
    if 'error' in learning_path:
        flash(learning_path['error'], 'error')
        return redirect(url_for('admin_learning.learning_dashboard'))
    
    return render_template('admin/learning_path_builder.html', learning_path=learning_path)

@admin_learning_bp.route('/delete/<int:path_id>', methods=['DELETE'])
@login_required
def delete_learning_path(path_id):
    """Delete a learning path"""
    result = learning_controller.delete_learning_path(path_id)
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)

@admin_learning_bp.route('/preview/<int:path_id>')
@login_required
def preview_learning_path(path_id):
    """Preview a learning path"""
    learning_path = learning_controller.get_learning_path_by_id(path_id)
    if 'error' in learning_path:
        flash(learning_path['error'], 'error')
        return redirect(url_for('admin_learning.learning_dashboard'))
    
    return render_template('admin/learning_path_preview.html', learning_path=learning_path)

@admin_learning_bp.route('/api/all')
@login_required
def get_all_learning_paths_api():
    """Get all learning paths API endpoint"""
    learning_paths = learning_controller.get_all_learning_paths()
    return jsonify(learning_paths)
