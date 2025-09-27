"""
Debug patch for the simulation save functionality
"""

# Add this debugging code to the save route
SAVE_ROUTE_DEBUG_PATCH = '''
@admin_simulation_bp.route('/edit/<int:simulation_id>/save', methods=['POST'])
@login_required
@teacher_required
def save_simulation_from_troubleshooting_editor(simulation_id):
    """Save simulation changes from troubleshooting editor"""
    try:
        # Add debugging for the request
        current_app.logger.info(f"[DEBUG] Save endpoint called for simulation {simulation_id}")
        current_app.logger.info(f"[DEBUG] Request content type: {request.content_type}")
        current_app.logger.info(f"[DEBUG] Request method: {request.method}")
        current_app.logger.info(f"[DEBUG] Current user authenticated: {current_user.is_authenticated}")
        current_app.logger.info(f"[DEBUG] Current user ID: {getattr(current_user, 'id', None)}")
        
        # Check if request has JSON data
        if not request.is_json:
            current_app.logger.error(f"[DEBUG] Request is not JSON: {request.content_type}")
            return jsonify({'success': False, 'message': 'Request must be JSON'}), 400
        
        data = request.json
        if not data:
            current_app.logger.error("[DEBUG] No JSON data in request")
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        current_app.logger.info(f"[DEBUG] Received data keys: {list(data.keys())}")

        # Convert troubleshooting editor data back to simulation format
        update_data = {
            'title': data.get('title'),
            'description': data.get('description'),
            'difficulty': data.get('difficulty'),
            'type': data.get('problem_type', 'network'),
            'estimated_duration': data.get('time_limit', 15),
            'base_score': data.get('base_score', 50),
            'time_bonus': data.get('time_bonus', 10),
            'hints': data.get('hints', []),
            'step_definitions': data.get('required_steps', []),
            'solution_steps': data.get('solution'),
            'simulation_config': {
                'network_topology': data.get('initial_topology', {}),
                'devices': data.get('devices', []),
                'solution_topology': data.get('solution_topology', {}),
                'cli_rules': data.get('cli_rules', {}),
                'collab': data.get('collab', {}),
                'tutorial': data.get('tutorial', {}),
                'achievements': data.get('achievements', {}),
                'scoring': data.get('scoring', {})
            }
        }

        current_app.logger.info(f"[DEBUG] Update data prepared for simulation {simulation_id}")

        # Update the simulation
        result = simulation_controller.update_simulation(simulation_id, update_data)

        current_app.logger.info(f"[DEBUG] Update result: {result}")

        if result.get('success'):
            current_app.logger.info(f"[DEBUG] Simulation {simulation_id} updated successfully")
            return jsonify({
                'success': True,
                'message': 'Simulation updated successfully',
                'simulation_id': simulation_id
            })
        else:
            current_app.logger.error(f"[DEBUG] Simulation update failed: {result.get('error')}")
            return jsonify({
                'success': False,
                'message': result.get('error', 'Error updating simulation')
            }), 400

    except Exception as e:
        current_app.logger.error(f"[DEBUG] Exception in save endpoint: {str(e)}")
        import traceback
        current_app.logger.error(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Error saving simulation: {str(e)}'
        }), 500
'''

print("Debug patch prepared. Apply this to the simulation_routes.py file to get better error information.")