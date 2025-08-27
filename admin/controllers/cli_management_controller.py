"""
CLI Management Controller for Admin Interface
Handles CRUD operations for device CLI commands and command libraries
"""

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from utils.render_utils import render_safe_template
from utils.auth_decorators import admin_required
import json

# Create blueprint
cli_management_bp = Blueprint('cli_management', __name__, url_prefix='/admin/cli')

# Try to import dynamic content models
try:
    from admin.models.simulation_content import DeviceCLICommand, DeviceConfiguration
    from admin.models.simulation import Simulation
    CLI_MODELS_AVAILABLE = True
except ImportError:
    CLI_MODELS_AVAILABLE = False

class CLIManagementController:
    """Controller for managing CLI commands across simulations"""
    
    def __init__(self):
        self.command_templates = {
            'router': {
                'basic': [
                    'enable',
                    'configure terminal',
                    'interface {interface}',
                    'ip address {ip} {subnet}',
                    'no shutdown',
                    'exit',
                    'router ospf {process_id}',
                    'network {network} {wildcard} area {area}',
                    'exit',
                    'copy running-config startup-config'
                ],
                'advanced': [
                    'enable',
                    'configure terminal',
                    'access-list {number} {action} {source} {wildcard}',
                    'interface {interface}',
                    'ip access-group {number} {direction}',
                    'exit',
                    'ip route {network} {subnet} {next_hop}',
                    'copy running-config startup-config'
                ]
            },
            'switch': {
                'basic': [
                    'enable',
                    'configure terminal',
                    'vlan {vlan_id}',
                    'name {vlan_name}',
                    'exit',
                    'interface {interface}',
                    'switchport mode access',
                    'switchport access vlan {vlan_id}',
                    'exit',
                    'copy running-config startup-config'
                ],
                'advanced': [
                    'enable',
                    'configure terminal',
                    'spanning-tree vlan {vlan_id} root primary',
                    'interface range {interface_range}',
                    'switchport trunk encapsulation dot1q',
                    'switchport mode trunk',
                    'switchport trunk allowed vlan {vlan_list}',
                    'exit',
                    'copy running-config startup-config'
                ]
            },
            'pc': {
                'windows': [
                    'ipconfig',
                    'ipconfig /all',
                    'ping {target}',
                    'tracert {target}',
                    'nslookup {hostname}',
                    'netstat -an',
                    'arp -a'
                ],
                'linux': [
                    'ifconfig',
                    'ip addr show',
                    'ping {target}',
                    'traceroute {target}',
                    'nslookup {hostname}',
                    'netstat -tuln',
                    'arp -a'
                ]
            }
        }

    def get_command_library(self, device_type=None):
        """Get command library for device types"""
        if device_type:
            return self.command_templates.get(device_type, {})
        return self.command_templates

    def get_simulation_cli_commands(self, simulation_id):
        """Get all CLI commands for a simulation"""
        if not CLI_MODELS_AVAILABLE:
            return {'error': 'CLI models not available'}
        
        try:
            # Get all devices for the simulation
            devices = DeviceConfiguration.query.filter_by(
                simulation_id=simulation_id,
                is_active=True
            ).all()
            
            cli_data = []
            for device in devices:
                commands = DeviceCLICommand.query.filter_by(
                    device_id=device.id,
                    is_active=True
                ).order_by(DeviceCLICommand.command_order).all()
                
                device_cli = {
                    'device_id': device.id,
                    'device_name': device.device_name,
                    'device_type': device.device_type,
                    'commands': [
                        {
                            'id': cmd.id,
                            'command': cmd.command,
                            'command_type': cmd.command_type,
                            'expected_output': cmd.expected_output,
                            'description': cmd.description,
                            'hints': cmd.hints,
                            'is_correct_command': cmd.is_correct_command,
                            'command_order': cmd.command_order,
                            'timeout_seconds': cmd.timeout_seconds
                        } for cmd in commands
                    ]
                }
                cli_data.append(device_cli)
            
            return {
                'success': True,
                'simulation_id': simulation_id,
                'devices': cli_data
            }
            
        except Exception as e:
            return {'error': f'Failed to get CLI commands: {str(e)}'}

    def create_cli_command(self, command_data):
        """Create a new CLI command"""
        if not CLI_MODELS_AVAILABLE:
            return {'error': 'CLI models not available'}
        
        try:
            from admin.models import db
            
            command = DeviceCLICommand(
                device_id=command_data['device_id'],
                command=command_data['command'],
                command_type=command_data.get('command_type', 'configuration'),
                expected_output=command_data.get('expected_output', ''),
                description=command_data.get('description', ''),
                hints=command_data.get('hints', []),
                is_correct_command=command_data.get('is_correct_command', True),
                command_order=command_data.get('command_order', 0),
                timeout_seconds=command_data.get('timeout_seconds', 30),
                is_active=True
            )
            
            db.session.add(command)
            db.session.commit()
            
            return {
                'success': True,
                'command_id': command.id,
                'message': 'CLI command created successfully'
            }
            
        except Exception as e:
            return {'error': f'Failed to create CLI command: {str(e)}'}

    def update_cli_command(self, command_id, update_data):
        """Update existing CLI command"""
        if not CLI_MODELS_AVAILABLE:
            return {'error': 'CLI models not available'}
        
        try:
            from admin.models import db
            
            command = DeviceCLICommand.query.get(command_id)
            if not command:
                return {'error': 'CLI command not found'}
            
            # Update fields
            for field in ['command', 'command_type', 'expected_output', 'description', 
                         'hints', 'is_correct_command', 'command_order', 'timeout_seconds']:
                if field in update_data:
                    setattr(command, field, update_data[field])
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'CLI command updated successfully'
            }
            
        except Exception as e:
            return {'error': f'Failed to update CLI command: {str(e)}'}

    def delete_cli_command(self, command_id):
        """Delete CLI command (soft delete)"""
        if not CLI_MODELS_AVAILABLE:
            return {'error': 'CLI models not available'}
        
        try:
            from admin.models import db
            
            command = DeviceCLICommand.query.get(command_id)
            if not command:
                return {'error': 'CLI command not found'}
            
            command.is_active = False
            db.session.commit()
            
            return {
                'success': True,
                'message': 'CLI command deleted successfully'
            }
            
        except Exception as e:
            return {'error': f'Failed to delete CLI command: {str(e)}'}

    def bulk_import_commands(self, device_id, device_type, template_name):
        """Bulk import commands from template"""
        if not CLI_MODELS_AVAILABLE:
            return {'error': 'CLI models not available'}
        
        try:
            from admin.models import db
            
            template_commands = self.command_templates.get(device_type, {}).get(template_name, [])
            if not template_commands:
                return {'error': f'No template found for {device_type}/{template_name}'}
            
            # Clear existing commands for this device
            DeviceCLICommand.query.filter_by(device_id=device_id).update({'is_active': False})
            
            # Import template commands
            for order, command_text in enumerate(template_commands):
                command = DeviceCLICommand(
                    device_id=device_id,
                    command=command_text,
                    command_type='configuration',
                    expected_output='Command executed successfully',
                    description=f'Template command for {device_type}',
                    command_order=order,
                    is_correct_command=True,
                    is_active=True
                )
                db.session.add(command)
            
            db.session.commit()
            
            return {
                'success': True,
                'imported_count': len(template_commands),
                'message': f'Imported {len(template_commands)} commands from template'
            }
            
        except Exception as e:
            return {'error': f'Failed to import commands: {str(e)}'}

# Initialize controller
cli_controller = CLIManagementController()

# Routes
@cli_management_bp.route('/')
@login_required
@admin_required
def cli_management_dashboard():
    """CLI management dashboard"""
    return render_safe_template('admin/cli_management/dashboard.html')

@cli_management_bp.route('/simulation/<int:simulation_id>')
@login_required
@admin_required
def manage_simulation_cli(simulation_id):
    """Manage CLI commands for a specific simulation"""
    try:
        if CLI_MODELS_AVAILABLE:
            simulation = Simulation.query.get_or_404(simulation_id)
        else:
            simulation = {'id': simulation_id, 'title': f'Simulation {simulation_id}'}
        
        return render_safe_template('admin/cli_management/simulation_cli.html', 
                                   simulation=simulation)
    except Exception as e:
        flash(f'Error loading simulation: {str(e)}', 'error')
        return redirect(url_for('cli_management.cli_management_dashboard'))

# API Routes
@cli_management_bp.route('/api/simulation/<int:simulation_id>/commands')
@login_required
@admin_required
def get_simulation_cli_api(simulation_id):
    """Get CLI commands for simulation"""
    result = cli_controller.get_simulation_cli_commands(simulation_id)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@cli_management_bp.route('/api/commands', methods=['POST'])
@login_required
@admin_required
def create_cli_command_api():
    """Create new CLI command"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result = cli_controller.create_cli_command(data)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result), 201

@cli_management_bp.route('/api/commands/<int:command_id>', methods=['PUT'])
@login_required
@admin_required
def update_cli_command_api(command_id):
    """Update CLI command"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result = cli_controller.update_cli_command(command_id, data)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@cli_management_bp.route('/api/commands/<int:command_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_cli_command_api(command_id):
    """Delete CLI command"""
    result = cli_controller.delete_cli_command(command_id)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@cli_management_bp.route('/api/templates')
@login_required
@admin_required
def get_command_templates():
    """Get command templates"""
    return jsonify({
        'success': True,
        'templates': cli_controller.get_command_library()
    })

@cli_management_bp.route('/api/device/<int:device_id>/import/<device_type>/<template_name>', methods=['POST'])
@login_required
@admin_required
def bulk_import_commands_api(device_id, device_type, template_name):
    """Bulk import commands from template"""
    result = cli_controller.bulk_import_commands(device_id, device_type, template_name)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)
