"""
User-facing API routes for accessing dynamic simulation content.
Provides endpoints for retrieving tutorials, devices, CLI commands, and connections.
"""

from flask import Blueprint, jsonify, current_app, request
from flask_login import current_user

try:
    from admin.models.simulation_content import (
        SimulationTutorial, DeviceConfiguration, 
        DeviceCLICommand, DeviceConnection
    )
    CONTENT_MODELS_AVAILABLE = True
except ImportError:
    CONTENT_MODELS_AVAILABLE = False

from utils.auth_decorators import user_required

# Create blueprint for user simulation content API
user_simulation_content_bp = Blueprint('user_simulation_content', __name__, url_prefix='/api/simulation-content')

@user_simulation_content_bp.route('/simulation/<int:simulation_id>/tutorials', methods=['GET'])
@user_required
def get_simulation_tutorials(simulation_id):
    """Get tutorial steps for a simulation"""
    if not CONTENT_MODELS_AVAILABLE:
        return jsonify({'error': 'Dynamic content not available'}), 501
    
    try:
        tutorials = SimulationTutorial.query.filter_by(
            simulation_id=simulation_id,
            is_active=True
        ).order_by(SimulationTutorial.order).all()
        
        tutorial_data = []
        for tutorial in tutorials:
            tutorial_data.append({
                'id': tutorial.id,
                'title': tutorial.title,
                'step_number': tutorial.step_number,
                'content': tutorial.get_content_dict(),
                'objectives': tutorial.objectives,
                'estimated_time': tutorial.estimated_time,
                'is_optional': tutorial.is_optional,
                'order': tutorial.order
            })
        
        return jsonify({
            'success': True,
            'tutorials': tutorial_data,
            'total_steps': len(tutorial_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting tutorials for simulation {simulation_id}: {e}")
        return jsonify({'error': 'Failed to load tutorial content'}), 500

@user_simulation_content_bp.route('/simulation/<int:simulation_id>/devices', methods=['GET'])
@user_required
def get_simulation_devices(simulation_id):
    """Get device configurations for a simulation"""
    if not CONTENT_MODELS_AVAILABLE:
        return jsonify({'error': 'Dynamic content not available'}), 501
    
    try:
        devices = DeviceConfiguration.query.filter_by(
            simulation_id=simulation_id,
            is_active=True
        ).order_by(DeviceConfiguration.position_x, DeviceConfiguration.position_y).all()
        
        device_data = []
        for device in devices:
            device_info = {
                'id': device.id,
                'name': device.device_name,
                'device_type': device.device_type,
                'tooltip': device.tooltip,
                'position': {
                    'x': device.position_x,
                    'y': device.position_y
                },
                'power_state': device.power_state,
                'configuration': device.get_configuration_dict(),
                'visual_settings': device.get_visual_settings_dict()
            }
            device_data.append(device_info)
        
        return jsonify({
            'success': True,
            'devices': device_data,
            'total_devices': len(device_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting devices for simulation {simulation_id}: {e}")
        return jsonify({'error': 'Failed to load device configurations'}), 500

@user_simulation_content_bp.route('/simulation/<int:simulation_id>/device/<int:device_id>/cli', methods=['GET'])
@user_required
def get_device_cli_commands(simulation_id, device_id):
    """Get CLI commands for a specific device"""
    if not CONTENT_MODELS_AVAILABLE:
        return jsonify({'error': 'Dynamic content not available'}), 501
    
    try:
        # Verify device belongs to simulation
        device = DeviceConfiguration.query.filter_by(
            id=device_id,
            simulation_id=simulation_id
        ).first()
        
        if not device:
            return jsonify({'error': 'Device not found in simulation'}), 404
        
        cli_commands = DeviceCLICommand.query.filter_by(
            device_id=device_id,
            is_active=True
        ).order_by(DeviceCLICommand.command_order).all()
        
        commands_data = []
        for cmd in cli_commands:
            command_info = {
                'id': cmd.id,
                'command': cmd.command,
                'command_type': cmd.command_type,
                'expected_output': cmd.expected_output,
                'description': cmd.description,
                'is_correct_command': cmd.is_correct_command,
                'hints': cmd.hints,
                'order': cmd.command_order,
                'validation_rules': cmd.get_validation_rules_dict() if cmd.validation_rules else None
            }
            commands_data.append(command_info)
        
        return jsonify({
            'success': True,
            'device_name': device.device_name,
            'device_type': device.device_type,
            'cli_commands': commands_data,
            'total_commands': len(commands_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting CLI for device {device_id}: {e}")
        return jsonify({'error': 'Failed to load CLI commands'}), 500

@user_simulation_content_bp.route('/simulation/<int:simulation_id>/connections', methods=['GET'])
@user_required
def get_simulation_connections(simulation_id):
    """Get device connections for a simulation"""
    if not CONTENT_MODELS_AVAILABLE:
        return jsonify({'error': 'Dynamic content not available'}), 501
    
    try:
        connections = DeviceConnection.query.filter_by(
            simulation_id=simulation_id,
            is_active=True
        ).all()
        
        connection_data = []
        for conn in connections:
            connection_info = {
                'id': conn.id,
                'from_device_id': conn.from_device_id,
                'to_device_id': conn.to_device_id,
                'from_device_name': conn.from_device.device_name if conn.from_device else None,
                'to_device_name': conn.to_device.device_name if conn.to_device else None,
                'connection_type': conn.connection_type,
                'from_port': conn.from_port,
                'to_port': conn.to_port,
                'is_wireless': conn.is_wireless,
                'cable_type': conn.cable_type,
                'status': conn.status,
                'bandwidth': conn.bandwidth,
                'configuration': conn.get_configuration_dict(),
                'visual_settings': conn.get_visual_settings_dict()
            }
            connection_data.append(connection_info)
        
        return jsonify({
            'success': True,
            'connections': connection_data,
            'total_connections': len(connection_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting connections for simulation {simulation_id}: {e}")
        return jsonify({'error': 'Failed to load device connections'}), 500

@user_simulation_content_bp.route('/simulation/<int:simulation_id>/content/summary', methods=['GET'])
@user_required
def get_simulation_content_summary(simulation_id):
    """Get a summary of all dynamic content for a simulation"""
    if not CONTENT_MODELS_AVAILABLE:
        return jsonify({'error': 'Dynamic content not available'}), 501
    
    try:
        # Get counts of each content type
        tutorial_count = SimulationTutorial.query.filter_by(
            simulation_id=simulation_id, is_active=True
        ).count()
        
        device_count = DeviceConfiguration.query.filter_by(
            simulation_id=simulation_id, is_active=True
        ).count()
        
        connection_count = DeviceConnection.query.filter_by(
            simulation_id=simulation_id, is_active=True
        ).count()
        
        # Get total CLI commands across all devices
        cli_command_count = DeviceCLICommand.query.join(DeviceConfiguration).filter(
            DeviceConfiguration.simulation_id == simulation_id,
            DeviceCLICommand.is_active == True
        ).count()
        
        # Get simulation info if available
        try:
            from admin.models.simulation import Simulation
            simulation = Simulation.query.get(simulation_id)
            simulation_name = simulation.title if simulation else f"Simulation {simulation_id}"
        except:
            simulation_name = f"Simulation {simulation_id}"
        
        return jsonify({
            'success': True,
            'simulation_id': simulation_id,
            'simulation_name': simulation_name,
            'content_summary': {
                'tutorial_steps': tutorial_count,
                'devices': device_count,
                'connections': connection_count,
                'cli_commands': cli_command_count
            },
            'has_dynamic_content': any([
                tutorial_count > 0,
                device_count > 0,
                connection_count > 0,
                cli_command_count > 0
            ])
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting content summary for simulation {simulation_id}: {e}")
        return jsonify({'error': 'Failed to load content summary'}), 500

@user_simulation_content_bp.route('/simulation/<int:simulation_id>/validate-command', methods=['POST'])
@user_required
def validate_cli_command(simulation_id):
    """Validate a CLI command against expected commands"""
    if not CONTENT_MODELS_AVAILABLE:
        return jsonify({'error': 'Dynamic content not available'}), 501
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
        
        device_id = data.get('device_id')
        command = data.get('command', '').strip()
        
        if not device_id or not command:
            return jsonify({'error': 'Device ID and command are required'}), 400
        
        # Find matching CLI command
        cli_command = DeviceCLICommand.query.filter_by(
            device_id=device_id,
            is_active=True
        ).filter(DeviceCLICommand.command.ilike(f'%{command}%')).first()
        
        if cli_command:
            return jsonify({
                'success': True,
                'is_valid': cli_command.is_correct_command,
                'expected_output': cli_command.expected_output,
                'hints': cli_command.hints,
                'description': cli_command.description
            })
        else:
            return jsonify({
                'success': True,
                'is_valid': False,
                'message': 'Command not recognized',
                'hints': ['Check command syntax', 'Use help command for available options']
            })
        
    except Exception as e:
        current_app.logger.error(f"Error validating command: {e}")
        return jsonify({'error': 'Failed to validate command'}), 500

@user_simulation_content_bp.route('/device-types', methods=['GET'])
@user_required
def get_available_device_types():
    """Get list of available device types"""
    if not CONTENT_MODELS_AVAILABLE:
        return jsonify({'error': 'Dynamic content not available'}), 501
    
    try:
        # Get distinct device types from database
        device_types = DeviceConfiguration.query.with_entities(
            DeviceConfiguration.device_type
        ).distinct().all()
        
        type_list = [dt[0] for dt in device_types if dt[0]]
        
        return jsonify({
            'success': True,
            'device_types': sorted(type_list)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting device types: {e}")
        return jsonify({'error': 'Failed to load device types'}), 500

@user_simulation_content_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for simulation content API"""
    return jsonify({
        'success': True,
        'service': 'User Simulation Content API',
        'dynamic_content_available': CONTENT_MODELS_AVAILABLE,
        'endpoints': [
            '/simulation/<id>/tutorials',
            '/simulation/<id>/devices', 
            '/simulation/<id>/device/<device_id>/cli',
            '/simulation/<id>/connections',
            '/simulation/<id>/content/summary',
            '/simulation/<id>/validate-command',
            '/device-types'
        ]
    })