"""
Enhanced Network Simulation API Endpoints
Provides comprehensive API support for the new network simulation engine
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from user.models import db, User, SimulationProgress
from admin.models.simulation import Simulation
from user.utils import validate_simulation_access
import json
from datetime import datetime
import logging

# Create blueprint
enhanced_simulation_api = Blueprint('enhanced_simulation_api', __name__)
logger = logging.getLogger(__name__)

@enhanced_simulation_api.route('/api/simulation/<int:simulation_id>/device-config', methods=['POST'])
@login_required
def update_device_configuration(simulation_id):
    """
    Update device configuration for network simulation
    """
    try:
        # Validate simulation access
        simulation = Simulation.query.get_or_404(simulation_id)
        if not validate_simulation_access(simulation, current_user):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        device_id = data.get('deviceId')
        config = data.get('config', {})
        
        if not device_id:
            return jsonify({'error': 'Device ID is required'}), 400
        
        # Get current simulation data
        simulation_data = json.loads(simulation.simulation_data) if simulation.simulation_data else {}
        
        # Initialize topology structure if not exists
        if 'topology' not in simulation_data:
            simulation_data['topology'] = {'devices': {}, 'connections': {}}
        
        # Update device configuration
        if device_id not in simulation_data['topology']['devices']:
            simulation_data['topology']['devices'][device_id] = {
                'id': device_id,
                'type': config.get('deviceType', 'router'),
                'position': {'x': 100, 'y': 100}
            }
        
        # Merge new configuration
        device = simulation_data['topology']['devices'][device_id]
        device['config'] = {**device.get('config', {}), **config}
        device['interfaces'] = config.get('interfaces', {})
        device['lastModified'] = datetime.utcnow().isoformat()
        
        # Update simulation in database
        simulation.simulation_data = json.dumps(simulation_data)
        simulation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Update progress if this is a configuration step
        update_configuration_progress(simulation_id, device_id, config)
        
        logger.info(f"Device {device_id} configured for simulation {simulation_id}")
        
        return jsonify({
            'success': True,
            'deviceId': device_id,
            'config': device['config'],
            'message': 'Device configuration updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to update device configuration: {str(e)}")
        return jsonify({'error': 'Failed to update device configuration'}), 500


@enhanced_simulation_api.route('/api/simulation/<int:simulation_id>/device-add', methods=['POST'])
@login_required
def add_network_device(simulation_id):
    """
    Add a new device to network simulation
    """
    try:
        simulation = Simulation.query.get_or_404(simulation_id)
        if not validate_simulation_access(simulation, current_user):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        device_type = data.get('type', 'router')
        position = data.get('position', {'x': 100, 'y': 100})
        device_id = data.get('id') or f"{device_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Get current simulation data
        simulation_data = json.loads(simulation.simulation_data) if simulation.simulation_data else {}
        
        # Initialize topology if needed
        if 'topology' not in simulation_data:
            simulation_data['topology'] = {'devices': {}, 'connections': {}}
        
        # Create new device
        new_device = {
            'id': device_id,
            'type': device_type,
            'position': position,
            'config': get_default_device_config(device_type),
            'interfaces': get_default_interfaces(device_type),
            'state': 'up',
            'created': datetime.utcnow().isoformat(),
            'lastModified': datetime.utcnow().isoformat()
        }
        
        # Add to simulation
        simulation_data['topology']['devices'][device_id] = new_device
        
        # Update simulation in database
        simulation.simulation_data = json.dumps(simulation_data)
        simulation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Update progress
        update_device_add_progress(simulation_id, device_id, device_type)
        
        logger.info(f"Device {device_id} added to simulation {simulation_id}")
        
        return jsonify({
            'success': True,
            'device': new_device,
            'message': 'Device added successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to add device: {str(e)}")
        return jsonify({'error': 'Failed to add device'}), 500


@enhanced_simulation_api.route('/api/simulation/<int:simulation_id>/connection-create', methods=['POST'])
@login_required
def create_network_connection(simulation_id):
    """
    Create connection between network devices
    """
    try:
        simulation = Simulation.query.get_or_404(simulation_id)
        if not validate_simulation_access(simulation, current_user):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        source_id = data.get('sourceId')
        target_id = data.get('targetId')
        connection_type = data.get('type', 'ethernet')
        
        if not source_id or not target_id:
            return jsonify({'error': 'Source and target device IDs are required'}), 400
        
        # Get current simulation data
        simulation_data = json.loads(simulation.simulation_data) if simulation.simulation_data else {}
        
        # Validate devices exist
        devices = simulation_data.get('topology', {}).get('devices', {})
        if source_id not in devices or target_id not in devices:
            return jsonify({'error': 'One or both devices not found'}), 404
        
        # Create connection ID
        connection_id = f"{source_id}_{target_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create connection object
        connection = {
            'id': connection_id,
            'sourceId': source_id,
            'targetId': target_id,
            'type': connection_type,
            'status': 'up',
            'bandwidth': get_default_bandwidth(connection_type),
            'latency': 1,
            'created': datetime.utcnow().isoformat(),
            'config': {}
        }
        
        # Initialize connections structure if needed
        if 'connections' not in simulation_data['topology']:
            simulation_data['topology']['connections'] = {}
        
        # Add connection
        simulation_data['topology']['connections'][connection_id] = connection
        
        # Update device interfaces to reflect connection
        update_device_interfaces_for_connection(simulation_data, source_id, target_id, connection_id)
        
        # Update simulation in database
        simulation.simulation_data = json.dumps(simulation_data)
        simulation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Update progress
        update_connection_progress(simulation_id, connection_id, connection_type)
        
        logger.info(f"Connection {connection_id} created for simulation {simulation_id}")
        
        return jsonify({
            'success': True,
            'connection': connection,
            'message': 'Connection created successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to create connection: {str(e)}")
        return jsonify({'error': 'Failed to create connection'}), 500


@enhanced_simulation_api.route('/api/simulation/<int:simulation_id>/validate', methods=['POST'])
@login_required
def validate_network_simulation(simulation_id):
    """
    Validate network simulation configuration
    """
    try:
        simulation = Simulation.query.get_or_404(simulation_id)
        if not validate_simulation_access(simulation, current_user):
            return jsonify({'error': 'Access denied'}), 403
        
        # Get current simulation data
        simulation_data = json.loads(simulation.simulation_data) if simulation.simulation_data else {}
        topology = simulation_data.get('topology', {})
        
        # Perform comprehensive validation
        validation_result = perform_network_validation(topology)
        
        # Update simulation with validation results
        simulation_data['lastValidation'] = {
            'timestamp': datetime.utcnow().isoformat(),
            'result': validation_result
        }
        
        simulation.simulation_data = json.dumps(simulation_data)
        simulation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Update progress if validation successful
        if validation_result['isValid']:
            update_validation_progress(simulation_id, validation_result)
        
        logger.info(f"Validation completed for simulation {simulation_id}")
        
        return jsonify({
            'success': True,
            'validation': validation_result,
            'message': 'Network validation completed'
        })
        
    except Exception as e:
        logger.error(f"Failed to validate simulation: {str(e)}")
        return jsonify({'error': 'Failed to validate simulation'}), 500


@enhanced_simulation_api.route('/api/simulation/<int:simulation_id>/export', methods=['GET'])
@login_required
def export_simulation_data(simulation_id):
    """
    Export complete simulation data
    """
    try:
        simulation = Simulation.query.get_or_404(simulation_id)
        if not validate_simulation_access(simulation, current_user):
            return jsonify({'error': 'Access denied'}), 403
        
        # Get complete simulation data
        simulation_data = json.loads(simulation.simulation_data) if simulation.simulation_data else {}
        
        # Get progress data
        progress = SimulationProgress.query.filter_by(
            simulation_id=simulation_id,
            user_id=current_user.id
        ).first()
        
        progress_data = json.loads(progress.progress_data) if progress and progress.progress_data else {}
        
        # Compile export data
        export_data = {
            'simulation': {
                'id': simulation.id,
                'title': simulation.title,
                'description': simulation.description,
                'created_at': simulation.created_at.isoformat(),
                'updated_at': simulation.updated_at.isoformat()
            },
            'topology': simulation_data.get('topology', {}),
            'configuration': simulation_data.get('configuration', {}),
            'progress': progress_data,
            'metadata': {
                'exported_at': datetime.utcnow().isoformat(),
                'exported_by': current_user.username,
                'version': '2.0'
            }
        }
        
        return jsonify({
            'success': True,
            'data': export_data,
            'message': 'Simulation data exported successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to export simulation: {str(e)}")
        return jsonify({'error': 'Failed to export simulation'}), 500


@enhanced_simulation_api.route('/api/simulation/<int:simulation_id>/cli-execute', methods=['POST'])
@login_required
def execute_cli_command(simulation_id):
    """
    Execute CLI command on network device
    """
    try:
        simulation = Simulation.query.get_or_404(simulation_id)
        if not validate_simulation_access(simulation, current_user):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        device_id = data.get('deviceId')
        command = data.get('command', '').strip()
        
        if not device_id or not command:
            return jsonify({'error': 'Device ID and command are required'}), 400
        
        # Get device from simulation
        simulation_data = json.loads(simulation.simulation_data) if simulation.simulation_data else {}
        devices = simulation_data.get('topology', {}).get('devices', {})
        
        if device_id not in devices:
            return jsonify({'error': 'Device not found'}), 404
        
        device = devices[device_id]
        
        # Execute command simulation
        command_result = simulate_cli_command(device, command)
        
        # Log command execution
        if 'cliHistory' not in device:
            device['cliHistory'] = []
        
        device['cliHistory'].append({
            'command': command,
            'timestamp': datetime.utcnow().isoformat(),
            'result': command_result
        })
        
        # Update simulation data
        simulation.simulation_data = json.dumps(simulation_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'result': command_result,
            'message': 'CLI command executed successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to execute CLI command: {str(e)}")
        return jsonify({'error': 'Failed to execute CLI command'}), 500


# Helper functions

def get_default_device_config(device_type):
    """Get default configuration for device type"""
    configs = {
        'router': {
            'hostname': f'Router{datetime.utcnow().strftime("%M%S")}',
            'ipAddress': '192.168.1.1',
            'subnetMask': '255.255.255.0',
            'routingProtocols': {'ospf': False, 'rip': False, 'bgp': False},
            'services': ['routing', 'dhcp']
        },
        'switch': {
            'hostname': f'Switch{datetime.utcnow().strftime("%M%S")}',
            'managementIP': '192.168.1.10',
            'vlans': {'1': {'name': 'default', 'ports': []}},
            'spanningTree': {'enabled': True, 'priority': 32768},
            'services': ['switching']
        },
        'server': {
            'hostname': f'Server{datetime.utcnow().strftime("%M%S")}',
            'ipAddress': '192.168.1.100',
            'subnetMask': '255.255.255.0',
            'gateway': '192.168.1.1',
            'services': ['web', 'dns']
        },
        'pc': {
            'hostname': f'PC{datetime.utcnow().strftime("%M%S")}',
            'ipAddress': 'dhcp',
            'subnetMask': '255.255.255.0',
            'gateway': '192.168.1.1',
            'services': []
        }
    }
    
    return configs.get(device_type, configs['router'])


def get_default_interfaces(device_type):
    """Get default interfaces for device type"""
    interfaces = {
        'router': {
            'FastEthernet0/0': {
                'ipAddress': '192.168.1.1',
                'subnetMask': '255.255.255.0',
                'status': 'up',
                'duplex': 'auto',
                'speed': 'auto'
            },
            'FastEthernet0/1': {
                'ipAddress': '192.168.2.1',
                'subnetMask': '255.255.255.0',
                'status': 'up',
                'duplex': 'auto',
                'speed': 'auto'
            }
        },
        'switch': {
            'FastEthernet0/1': {'status': 'up', 'vlan': 1, 'duplex': 'auto', 'speed': 'auto'},
            'FastEthernet0/2': {'status': 'up', 'vlan': 1, 'duplex': 'auto', 'speed': 'auto'},
            'FastEthernet0/3': {'status': 'up', 'vlan': 1, 'duplex': 'auto', 'speed': 'auto'},
            'FastEthernet0/4': {'status': 'up', 'vlan': 1, 'duplex': 'auto', 'speed': 'auto'}
        },
        'server': {
            'eth0': {
                'ipAddress': '192.168.1.100',
                'subnetMask': '255.255.255.0',
                'status': 'up',
                'duplex': 'full',
                'speed': '1000'
            }
        },
        'pc': {
            'eth0': {
                'ipAddress': 'dhcp',
                'status': 'up',
                'duplex': 'full',
                'speed': '100'
            }
        }
    }
    
    return interfaces.get(device_type, interfaces['router'])


def get_default_bandwidth(connection_type):
    """Get default bandwidth for connection type"""
    bandwidths = {
        'ethernet': '100 Mbps',
        'serial': '1.544 Mbps',
        'fiber': '1 Gbps',
        'wireless': '54 Mbps'
    }
    
    return bandwidths.get(connection_type, '100 Mbps')


def update_device_interfaces_for_connection(simulation_data, source_id, target_id, connection_id):
    """Update device interfaces when connection is created"""
    devices = simulation_data['topology']['devices']
    
    # Find available interfaces and assign connection
    for device_id in [source_id, target_id]:
        device = devices[device_id]
        interfaces = device.get('interfaces', {})
        
        # Find first available interface
        for interface_name, interface_config in interfaces.items():
            if not interface_config.get('connectedTo'):
                interface_config['connectedTo'] = connection_id
                interface_config['connectedDevice'] = target_id if device_id == source_id else source_id
                break


def perform_network_validation(topology):
    """Perform comprehensive network validation"""
    devices = topology.get('devices', {})
    connections = topology.get('connections', {})
    
    errors = []
    warnings = []
    
    # Validate devices
    for device_id, device in devices.items():
        # Check basic configuration
        if not device.get('config', {}).get('hostname'):
            errors.append(f"Device {device_id} missing hostname")
        
        # Check IP configuration
        config = device.get('config', {})
        if 'ipAddress' in config and config['ipAddress']:
            if not is_valid_ip(config['ipAddress']):
                errors.append(f"Device {device_id} has invalid IP address")
        
        # Check interfaces
        interfaces = device.get('interfaces', {})
        for interface_name, interface_config in interfaces.items():
            if 'ipAddress' in interface_config and interface_config['ipAddress']:
                if not is_valid_ip(interface_config['ipAddress']):
                    errors.append(f"Device {device_id} interface {interface_name} has invalid IP address")
    
    # Validate connections
    for connection_id, connection in connections.items():
        source_id = connection.get('sourceId')
        target_id = connection.get('targetId')
        
        if source_id not in devices:
            errors.append(f"Connection {connection_id} references non-existent source device {source_id}")
        if target_id not in devices:
            errors.append(f"Connection {connection_id} references non-existent target device {target_id}")
    
    # Check network connectivity
    if len(devices) > 1 and len(connections) == 0:
        warnings.append("No connections defined between devices")
    
    # Check for IP conflicts
    ip_addresses = []
    for device in devices.values():
        config = device.get('config', {})
        if 'ipAddress' in config and config['ipAddress']:
            ip_addresses.append(config['ipAddress'])
        
        interfaces = device.get('interfaces', {})
        for interface_config in interfaces.values():
            if 'ipAddress' in interface_config and interface_config['ipAddress']:
                ip_addresses.append(interface_config['ipAddress'])
    
    # Find duplicates
    seen_ips = set()
    for ip in ip_addresses:
        if ip in seen_ips and ip != 'dhcp':
            errors.append(f"Duplicate IP address: {ip}")
        seen_ips.add(ip)
    
    return {
        'isValid': len(errors) == 0,
        'hasErrors': len(errors) > 0,
        'hasWarnings': len(warnings) > 0,
        'errors': errors,
        'warnings': warnings,
        'summary': {
            'devices': len(devices),
            'connections': len(connections),
            'issues': len(errors) + len(warnings)
        }
    }


def is_valid_ip(ip):
    """Validate IP address format"""
    if ip == 'dhcp':
        return True
    
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                return False
        
        return True
    except (ValueError, AttributeError):
        return False


def simulate_cli_command(device, command):
    """Simulate CLI command execution"""
    device_type = device.get('type', 'router')
    config = device.get('config', {})
    
    cmd_parts = command.lower().split()
    
    if not cmd_parts:
        return "% Invalid command"
    
    main_cmd = cmd_parts[0]
    
    if main_cmd == 'show':
        return handle_show_command(device, cmd_parts[1:])
    elif main_cmd == 'ping':
        return handle_ping_command(cmd_parts[1:] if len(cmd_parts) > 1 else [])
    elif main_cmd == 'help':
        return get_help_text(device_type)
    elif main_cmd in ['config', 'configure']:
        return "Entering configuration mode..."
    elif main_cmd == 'exit':
        return "Goodbye!"
    else:
        return f"% Unknown command: {command}"


def handle_show_command(device, args):
    """Handle show commands"""
    if not args:
        return "% Incomplete command"
    
    sub_cmd = args[0]
    
    if sub_cmd == 'interfaces':
        output = "Interface Status:\n"
        interfaces = device.get('interfaces', {})
        for name, config in interfaces.items():
            status = config.get('status', 'down')
            ip = config.get('ipAddress', 'unassigned')
            output += f"{name}: {status} - {ip}\n"
        return output
    
    elif sub_cmd == 'ip' and len(args) > 1 and args[1] == 'route':
        output = "Routing Table:\n"
        routes = device.get('config', {}).get('routingTable', [])
        for route in routes:
            output += f"{route.get('network', '0.0.0.0')}/{route.get('mask', '0.0.0.0')} "
            output += f"via {route.get('gateway', '0.0.0.0')} [{route.get('metric', 1)}]\n"
        return output or "No routes configured"
    
    elif sub_cmd == 'version':
        hostname = device.get('config', {}).get('hostname', 'Device')
        device_type = device.get('type', 'router')
        return f"""
Device: {device_type}
Hostname: {hostname}
OS Version: NetworkOS 2.0
Uptime: 0 days, 0 hours, 0 minutes
        """.strip()
    
    elif sub_cmd == 'running-config':
        return generate_running_config(device)
    
    else:
        return f"% Invalid show command: {' '.join(args)}"


def handle_ping_command(args):
    """Handle ping command"""
    if not args:
        return "% Usage: ping <ip-address>"
    
    target = args[0]
    
    return f"""
PING {target}: 56 data bytes
64 bytes from {target}: icmp_seq=0 ttl=64 time=1.234 ms
64 bytes from {target}: icmp_seq=1 ttl=64 time=1.156 ms
64 bytes from {target}: icmp_seq=2 ttl=64 time=1.089 ms

--- {target} ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
    """.strip()


def get_help_text(device_type):
    """Get help text for device type"""
    return """
Available Commands:
  help                   - Show this help
  show <option>          - Display information
    interfaces           - Show interface configuration
    ip route            - Show routing table
    version             - Show device version
    running-config      - Show running configuration
  ping <ip>              - Test connectivity
  config                 - Enter configuration mode
  exit                   - Exit CLI
    """.strip()


def generate_running_config(device):
    """Generate running configuration"""
    config = device.get('config', {})
    interfaces = device.get('interfaces', {})
    
    output = "!\n! Running configuration\n!\n"
    
    hostname = config.get('hostname', 'Device')
    output += f"hostname {hostname}\n!\n"
    
    # Interfaces
    for name, iface in interfaces.items():
        output += f"interface {name}\n"
        if iface.get('ipAddress') and iface['ipAddress'] != 'dhcp':
            output += f" ip address {iface['ipAddress']} {iface.get('subnetMask', '255.255.255.0')}\n"
        if iface.get('status') == 'up':
            output += " no shutdown\n"
        else:
            output += " shutdown\n"
        output += "!\n"
    
    # Routes
    routes = config.get('routingTable', [])
    for route in routes:
        output += f"ip route {route.get('network', '0.0.0.0')} "
        output += f"{route.get('mask', '0.0.0.0')} {route.get('gateway', '0.0.0.0')}\n"
    
    output += "!\nend\n"
    return output


def update_configuration_progress(simulation_id, device_id, config):
    """Update progress when device is configured"""
    # Implementation depends on your progress tracking system
    logger.info(f"Configuration progress updated for device {device_id} in simulation {simulation_id}")


def update_device_add_progress(simulation_id, device_id, device_type):
    """Update progress when device is added"""
    logger.info(f"Device add progress updated for {device_type} {device_id} in simulation {simulation_id}")


def update_connection_progress(simulation_id, connection_id, connection_type):
    """Update progress when connection is created"""
    logger.info(f"Connection progress updated for {connection_type} connection {connection_id} in simulation {simulation_id}")


def update_validation_progress(simulation_id, validation_result):
    """Update progress when simulation is validated"""
    logger.info(f"Validation progress updated for simulation {simulation_id}")


# Register blueprint
def register_enhanced_simulation_api(app):
    """Register the enhanced simulation API blueprint"""
    app.register_blueprint(enhanced_simulation_api, url_prefix='/dynamic')
    logger.info("Enhanced simulation API registered")
