"""
Simple test endpoint to verify simulation save functionality
Add this to the simulation routes for debugging
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from admin.controllers.simulation_controller import SimulationController
from utils.permission_decorators import teacher_required

# Add this route to the simulation_routes.py file:

@admin_simulation_bp.route('/edit/<int:simulation_id>/test-save', methods=['GET', 'POST'])
@login_required  
@teacher_required
def test_save_endpoint(simulation_id):
    """Test endpoint to verify save functionality"""
    try:
        if request.method == 'GET':
            # Return basic info about the simulation and authentication status
            simulation_controller = SimulationController()
            sim_data = simulation_controller.get_simulation_by_id(simulation_id)
            
            return jsonify({
                'success': True,
                'message': 'Test endpoint working',
                'simulation_id': simulation_id,
                'authenticated': current_user.is_authenticated,
                'user_id': getattr(current_user, 'id', None),
                'simulation_exists': 'error' not in sim_data,
                'simulation_title': sim_data.get('simulation', {}).get('title') if 'error' not in sim_data else 'Not found'
            })
        
        # POST request - simple save test
        data = request.get_json() or {}
        simulation_controller = SimulationController()
        
        # Minimal update data
        update_data = {
            'title': data.get('title', 'Test Save ' + str(simulation_id)),
            'description': data.get('description', 'Testing save functionality'),
            'is_active': True
        }
        
        result = simulation_controller.update_simulation(simulation_id, update_data)
        
        return jsonify({
            'success': result.get('success', False),
            'message': result.get('message', result.get('error', 'Unknown result')),
            'test_data': update_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Test save endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Test endpoint error: {str(e)}'
        }), 500

print("Add this test endpoint to admin/routes/simulation_routes.py for debugging")