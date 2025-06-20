from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from admin.controllers.simulation_controller import SimulationController

# Create admin simulation routes blueprint
admin_simulation_bp = Blueprint('admin_simulation', __name__, url_prefix='/admin/simulation')

# Initialize controller
simulation_controller = SimulationController()

@admin_simulation_bp.route('/dashboard')
@login_required
def simulation_dashboard():
    """Admin simulation dashboard"""
    simulations = simulation_controller.get_all_simulations()
    return render_template('admin/simulation_dashboard.html', simulations=simulations)

@admin_simulation_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_simulation():
    """Create a new simulation"""
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = simulation_controller.create_simulation(data, current_user.id)
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
    
    return render_template('admin/simulation_builder.html')

@admin_simulation_bp.route('/edit/<int:simulation_id>', methods=['GET', 'PUT'])
@login_required
def edit_simulation(simulation_id):
    """Edit an existing simulation"""
    if request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = simulation_controller.update_simulation(simulation_id, data, current_user.id)
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    # GET request - show edit form with simulation data
    simulation = simulation_controller.get_simulation_by_id(simulation_id)
    if 'error' in simulation:
        flash(simulation['error'], 'error')
        return redirect(url_for('admin_simulation.simulation_dashboard'))
    
    return render_template('admin/simulation_builder.html', simulation=simulation)

@admin_simulation_bp.route('/delete/<int:simulation_id>', methods=['DELETE'])
@login_required
def delete_simulation(simulation_id):
    """Delete a simulation"""
    result = simulation_controller.delete_simulation(simulation_id)
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)

@admin_simulation_bp.route('/preview/<int:simulation_id>')
@login_required
def preview_simulation(simulation_id):
    """Preview a simulation"""
    simulation = simulation_controller.get_simulation_by_id(simulation_id)
    if 'error' in simulation:
        flash(simulation['error'], 'error')
        return redirect(url_for('admin_simulation.simulation_dashboard'))
    
    return render_template('admin/simulation_preview.html', simulation=simulation)

@admin_simulation_bp.route('/api/builder', methods=['POST'])
@login_required
def create_simulation_from_builder():
    """Create simulation from builder interface"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result = simulation_controller.create_simulation_from_builder(data, current_user.id)
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result), 201

@admin_simulation_bp.route('/api/<int:simulation_id>/validate/<int:step_index>', methods=['POST'])
@login_required
def validate_simulation_step(simulation_id, step_index):
    """Validate a simulation step (admin endpoint for testing)"""
    data = request.get_json()
    if not data or 'response' not in data:
        return jsonify({'valid': False, 'message': 'No response provided'}), 400
    
    result = simulation_controller.validate_simulation_step(
        simulation_id, 
        step_index, 
        data['response']
    )
    
    return jsonify(result)
