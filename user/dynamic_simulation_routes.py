"""
Dynamic Simulation Routes Generator
Automatically creates routes for instructor-created simulations - Learning Paths feature removed
"""

from flask import Blueprint, render_template, session, request, jsonify, redirect, url_for, flash, current_app
from user.models.user import User as UserModel
from user.models.score import Score
from instructor.models.simulation import Simulation, SimulationAttempt
from instructor.models.class_model import Class
# Learning Path models removed - import stubs to prevent errors
from instructor.models.learning_path import LearningPath, LearningPathSimulation, UserLearningProgress
from instructor.models.simulation_assignment import SimulationAssignment
from instructor.services.assignment_service import assignment_service
from __init__ import db
from functools import wraps
import json
import re
from datetime import datetime

# Import login_required from proper location
def login_required(f):
    """Login required decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

# Enhanced validation functions for network simulations
def validate_network_configuration(network_state, expected_config):
    """Enhanced network device configuration validation"""
    errors = []
    # Normalize structures
    actual_devices = {}
    # network_state may be { devices: [ {id|name|label, type, config, ...}, ... ] } or a dict
    devices = []
    if isinstance(network_state, dict):
        devices = network_state.get('devices') or network_state.get('networkDevices') or []
    elif isinstance(network_state, list):
        devices = network_state

    for d in devices:
        name = d.get('name') or d.get('label') or d.get('id')
        if name:
            actual_devices[str(name)] = d

    # expected_config format:
    # { devices: { "<DeviceName>": { ip, subnet, gateway, interfaces: { intf: { ip }, ... }, wireless: { ssid, psk } } } }
    exp_devices = {}
    if isinstance(expected_config, dict):
        exp_devices = expected_config.get('devices') or expected_config.get('expected_devices') or {}

    # Validate each expected device
    for exp_name, exp in exp_devices.items():
        actual = actual_devices.get(str(exp_name))
        if not actual:
            errors.append(f"Missing device: {exp_name}")
            continue

        a_cfg = actual.get('config') or {
            # allow top-level fallbacks commonly used on the canvas
            'ip': actual.get('ipv4') or actual.get('ip'),
            'subnet': actual.get('subnet'),
            'gateway': actual.get('gateway'),
            'interfaces': actual.get('interfaces') or {}
        }

        # 1) Simple endpoint config (PC/Printer)
        if 'ip' in exp:
            act_ip = (a_cfg.get('ip') or a_cfg.get('ip_address') or actual.get('ipv4') or '').strip()
            if act_ip.lower() != str(exp['ip']).strip().lower():
                errors.append(f"{exp_name}: expected IP {exp['ip']}, got {act_ip or 'unset'}")

        if 'subnet' in exp:
            act_mask = (a_cfg.get('subnet') or a_cfg.get('mask') or '').strip()
            if act_mask != str(exp['subnet']).strip():
                errors.append(f"{exp_name}: expected subnet {exp['subnet']}, got {act_mask or 'unset'}")

        if 'gateway' in exp:
            act_gw = (a_cfg.get('gateway') or a_cfg.get('default_gw') or '').strip()
            if act_gw != str(exp['gateway']).strip():
                errors.append(f"{exp_name}: expected gateway {exp['gateway']}, got {act_gw or 'unset'}")

        # 2) Router/Switch interface config
        if 'interfaces' in exp:
            act_ifaces = a_cfg.get('interfaces') or actual.get('interfaces') or {}
            for if_name, if_exp in exp['interfaces'].items():
                if if_name not in act_ifaces:
                    errors.append(f"{exp_name}: missing interface {if_name}")
                    continue
                act_if = act_ifaces.get(if_name) or {}
                exp_ip = if_exp.get('ip') or if_exp.get('ip_address')
                if exp_ip:
                    act_if_ip = (act_if.get('ip') or act_if.get('ip_address') or '').strip()
                    if act_if_ip.lower() != str(exp_ip).strip().lower():
                        errors.append(f"{exp_name} {if_name}: expected IP {exp_ip}, got {act_if_ip or 'unset'}")

                if 'status' in if_exp:
                    if (act_if.get('status') or '').lower() != str(if_exp['status']).lower():
                        errors.append(f"{exp_name} {if_name}: expected status {if_exp['status']}, got {act_if.get('status') or 'unset'}")

        # 3) Wireless/AP config
        if 'wireless' in exp:
            exp_wifi = exp['wireless'] or {}
            act_wifi = (a_cfg.get('wireless') or a_cfg.get('wifi') or {})
            if 'ssid' in exp_wifi:
                if (act_wifi.get('ssid') or '').strip() != str(exp_wifi['ssid']).strip():
                    errors.append(f"{exp_name}: expected SSID {exp_wifi['ssid']}, got {act_wifi.get('ssid') or 'unset'}")
            if 'psk' in exp_wifi:
                if (act_wifi.get('psk') or act_wifi.get('password') or '').strip() != str(exp_wifi['psk']).strip():
                    errors.append(f"{exp_name}: expected PSK set, got unset or different value")

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_single_device(device_id, actual_state, expected_config):
    """Validate a single device configuration"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'score': 100
    }
    
    # Check interfaces configuration
    if 'interfaces' in expected_config:
        actual_interfaces = actual_state.get('interfaces', {})
        for intf_name, intf_config in expected_config['interfaces'].items():
            if intf_name not in actual_interfaces:
                result['errors'].append(f'Device {device_id}: Interface {intf_name} not configured')
                result['valid'] = False
                result['score'] -= 20
                continue
            
            actual_intf = actual_interfaces[intf_name]
            
            # Check IP address
            if 'ip_address' in intf_config:
                expected_ip = intf_config['ip_address']
                actual_ip = actual_intf.get('ip_address')
                if actual_ip != expected_ip:
                    result['errors'].append(f'Device {device_id} {intf_name}: Expected IP {expected_ip}, got {actual_ip}')
                    result['valid'] = False
                    result['score'] -= 15
            
            # Check interface status
            if 'status' in intf_config:
                expected_status = intf_config['status']
                actual_status = actual_intf.get('status', 'down')
                if actual_status != expected_status:
                    result['errors'].append(f'Device {device_id} {intf_name}: Expected status {expected_status}, got {actual_status}')
                    result['valid'] = False
                    result['score'] -= 10
    
    # Check routing table for routers
    if 'routing_table' in expected_config:
        actual_routing = actual_state.get('routingTable', [])
        expected_routes = expected_config['routing_table']
        
        for expected_route in expected_routes:
            route_found = False
            for actual_route in actual_routing:
                if (actual_route.get('network') == expected_route.get('network') and
                    actual_route.get('gateway') == expected_route.get('gateway')):
                    route_found = True
                    break
            
            if not route_found:
                result['errors'].append(f'Device {device_id}: Missing route to {expected_route.get("network")}')
                result['valid'] = False
                result['score'] -= 15
    
    # Check VLAN configuration for switches
    if 'vlans' in expected_config:
        actual_vlans = actual_state.get('vlans', {})
        for vlan_id, vlan_config in expected_config['vlans'].items():
            if vlan_id not in actual_vlans:
                result['warnings'].append(f'Device {device_id}: VLAN {vlan_id} not configured')
                result['score'] -= 5
    
    return result

def validate_network_connectivity(network_state):
    """Validate network connectivity and topology"""
    result = {
        'valid': True,
        'warnings': []
    }
    
    try:
        devices = network_state.get('networkDevices', [])
        connections = network_state.get('networkConnections', [])
        
        # Find isolated devices
        connected_devices = set()
        for conn in connections:
            connected_devices.add(conn.get('from'))
            connected_devices.add(conn.get('to'))
        
        device_ids = {device.get('id') for device in devices}
        isolated_devices = device_ids - connected_devices
        
        if isolated_devices:
            result['warnings'].append(f'Isolated devices found: {list(isolated_devices)}')
        
        # Check for network segments
        segments = analyze_network_segments(devices, connections)
        if len(segments) > 1:
            result['warnings'].append(f'Network has {len(segments)} isolated segments')
    
    except Exception as e:
        result['warnings'].append(f'Connectivity analysis error: {str(e)}')
    
    return result

def validate_ip_addressing(network_state):
    """Validate IP addressing scheme"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    try:
        device_states = network_state.get('deviceStates', {})
        used_ips = set()
        networks = {}
        
        for device_id, device_state in device_states.items():
            interfaces = device_state.get('interfaces', {})
            for intf_name, intf_config in interfaces.items():
                ip_address = intf_config.get('ip_address')
                if not ip_address:
                    continue
                
                # Parse IP and mask
                if ' ' in ip_address:
                    ip, mask = ip_address.split(' ')
                else:
                    ip = ip_address
                    mask = '255.255.255.0'
                
                # Check for duplicate IPs
                if ip in used_ips:
                    result['errors'].append(f'Duplicate IP address: {ip}')
                    result['valid'] = False
                else:
                    used_ips.add(ip)
                
                # Analyze network addressing
                network_addr = get_network_address(ip, mask)
                if network_addr not in networks:
                    networks[network_addr] = []
                networks[network_addr].append({
                    'device': device_id,
                    'interface': intf_name,
                    'ip': ip
                })
        
        # Check network consistency
        for network, addresses in networks.items():
            if len(addresses) == 1:
                result['warnings'].append(f'Network {network} has only one device')
    
    except Exception as e:
        result['errors'].append(f'IP addressing validation error: {str(e)}')
        result['valid'] = False
    
    return result

def analyze_network_segments(devices, connections):
    """Analyze network topology to find isolated segments"""
    device_ids = {device.get('id') for device in devices}
    visited = set()
    segments = []
    
    for device_id in device_ids:
        if device_id not in visited:
            segment = explore_segment(device_id, connections, visited)
            if segment:
                segments.append(segment)
    
    return segments

def explore_segment(start_device, connections, visited):
    """Explore a network segment using DFS"""
    segment = []
    stack = [start_device]
    
    while stack:
        device_id = stack.pop()
        if device_id in visited:
            continue
        
        visited.add(device_id)
        segment.append(device_id)
        
        # Add connected devices
        for conn in connections:
            if conn.get('from') == device_id and conn.get('to') not in visited:
                stack.append(conn.get('to'))
            elif conn.get('to') == device_id and conn.get('from') not in visited:
                stack.append(conn.get('from'))
    
    return segment

def get_network_address(ip, mask):
    """Calculate network address from IP and subnet mask"""
    try:
        ip_parts = list(map(int, ip.split('.')))
        mask_parts = list(map(int, mask.split('.')))
        
        network_parts = [ip_parts[i] & mask_parts[i] for i in range(4)]
        return '.'.join(map(str, network_parts))
    except:
        return ip  # Return original IP if calculation fails

def validate_network_connectivity_old(network_state, expected_config):
    """Legacy connectivity validation function"""
    if not network_state or not expected_config:
        return False
    
    try:
        device_states = network_state.get('deviceStates', {})
        
        for device_id, expected in expected_config.items():
            if device_id not in device_states:
                return False
            
            actual = device_states[device_id]
            
            # Check interfaces configuration
            if 'interfaces' in expected:
                actual_interfaces = actual.get('interfaces', {})
                for intf_name, intf_config in expected['interfaces'].items():
                    if intf_name not in actual_interfaces:
                        return False
                    
                    actual_intf = actual_interfaces[intf_name]
                    
                    # Check IP address
                    if 'ip' in intf_config and actual_intf.get('ip') != intf_config['ip']:
                        return False
                    
                    # Check subnet mask
                    if 'mask' in intf_config and actual_intf.get('mask') != intf_config['mask']:
                        return False
            
            # Check routing table
            if 'routes' in expected:
                actual_routes = actual.get('routingTable', [])
                for expected_route in expected['routes']:
                    route_found = any(
                        route.get('network') == expected_route.get('network') and
                        route.get('gateway') == expected_route.get('gateway')
                        for route in actual_routes
                    )
                    if not route_found:
                        return False
        
        return True
        
    except (KeyError, AttributeError, TypeError) as e:
        print(f"Network configuration validation error: {e}")
        return False

def validate_network_connectivity(topology, expected_topology):
    """Validate network topology connections"""
    if not topology or not expected_topology:
        return False
    
    try:
        actual_connections = set()
        expected_connections = set()
        
        # Normalize actual connections
        for conn in topology.get('connections', []):
            if isinstance(conn, list) and len(conn) >= 2:
                # Create bidirectional connection tuple (sorted for consistency)
                connection = tuple(sorted([conn[0], conn[1]]))
                actual_connections.add(connection)
            elif isinstance(conn, dict) and 'from' in conn and 'to' in conn:
                connection = tuple(sorted([conn['from'], conn['to']]))
                actual_connections.add(connection)
        
        # Normalize expected connections
        for conn in expected_topology.get('connections', []):
            if isinstance(conn, list) and len(conn) >= 2:
                connection = tuple(sorted([conn[0], conn[1]]))
                expected_connections.add(connection)
            elif isinstance(conn, dict) and 'from' in conn and 'to' in conn:
                connection = tuple(sorted([conn['from'], conn['to']]))
                expected_connections.add(connection)
        
        # Check if all expected connections exist
        return expected_connections.issubset(actual_connections)
        
    except (KeyError, AttributeError, TypeError) as e:
        print(f"Network connectivity validation error: {e}")
        return False

def validate_cli_output(cli_output, expected_patterns):
    """Validate CLI command output against expected patterns"""
    if not cli_output or not expected_patterns:
        return False
    
    try:
        for pattern_config in expected_patterns:
            if isinstance(pattern_config, str):
                # Simple string contains check
                if pattern_config.lower() not in cli_output.lower():
                    return False
            elif isinstance(pattern_config, dict):
                pattern = pattern_config.get('pattern', '')
                match_type = pattern_config.get('type', 'contains')
                
                if match_type == 'regex':
                    if not re.search(pattern, cli_output, re.IGNORECASE):
                        return False
                elif match_type == 'contains':
                    if pattern.lower() not in cli_output.lower():
                        return False
                elif match_type == 'exact':
                    if cli_output.strip().lower() != pattern.lower():
                        return False
        
        return True
        
    except (re.error, KeyError, AttributeError, TypeError) as e:
        print(f"CLI output validation error: {e}")
        return False

# Create dynamic blueprint
dynamic_sim_bp = Blueprint('dynamic_simulations', __name__, url_prefix='/dynamic')

# Feature flag for Learning Paths visibility on user side
LEARNING_PATHS_ENABLED = False

def user_login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_from_session():
    """Get current user from session"""
    if 'user_id' in session:
        return UserModel.query.get(session['user_id'])
    return None

def validate_topology_data(topology):
    """Validate topology structure and return validation result with enhanced MVP schema support"""
    validation_result = {
        'isValid': True,
        'errors': [],
        'warnings': []
    }
    
    if not isinstance(topology, dict):
        validation_result['isValid'] = False
        validation_result['errors'].append("Topology must be an object")
        return validation_result
    
    devices = topology.get('devices', [])
    connections = topology.get('connections', [])
    
    if not isinstance(devices, list):
        validation_result['isValid'] = False
        validation_result['errors'].append("Devices must be an array")
        return validation_result
        
    if not isinstance(connections, list):
        validation_result['isValid'] = False
        validation_result['errors'].append("Connections must be an array")
        return validation_result
    
    # Validate device structure with enhanced MVP schema
    device_ids = set()
    valid_device_types = {'pc', 'switch', 'router', 'server', 'hub', 'firewall', 'printer', 'wireless-ap'}
    
    for i, device in enumerate(devices):
        if not isinstance(device, dict):
            validation_result['errors'].append(f"Device {i} must be an object")
            validation_result['isValid'] = False
            continue
            
        device_id = device.get('id')
        if not device_id:
            validation_result['errors'].append(f"Device {i} must have an id")
            validation_result['isValid'] = False
            continue
            
        if device_id in device_ids:
            validation_result['errors'].append(f"Duplicate device id: {device_id}")
            validation_result['isValid'] = False
        device_ids.add(device_id)
        
        # Validate device type
        device_type = device.get('type')
        if not device_type:
            validation_result['errors'].append(f"Device {device_id} must have a type")
            validation_result['isValid'] = False
        elif device_type not in valid_device_types:
            validation_result['warnings'].append(f"Device {device_id} has uncommon type: {device_type}")
            
        # Validate optional fields
        if 'interfaces' in device:
            interfaces = device['interfaces']
            if not isinstance(interfaces, list):
                validation_result['warnings'].append(f"Device {device_id} interfaces should be an array")
            else:
                for j, interface in enumerate(interfaces):
                    if not isinstance(interface, dict):
                        validation_result['warnings'].append(f"Device {device_id} interface {j} should be an object")
                    elif not interface.get('name'):
                        validation_result['warnings'].append(f"Device {device_id} interface {j} should have a name")
        
        # Validate IP address format
        if 'ip' in device:
            ip = device['ip']
            if not isinstance(ip, str) or not _is_valid_ip(ip):
                validation_result['warnings'].append(f"Device {device_id} has invalid IP address: {ip}")
        
        # Validate position
        if 'position' in device:
            position = device['position']
            if not isinstance(position, dict):
                validation_result['warnings'].append(f"Device {device_id} position should be an object")
            elif not all(isinstance(position.get(coord), (int, float)) for coord in ['x', 'y']):
                validation_result['warnings'].append(f"Device {device_id} position should have numeric x and y coordinates")
    
    # Validate connections structure with enhanced MVP schema
    for i, connection in enumerate(connections):
        if not isinstance(connection, dict):
            validation_result['errors'].append(f"Connection {i} must be an object")
            validation_result['isValid'] = False
            continue
            
        # Support both object format {from: {deviceId, port}, to: {deviceId, port}} and legacy formats
        from_device = None
        to_device = None
        
        if 'from' in connection and 'to' in connection:
            # MVP format
            from_spec = connection['from']
            to_spec = connection['to']
            
            if isinstance(from_spec, dict):
                from_device = from_spec.get('deviceId')
                from_port = from_spec.get('port')
            else:
                from_device = from_spec
                from_port = None
                
            if isinstance(to_spec, dict):
                to_device = to_spec.get('deviceId')
                to_port = to_spec.get('port')
            else:
                to_device = to_spec
                to_port = None
                
        elif 'device1' in connection and 'device2' in connection:
            # Legacy format
            from_device = connection['device1']
            to_device = connection['device2']
            
        if not from_device or not to_device:
            validation_result['errors'].append(f"Connection {i} must specify both from and to devices")
            validation_result['isValid'] = False
            continue
            
        # Validate device references
        if from_device not in device_ids:
            validation_result['warnings'].append(f"Connection {i} references unknown device: {from_device}")
        if to_device not in device_ids:
            validation_result['warnings'].append(f"Connection {i} references unknown device: {to_device}")
        if from_device == to_device:
            validation_result['warnings'].append(f"Connection {i} connects device to itself: {from_device}")
            
        # Validate cable type
        if 'cable' in connection:
            cable = connection['cable']
            valid_cables = {'copper', 'fiber', 'ethernet', 'serial', 'console'}
            if cable not in valid_cables:
                validation_result['warnings'].append(f"Connection {i} has uncommon cable type: {cable}")
    
    return validation_result

def _is_valid_ip(ip):
    """Helper function to validate IP address format"""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    except (ValueError, AttributeError):
        return False

class DynamicSimulationController:
    """Controller for handling dynamic simulations and learning paths"""
    
    @staticmethod
    def get_user_class_simulations(user_id):
        """Get simulations available to user based on their class"""
        try:
            user = UserModel.query.get(user_id)
            if not user:
                return []
            
            # Get user's enrolled classes
            user_classes = user.enrolled_classes.all()
            if not user_classes:
                return []
            
            simulations = []
            
            # Get simulations for all enrolled classes
            for user_class in user_classes:
                class_level = user_class.name.lower()
                
                # Get published simulations for this class level
                if 'networking 1' in class_level:
                    class_simulations = Simulation.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).filter(
                        Simulation.simulation_type.ilike('%networking 1%')
                    ).all()
                elif 'networking 2' in class_level:
                    class_simulations = Simulation.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).filter(
                        Simulation.simulation_type.ilike('%networking 2%')
                    ).all()
                else:
                    class_simulations = Simulation.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).all()
                
                simulations.extend(class_simulations)
            
            # Remove duplicates
            unique_simulations = []
            seen_ids = set()
            for sim in simulations:
                if sim.id not in seen_ids:
                    unique_simulations.append(sim)
                    seen_ids.add(sim.id)
            
            return unique_simulations
            
        except Exception as e:
            print(f"Error getting user class simulations: {e}")
            return []
    
    @staticmethod
    def get_user_learning_paths(user_id):
        """Get learning paths available to user"""
        try:
            user = UserModel.query.get(user_id)
            if not user:
                return []
            
            # Get user's enrolled classes
            user_classes = user.enrolled_classes.all()
            if not user_classes:
                return []
            
            learning_paths = []
            
            # Get learning paths for all enrolled classes
            for user_class in user_classes:
                class_level = user_class.name.lower()
                
                # Get published learning paths for this class level
                if 'networking 1' in class_level:
                    class_paths = LearningPath.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).filter(
                        LearningPath.course_level.ilike('%networking 1%')
                    ).all()
                elif 'networking 2' in class_level:
                    class_paths = LearningPath.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).filter(
                        LearningPath.course_level.ilike('%networking 2%')
                    ).all()
                else:
                    class_paths = LearningPath.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).all()
                
                learning_paths.extend(class_paths)
            
            # Remove duplicates
            unique_paths = []
            seen_ids = set()
            for path in learning_paths:
                if path.id not in seen_ids:
                    unique_paths.append(path)
                    seen_ids.add(path.id)
            
            return unique_paths
            
        except Exception as e:
            print(f"Error getting user learning paths: {e}")
            return []
    
    @staticmethod
    def get_simulation_progress(user_id, simulation_id):
        """Get user's progress for a specific simulation (based on SimulationAttempt)"""
        try:
            attempts = SimulationAttempt.query.filter_by(
                user_id=user_id,
                simulation_id=simulation_id
            ).all()

            if attempts:
                latest = max(attempts, key=lambda a: a.started_at or a.id)
                best_score = max((a.total_score or 0 for a in attempts), default=0)
                status = 'completed' if any(a.is_completed for a in attempts) else 'in_progress'
                completion_pct = latest.completion_percentage if latest else 0
                return {
                    'status': status,
                    'attempts': len(attempts),
                    'best_score': best_score,
                    'completion_percentage': round(completion_pct, 2)
                }

            return {
                'status': 'not_started',
                'attempts': 0,
                'best_score': 0,
                'completion_percentage': 0
            }

        except Exception as e:
            print(f"Error getting simulation progress: {e}")
            return None
    
    @staticmethod
    def can_access_simulation(user_id, simulation_id):
        """Check if user can access a simulation (simplified without Learning Paths)"""
        try:
            simulation = Simulation.query.get(simulation_id)
            return bool(simulation and simulation.is_published and simulation.is_active)
        except Exception as e:
            print(f"Error checking simulation access: {e}")
            return False

# Route Handlers
@dynamic_sim_bp.route('/dashboard')
def simulations_dashboard():
    """Show user's available simulations dashboard"""
    user = get_user_from_session()
    category_filter = request.args.get('category')
    class_filter = request.args.get('class')  # New: allow filtering by specific class
    
    try:
        # Get user's enrolled classes
        user_classes = []
        selected_class = None
        
        if user:
            user_classes = user.enrolled_classes.all()
            
            # If user specified a class filter, use that
            if class_filter:
                selected_class = next((cls for cls in user_classes if str(cls.id) == class_filter), None)
            # If user is enrolled in only one class, use that
            elif len(user_classes) == 1:
                selected_class = user_classes[0]
            # If user is enrolled in multiple classes but no filter specified, default to first class
            elif len(user_classes) > 1:
                selected_class = user_classes[0]  # Could be made smarter by user preference
        
        # Get simulations and learning paths based on selected class
        if selected_class:
            class_level = selected_class.name.lower()  # Use class name instead of class_type
            
            # Filter simulations by selected class level
            if 'networking 1' in class_level:
                simulations = Simulation.query.filter_by(is_active=True, is_published=True).filter(
                    Simulation.simulation_type.ilike('%networking 1%')
                ).all()
                learning_paths = [] if not LEARNING_PATHS_ENABLED else LearningPath.query.filter_by(is_active=True, is_published=True).filter(
                    LearningPath.course_level.ilike('%networking 1%')
                ).all()
            elif 'networking 2' in class_level:
                simulations = Simulation.query.filter_by(is_active=True, is_published=True).filter(
                    Simulation.simulation_type.ilike('%networking 2%')
                ).all()
                learning_paths = [] if not LEARNING_PATHS_ENABLED else LearningPath.query.filter_by(is_active=True, is_published=True).filter(
                    LearningPath.course_level.ilike('%networking 2%')
                ).all()
            else:
                # For other class types, show all simulations
                simulations = Simulation.query.filter_by(is_active=True, is_published=True).all()
                learning_paths = [] if not LEARNING_PATHS_ENABLED else LearningPath.query.filter_by(is_active=True, is_published=True).all()
        else:
            # If no class assigned, show all simulations
            simulations = Simulation.query.filter_by(is_active=True, is_published=True).all()
            learning_paths = [] if not LEARNING_PATHS_ENABLED else LearningPath.query.filter_by(is_active=True, is_published=True).all()
        
        # Apply additional category filter if provided
        if category_filter:
            # Handle special cases for networking1/networking2 filters
            if category_filter.lower() == 'networking1':
                simulations = [sim for sim in simulations if sim.simulation_type == 'Networking 1']
                learning_paths = [path for path in learning_paths if 'networking 1' in path.course_level.lower()]
            elif category_filter.lower() == 'networking2':
                simulations = [sim for sim in simulations if sim.simulation_type == 'Networking 2']
                learning_paths = [path for path in learning_paths if 'networking 2' in path.course_level.lower()]
            else:
                # Regular category filter
                simulations = [sim for sim in simulations if category_filter.lower() in (sim.category or '').lower()]
        
        # Group simulations by category
        simulations_by_category = {}
        
        for sim in simulations:
            category = sim.category or 'General'
            
            if category not in simulations_by_category:
                simulations_by_category[category] = []
            
            sim_data = {
                'simulation': {
                    'id': sim.id,
                    'title': sim.title,
                    'description': sim.description or '',
                    'difficulty': sim.difficulty or 'Beginner',
                    'estimated_duration': sim.estimated_duration or 30,
                    'simulation_type': sim.simulation_type or 'General',
                    'category': sim.category or 'General'
                },
                'can_access': True,
                'progress': {
                    'status': 'not_started',
                    'completion_percentage': 0,
                    'attempts': 0,
                    'best_score': 0
                }
            }
            
            simulations_by_category[category].append(sim_data)
        
        # Process learning paths
        learning_paths_data = []
        for path in (learning_paths if LEARNING_PATHS_ENABLED else []):
            # Get actual simulation count for this path
            simulation_count = path.simulation_count
            
            # Get user progress if user is logged in
            user_progress = {
                'completion_percentage': 0,
                'completed_count': 0,
                'in_progress_count': 0,
                'not_started_count': simulation_count
            }
            
            if user and user.id:
                user_progress = path.calculate_user_progress(user.id)
            
            path_data = {
                'path': {
                    'id': path.id,
                    'title': path.title,
                    'description': path.description or '',
                    'course_level': path.course_level,
                    'difficulty': getattr(path, 'difficulty_level', 'Beginner')
                },
                'category': path.course_level,
                'difficulty': getattr(path, 'difficulty_level', 'Beginner'),
                'estimated_duration': getattr(path, 'estimated_total_duration', 0),
                'simulation_count': simulation_count,
                'total_simulations': simulation_count,
                'progress': user_progress
            }
            learning_paths_data.append(path_data)
        
        # Prepare dashboard data
        dashboard_data = {
            'simulations_by_category': simulations_by_category,
            'learning_paths': learning_paths_data,
            'recent_attempts': [],
            'user_stats': {
                'total_simulations_available': len(simulations),
                'total_learning_paths_available': len(learning_paths),
                'total_attempts': 0,
                'completed_simulations': 0
            }
        }
        
        return render_template('user/dynamic_simulations_dashboard.html',
                             user=user,
                             dashboard_data=dashboard_data,
                             user_classes=user_classes,
                             selected_class=selected_class)
    
    except Exception as e:
        # Log the error and return empty data
        print(f"Dashboard Error: {e}")
        dashboard_data = {
            'simulations_by_category': {},
            'learning_paths': [],
            'recent_attempts': [],
            'user_stats': {
                'total_simulations_available': 0,
                'total_learning_paths_available': 0,
                'total_attempts': 0,
                'completed_simulations': 0
            }
        }
        return render_template('user/dynamic_simulations_dashboard.html',
                             user=user,
                             dashboard_data=dashboard_data,
                             user_classes=[],
                             selected_class=None)

@dynamic_sim_bp.route('/my-simulations', endpoint='my_simulations')
@user_login_required
def my_simulations():
    """Show user's available simulations"""
    user = get_user_from_session()
    controller = DynamicSimulationController()
    
    try:
        # Get user's simulations
        simulations = controller.get_user_class_simulations(user.id)
        
        # Get progress for each simulation
        simulation_data = []
        for sim in simulations:
            progress = controller.get_simulation_progress(user.id, sim.id)
            can_access = controller.can_access_simulation(user.id, sim.id)
            
            simulation_data.append({
                'simulation': sim,
                'progress': progress,
                'can_access': can_access
            })
        
        return render_template('user/my_simulations.html',
                             user=user,
                             simulations=simulation_data)
    
    except Exception as e:
        print(f"Error in my_simulations: {e}")
        flash(f'Error loading simulations: {str(e)}', 'error')
        return render_template('user/my_simulations.html',
                             user=user,
                             simulations=[])

@dynamic_sim_bp.route('/simulation/<int:simulation_id>/tutorial', methods=['GET'])
def get_simulation_tutorial(simulation_id):
    """Get tutorial content for popup display (no auth required for flexibility)"""
    print(f"🔍 TUTORIAL ROUTE CALLED! simulation_id={simulation_id}")
    try:
        # Try to import Tutorial model - handle gracefully if it doesn't exist
        try:
            from instructor.models.tutorial_system import Tutorial
            # Get tutorial data for the simulation
            tutorial = Tutorial.query.filter_by(simulation_id=simulation_id).first()
            
            if tutorial and tutorial.steps:
                # Return tutorial data in a format suitable for popup display
                tutorial_data = tutorial.to_dict()
                
                return jsonify({
                    'success': True,
                    'tutorial': tutorial_data
                })
        except ImportError:
            print(f"Tutorial system not available - using fallback for simulation {simulation_id}")
        except Exception as e:
            print(f"Error loading tutorial from database: {e}")
        
        # Fallback - return empty tutorial structure
        return jsonify({
            'success': True,
            'tutorial': {
                'id': None,
                'title': 'Tutorial Not Available',
                'steps': [{
                    'step_type': 'text',
                    'content': 'No tutorial has been created for this simulation yet.',
                    'order_index': 1
                }]
            }
        })
        
    except Exception as e:
        print(f"Error getting tutorial for simulation {simulation_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_sim_bp.route('/simulation/<int:simulation_id>')
@user_login_required
def run_simulation(simulation_id):
    """Run a specific simulation"""
    user = get_user_from_session()
    
    try:
        # Get simulation from database
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Parse simulation data with proper type handling
        simulation_config = simulation.simulation_config or {}
        if isinstance(simulation_config, str):
            try:
                import json
                simulation_config = json.loads(simulation_config)
            except Exception:
                simulation_config = {}

        step_definitions = simulation.step_definitions or []
        if isinstance(step_definitions, str):
            try:
                import json
                step_definitions = json.loads(step_definitions)
            except Exception:
                step_definitions = []

        validation_rules = simulation.validation_rules or {}
        if isinstance(validation_rules, str):
            try:
                import json
                validation_rules = json.loads(validation_rules)
            except Exception:
                validation_rules = {}
        
        # Ensure step_definitions is a list
        if not isinstance(step_definitions, list):
            step_definitions = []

        # Normalize steps to UI schema with troubleshooting support
        normalized_steps = []
        for step in step_definitions:
            s = dict(step) if isinstance(step, dict) else {'content': str(step)}
            
            # Builder field normalization
            if 'questionText' in s and 'question_text' not in s:
                s['question_text'] = s.get('questionText')
            if 'questionType' in s and 'question_type' not in s:
                s['question_type'] = s.get('questionType')
                
            # Troubleshooting-specific field mappings
            if 'instruction' in s and 'question_text' not in s:
                s['question_text'] = s.get('instruction')
            if 'description' in s and 'content' not in s:
                s['content'] = s.get('description')
                
            # Handle troubleshooting step types
            step_type = s.get('type', 'instruction')
            if step_type in ['content_review', 'multiple_choice', 'text_input']:
                s['troubleshooting_type'] = step_type
                # Map to compatible user interface types
                if step_type == 'content_review':
                    s['type'] = 'instruction'
                elif step_type == 'multiple_choice':
                    s['type'] = 'question'
                    s['question_type'] = 'multiple_choice'
                elif step_type == 'text_input':
                    s['type'] = 'question'
                    s['question_type'] = 'text'
                    
            # Validation mapping (inline)
            v = s.get('validation') or {}
            if isinstance(v, dict):
                if 'expectedAnswer' in v and 'expected_answer' not in s:
                    s['expected_answer'] = v.get('expectedAnswer')
                if 'score' in v and 'score' not in s:
                    s['score'] = v.get('score')
                # Handle troubleshooting validation types
                if v.get('type') in ['completion', 'contains']:
                    s['validation_type'] = v.get('type')
                    
            # Handle max_score from troubleshooting editor
            if 'max_score' in s and 'score' not in s:
                s['score'] = s.get('max_score')
                
            # Ensure options are an array
            if 'options' in s and isinstance(s['options'], list):
                # leave as-is (template handles both string or {text,value})
                pass
            normalized_steps.append(s)

        # Build validation dict keyed by step index (string keys)
        validation = {}
        if isinstance(validation_rules, dict):
            for k, v in validation_rules.items():
                validation[str(k)] = v
        # Generate simple rules from steps if missing
        if not validation and normalized_steps:
            for idx, s in enumerate(normalized_steps):
                if 'expected_answer' in s and s['expected_answer']:
                    validation[str(idx)] = {
                        'type': 'exact_match',
                        'expected_answer': s['expected_answer'],
                        'score': s.get('score', 10)
                    }

        # Enhanced topology mapping with fallback support
        network_topology = simulation_config.get('network_topology', {})
        topology_config = simulation_config.get('topology_config', {})
        selected_topology = simulation_config.get('selected_topology', '')
        topology_requirements = simulation_config.get('topology_requirements', {})
        topology_enabled = simulation_config.get('topology_enabled', False)
        
        # CRITICAL FIX: Always prioritize network_topology to match admin edit page
        # The admin edit page uses simulation_config.network_topology.devices exclusively
        # We need to ensure dynamic simulation uses the same source for consistency
        if network_topology and (network_topology.get('devices') or network_topology.get('connections')):
            # Use the canonical network topology structure (SAME as admin edit page)
            simulation_topology = network_topology
            print(f"DEBUG [USER ROUTE CONSISTENCY]: Using network_topology with {len(network_topology.get('devices', []))} devices (matches admin)")
        else:
            # Fallback to legacy root-level fields only if network_topology is completely empty
            simulation_topology = simulation_config
            print(f"DEBUG [USER ROUTE CONSISTENCY]: Using simulation_config fallback with {len(simulation_config.get('devices', []))} devices")
        
        # Check lobby participation
        lobby_id = request.args.get('lobby_id')
        lobby = None
        team_assignment = None
        
        if lobby_id:
            # Check if user is in this lobby
            from services.troubleshooting_lobbies import lobby_manager
            from instructor.models.collaboration import CollaborationLobby, TeamAssignment
            
            # Get lobby from memory first
            lobby = lobby_manager.get_lobby(lobby_id)
            if not lobby:
                # Try to restore from database
                db_lobby = CollaborationLobby.query.get(lobby_id)
                if db_lobby and db_lobby.is_active:
                    # Restore lobby to memory (simplified restoration)
                    lobby_config = {
                        'name': db_lobby.name,
                        'scenario_type': db_lobby.scenario_type,
                        'scenario_id': db_lobby.scenario_id,
                        'max_participants': db_lobby.max_participants,
                        'class_id': db_lobby.class_id,
                        'simulation_id': db_lobby.simulation_id,
                        'instructor_created': True
                    }
                    lobby = lobby_manager.create_lobby(
                        creator_id=db_lobby.creator_id,
                        creator_name=db_lobby.creator_name,
                        creator_profile_image=db_lobby.creator_profile_image,
                        lobby_config=lobby_config,
                        lobby_id=lobby_id
                    )
                    print(f"DEBUG: Restored lobby {lobby_id} from database for user simulation")
                else:
                    print(f"DEBUG: Could not find or restore lobby {lobby_id} from database")
            else:
                print(f"DEBUG: Found existing lobby {lobby_id} in memory")
            
            # Check team assignment
            if lobby:
                # Look for team assignment where user is a member
                team_assignments = TeamAssignment.query.filter_by(
                    lobby_id=lobby_id,
                    is_active=True
                ).all()
                
                # Find assignment where user is in team_members
                team_assignment = None
                for assignment in team_assignments:
                    if assignment.team_members and str(user.id) in [str(member_id) for member_id in assignment.team_members]:
                        team_assignment = assignment
                        break
                
                if not team_assignment:
                    print(f"DEBUG: No team assignment found for user {user.id} in lobby {lobby_id}")
                else:
                    print(f"DEBUG: Found team assignment '{team_assignment.team_name}' for user {user.id} in lobby {lobby_id}")
            else:
                print(f"WARNING: Lobby {lobby_id} not found, collaboration session will not be inherited")
        
        # Import collaboration model and get settings
        from instructor.models.collaboration import CollaborationSetting
        
        # Get collaboration settings
        collaboration_setting = CollaborationSetting.query.filter_by(simulation_id=simulation_id).first()

        # Check if user has access to this simulation - now with proper import
        from instructor.models.simulation import SimulationAttempt
        from instructor.models.class_model import Class
        from flask_login import current_user
        from flask import url_for
        
        user_class_ids = [class_obj.id for class_obj in user.enrolled_classes.all()]
        simulation_class_ids = [assignment.class_id for assignment in simulation.class_assignments]
        
        if not any(class_id in user_class_ids for class_id in simulation_class_ids):
            flash('You do not have access to this simulation.', 'error')
            return redirect(url_for('user.dashboard'))
        
        # Get user progress for this simulation
        progress_model = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id
        ).first()
        
        if not progress_model:
            # Create initial progress
            progress_model = SimulationAttempt(
                user_id=user.id,
                simulation_id=simulation_id,
                current_step=1,
                total_score=0,
                is_completed=False
            )
            db.session.add(progress_model)
            db.session.commit()
        
        # Debug logging for device count investigation
        debug_file_path = r'c:\Users\gilbe\OneDrive\Desktop\RiddleNet\user_debug.txt'
        try:
            device_count = len(simulation_topology.get('devices', [])) if simulation_topology else 0
            debug_msg = f"DEBUG [USER SIMULATION {simulation_id}]: Device count = {device_count}\n"
            debug_msg += f"DEBUG [USER SIMULATION {simulation_id}]: Topology source = {'network_topology' if network_topology and (network_topology.get('devices') or network_topology.get('connections')) else 'simulation_config fallback'}\n"
            if simulation_topology and 'devices' in simulation_topology:
                device_types = [d.get('type', 'unknown') for d in simulation_topology['devices']]
                debug_msg += f"DEBUG [USER SIMULATION {simulation_id}]: Device types = {device_types}\n"
            
            print("USER ROUTE DEBUG:")
            print(debug_msg)
            print("=" * 80)  # Separator to make it stand out
            
            # Also log to file for easier debugging
            with open(debug_file_path, 'w', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()}: USER ROUTE\n")
                f.write(debug_msg + "\n")
                f.write("=" * 50 + "\n")
                
            # Also use Flask logger
            current_app.logger.info(debug_msg)
        except Exception as e:
            error_msg = f"DEBUG [USER SIMULATION {simulation_id}]: Error logging device info: {e}"
            print("USER ROUTE ERROR:")
            print(error_msg)
            try:
                with open(debug_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"{datetime.now().isoformat()}: USER ERROR: {error_msg}\n")
            except Exception as e2:
                print(f"Could not write error to file: {e2}")
            
        # Add task mode configuration
        task_mode = simulation_config.get('task_mode', 'combined')  # 'topology', 'configuration', 'combined'
        topology_locked = task_mode in ['configuration']  # Lock topology if config-only mode
        configuration_enabled = task_mode in ['configuration', 'combined']
        
        # Prepare simulation data for the template with troubleshooting support
        simulation_data = {
            'id': simulation.id,
            'title': simulation.title,
            'description': simulation.description,
            'simulation_type': simulation.simulation_type,
            'category': simulation.category,
            'difficulty': simulation.difficulty,
            'estimated_duration': simulation.estimated_duration,
            'learning_objectives': simulation.learning_objectives if isinstance(simulation.learning_objectives, list) else [],
            
            # Process scenario steps
            'step_definitions': normalized_steps,
            'validation': validation,
            'topology': simulation_topology,
            'simulation_config': simulation_config,  # Include full config for backward compatibility
            
            # Task mode configuration
            'task_mode': task_mode,
            'topology_locked': topology_locked,
            'configuration_enabled': configuration_enabled,
            'instructor_provided_topology': simulation_config.get('instructor_topology', {}),
            'device_config_templates': simulation_config.get('device_templates', {}),
            
            # Troubleshooting-specific data
            'is_troubleshooting': simulation_config.get('use_troubleshoot_template', False),
            'canvas_enabled': simulation_config.get('canvas_enabled', False),
            'live_scoring': simulation_config.get('live_scoring', True),
            'lesson_key': simulation_config.get('lesson_key'),
            'source_content': simulation_config.get('source_content'),

            # Topology configuration for network simulations
            'topology_enabled': topology_enabled,
            'selected_topology': selected_topology,
            'topology_config': topology_config,
            'topology_requirements': topology_requirements,
            'available_topologies': [],  # Will be populated if topology_enabled is True

            # New structured authoring blocks (safe defaults)
            'collab': simulation_config.get('collab') or {
                'mode': 'Solo',
                'enabled': False,
                'teamSize': 0,
                'sharedTerminal': False,
                'individualTerminals': True,
                'followLeader': False,
                'roles': ['Leader', 'Observer', 'Operator'],
                'chatEnabled': False,
                'transcriptLogging': False,
                'roomPolicy': {
                    'allowLateJoin': True,
                    'requireInstructor': False,
                    'timeWindow': None
                }
            },
            'tutorial': simulation_config.get('tutorial') or {
                'positions': {},  # { stepId: {anchor: '#selector', offset:{x,y}, breakpoints:{}} }
                'steps': []
            },
            'scoring': simulation_config.get('scoring') or {
                'base': getattr(simulation, 'base_score', None) or 100,
                'timeBonus': getattr(simulation, 'time_bonus', None) or 0,
                'wrongCommandPenalty': 0,
                'comboMultiplier': 1.0,
                'leaderboard': {'class': True, 'global': False, 'anonymize': False}
            },
            'achievements': simulation_config.get('achievements') or {
                'noHintRun': False,
                'underTime': False,
                'perfectCommands': False,
                'custom': []
            },
            'cli_rules': simulation_config.get('cli_rules') or {},
            
            # Default values for new fields
            'total_steps': len(normalized_steps),
            'base_score': simulation.base_score or 100,
            'time_bonus': simulation.time_bonus or 20,
            'perfect_completion_bonus': simulation.perfect_completion_bonus or 30
        }
        
        # Load available topologies if topology is enabled
        if topology_enabled:
            try:
                from instructor.models.topology import Topology
                topologies = Topology.query.filter_by(is_active=True).all()
                
                available_topologies = []
                for topo in topologies:
                    available_topologies.append({
                        'id': topo.id,
                        'title': topo.title,
                        'description': topo.description,
                        'topology_type': topo.topology_type,
                        'difficulty': topo.difficulty,
                        'device_requirements': topo.device_requirements,
                        'scoring_metrics': topo.scoring_metrics,
                        'base_score': topo.base_score
                    })
                
                # If no topologies in database, provide defaults
                if not available_topologies:
                    default_topologies = [
                        {'id': 'point-to-point', 'title': 'Point-to-Point', 'topology_type': 'point-to-point', 'difficulty': 'easy'},
                        {'id': 'star', 'title': 'Star Topology', 'topology_type': 'star', 'difficulty': 'medium'},
                        {'id': 'mesh', 'title': 'Mesh Topology', 'topology_type': 'mesh', 'difficulty': 'hard'},
                        {'id': 'bus', 'title': 'Bus Topology', 'topology_type': 'bus', 'difficulty': 'medium'},
                        {'id': 'ring', 'title': 'Ring Topology', 'topology_type': 'ring', 'difficulty': 'medium'},
                        {'id': 'tree', 'title': 'Tree Topology', 'topology_type': 'tree', 'difficulty': 'hard'},
                        {'id': 'hybrid', 'title': 'Hybrid Topology', 'topology_type': 'hybrid', 'difficulty': 'hard'}
                    ]
                    available_topologies = default_topologies
                
                simulation_data['available_topologies'] = available_topologies
                
            except Exception as e:
                print(f"Error loading topologies: {e}")
                simulation_data['available_topologies'] = []
        
        # Check if user has an existing attempt
        # Basic progress snapshot (attempts summary)
        controller = DynamicSimulationController()
        progress = controller.get_simulation_progress(user.id, simulation.id) or {
                'status': 'not_started',
                'attempts': 0,
                'best_score': 0,
                'completion_percentage': 0
            }
        
        # Add current attempt state for resumption
        current_attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id,
            is_completed=False
        ).first()
        
        if current_attempt:
            progress.update({
                'last_step_index': getattr(current_attempt, 'last_step_index', 0) or 0,
                'current_score': current_attempt.total_score or 0,
                'answers': current_attempt.step_responses or {},  # Include step responses for answer restoration
                'status': 'in_progress'
            })

        # Provide assignment gating info to UI
        gating = check_assignment_gating(user, simulation.id)

        # Clean simulation data for JSON serialization to prevent JavaScript syntax errors
        def clean_for_json(obj):
            """Recursively clean objects to ensure JSON serializability"""
            if obj is None:
                return None
            elif isinstance(obj, (str, int, float, bool)):
                return obj
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, dict):
                return {str(k): clean_for_json(v) for k, v in obj.items() if v is not None}
            else:
                # Convert non-serializable objects to string
                return str(obj)
        
        # Clean the simulation data to prevent JSON serialization issues
        clean_simulation_data = clean_for_json(simulation_data)
        clean_progress = clean_for_json(progress)

        # Prepare context for template including collaboration data
        context = {
            'user': user,
            'simulation': clean_simulation_data,
            'simulation_data': clean_simulation_data,  # Add this for JavaScript compatibility
            'progress': clean_progress,
            'gating': gating,
            'lobby': lobby.to_dict() if lobby else None,
            'team_assignment': {
                'team_name': team_assignment.team_name,
                'team_leader': team_assignment.team_leader,
                'team_members': team_assignment.team_members or [],
                'is_active': team_assignment.is_active
            } if team_assignment else None,
            'collaboration_enabled': collaboration_setting.collaboration_enabled if collaboration_setting else False,
            'collaboration_settings': collaboration_setting.to_dict() if collaboration_setting else {}
        }

        return render_template('user/dynamic_simulation.html', **context)

    except Exception as e:
        print(f"Error loading simulation {simulation_id}: {e}")
        flash(f'Error loading simulation: {str(e)}', 'error')
        # Don't use fallback - return error directly
        return f"Error loading simulation: {str(e)}", 500

@dynamic_sim_bp.route('/learning-path/<int:path_id>')
@user_login_required
def learning_path_view(path_id):
    """View learning path with simulations"""
    user = get_user_from_session()
    controller = DynamicSimulationController()
    
    learning_path = LearningPath.query.get_or_404(path_id)
    
    # Check if user has access to this learning path
    user_classes = user.enrolled_classes.all()
    if not user_classes:
        return render_template('user/access_denied.html',
                             user=user,
                             message="You must be enrolled in a class to access learning paths.")
    
    # Check if any of user's classes match the learning path
    has_access = False
    for user_class in user_classes:
        class_level = user_class.name.lower()
        if class_level in learning_path.course_level.lower():
            has_access = True
            break
    
    if not has_access:
        return render_template('user/access_denied.html',
                             user=user,
                             message="This learning path is not available for your class level.")
    
    # Get ordered simulations with progress
    ordered_simulations = learning_path.get_ordered_simulations()
    simulation_data = []
    
    for assoc in ordered_simulations:
        progress = controller.get_simulation_progress(user.id, assoc.simulation_id)
        can_access = controller.can_access_simulation(user.id, assoc.simulation_id)
        
        simulation_data.append({
            'association': assoc,
            'simulation': assoc.simulation,
            'progress': progress,
            'can_access': can_access
        })
    
    # Get overall path progress
    path_progress = learning_path.calculate_user_progress(user.id)
    
    return render_template('user/learning_path.html',
                         user=user,
                         learning_path=learning_path,
                         simulations=simulation_data,
                         path_progress=path_progress)

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/start', methods=['POST'])
@user_login_required
def start_simulation(simulation_id):
    """Start a simulation and track progress"""
    try:
        user = get_user_from_session()
        controller = DynamicSimulationController()

        if not controller.can_access_simulation(user.id, simulation_id):
            return jsonify({'error': 'Access denied'}), 403

        # Enforce assignment gating if an active assignment exists for user's classes
        gating = check_assignment_gating(user, simulation_id)
        if not gating.get('allowed', True):
            return jsonify({'error': gating.get('message', 'Assignment requirements not met'), 'gating': gating}), 403

        # Create or reuse an ongoing SimulationAttempt
        attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id,
            is_completed=False
        ).first()

        if not attempt:
            attempt = SimulationAttempt(
                user_id=user.id,
                simulation_id=simulation_id
            )
            db.session.add(attempt)

        if not attempt.started_at:
            attempt.started_at = db.func.now()

        db.session.commit()

        return jsonify({
            'success': True, 
            'message': 'Simulation started',
            'attemptId': attempt.id,
            'lastStepIndex': getattr(attempt, 'last_step_index', 0) or 0,
            'totalScore': attempt.total_score or 0
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/submit-step', methods=['POST'])
@user_login_required  
def submit_step(simulation_id):
    """Submit a single step answer and get validation results"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        
        step_index = data.get('stepIndex')
        user_answer = data.get('answer', '').strip()
        
        if step_index is None:
            return jsonify({'error': 'Step index required'}), 400
            
        # Get simulation and validation rules
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Parse validation rules  
        validation_rules = simulation.validation_rules or {}
        if isinstance(validation_rules, str):
            try:
                validation_rules = json.loads(validation_rules)
            except Exception:
                validation_rules = {}
                
        # Parse step definitions for fallback
        step_definitions = simulation.step_definitions or []
        if isinstance(step_definitions, str):
            try:
                step_definitions = json.loads(step_definitions)
            except Exception:
                step_definitions = []
        
        # Get validation rule for this step
        step_key = str(step_index)
        rule = validation_rules.get(step_key) or {}
        
        # Fallback to step expected_answer if no rule
        if not rule and step_index < len(step_definitions):
            step = step_definitions[step_index]
            if isinstance(step, dict):
                # Check for normalized expected_answer or validation.expectedAnswer
                expected = step.get('expected_answer') or (step.get('validation', {}) or {}).get('expectedAnswer')
                if expected:
                    rule = {
                        'type': 'exact_match',
                        'expected_answer': expected,
                        'score': step.get('score') or (step.get('validation', {}) or {}).get('score', 10)
                    }
        
        # Enhanced validation with network state checking
        is_correct = False
        validation_type = (rule.get('type', 'exact_match') or 'exact_match').lower()
        expected_answer = rule.get('expected_answer', '')
        validation_detail = None
        
        # Handle different validation types including network configurations
        if validation_type == 'exact_match':
            is_correct = user_answer.lower().strip() == expected_answer.lower().strip()
        elif validation_type == 'contains':
            is_correct = expected_answer.lower() in user_answer.lower()
        elif validation_type == 'regex':
            try:
                import re
                # Safety limits for regex
                if len(expected_answer) > 200:
                    is_correct = False
                else:
                    pattern = re.compile(expected_answer, re.IGNORECASE)
                    is_correct = bool(pattern.search(user_answer))
            except (re.error, Exception):
                is_correct = False
        elif validation_type == 'multiple_choice':
            # For multiple choice, expected_answer should be the correct option
            is_correct = user_answer.strip() == expected_answer.strip()
        elif validation_type == 'completion':
            # Troubleshooting completion validation - any non-empty answer is correct
            is_correct = bool(user_answer.strip())
        elif validation_type == 'network_config':
            # Advanced network configuration validation
            validation_detail = validate_network_configuration(data.get('networkState'), rule.get('expected_config'))
            is_correct = bool(validation_detail.get('valid')) if isinstance(validation_detail, dict) else bool(validation_detail)
        elif validation_type == 'connectivity':
            # Network connectivity validation
            validation_detail = {'valid': validate_network_connectivity(data.get('topology'), rule.get('expected_topology')),
                                 'errors': [], 'warnings': []}
            is_correct = bool(validation_detail['valid'])
        elif validation_type == 'cli_output':
            # CLI command output validation
            validation_detail = {'valid': validate_cli_output(user_answer, rule.get('expected_patterns', [])),
                                 'errors': [], 'warnings': []}
            is_correct = bool(validation_detail['valid'])
        else:
            # Default to exact match
            is_correct = user_answer.lower().strip() == expected_answer.lower().strip()
        
        # Calculate score
        awarded_score = 0
        if is_correct:
            base_score = rule.get('score', 10)
            if validation_detail and isinstance(validation_detail, dict) and 'score' in validation_detail:
                # Map validation_detail.score (0-100) proportionally to base_score
                try:
                    awarded_score = round(base_score * (float(validation_detail.get('score', 100)) / 100.0))
                except Exception:
                    awarded_score = base_score
            else:
                awarded_score = base_score
        
        # Get or create attempt
        attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id,
            is_completed=False
        ).first()
        
        if not attempt:
            return jsonify({'error': 'Simulation not started. Call start endpoint first.'}), 400
        
        # Update attempt with step response
        if not attempt.step_responses:
            attempt.step_responses = {}
        
        attempt.step_responses[step_key] = {
            'answer': user_answer,
            'correct': is_correct,
            'awarded_score': awarded_score
        }
        
        # Update last step index and total score
        attempt.last_step_index = max(step_index, getattr(attempt, 'last_step_index', 0) or 0)
        
        # Recalculate total score from all step responses
        total_score = 0
        for step_resp in attempt.step_responses.values():
            if isinstance(step_resp, dict) and step_resp.get('awarded_score'):
                total_score += step_resp['awarded_score']
        attempt.total_score = total_score
        
        db.session.commit()
        
        # Determine if this is the final step
        total_steps = len(step_definitions)
        is_finished = (step_index >= total_steps - 1) if total_steps > 0 else False
        next_index = step_index + 1 if not is_finished else None
        
        return jsonify({
            'correct': is_correct,
            'awardedScore': awarded_score,
            'totalScore': total_score,
            'nextIndex': next_index,
            'finished': is_finished,
            'message': rule.get('success_message' if is_correct else 'error_message', 
                              'Correct! Well done.' if is_correct else 'Incorrect answer. Please try again.'),
            'hint': rule.get('hint', '') if not is_correct else '',
            'validation': validation_detail or {}
        })
        
    except Exception as e:
        print(f"Error in submit_step: {e}")
        return jsonify({'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/network-state', methods=['POST'])
@user_login_required
def update_network_state(simulation_id):
    """Update network topology and device states with enhanced validation"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        
        # Get current attempt
        attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id,
            is_completed=False
        ).first()
        
        if not attempt:
            return jsonify({'error': 'No active simulation found'}), 400
        
        # Validate topology if provided and topology is enabled for this simulation
        topology_validation = {'isValid': True, 'errors': [], 'warnings': []}
        topology_data = data.get('topology')
        
        # Get simulation to check if topology validation is needed
        simulation = Simulation.query.get(simulation_id)
        simulation_config = simulation.simulation_config or {} if simulation else {}
        
        # Parse simulation_config if it's a string
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except (json.JSONDecodeError, ValueError):
                simulation_config = {}
        
        topology_enabled = simulation_config.get('topology_enabled', False)
        selected_topology = simulation_config.get('selected_topology', '')
        
        if topology_data and topology_enabled:
            topology_validation = validate_topology_data(topology_data)
            if not topology_validation['isValid']:
                print(f"Topology validation failed for simulation {simulation_id}: {topology_validation['errors']}")
                return jsonify({
                    'error': 'Invalid topology data', 
                    'validation': topology_validation
                }), 400
            
            # Additional validation against selected topology type if specified
            if selected_topology:
                try:
                    from instructor.models.topology import Topology as TopologyModel
                    topology_model = TopologyModel.query.filter_by(topology_type=selected_topology).first()
                    if topology_model:
                        # Validate device requirements
                        device_requirements = topology_model.device_requirements
                        if device_requirements:
                            devices = topology_data.get('devices', [])
                            device_counts = {}
                            for device in devices:
                                device_type = device.get('type', 'unknown')
                                device_counts[device_type] = device_counts.get(device_type, 0) + 1
                            
                            for req_type, req_count in device_requirements.items():
                                actual_count = device_counts.get(req_type, 0)
                                if actual_count < req_count:
                                    topology_validation['warnings'].append(
                                        f'Topology requires {req_count} {req_type} devices, but only {actual_count} found'
                                    )
                except Exception as e:
                    print(f"Error validating topology requirements: {e}")
        elif topology_data:
            # Basic validation even if topology not explicitly enabled
            topology_validation = validate_topology_data(topology_data)
            if not topology_validation['isValid']:
                print(f"Topology validation failed for simulation {simulation_id}: {topology_validation['errors']}")
                return jsonify({
                    'error': 'Invalid topology data', 
                    'validation': topology_validation
                }), 400
        
        # Update session data with network state
        if not attempt.session_data:
            attempt.session_data = {}
        elif isinstance(attempt.session_data, str):
            # Handle case where session_data is stored as JSON string
            try:
                attempt.session_data = json.loads(attempt.session_data)
            except (json.JSONDecodeError, ValueError):
                attempt.session_data = {}

        # Prepare update data
        update_data = {
            'lastUpdated': datetime.utcnow().isoformat()
        }
        
        # Update topology if provided and valid
        if topology_data:
            update_data['networkTopology'] = topology_data
            print(f"Updated topology for simulation {simulation_id}, attempt {attempt.id}")
        
        # Update device states if provided
        device_states = data.get('deviceStates')
        if device_states:
            update_data['deviceStates'] = device_states
            print(f"Updated device states for simulation {simulation_id}, attempt {attempt.id}")
        
        # Include metadata if provided
        metadata = data.get('metadata', {})
        if metadata:
            update_data['metadata'] = metadata
        
        attempt.session_data.update(update_data)
        
        db.session.commit()

        # Enhanced response matching MVP API contract
        return jsonify({
            'success': True,
            'attemptId': attempt.id,
            'lastUpdated': update_data['lastUpdated'],
            'validation': {
                'errors': topology_validation.get('errors', []),
                'warnings': topology_validation.get('warnings', [])
            },
            'metadata': {
                'action': metadata.get('action', 'save'),
                'timestamp': update_data['lastUpdated'],
                'topologyUpdated': 'networkTopology' in update_data,
                'deviceStatesUpdated': 'deviceStates' in update_data,
                'dataSize': len(str(update_data))
            }
        })
        
    except Exception as e:
        print(f"Error updating network state for simulation {simulation_id}: {e}")
        return jsonify({
            'error': 'Failed to update network state',
            'details': str(e) if current_app.debug else 'Internal server error'
        }), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/topology', methods=['GET'])
@user_login_required
def get_simulation_topology_config(simulation_id):
    """Get topology configuration for a specific simulation"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get simulation
        simulation = Simulation.query.get_or_404(simulation_id)
        simulation_config = simulation.simulation_config or {}
        
        # Parse simulation_config if it's a string
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except (json.JSONDecodeError, ValueError):
                simulation_config = {}
        
        # Check if topology is enabled - if not, return empty config instead of error
        topology_enabled = simulation_config.get('topology_enabled', False)
        if not topology_enabled:
            return jsonify({
                'success': True,
                'topology_enabled': False,
                'selected_topology': '',
                'topology_config': {},
                'topology_requirements': {},
                'topology_data': None,
                'message': 'Topology not enabled for this simulation'
            })
        
        # Get selected topology details
        selected_topology = simulation_config.get('selected_topology', '')
        topology_config = simulation_config.get('topology_config', {})
        topology_requirements = simulation_config.get('topology_requirements', {})
        
        # Get topology model data if available
        topology_data = None
        if selected_topology:
            try:
                from instructor.models.topology import Topology
                topology_model = Topology.query.filter_by(topology_type=selected_topology).first()
                if topology_model:
                    topology_data = {
                        'id': topology_model.id,
                        'title': topology_model.title,
                        'description': topology_model.description,
                        'topology_type': topology_model.topology_type,
                        'difficulty': topology_model.difficulty,
                        'device_requirements': topology_model.device_requirements,
                        'scoring_metrics': topology_model.scoring_metrics,
                        'base_score': topology_model.base_score,
                        'expected_config': topology_model.expected_config
                    }
            except Exception as e:
                print(f"Error loading topology model: {e}")
        
        return jsonify({
            'success': True,
            'topology_enabled': True,
            'selected_topology': selected_topology,
            'topology_config': topology_config,
            'topology_requirements': topology_requirements,
            'topology_data': topology_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/topology/validate', methods=['POST'])
@user_login_required
def validate_simulation_topology(simulation_id):
    """Validate user's topology against expected configuration"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        
        user_topology = data.get('topology', {})
        if not user_topology:
            return jsonify({'error': 'No topology data provided'}), 400
        
        # Get simulation and topology configuration
        simulation = Simulation.query.get_or_404(simulation_id)
        simulation_config = simulation.simulation_config or {}
        
        # Parse simulation_config if it's a string
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except (json.JSONDecodeError, ValueError):
                simulation_config = {}
        
        if not simulation_config.get('topology_enabled', False):
            return jsonify({'error': 'Topology validation not enabled for this simulation'}), 400
        
        selected_topology = simulation_config.get('selected_topology', '')
        
        # Basic topology validation
        topology_validation = validate_topology_data(user_topology)
        
        # Topology-specific validation
        topology_score = 0
        topology_feedback = []
        
        if selected_topology and topology_validation['isValid']:
            try:
                from instructor.models.topology import Topology
                topology_model = Topology.query.filter_by(topology_type=selected_topology).first()
                
                if topology_model:
                    expected_config = topology_model.expected_config
                    device_requirements = topology_model.device_requirements
                    scoring_metrics = topology_model.scoring_metrics
                    
                    # Validate device requirements
                    devices = user_topology.get('devices', [])
                    connections = user_topology.get('connections', [])
                    
                    device_counts = {}
                    for device in devices:
                        device_type = device.get('type', 'unknown')
                        device_counts[device_type] = device_counts.get(device_type, 0) + 1
                    
                    # Check device requirements
                    requirements_met = True
                    for req_type, req_count in (device_requirements or {}).items():
                        actual_count = device_counts.get(req_type, 0)
                        if actual_count < req_count:
                            requirements_met = False
                            topology_feedback.append(f'Missing {req_count - actual_count} {req_type} device(s)')
                        elif actual_count > req_count:
                            topology_feedback.append(f'Extra {actual_count - req_count} {req_type} device(s)')
                    
                    # Validate topology structure using existing validator
                    if hasattr(validate_network_connectivity, '__call__'):
                        connectivity_valid = validate_network_connectivity(user_topology, expected_config)
                        if not connectivity_valid:
                            topology_feedback.append('Network connectivity does not match expected topology')
                            requirements_met = False
                    
                    # Calculate score based on correctness
                    base_score = topology_model.base_score or 100
                    if requirements_met and len(topology_feedback) == 0:
                        topology_score = base_score
                        topology_feedback.append('Perfect topology! All requirements met.')
                    elif requirements_met:
                        topology_score = int(base_score * 0.8)  # 80% for meeting requirements with warnings
                    else:
                        topology_score = int(base_score * 0.4)  # 40% for partial completion
                        
            except Exception as e:
                print(f"Error in topology-specific validation: {e}")
                topology_feedback.append('Error validating topology requirements')
        
        return jsonify({
            'success': True,
            'valid': topology_validation['isValid'] and len(topology_validation['errors']) == 0,
            'score': topology_score,
            'feedback': topology_feedback,
            'validation': topology_validation,
            'requirements_met': len([f for f in topology_feedback if 'Missing' not in f and 'Extra' not in f]) == len(topology_feedback)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/execute-cli', methods=['POST'])
@user_login_required
def execute_cli_command(simulation_id):
    """Execute CLI command and return response"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        
        command = data.get('command', '').strip()
        device_id = data.get('deviceId', '')
        
        if not command or not device_id:
            return jsonify({'error': 'Command and device ID required'}), 400
        
        # Get simulation and current attempt
        simulation = Simulation.query.get_or_404(simulation_id)
        attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id,
            is_completed=False
        ).first()
        
        if not attempt:
            return jsonify({'error': 'No active simulation found'}), 400
        
        # Process CLI command based on device type and current state
        response = process_cli_command(command, device_id, attempt.session_data)

        # Evaluate against instructor-authored CLI rules if present in simulation_config
        try:
            sim_cfg = simulation.simulation_config or {}
            if isinstance(sim_cfg, str):
                sim_cfg = json.loads(sim_cfg)
        except Exception:
            sim_cfg = {}

        cli_rules = (sim_cfg or {}).get('cli_rules') or {}
        rule_feedback = None
        rule_score_delta = 0

        try:
            device_rules = []
            # Support both dict keyed by device and flat list
            if isinstance(cli_rules, dict):
                device_rules = cli_rules.get(device_id) or cli_rules.get('*') or []
            elif isinstance(cli_rules, list):
                device_rules = cli_rules

            def matches(rule_cmd, actual_cmd, match_type, case_sensitive=False):
        
                mt = (match_type or 'exact').lower()
                cs = bool(case_sensitive)
                if mt == 'regex':
                    try:
                        flags = 0 if cs else re.IGNORECASE
                        return bool(re.search(rule_cmd, actual_cmd, flags))
                    except re.error:
                        return False
                if mt == 'contains':
                    return (str(rule_cmd) in actual_cmd) if cs else (str(rule_cmd).lower() in actual_cmd.lower())
                # default exact
                if cs:
                    return actual_cmd.strip() == str(rule_cmd).strip()
                return actual_cmd.strip().lower() == str(rule_cmd).strip().lower()

            for rule in device_rules if isinstance(device_rules, list) else []:
                if not isinstance(rule, dict):
                    continue
                cmd_pat = rule.get('command') or rule.get('pattern') or ''
                match_type = rule.get('type') or rule.get('match') or 'exact'
                case_sensitive = bool(rule.get('caseSensitive') or rule.get('case_sensitive'))
                if cmd_pat and matches(cmd_pat, command, match_type, case_sensitive):
                    # On match, override/append response and collect scoring/feedback
                    custom_output = rule.get('output') or rule.get('response')
                    if isinstance(custom_output, str) and custom_output.strip():
                        response = custom_output
                    rule_feedback = rule.get('feedback') or rule.get('message')
                    try:
                        rule_score_delta = int(rule.get('scoreDelta') or rule.get('score') or 0)
                    except Exception:
                        rule_score_delta = 0
                    # Optional expected output matchers to refine pass/fail
                    try:
                        expected_output = rule.get('expectedOutput') or rule.get('expected_outputs') or []
                        if expected_output:
                            # Normalize to list of dicts {pattern, type}
                            checks = expected_output if isinstance(expected_output, list) else [expected_output]
                            ok = True
                            for chk in checks:
                                if isinstance(chk, str):
                                    # contains, case-insensitive by default
                                    if chk.lower() not in response.lower():
                                        ok = False
                                        break
                                elif isinstance(chk, dict):
                                    p = chk.get('pattern', '')
                                    t = (chk.get('type') or 'contains').lower()
                                    cs2 = bool(chk.get('caseSensitive') or chk.get('case_sensitive'))
                                    if t == 'regex':
                                        try:
                                            flags = 0 if cs2 else re.IGNORECASE
                                            if not re.search(p, response, flags):
                                                ok = False
                                                break
                                        except re.error:
                                            ok = False
                                            break
                                    elif t == 'exact':
                                        if (response == p) if cs2 else (response.lower() == p.lower()):
                                            pass
                                        else:
                                            ok = False
                                            break
                                    else:  # contains
                                        if (p in response) if cs2 else (p.lower() in response.lower()):
                                            pass
                                        else:
                                            ok = False
                                            break
                            if not ok:
                                # If expected output didn't match, zero out score delta for this rule
                                rule_score_delta = 0
                    except Exception:
                        pass
                    break
        except Exception as _e:
            # Fail-safe: ignore bad rules
            rule_feedback = None
            rule_score_delta = 0
        
        # Update session data with command history
        if not attempt.session_data:
            attempt.session_data = {}
        elif isinstance(attempt.session_data, str):
            try:
                attempt.session_data = json.loads(attempt.session_data)
            except (json.JSONDecodeError, ValueError):
                attempt.session_data = {}
        
        if 'cliHistory' not in attempt.session_data:
            attempt.session_data['cliHistory'] = {}
        
        if device_id not in attempt.session_data['cliHistory']:
            attempt.session_data['cliHistory'][device_id] = []
        
        attempt.session_data['cliHistory'][device_id].append({
            'command': command,
            'response': response,
            'timestamp': datetime.utcnow().isoformat()
        })

        # Apply optional score delta and feedback note into attempt
        if rule_score_delta:
            try:
                attempt.total_score = int(attempt.total_score or 0) + int(rule_score_delta)
            except Exception:
                pass
        if rule_feedback:
            fb = attempt.feedback_given or []
            if isinstance(fb, list):
                fb.append({'type': 'cli_rule', 'device': device_id, 'command': command, 'message': rule_feedback, 'delta': rule_score_delta, 'ts': datetime.utcnow().isoformat()})
                attempt.feedback_given = fb
        
        # CRITICAL FIX: Mark session_data as modified so SQLAlchemy knows to save the device state changes
        # This ensures CLI mode (interface config, etc.) persists between commands
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(attempt, 'session_data')
        
        db.session.commit()
        
        # Get current device state to return CLI mode info for prompt updates
        device_states = attempt.session_data.get('deviceStates', {})
        current_device_state = device_states.get(device_id, {})
        cli_mode = current_device_state.get('cli_mode', 'exec')
        current_interface = current_device_state.get('current_interface')
        
        return jsonify({
            'success': True,
            'response': response,
            'deviceId': device_id,
            'cliMode': cli_mode,
            'currentInterface': current_interface
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dynamic_sim_bp.route('/simulation/<int:simulation_id>/qr')
def generate_qr_code(simulation_id):
    """Generate QR code for simulation confirmation"""
    try:
        # Get simulation to ensure it exists
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Generate confirmation URL
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        
        serializer = URLSafeTimedSerializer(current_app.secret_key)
        token = serializer.dumps({'simulation_id': simulation_id}, salt='simulation-confirm')
        
        # Build full confirmation URL
        confirm_url = url_for('dynamic_simulations.confirm_simulation', 
                             simulation_id=simulation_id, 
                             token=token, 
                             _external=True)
        
        # Generate QR code
        import qrcode
        from io import BytesIO
        import base64
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(confirm_url)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to PNG bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        from flask import Response
        return Response(
            img_buffer.getvalue(),
            mimetype='image/png',
            headers={
                'Content-Disposition': f'inline; filename=simulation_{simulation_id}_qr.png'
            }
        )
        
    except Exception as e:
        from flask import abort
        print(f"Error generating QR code for simulation {simulation_id}: {e}")
        abort(500)

@dynamic_sim_bp.route('/simulation/<int:simulation_id>/confirm')
def confirm_simulation(simulation_id):
    """Display simulation confirmation page"""
    try:
        # Get simulation
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Verify token if provided
        token = request.args.get('token')
        token_valid = False
        token_data = None
        
        if token:
            try:
                from services.qr_service import QRCodeService
                qr_service = QRCodeService()
                
                verification_result = qr_service.verify_qr_token(token, simulation_id)
                
                if verification_result['valid']:
                    token_valid = True
                    token_data = verification_result['data']
            except Exception as e:
                print(f"Token verification error: {e}")
                token_valid = False
        
        # Get simulation data for display
        simulation_data = {
            'id': simulation.id,
            'title': simulation.title,
            'description': simulation.description,
            'simulation_type': simulation.simulation_type,
            'category': simulation.category,
            'difficulty': simulation.difficulty,
            'estimated_duration': simulation.estimated_duration,
            'is_published': simulation.is_published,
            'is_active': simulation.is_active
        }
        
        # Generate start URL
        start_url = url_for('dynamic_simulations.run_simulation', 
                           simulation_id=simulation_id, 
                           _external=True)
        
        return render_template('user/simulation_confirmation.html',
                             simulation=simulation_data,
                             start_url=start_url,
                             token_valid=token_valid,
                             token_data=token_data)
        
    except Exception as e:
        print(f"Error in confirm_simulation: {e}")
        flash(f'Error loading simulation confirmation: {str(e)}', 'error')
        return render_template('user/simulation_confirmation.html',
                             simulation=None,
                             start_url=None,
                             token_valid=False,
                             token_data=None)

def expand_interface_name(short_name):
    """Expand abbreviated interface names to full names"""
    short = short_name.lower()
    
    # Common Cisco interface abbreviations
    if short.startswith('gi') or short.startswith('g'):
        # GigabitEthernet: Gi0/0, G0/0 -> GigabitEthernet0/0
        return 'gigabitethernet' + short[2:] if short.startswith('gi') else 'gigabitethernet' + short[1:]
    elif short.startswith('fa') or short.startswith('f'):
        # FastEthernet: Fa0/0, F0/0 -> FastEthernet0/0
        return 'fastethernet' + short[2:] if short.startswith('fa') else 'fastethernet' + short[1:]
    elif short.startswith('se') or short.startswith('s'):
        # Serial: Se0/0, S0/0 -> Serial0/0
        return 'serial' + short[2:] if short.startswith('se') else 'serial' + short[1:]
    elif short.startswith('eth') or short.startswith('e'):
        # Ethernet: Eth0/0, E0/0 -> Ethernet0/0
        return 'ethernet' + short[3:] if short.startswith('eth') else 'ethernet' + short[1:]
    elif short.startswith('te'):
        # TenGigabitEthernet: Te0/0 -> TenGigabitEthernet0/0
        return 'tengigabitethernet' + short[2:]
    elif short.startswith('lo'):
        # Loopback: Lo0 -> Loopback0
        return 'loopback' + short[2:]
    elif short.startswith('vlan'):
        # VLAN: Vlan1 -> Vlan1 (keep as-is)
        return short
    else:
        # If not recognized, return as-is (already lowercase)
        return short

def process_cli_command(command, device_id, session_data):
    """Process CLI command and return appropriate response with mode awareness"""
    try:
        parts = command.lower().split()
        if not parts:
            return "Invalid command"
        
        cmd = parts[0]
        
        # CRITICAL FIX: Ensure deviceStates exists and get/create device_state properly
        if 'deviceStates' not in session_data:
            session_data['deviceStates'] = {}
        
        device_states = session_data['deviceStates']
        
        # If device doesn't exist yet, create it with default state
        if device_id not in device_states:
            device_states[device_id] = {}
        
        # Get reference to the device state (not a copy!)
        device_state = device_states[device_id]
        
        # Get current CLI mode from device state
        cli_mode = device_state.get('cli_mode', 'exec')
        current_interface = device_state.get('current_interface', None)
        
        # Handle mode-specific commands
        if cli_mode == 'interface_config' and current_interface:
            # In interface configuration mode
            if cmd == 'ip' and len(parts) >= 4 and parts[1] == 'address':
                # ip address <IP> <MASK>
                ip_addr = parts[2]
                subnet_mask = parts[3]
                return handle_interface_ip_config(device_state, device_id, current_interface, ip_addr, subnet_mask, session_data)
            elif cmd == 'no' and len(parts) >= 2 and parts[1] == 'shutdown':
                return handle_interface_no_shutdown(device_state, device_id, current_interface, session_data)
            elif cmd == 'shutdown':
                return handle_interface_shutdown(device_state, device_id, current_interface, session_data)
            elif cmd == 'exit':
                device_state['cli_mode'] = 'config'
                device_state['current_interface'] = None
                return "Exiting interface configuration mode"
            elif cmd == 'end':
                device_state['cli_mode'] = 'exec'
                device_state['current_interface'] = None
                return "Exiting to exec mode"
        
        # Global configuration mode
        if cli_mode == 'config':
            if (cmd == 'interface' or cmd == 'int') and len(parts) >= 2:
                # Expand abbreviated interface names (e.g., G0/0 -> GigabitEthernet0/0)
                interface_name = expand_interface_name(parts[1])
                device_state['cli_mode'] = 'interface_config'
                device_state['current_interface'] = interface_name
                return f"Entering interface configuration mode for {interface_name}..."
            elif cmd == 'exit':
                device_state['cli_mode'] = 'exec'
                return "Exiting configuration mode"
            elif cmd == 'end':
                device_state['cli_mode'] = 'exec'
                return "Exiting to exec mode"
        
        # Exec mode commands
        if cmd == 'show':
            return handle_show_command(parts[1:], device_state, device_id)
        elif cmd == 'ping':
            # Extract topology data for connectivity validation
            topology_data = session_data.get('topology') or session_data.get('networkTopology')
            return handle_ping_command(parts[1:], device_states, topology_data)
        elif (cmd == 'configure' or cmd == 'conf') and len(parts) >= 2 and (parts[1] == 'terminal' or parts[1] == 't'):
            device_state['cli_mode'] = 'config'
            return "Entering configuration mode..."
        elif cmd == 'interface' or cmd == 'int':
            return handle_interface_command(parts[1:], device_state)
        elif cmd == 'ip' and len(parts) >= 2 and parts[1] == 'address':
            # Helpful error message when IP config attempted in wrong mode
            return """% Invalid command. IP address configuration must be done in interface configuration mode.

To configure an IP address, use:
  configure terminal
  interface <interface-name>
  ip address <IP> <MASK>
  no shutdown
  exit
  exit

Example:
  configure terminal
  interface GigabitEthernet0/0
  ip address 192.168.1.81 255.255.255.0
  no shutdown"""
        elif cmd == 'ip':
            return handle_ip_command(parts[1:], device_state)
        elif cmd == 'help' or cmd == '?':
            return get_help_text()
        elif cmd == 'exit':
            return "Goodbye!"
        elif cmd == 'enable' or cmd == 'en':
            # User is already in privileged mode in this simulator
            return ""  # Silent success, already privileged
        elif cmd == 'disable':
            return "Entering User EXEC mode"
        elif cmd == 'write':
            if len(parts) >= 2 and parts[1] == 'memory':
                return "Building configuration...\nConfiguration saved to NVRAM\n[OK]"
            else:
                return "Building configuration...\nConfiguration saved to NVRAM\n[OK]"
        elif cmd == 'copy' and len(parts) >= 3:
            if parts[1] == 'running-config' and parts[2] == 'startup-config':
                return "Building configuration...\nConfiguration saved to NVRAM\n[OK]"
            else:
                return f"% Invalid copy command"
        elif cmd == 'end':
            device_state['cli_mode'] = 'exec'
            return "Exiting to exec mode"
        elif cmd == 'reload':
            return "% Reload command not available in simulation mode"
        else:
            return f"% Invalid command: {command}\nType 'help' for available commands."
            
    except Exception as e:
        import logging
        logging.error(f"CLI Command Error: {str(e)}")
        return f"Command processing error: {str(e)}"

def handle_show_command(args, device_state, device_id):
    """Handle 'show' commands"""
    if not args:
        return "Incomplete command. Use 'show ?' for help"
    
    subcmd = ' '.join(args)
    
    if subcmd in ['running-config', 'run']:
        return generate_running_config(device_state, device_id)
    elif subcmd in ['interfaces', 'int']:
        return generate_interfaces_output(device_state)
    elif subcmd in ['ip interface', 'ip int', 'ip interfaces']:
        return generate_ip_interfaces_output(device_state)
    elif subcmd in ['ip interface brief', 'ip int brief']:
        return generate_ip_interfaces_brief(device_state)
    elif subcmd in ['ip route', 'route']:
        return generate_routing_table(device_state)
    elif subcmd == 'version':
        return generate_version_output(device_id)
    elif subcmd == 'arp':
        return generate_arp_table(device_state)
    elif subcmd == 'ip':
        return "% Incomplete command. Available: ip interface, ip route, ip arp"
    else:
        return f"% Invalid show command: {subcmd}"

def generate_version_output(device_id):
    """Generate version command output for network device"""
    return f"""
Cisco IOS Software, IOSv Software (VIOS-ADVENTERPRISEK9-M), Version 15.6(2)T, RELEASE SOFTWARE (fc2)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2016 by Cisco Systems, Inc.
Compiled Tue 22-Mar-16 16:19 by prod_rel_team

ROM: Bootstrap program is IOSv

{device_id} uptime is 1 day, 2 hours, 34 minutes
System returned to ROM by reload at 21:32:45 UTC Mon Oct 14 2024
System restarted at 21:33:12 UTC Mon Oct 14 2024
System image file is "flash0:/vios-adventerprisek9-m"
Last reload reason: Unknown reason

This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

Cisco IOSv (revision 1.0) with  with 2048000K/6147K bytes of memory.
Processor board ID 9112003
4 Gigabit Ethernet interfaces
DRAM configuration is 72 bits wide with parity disabled.
256K bytes of non-volatile configuration memory.
2097152K bytes of ATA System CompactFlash 0 (Read/Write)
0K bytes of ATA CompactFlash 1 (Read/Write)
11264K bytes of ATA CompactFlash 2 (Read/Write)
0K bytes of ATA CompactFlash 3 (Read/Write)

Configuration register is 0x0
"""

def generate_arp_table(device_state):
    """Generate ARP table output for network device"""
    arp_entries = []
    
    # Generate realistic ARP entries based on device connections
    for connection in device_state.get('connections', []):
        if connection.get('status') == 'up':
            ip_parts = connection.get('ip', '192.168.1.1').split('.')
            mac_suffix = f"{int(ip_parts[2]):02x}:{int(ip_parts[3]):02x}"
            arp_entries.append({
                'protocol': 'Internet',
                'address': connection.get('ip', '192.168.1.1'),
                'age': '-' if connection.get('type') == 'local' else str(hash(connection.get('interface', '')) % 60),
                'hardware_addr': f"0050.56c0.{mac_suffix}",
                'type': 'ARPA',
                'interface': connection.get('interface', 'GigabitEthernet0/0')
            })
    
    if not arp_entries:
        return "% No ARP entries found"
    
    output = "Protocol  Address          Age (min)  Hardware Addr   Type   Interface\n"
    for entry in arp_entries:
        output += f"{entry['protocol']:<10} {entry['address']:<16} {entry['age']:>9} {entry['hardware_addr']} {entry['type']:<7} {entry['interface']}\n"
    
    return output

def check_physical_connectivity(device_states, target_device_id, topology_data):
    """MVP: Check if target device has physical wire connections
    Returns True if device is connected via wire, False otherwise
    """
    if not topology_data:
        # If no topology data, assume connectivity for backward compatibility
        return True
    
    connections = topology_data.get('connections', [])
    
    # Check if target device has any active connections
    for connection in connections:
        from_device = connection.get('from', {}).get('deviceId') or connection.get('from')
        to_device = connection.get('to', {}).get('deviceId') or connection.get('to')
        
        # Check if target device is part of this connection
        if target_device_id in [from_device, to_device]:
            # Verify both connected devices have interfaces up
            other_device = to_device if from_device == target_device_id else from_device
            
            # Check if both devices have operational interfaces
            target_has_up_interface = any(
                interface.get('status') == 'up' 
                for interface in device_states.get(target_device_id, {}).get('interfaces', {}).values()
            )
            
            other_has_up_interface = any(
                interface.get('status') == 'up' 
                for interface in device_states.get(other_device, {}).get('interfaces', {}).values()
            )
            
            if target_has_up_interface and other_has_up_interface:
                return True
    
    return False


def handle_ping_command(args, device_states, topology_data=None):
    """MVP: Handle ping command with accurate connectivity validation
    
    Validates:
    1. Device existence
    2. Interface status
    3. Physical wire connections
    """
    if not args:
        return "% Incomplete command."
    
    target = args[0]
    
    # Step 1: Validate IP address format
    if not re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', target):
        return f"% Invalid IP address: {target}"
    
    # DEBUG: Log available devices and IPs
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 MVP PING DEBUG: Looking for target IP: {target}")
    logger.info(f"🔍 Device states available: {list(device_states.keys())}")
    for dev_id, dev_state in device_states.items():
        interfaces = dev_state.get('interfaces', {})
        for int_name, int_config in interfaces.items():
            ip = int_config.get('ip_address') or int_config.get('ipAddress')
            logger.info(f"   - Device {dev_id}, Interface {int_name}: IP = {ip}, Status = {int_config.get('status')}")
    
    # Step 2: Check if target device exists
    target_device_id = None
    target_interface = None
    
    for device_id, device_state in device_states.items():
        interfaces = device_state.get('interfaces', {})
        for interface_name, interface_config in interfaces.items():
            # Check both 'ip_address' and 'ipAddress' (camelCase)
            ip_addr = interface_config.get('ip_address') or interface_config.get('ipAddress')
            if ip_addr == target:
                target_device_id = device_id
                target_interface = interface_name
                logger.info(f"✅ Found target device: {device_id}, interface: {interface_name}")
                break
        if target_device_id:
            break
    
    # Step 3: Handle non-existent device
    if not target_device_id:
        logger.warning(f"❌ Target device NOT FOUND for IP: {target}")
        logger.info(f"📋 Available IPs in topology: {[int_cfg.get('ip_address') or int_cfg.get('ipAddress') for dev in device_states.values() for int_cfg in dev.get('interfaces', {}).values()]}")
        
        # Check for well-known external addresses
        if target in ['8.8.8.8', '1.1.1.1', '208.67.222.222']:
            import random
            delay = random.randint(15, 35)
            return f"""
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to {target}, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = {delay-5}/{delay}/{delay+5} ms
"""
        
        # Device not found in topology - provide helpful debug info
        available_ips = []
        for dev in device_states.values():
            for int_cfg in dev.get('interfaces', {}).values():
                ip = int_cfg.get('ip_address') or int_cfg.get('ipAddress')
                if ip:
                    available_ips.append(ip)
        
        debug_msg = f"\n[DEBUG: Available IPs: {', '.join(available_ips) if available_ips else 'None configured'}]" if available_ips else ""
        
        return f"""
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to {target}, timeout is 2 seconds:
U.U.U
Success rate is 0 percent (0/5)
% Destination host unreachable{debug_msg}"""
    
    # Step 4: Check if target interface is up
    target_state = device_states.get(target_device_id, {})
    target_interfaces = target_state.get('interfaces', {})
    target_int_config = target_interfaces.get(target_interface, {})
    
    if target_int_config.get('status') != 'up':
        return f"""
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to {target}, timeout is 2 seconds:
.....
Success rate is 0 percent (0/5)
% Destination host unreachable - interface is down"""
    
    # Step 5: Check physical connectivity (wire connection)
    if topology_data:
        has_physical_connection = check_physical_connectivity(
            device_states, 
            target_device_id, 
            topology_data
        )
        
        if not has_physical_connection:
            return f"""
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to {target}, timeout is 2 seconds:
.....
Success rate is 0 percent (0/5)
% No physical connection to destination"""
    
    # Step 6: Successful ping
    import random
    delay = random.randint(1, 8)
    return f"""
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to {target}, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = {delay}/{delay+1}/{delay+3} ms
"""

def handle_interface_ip_config(device_state, device_id, interface_name, ip_addr, subnet_mask, session_data):
    """Configure IP address on interface"""
    import re
    import logging
    logger = logging.getLogger(__name__)
    
    # Validate IP address format
    if not re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip_addr):
        return f"% Invalid IP address: {ip_addr}"
    
    # Validate subnet mask format
    if not re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', subnet_mask):
        return f"% Invalid subnet mask: {subnet_mask}"
    
    # Get or create interfaces dict
    if 'interfaces' not in device_state:
        device_state['interfaces'] = {}
    
    if interface_name not in device_state['interfaces']:
        device_state['interfaces'][interface_name] = {}
    
    # Configure the IP address
    device_state['interfaces'][interface_name]['ip_address'] = ip_addr
    device_state['interfaces'][interface_name]['ipAddress'] = ip_addr  # Also set camelCase for frontend
    device_state['interfaces'][interface_name]['subnet_mask'] = subnet_mask
    device_state['interfaces'][interface_name]['subnetMask'] = subnet_mask
    
    logger.info(f"✅ Configured {interface_name} on {device_id}: IP={ip_addr}, Mask={subnet_mask}")
    
    return f"IP address {ip_addr} {subnet_mask} configured on {interface_name}"


def handle_interface_no_shutdown(device_state, device_id, interface_name, session_data):
    """Bring interface up (no shutdown)"""
    import logging
    logger = logging.getLogger(__name__)
    
    if 'interfaces' not in device_state:
        device_state['interfaces'] = {}
    
    if interface_name not in device_state['interfaces']:
        device_state['interfaces'][interface_name] = {}
    
    device_state['interfaces'][interface_name]['status'] = 'up'
    device_state['interfaces'][interface_name]['protocol'] = 'up'
    
    logger.info(f"✅ Interface {interface_name} on {device_id} is now UP")
    
    return f"{interface_name} is now administratively up"


def handle_interface_shutdown(device_state, device_id, interface_name, session_data):
    """Shutdown interface"""
    import logging
    logger = logging.getLogger(__name__)
    
    if 'interfaces' not in device_state:
        device_state['interfaces'] = {}
    
    if interface_name not in device_state['interfaces']:
        device_state['interfaces'][interface_name] = {}
    
    device_state['interfaces'][interface_name]['status'] = 'down'
    device_state['interfaces'][interface_name]['protocol'] = 'down'
    
    logger.info(f"⚠️ Interface {interface_name} on {device_id} is now DOWN")
    
    return f"{interface_name} is now administratively down"


def handle_interface_command(args, device_state):
    """Handle interface configuration commands"""
    if not args:
        # Show all interfaces
        interfaces = device_state.get('interfaces', {})
        if not interfaces:
            return "% No interfaces configured"
        
        output = ""
        for int_name, int_config in interfaces.items():
            status = "up" if int_config.get('status') == 'up' else "administratively down"
            protocol = "up" if int_config.get('status') == 'up' else "down"
            ip_addr = int_config.get('ip_address', 'unassigned')
            
            output += f"{int_name} is {status}, line protocol is {protocol}\n"
            output += f"  Internet address is {ip_addr}\n"
            output += f"  MTU {int_config.get('mtu', '1500')} bytes, BW {int_config.get('bandwidth', '1000000')} Kbit/sec\n"
            output += f"  Encapsulation ARPA, loopback not set\n"
            output += f"  Last input never, output never, output hang never\n"
            output += f"  Last clearing of \"show interface\" counters never\n"
            output += f"  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0\n"
            output += f"  5 minute input rate 0 bits/sec, 0 packets/sec\n"
            output += f"  5 minute output rate 0 bits/sec, 0 packets/sec\n\n"
        
        return output
    
    # Handle specific interface
    interface_name = args[0]
    interfaces = device_state.get('interfaces', {})
    
    if interface_name not in interfaces:
        return f"% Invalid interface type and number: {interface_name}"
    
    int_config = interfaces[interface_name]
    status = "up" if int_config.get('status') == 'up' else "administratively down"
    protocol = "up" if int_config.get('status') == 'up' else "down"
    ip_addr = int_config.get('ip_address', 'unassigned')
    
    return f"""
{interface_name} is {status}, line protocol is {protocol}
  Hardware is {int_config.get('hardware', 'Gigabit Ethernet')}, address is {int_config.get('mac', '0050.56c0.0001')}
  Internet address is {ip_addr}
  MTU {int_config.get('mtu', '1500')} bytes, BW {int_config.get('bandwidth', '1000000')} Kbit/sec, DLY {int_config.get('delay', '10')} usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Full Duplex, 1000Mbps, media type is T
  output flow-control is unsupported, input flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input never, output 00:00:01, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/2000/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 0 bits/sec, 0 packets/sec
     0 packets input, 0 bytes, 0 no buffer
     Received 0 broadcasts (0 IP multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog, 0 multicast, 0 pause input
     0 packets output, 0 bytes, 0 underruns
     0 output errors, 0 collisions, 1 interface resets
     0 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier, 0 pause output
     0 output buffer failures, 0 output buffers swapped out
"""

def handle_ip_command(args, device_state):
    """Handle IP-related commands"""
    if not args:
        return "% Incomplete command."
    
    subcommand = args[0].lower()
    
    if subcommand == "route":
        # Show routing table
        routes = device_state.get('routes', [])
        if not routes:
            return """Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area 
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override, p - overrides from PfR

Gateway of last resort is not set
"""
        
        output = """Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area 
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override, p - overrides from PfR

Gateway of last resort is not set

"""
        
        for route in routes:
            route_type = route.get('type', 'C')
            network = route.get('network', '192.168.1.0/24')
            next_hop = route.get('next_hop', 'is directly connected')
            interface = route.get('interface', 'GigabitEthernet0/0')
            
            if next_hop == 'is directly connected':
                output += f"     {route_type}    {network} is directly connected, {interface}\n"
            else:
                output += f"     {route_type}    {network} [{route.get('admin_distance', '1')}/{route.get('metric', '0')}] via {next_hop}, {interface}\n"
        
        return output
    
    elif subcommand == "interface":
        if len(args) < 2:
            return "% Incomplete command."
        return handle_interface_command(args[1:], device_state)
    
    else:
        return f"% Invalid input detected at '^' marker: {subcommand}"

def get_help_text():
    """Generate help text for available CLI commands"""
    return """Exec commands:
  arp         ARP commands
  clear       Reset functions
  configure   Enter configuration mode
  copy        Copy from one file to another
  debug       Debugging functions (see also 'undebug')
  disable     Turn off privileged commands
  disconnect  Disconnect an existing network connection
  enable      Turn on privileged commands
  exit        Exit from the EXEC
  logout      Exit from the EXEC
  ping        Send echo messages
  reload      Halt and perform a cold restart
  resume      Resume an active network connection
  setup       Run the SETUP command facility
  show        Show running system information
  ssh         Open a secure shell client connection
  telnet      Open a telnet connection
  terminal    Set terminal line parameters
  traceroute  Trace route to destination
  undebug     Disable debugging functions (see also 'debug')
  write       Write running configuration to memory, network, or terminal
"""

def generate_running_config(device_state, device_id):
    """Generate running configuration output"""
    config = f"""Building configuration...

Current configuration : 1234 bytes
!
version 15.1
hostname {device_id.upper()}
!
"""
    
    # Add interface configurations
    interfaces = device_state.get('interfaces', {})
    for intf_name, intf_config in interfaces.items():
        config += f"interface {intf_name}\n"
        if intf_config.get('ip'):
            config += f" ip address {intf_config['ip']} {intf_config.get('mask', '255.255.255.0')}\n"
        if intf_config.get('status', 'up') == 'up':
            config += " no shutdown\n"
        config += "!\n"
    
    config += "end"
    return config

def generate_interfaces_output(device_state):
    """Generate interfaces status output"""
    output = "Interface                  IP-Address      OK? Method Status                Protocol\n"
    
    interfaces = device_state.get('interfaces', {})
    if not interfaces:
        # Default interfaces for demonstration
        interfaces = {
            'GigabitEthernet0/0': {'ip': 'unassigned', 'status': 'administratively down'},
            'GigabitEthernet0/1': {'ip': 'unassigned', 'status': 'administratively down'}
        }
    
    for intf_name, intf_config in interfaces.items():
        ip = intf_config.get('ip', 'unassigned')
        status = intf_config.get('status', 'administratively down')
        protocol = 'up' if status == 'up' else 'down'
        output += f"{intf_name:<25} {ip:<15} YES manual {status:<20} {protocol}\n"
    
    return output

def generate_ip_interfaces_output(device_state):
    """Generate detailed IP interface configuration output"""
    interfaces = device_state.get('interfaces', {})
    if not interfaces:
        return "% No interfaces configured"
    
    output = ""
    for intf_name, intf_config in interfaces.items():
        ip_addr = intf_config.get('ip_address', 'unassigned')
        subnet_mask = intf_config.get('subnet_mask', '255.255.255.0')
        status = intf_config.get('status', 'administratively down')
        protocol = 'up' if status == 'up' else 'down'
        
        output += f"{intf_name} is {status}, line protocol is {protocol}\n"
        if ip_addr != 'unassigned':
            output += f"  Internet address is {ip_addr}/{subnet_mask}\n"
            output += f"  Broadcast address is 255.255.255.255\n"
        else:
            output += f"  Internet protocol processing disabled\n"
        
        output += f"  MTU is {intf_config.get('mtu', '1500')} bytes\n"
        output += f"  Helper address is not set\n"
        output += f"  Directed broadcast forwarding is disabled\n"
        output += f"  Outgoing access list is not set\n"
        output += f"  Inbound access list is not set\n"
        output += f"  Proxy ARP is enabled\n"
        output += f"  Local proxy ARP is disabled\n"
        output += f"  Security level is default\n"
        output += f"  Split horizon is enabled\n\n"
    
    return output

def generate_ip_interfaces_brief(device_state):
    """Generate brief IP interface status output"""
    output = "Interface                  IP-Address      OK? Method Status                Protocol\n"
    
    interfaces = device_state.get('interfaces', {})
    if not interfaces:
        # Default interfaces for demonstration
        interfaces = {
            'GigabitEthernet0/0': {'ip_address': 'unassigned', 'status': 'administratively down'},
            'GigabitEthernet0/1': {'ip_address': 'unassigned', 'status': 'administratively down'}
        }
    
    for intf_name, intf_config in interfaces.items():
        ip = intf_config.get('ip_address', 'unassigned')
        status = intf_config.get('status', 'administratively down')
        protocol = 'up' if status == 'up' else 'down'
        method = 'manual' if ip != 'unassigned' else 'unset'
        ok_status = 'YES' if ip != 'unassigned' else 'NO'
        
        output += f"{intf_name:<25} {ip:<15} {ok_status:<3} {method:<6} {status:<20} {protocol}\n"
    
    return output

def generate_routing_table(device_state):
    """Generate routing table output"""
    output = """Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area 
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override

Gateway of last resort is not set

"""
    
    routes = device_state.get('routingTable', [])
    for route in routes:
        network = route.get('network', '192.168.1.0/24')
        interface = route.get('interface', 'GigabitEthernet0/0')
        route_type = route.get('type', 'C')
        output += f"{route_type}        {network} is directly connected, {interface}\n"
    
    return output

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/validate-step', methods=['POST'])
@user_login_required
def validate_simulation_step(simulation_id):
    """Validate current simulation step with enhanced network state checking"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}

        step_index = int(data.get('stepIndex', 0))
        network_state = data.get('networkState') or {}
        topology = data.get('topology') or data.get('networkTopology') or {}

        simulation = Simulation.query.get_or_404(simulation_id)
        steps = simulation.step_definitions or []

        validation_rule = data.get('validation') or {}
        if not validation_rule and 0 <= step_index < len(steps):
            validation_rule = (steps[step_index] or {}).get('validation') or {}

        step_type = validation_rule.get('type') or (steps[step_index].get('type') if 0 <= step_index < len(steps) else None)

        message = "Validation failed"
        score = 0
        is_valid = False

        if step_type == 'network_config':
            expected_config = validation_rule.get('expected_config', {})
            result = validate_network_configuration(network_state, expected_config)
            is_valid = result.get('valid')
            message = "Network configuration is correct!" if is_valid else ("; ".join(result.get('errors') or []) or "Incorrect device configuration.")
            score = validation_rule.get('score', 10) if is_valid else 0

        elif step_type == 'connectivity':
            expected_topology = validation_rule.get('expected_topology', {})
            result = validate_network_connectivity(topology or network_state)
            # If expected_topology has expected_connections, reinforce that check
            missing = []
            if 'expected_connections' in expected_topology:
                exp = expected_topology['expected_connections'] or []
                actual = []
                if isinstance(topology, dict):
                    # support either { connections: [{from,to}, ...] } or networkConnections in state
                    links = topology.get('connections') or topology.get('links') or network_state.get('networkConnections') or []
                    for l in links:
                        f = l.get('from') or l.get('a') or l.get('source')
                        t = l.get('to') or l.get('b') or l.get('target')
                        if f and t:
                            actual.append((str(f), str(t)))
                for (a, b) in exp:
                    if not any((x == a and y == b) or (x == b and y == a) for (x, y) in actual):
                        missing.append(f"Missing connection: {a} - {b}")
            is_valid = result.get('isValid', result.get('valid', False)) and not missing
            message = "Network connectivity is correct!" if is_valid else ("; ".join(missing) or "Incorrect connectivity.")
            score = validation_rule.get('score', 10) if is_valid else 0

        elif step_type == 'troubleshooting':
            # keep existing troubleshooting flow if present
            is_valid = False  # implement if needed
            message = "Troubleshooting validation not implemented"
            score = 0

        return jsonify({
            'success': True,
            'valid': is_valid,
            'message': message,
            'score': score,
            'stepIndex': step_index
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/task-mode', methods=['GET'])
@user_login_required
def get_task_mode(simulation_id):
    """Get current task mode for simulation"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get simulation
        simulation = Simulation.query.get_or_404(simulation_id)
        simulation_config = simulation.simulation_config or {}
        
        # Parse simulation_config if it's a string
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except (json.JSONDecodeError, ValueError):
                simulation_config = {}
        
        task_mode = simulation_config.get('task_mode', 'combined')
        topology_locked = task_mode in ['configuration']
        configuration_enabled = task_mode in ['configuration', 'combined']
        
        return jsonify({
            'success': True,
            'task_mode': task_mode,
            'topology_locked': topology_locked,
            'configuration_enabled': configuration_enabled,
            'instructor_provided_topology': simulation_config.get('instructor_topology', {}),
            'device_config_templates': simulation_config.get('device_templates', {})
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/admin-topology', methods=['GET'])
@user_login_required
def get_instructor_topology(simulation_id):
    """Get admin-provided topology for configuration mode"""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get simulation
        simulation = Simulation.query.get_or_404(simulation_id)
        simulation_config = simulation.simulation_config or {}
        
        # Parse simulation_config if it's a string
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except (json.JSONDecodeError, ValueError):
                simulation_config = {}
        
        task_mode = simulation_config.get('task_mode', 'combined')
        
        # Only return admin topology if in configuration mode
        if task_mode not in ['configuration', 'combined']:
            return jsonify({
                'success': False,
                'message': 'Admin topology only available in configuration or combined mode'
            }), 400
        
        instructor_topology = simulation_config.get('instructor_topology', {})
        device_templates = simulation_config.get('device_templates', {})
        
        return jsonify({
            'success': True,
            'instructor_topology': instructor_topology,
            'device_templates': device_templates,
            'task_mode': task_mode
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/complete', methods=['POST'])
@user_login_required
def complete_simulation(simulation_id):
    """Complete a simulation and update progress"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}

        # Find latest in-progress attempt
        attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id,
            is_completed=False
        ).order_by(SimulationAttempt.started_at.desc()).first()

        if not attempt:
            return jsonify({'error': 'Simulation not started'}), 400

        # Store time spent from client
        attempt.time_spent_seconds = int(data.get('time_spent', 0) or 0)

        # Recompute final score from stored step responses (ignore client score)
        final_score = 0
        if attempt.step_responses:
            for step_resp in attempt.step_responses.values():
                if isinstance(step_resp, dict) and step_resp.get('awarded_score'):
                    final_score += step_resp['awarded_score']
        
        # Update attempt total to match recomputed score
        attempt.total_score = final_score
        attempt.complete_attempt(final_score=final_score)

        # Update simulation analytics
        sim = Simulation.query.get(simulation_id)
        if sim:
            sim.update_analytics({
                'completed': True,
                'score': attempt.total_score,
                'duration': attempt.time_spent_seconds
            })

        # Save score to Score table for dashboard display (topology category)
        # This ensures Link Up scores appear on the dashboard
        try:
            new_score = Score(
                user_id=user.id,
                score=final_score,
                category='topology'  # Link Up challenges use topology category
            )
            db.session.add(new_score)
            print(f"✅ Topology score {final_score} saved for user {user.id}")
        except Exception as score_error:
            print(f"⚠️ Error saving topology score to Score table: {score_error}")
            # Don't fail the entire request if score save fails

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Simulation completed successfully',
            'totalScore': final_score,
            'unlocked_simulations': []
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== ENHANCED VALIDATION AND TROUBLESHOOTING API ROUTES =====

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/validate-network', methods=['POST'])
@user_login_required
def validate_network_api(simulation_id):
    """Enhanced network configuration validation API"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        
        # Get current network state from request
        network_state = data.get('networkState', {})
        expected_config = data.get('expectedConfig', {})
        
        # If no expected config provided, get from simulation
        if not expected_config:
            simulation = Simulation.query.get_or_404(simulation_id)
            expected_config = simulation.expected_configuration or {}
            if isinstance(expected_config, str):
                try:
                    expected_config = json.loads(expected_config)
                except:
                    expected_config = {}
        
        # Perform comprehensive validation
        validation_result = validate_network_configuration(network_state, expected_config)
        
        # Log validation attempt
        print(f"Network validation for simulation {simulation_id}: {validation_result['valid']}")
        
        return jsonify({
            'success': True,
            'validation': validation_result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Network validation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/validate-device', methods=['POST'])
@user_login_required
def validate_device_api(simulation_id):
    """Validate a specific device configuration"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        
        device_id = data.get('deviceId')
        device_state = data.get('deviceState', {})
        expected_config = data.get('expectedConfig', {})
        
        if not device_id:
            return jsonify({'error': 'Device ID required'}), 400
        
        # Perform single device validation
        validation_result = validate_single_device(device_id, device_state, expected_config)
        
        return jsonify({
            'success': True,
            'validation': validation_result,
            'deviceId': device_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/troubleshoot', methods=['POST'])
@user_login_required
def troubleshooting_api(simulation_id):
    """Handle troubleshooting mode operations"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        
        action = data.get('action')
        
        if action == 'start_session':
            # Initialize troubleshooting session
            problem_type = data.get('problemType', 'random')
            
            # Generate or select a problem based on current network state
            troubleshooting_problem = {
                'id': f'problem_{datetime.utcnow().timestamp()}',
                'type': problem_type,
                'description': 'Network connectivity issues detected',
                'hints': [
                    'Check device interface status',
                    'Verify IP address configuration',
                    'Test network connectivity'
                ],
                'expected_solution': {
                    'steps': [
                        'Identify the problematic device',
                        'Check interface configuration',
                        'Correct the configuration',
                        'Verify connectivity'
                    ]
                }
            }
            
            return jsonify({
                'success': True,
                'problem': troubleshooting_problem,
                'session_started': True
            })
        
        elif action == 'run_diagnostic':
            # Run diagnostic tool
            tool_name = data.get('tool')
            network_state = data.get('networkState', {})
            
            diagnostic_result = run_diagnostic_tool(tool_name, network_state)
            
            return jsonify({
                'success': True,
                'diagnostic': diagnostic_result,
                'tool': tool_name
            })
        
        elif action == 'get_hint':
            # Provide troubleshooting hint
            problem_id = data.get('problemId')
            hint_level = data.get('hintLevel', 1)
            
            hints = {
                1: "Start by checking the status of all network interfaces",
                2: "Look for devices with 'down' interfaces or missing IP addresses", 
                3: "Use the 'show interfaces' command to identify configuration issues"
            }
            
            return jsonify({
                'success': True,
                'hint': hints.get(hint_level, "No more hints available"),
                'hint_level': hint_level
            })
        
        else:
            return jsonify({'error': 'Invalid action'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/autosave', methods=['POST'])
@user_login_required
def autosave_simulation_progress(simulation_id):
    """Auto-save simulation progress including topology data"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        
        # Get current attempt
        attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id,
            is_completed=False
        ).first()
        
        if not attempt:
            return jsonify({'error': 'No active simulation found'}), 400
        
        # Update session data with progress including device count
        if not attempt.session_data:
            attempt.session_data = {}
        elif isinstance(attempt.session_data, str):
            try:
                attempt.session_data = json.loads(attempt.session_data)
            except (json.JSONDecodeError, ValueError):
                attempt.session_data = {}
        
        # Update progress data
        progress_data = {
            'lastUpdated': datetime.utcnow().isoformat(),
            'autoSaveSource': 'dynamic_simulation'
        }
        
        # Include topology and device data if provided
        if 'topology' in data:
            progress_data['networkTopology'] = data['topology']
            device_count = len(data['topology'].get('devices', []))
            progress_data['deviceCount'] = device_count
            
            # Notify admin of device count for consistency
            try:
                import requests
                sync_data = {
                    'device_count': device_count,
                    'source_page': 'dynamic_simulation_autosave',
                    'devices': data['topology'].get('devices', [])
                }
                # Don't await this - fire and forget for performance
                # The device sync API will handle the update
                pass  # Will be implemented if needed
            except Exception as e:
                print(f"Note: Could not sync device count: {e}")
        
        if 'deviceStates' in data:
            progress_data['deviceStates'] = data['deviceStates']
        
        if 'currentStep' in data:
            progress_data['currentStep'] = data['currentStep']
            attempt.last_step_index = data['currentStep']
        
        if 'answers' in data:
            progress_data['stepAnswers'] = data['answers']
        
        attempt.session_data.update(progress_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress auto-saved',
            'timestamp': progress_data['lastUpdated'],
            'deviceCount': progress_data.get('deviceCount', 0)
        })
        
    except Exception as e:
        print(f"Error auto-saving simulation progress: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/current-device-count', methods=['GET'])
@user_login_required
def get_current_device_count(simulation_id):
    """Get current device count from dynamic simulation session"""
    try:
        user = get_user_from_session()
        
        # Get current attempt
        attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id,
            is_completed=False
        ).first()
        
        device_count = 0
        source = 'none'
        
        if attempt and attempt.session_data:
            session_data = attempt.session_data
            if isinstance(session_data, str):
                try:
                    session_data = json.loads(session_data)
                except Exception:
                    session_data = {}
            
            # Check for device count in session data
            if 'deviceCount' in session_data:
                device_count = session_data['deviceCount']
                source = 'session_data'
            elif 'networkTopology' in session_data:
                topology = session_data['networkTopology']
                device_count = len(topology.get('devices', []))
                source = 'session_topology'
        
        # Fallback to database
        if device_count == 0:
            simulation = Simulation.query.get(simulation_id)
            if simulation:
                simulation_config = simulation.simulation_config or {}
                if isinstance(simulation_config, str):
                    try:
                        simulation_config = json.loads(simulation_config)
                    except Exception:
                        simulation_config = {}
                
                network_topology = simulation_config.get('network_topology', {})
                device_count = len(network_topology.get('devices', []))
                source = 'database'
        
        return jsonify({
            'success': True,
            'simulation_id': simulation_id,
            'device_count': device_count,
            'source': source,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@user_login_required
def autosave_progress(simulation_id):
    """Auto-save simulation progress"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        
        progress_data = data.get('progress_data', {})

        # Find or create simulation attempt
        attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id,
            is_completed=False
        ).first()

        if not attempt:
            attempt = SimulationAttempt(
                user_id=user.id,
                simulation_id=simulation_id,
                started_at=datetime.utcnow()
            )
            db.session.add(attempt)

        # Merge into session_data and timestamp
        if not attempt.session_data:
            attempt.session_data = {}
        elif isinstance(attempt.session_data, str):
            try:
                attempt.session_data = json.loads(attempt.session_data)
            except (json.JSONDecodeError, ValueError):
                attempt.session_data = {}
        # Shallow merge expected keys
        for k in ['networkTopology', 'deviceStates', 'cliHistory']:
            if k in progress_data:
                attempt.session_data[k] = progress_data[k]
        attempt.session_data['lastUpdated'] = datetime.utcnow().isoformat()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress auto-saved',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_diagnostic_tool(tool_name, network_state):
    """Simulate diagnostic tool execution"""
    device_states = network_state.get('deviceStates', {})
    
    if tool_name == 'ping':
        return simulate_ping_diagnostic(device_states)
    elif tool_name == 'traceroute':
        return simulate_traceroute_diagnostic(device_states)
    elif tool_name == 'show-interfaces':
        return simulate_show_interfaces_diagnostic(device_states)
    elif tool_name == 'show-routing':
        return simulate_show_routing_diagnostic(device_states)
    elif tool_name == 'network-scan':
        return simulate_network_scan_diagnostic(device_states)
    else:
        return {'result': f'Unknown diagnostic tool: {tool_name}'}

def simulate_ping_diagnostic(device_states):
    """Simulate ping diagnostic results"""
    # Check for connectivity issues
    issues_found = []
    
    for device_id, device_state in device_states.items():
        interfaces = device_state.get('interfaces', {})
        for intf_name, intf_config in interfaces.items():
            if intf_config.get('status') == 'down':
                issues_found.append(f'{device_id}:{intf_name} is down')
    
    if issues_found:
        result = f"""PING 192.168.1.1: 56 data bytes
Request timeout for icmp_seq 0
Request timeout for icmp_seq 1
Request timeout for icmp_seq 2

--- 192.168.1.1 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss

Issues detected: {', '.join(issues_found)}"""
    else:
        result = """PING 192.168.1.1: 56 data bytes
64 bytes from 192.168.1.1: icmp_seq=0 ttl=64 time=0.123 ms
64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.098 ms
64 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=0.145 ms

--- 192.168.1.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss
round-trip min/avg/max/stddev = 0.098/0.122/0.145/0.024 ms"""
    
    return {'result': result}

def simulate_show_interfaces_diagnostic(device_states):
    """Simulate show interfaces command results"""
    result = "Interface Status Report:\n\n"
    
    for device_id, device_state in device_states.items():
        result += f"Device: {device_id}\n"
        interfaces = device_state.get('interfaces', {})
        
        for intf_name, intf_config in interfaces.items():
            status = intf_config.get('status', 'down')
            ip_addr = intf_config.get('ip_address', 'unassigned')
            status_icon = '🟢' if status == 'up' else '🔴'
            
            result += f"  {intf_name}: {status_icon} {status} - IP: {ip_addr}\n"
        
        result += "\n"
    
    return {'result': result}

def simulate_traceroute_diagnostic(device_states):
    """Simulate traceroute diagnostic results"""
    # Simple traceroute simulation
    result = """traceroute to 192.168.1.1 (192.168.1.1), 30 hops max, 60 byte packets
 1  192.168.1.1 (192.168.1.1)  0.123 ms  0.089 ms  0.145 ms
 2  10.0.0.1 (10.0.0.1)  1.234 ms  1.156 ms  1.289 ms
 3  172.16.1.1 (172.16.1.1)  5.678 ms  5.234 ms  5.789 ms"""
    
    return {'result': result}

def simulate_show_routing_diagnostic(device_states):
    """Simulate show routing table command results"""
    result = "Routing Table:\n\n"
    
    for device_id, device_state in device_states.items():
        result += f"Device: {device_id}\n"
        routing_table = device_state.get('routingTable', [])
        
        if routing_table:
            result += "Codes: C - connected, S - static, D - EIGRP, R - RIP, O - OSPF\n\n"
            for route in routing_table:
                network = route.get('network', '0.0.0.0/0')
                gateway = route.get('gateway', 'directly connected')
                route_type = route.get('type', 'C')
                metric = route.get('metric', 0)
                
                result += f"{route_type}    {network} [{metric}/0] via {gateway}\n"
        else:
            result += "No routes configured\n"
        
        result += "\n"
    
    return {'result': result}

def simulate_network_scan_diagnostic(device_states):
    """Simulate network discovery scan results"""
    result = "Network Device Discovery:\n\n"
    
    discovered_devices = []
    for device_id, device_state in device_states.items():
        interfaces = device_state.get('interfaces', {})
        for intf_name, intf_config in interfaces.items():
            if intf_config.get('status') == 'up' and intf_config.get('ip_address'):
                ip = intf_config.get('ip_address', '').split(' ')[0]
                discovered_devices.append({
                    'device': device_id,
                    'interface': intf_name,
                    'ip': ip,
                    'status': 'active'
                })
    
    if discovered_devices:
        result += "Active Devices Found:\n"
        for device in discovered_devices:
            result += f"  {device['ip']} - {device['device']} ({device['interface']}) - {device['status']}\n"
    else:
        result += "No active devices found on network\n"
    
    result += f"\nScan completed. {len(discovered_devices)} devices discovered.\n"
    
    return {'result': result}

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/device-config', methods=['POST'])
@user_login_required
def update_device_configuration(simulation_id):
    """API endpoint to update device configuration"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        config = data.get('config', {})
        
        if not device_id:
            return jsonify({'success': False, 'error': 'Device ID is required'}), 400
        
        # Get current attempt
        user_id = session.get('user_id')
        attempt = SimulationAttempt.query.filter_by(
            user_id=user_id,
            simulation_id=simulation_id,
            is_completed=False
        ).order_by(SimulationAttempt.started_at.desc()).first()
        
        if not attempt:
            return jsonify({'success': False, 'error': 'No active simulation attempt found'}), 404

        # Parse existing session data
        session_data = attempt.session_data or {}
        if isinstance(session_data, str):
            try:
                session_data = json.loads(session_data)
            except (json.JSONDecodeError, ValueError):
                session_data = {}
        network_state = session_data
        device_states = network_state.get('deviceStates', {})
        network_devices = network_state.get('networkDevices', [])
        
        # Update device configuration
        if device_id not in device_states:
            device_states[device_id] = {}
        
        device_states[device_id].update(config)
        
        # Also update the device in networkDevices array if it exists
        for device in network_devices:
            if device.get('id') == device_id:
                device['config'] = device.get('config', {})
                device['config'].update(config)
                break
        
        # Update network state
        network_state['deviceStates'] = device_states
        network_state['networkDevices'] = network_devices
        network_state['lastModified'] = datetime.utcnow().isoformat()

        # Save updated state
        attempt.session_data = network_state
        db.session.commit()
        
        # Validate configuration
        validation_result = validate_device_config(device_id, config)
        
        return jsonify({
            'success': True,
            'message': f'Device {device_id} configuration updated successfully',
            'validation': validation_result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/topology', methods=['GET'])
@user_login_required
def get_simulation_topology(simulation_id):
    """Get topology data for a simulation with attempt-specific overrides"""
    try:
        user = get_user_from_session()
        
        # Get simulation from database
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Parse simulation config
        simulation_config = simulation.simulation_config or {}
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except Exception:
                simulation_config = {}
        
        # Get admin-defined topology
        network_topology = simulation_config.get('network_topology', {})
        instructor_topology = network_topology if (network_topology.get('devices') or network_topology.get('connections')) else simulation_config
        
        # Check for attempt-specific topology and device states
        attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id,
            is_completed=False
        ).order_by(SimulationAttempt.started_at.desc()).first()
        
        attempt_topology = None
        device_states = {}
        actual_device_count = 0
        
        if attempt and attempt.session_data:
            session_data = attempt.session_data
            if isinstance(session_data, str):
                try:
                    session_data = json.loads(session_data)
                except (json.JSONDecodeError, ValueError):
                    session_data = {}
            
            # Get attempt-specific topology
            attempt_topology = session_data.get('networkTopology')
            
            # Get device states to count actual active devices
            device_states = session_data.get('deviceStates', {})
            if isinstance(device_states, dict):
                actual_device_count = len(device_states)
        
        # Determine source and topology to return
        if attempt_topology:
            topology = attempt_topology
            source = 'attempt'
            last_modified = attempt.updated_at.isoformat() if attempt.updated_at else None
        else:
            topology = instructor_topology
            source = 'admin' if network_topology else 'legacy'
            last_modified = simulation.updated_at.isoformat() if simulation.updated_at else None
        
        # Validate topology structure
        if not isinstance(topology, dict):
            return jsonify({'error': 'Invalid topology data format'}), 400
        
        # Ensure devices and connections are arrays
        devices = topology.get('devices', [])
        connections = topology.get('connections', topology.get('links', []))
        
        if not isinstance(devices, list):
            devices = []
        if not isinstance(connections, list):
            connections = []
        
        # Use actual device count from deviceStates if available, otherwise fall back to topology devices
        final_device_count = actual_device_count if actual_device_count > 0 else len(devices)
        
        return jsonify({
            'topology': {
                'devices': devices,
                'connections': connections
            },
            'source': source,
            'lastModified': last_modified,
            'metadata': {
                'simulationId': simulation_id,
                'attemptId': attempt.id if attempt else None,
                'hasAttemptData': attempt_topology is not None,
                'deviceCount': final_device_count,
                'connectionCount': len(connections),
                'deviceStatesCount': actual_device_count,
                'topologyDevicesCount': len(devices)
            }
        })
        
    except Exception as e:
        print(f"Error getting topology for simulation {simulation_id}: {e}")
        return jsonify({
            'error': 'Failed to retrieve topology data',
            'details': str(e) if current_app.debug else 'Internal server error'
        }), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/device-config/<device_id>', methods=['GET'])
@user_login_required
def get_device_configuration(simulation_id, device_id):
    """API endpoint to get device configuration"""
    try:
        # Get current attempt
        user_id = session.get('user_id')
        attempt = SimulationAttempt.query.filter_by(
            user_id=user_id,
            simulation_id=simulation_id,
            is_completed=False
        ).order_by(SimulationAttempt.started_at.desc()).first()
        
        if not attempt:
            return jsonify({'success': False, 'error': 'No active simulation attempt found'}), 404
        
        # Parse session data
        session_data = attempt.session_data or {}
        if isinstance(session_data, str):
            try:
                session_data = json.loads(session_data)
            except (json.JSONDecodeError, ValueError):
                session_data = {}
        network_state = session_data
        device_states = network_state.get('deviceStates', {})
        
        # Get device configuration
        device_config = device_states.get(device_id, {})
        
        return jsonify({
            'success': True,
            'config': device_config
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def validate_device_config(device_id, config):
    """Validate device configuration"""
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Validate IP addresses in interfaces
        if 'interfaces' in config:
            for intf_name, intf_config in config['interfaces'].items():
                if 'ip_address' in intf_config:
                    ip_addr = intf_config['ip_address']
                    if ip_addr and not is_valid_ip_config(ip_addr):
                        validation_result['errors'].append(f'Invalid IP configuration on {intf_name}: {ip_addr}')
                        validation_result['valid'] = False
        
        # Validate routing table
        if 'routes' in config:
            for route in config['routes']:
                if 'network' in route and route['network']:
                    if not is_valid_network(route['network']):
                        validation_result['errors'].append(f'Invalid route network: {route["network"]}')
                        validation_result['valid'] = False
                        
                if 'gateway' in route and route['gateway']:
                    if not is_valid_ip_address(route['gateway']):
                        validation_result['errors'].append(f'Invalid route gateway: {route["gateway"]}')
                        validation_result['valid'] = False
        
        # Validate VLANs
        if 'vlans' in config:
            for vlan_id, vlan_config in config['vlans'].items():
                try:
                    vlan_id_int = int(vlan_id)
                    if vlan_id_int < 1 or vlan_id_int > 4094:
                        validation_result['errors'].append(f'Invalid VLAN ID: {vlan_id} (must be 1-4094)')
                        validation_result['valid'] = False
                except ValueError:
                    validation_result['errors'].append(f'Invalid VLAN ID format: {vlan_id}')
                    validation_result['valid'] = False
        
    except Exception as e:
        validation_result['errors'].append(f'Configuration validation error: {str(e)}')
        validation_result['valid'] = False
    
    return validation_result

def is_valid_ip_config(ip_config):
    """Validate IP configuration string (e.g., '192.168.1.1 255.255.255.0')"""
    try:
        parts = ip_config.strip().split()
        if len(parts) >= 1:
            # Validate IP address
            ip_parts = parts[0].split('.')
            if len(ip_parts) != 4:
                return False
            for part in ip_parts:
                if not (0 <= int(part) <= 255):
                    return False
        
        if len(parts) >= 2:
            # Validate subnet mask
            mask_parts = parts[1].split('.')
            if len(mask_parts) != 4:
                return False
            for part in mask_parts:
                if not (0 <= int(part) <= 255):
                    return False
        
        return True
    except:
        return False

def is_valid_network(network):
    """Validate network address (CIDR or network/mask format)"""
    try:
        if '/' in network:
            # CIDR format
            ip, prefix = network.split('/')
            prefix_int = int(prefix)
            if not (0 <= prefix_int <= 32):
                return False
            return is_valid_ip_address(ip)
        else:
            # Just an IP address
            return is_valid_ip_address(network)
    except:
        return False

def is_valid_ip_address(ip):
    """Validate IP address format"""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            if not (0 <= int(part) <= 255):
                return False
        return True
    except:
        return False

# ===== Helper: Assignment gating =====
def check_assignment_gating(user, simulation_id):
    """Check if user is allowed to start based on active assignments in their classes.
    Returns dict: {allowed: bool, message: str, details: {...}}
    If no assignment applies, allow by default.
    """
    try:
        # Get user's enrolled class IDs
        class_ids = [c.id for c in (user.enrolled_classes.all() if hasattr(user, 'enrolled_classes') else [])]
        if not class_ids:
            # No class enrollment -> allow unless policy says otherwise
            return {'allowed': True, 'message': 'No class enrollment gating', 'details': {}}

        # Find active/published assignments tied to this simulation and user's classes
        q = SimulationAssignment.query.filter(
            SimulationAssignment.simulation_id == simulation_id,
            SimulationAssignment.class_id.in_(class_ids),
            SimulationAssignment.is_active.is_(True),
            SimulationAssignment.is_published.is_(True)
        )
        assignment = q.order_by(SimulationAssignment.due_date.asc().nulls_last()).first()
        if not assignment:
            return {'allowed': True, 'message': 'No assignment gating', 'details': {}}

        # Use model's can_user_attempt to enforce attempts and availability
        can_attempt, reason = assignment.can_user_attempt(user.id)
        attempts = assignment.get_user_attempts(user.id)
        return {
            'allowed': bool(can_attempt),
            'message': reason if not can_attempt else 'OK',
            'details': {
                'assignment_id': assignment.id,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'max_attempts': assignment.max_attempts,
                'attempts_used': len(attempts),
                'is_available': assignment.is_available
            }
        }
    except Exception as e:
        # Fail-open with log
        print(f"Assignment gating error: {e}")
        return {'allowed': True, 'message': 'Gating check failed open', 'details': {'error': str(e)}}

# Register routes dynamically
def register_dynamic_routes(app):
    """Register all dynamic simulation routes"""
    app.register_blueprint(dynamic_sim_bp)

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/collaboration-settings', methods=['GET'])
@user_login_required
def get_collaboration_settings(simulation_id):
    """Get collaboration settings for a simulation"""
    try:
        from instructor.models.collaboration import CollaborationSetting
        
        # Get collaboration settings for this simulation
        settings = CollaborationSetting.query.filter_by(simulation_id=simulation_id).first()
        
        if not settings:
            return jsonify({
                'success': True,
                'settings': {
                    'collaboration_enabled': False,
                    'team_size': 2,
                    'shared_terminal': False,
                    'individual_terminals': True,
                    'follow_leader': False,
                    'chat_enabled': False,
                    'transcript_logging': False,
                    'allow_late_join': True,
                    'require_instructor': False,
                    'time_window': None,
                    'roles': ['Leader', 'Observer', 'Operator']
                }
            })
        
        return jsonify({
            'success': True,
            'settings': {
                'collaboration_enabled': settings.collaboration_enabled,
                'team_size': settings.team_size or 2,
                'shared_terminal': settings.shared_terminal or False,
                'individual_terminals': settings.individual_terminals if settings.individual_terminals is not None else True,
                'follow_leader': settings.follow_leader or False,
                'chat_enabled': settings.chat_enabled or False,
                'transcript_logging': settings.transcript_logging or False,
                'allow_late_join': settings.allow_late_join if settings.allow_late_join is not None else True,
                'require_instructor': settings.require_instructor or False,
                'time_window': settings.time_window,
                'roles': settings.roles or ['Leader', 'Observer', 'Operator']
            }
        })
        
    except Exception as e:
        print(f"Error getting collaboration settings for simulation {simulation_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/join-lobby', methods=['POST'])
@user_login_required
def join_collaboration_lobby(simulation_id):
    """Join a collaboration lobby for a simulation"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        lobby_id = data.get('lobby_id')
        
        if not lobby_id:
            return jsonify({
                'success': False,
                'error': 'Lobby ID is required'
            }), 400
        
        # Get collaboration settings to verify lobby is allowed
        from instructor.models.collaboration import CollaborationSetting, CollaborationLobby, TeamAssignment
        
        setting = CollaborationSetting.query.filter_by(simulation_id=simulation_id).first()
        if not setting or not setting.collaboration_enabled:
            return jsonify({
                'success': False,
                'error': 'Collaboration is not enabled for this simulation'
            }), 400
        
        # Check if lobby exists and is active
        db_lobby = CollaborationLobby.query.get(lobby_id)
        if not db_lobby or not db_lobby.is_active or db_lobby.simulation_id != simulation_id:
            return jsonify({
                'success': False,
                'error': 'Lobby not found or inactive'
            }), 404
        
        # Try to get lobby from memory or restore it
        from services.troubleshooting_lobbies import lobby_manager
        
        lobby = lobby_manager.get_lobby(lobby_id)
        if not lobby:
            # Restore lobby to memory
            lobby_config = {
                'name': db_lobby.name,
                'scenario_type': db_lobby.scenario_type,
                'scenario_id': db_lobby.scenario_id,
                'max_participants': db_lobby.max_participants,
                'class_id': db_lobby.class_id,
                'simulation_id': db_lobby.simulation_id,
                'instructor_created': True,
                'collaboration_settings': setting.to_dict()
            }
            lobby = lobby_manager.create_lobby(
                creator_id=db_lobby.creator_id,
                creator_name=db_lobby.creator_name,
                creator_profile_image=db_lobby.creator_profile_image,
                lobby_config=lobby_config,
                lobby_id=lobby_id
            )
        
        # Check if user can join (not already in lobby)
        # Check if user is already assigned to a team in this lobby
        existing_assignments = TeamAssignment.query.filter_by(lobby_id=lobby_id).all()
        existing_assignment = None
        for assignment in existing_assignments:
            if str(user.id) in (assignment.team_members or []):
                existing_assignment = assignment
                break
        
        if existing_assignment:
            return jsonify({
                'success': True,
                'message': 'Already in lobby',
                'team_assignment': {
                    'team_name': existing_assignment.team_name,
                    'is_team_leader': existing_assignment.team_leader is not None
                },
                'lobby': lobby.to_dict()
            })
        
        # Add user to lobby memory
        success = lobby_manager.add_participant(
            lobby_id,
            str(user.id),
            user.username,
            getattr(user, 'profile_img', None)
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to join lobby - may be full'
            }), 400
        
        # Assign to team based on collaboration settings
        team_size = setting.team_size or 2
        existing_teams = TeamAssignment.query.filter_by(lobby_id=lobby_id).all()
        
        # Group by team name to find available team
        teams = {}
        for assignment in existing_teams:
            team_name = assignment.team_name
            if team_name not in teams:
                teams[team_name] = []
            teams[team_name].append(assignment)
        
        # Find team with space or create new one
        assigned_team = None
        for team_name, members in teams.items():
            if len(members) < team_size:
                assigned_team = team_name
                break
        
        if assigned_team is None:
            # Create new team
            assigned_team = f"Team {len(teams) + 1}"
        
        # Determine if user should be team leader (simple: first member is leader)
        team_members = teams.get(assigned_team, [])
        is_leader = len(team_members) == 0
        
        # Create or update team assignment in database
        if assigned_team in teams and teams[assigned_team]:
            # Update existing team assignment
            team_assignment = teams[assigned_team][0]  # Get the first (and should be only) assignment for this team
            current_members = team_assignment.team_members or []
            if str(user.id) not in current_members:
                current_members.append(str(user.id))
                team_assignment.team_members = current_members
                # Update leader if this is first member
                if not team_assignment.team_leader:
                    team_assignment.team_leader = str(user.id)
                    is_leader = True
                else:
                    is_leader = team_assignment.team_leader == str(user.id)
        else:
            # Create new team assignment
            team_assignment = TeamAssignment(
                lobby_id=lobby_id,
                class_id=lobby.class_id,
                simulation_id=simulation_id,
                team_name=assigned_team,
                team_members=[str(user.id)],
                team_leader=str(user.id),  # First member is leader
                created_by=1  # System created
            )
            is_leader = True
            db.session.add(team_assignment)
        db.session.commit()
        
        # Emit socket event to notify other participants
        from socket_events import socketio
        if socketio:
            socketio.emit('user_joined_lobby', {
                'lobby_id': lobby_id,
                'user_id': str(user.id),
                'username': user.username,
                'team_name': assigned_team,
                'is_team_leader': is_leader
            }, room=f'lobby_{lobby_id}')
        
        return jsonify({
            'success': True,
            'message': 'Successfully joined lobby',
            'team_assignment': {
                'team_name': assigned_team,
                'is_team_leader': is_leader
            },
            'lobby': lobby.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error joining collaboration lobby: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_sim_bp.route('/api/get_current_device_count', methods=['GET'])
def get_current_device_count_api():
    """Get the current device count from localStorage/session data for consistency checking"""
    try:
        simulation_id = request.args.get('simulation_id')
        if not simulation_id:
            return jsonify({'error': 'Missing simulation_id parameter'}), 400
        
        # Check if there's progress data in localStorage (via session if needed)
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401
        
        # Try to get the latest attempt data to see current device count
        latest_attempt = SimulationAttempt.query.filter_by(
            user_id=user_id,
            simulation_id=simulation_id
        ).order_by(SimulationAttempt.created_at.desc()).first()
        
        device_count = 0
        if latest_attempt and latest_attempt.progress_data:
            try:
                progress = json.loads(latest_attempt.progress_data) if isinstance(latest_attempt.progress_data, str) else latest_attempt.progress_data
                if 'network_topology' in progress and 'devices' in progress['network_topology']:
                    device_count = len(progress['network_topology']['devices'])
            except (json.JSONDecodeError, KeyError):
                pass
        
        return jsonify({
            'success': True,
            'device_count': device_count,
            'source': 'latest_attempt_data'
        })
        
    except Exception as e:
        print(f"Error getting current device count: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== NETWORK CONFIGURATION API ROUTES =====

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/network-config', methods=['GET'])
@user_login_required
def get_network_config_api(simulation_id):
    """Get network configuration for a simulation"""
    try:
        user = get_user_from_session()
        
        # Check if user has access to this simulation
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # First try to get user's saved configuration
        latest_attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id
        ).order_by(SimulationAttempt.created_at.desc()).first()
        
        network_config = {}
        
        # Get user's saved configuration from latest attempt
        if latest_attempt and latest_attempt.progress_data:
            try:
                progress = json.loads(latest_attempt.progress_data) if isinstance(latest_attempt.progress_data, str) else latest_attempt.progress_data
                network_config = progress.get('network_config', {})
            except (json.JSONDecodeError, KeyError):
                pass
        
        # If no user config, get default from simulation config
        if not network_config and simulation.simulation_config:
            try:
                sim_config = json.loads(simulation.simulation_config) if isinstance(simulation.simulation_config, str) else simulation.simulation_config
                network_config = sim_config.get('network_config', {})
            except (json.JSONDecodeError, KeyError):
                pass
        
        # If still no config, provide defaults
        if not network_config:
            network_config = {
                'networkType': 'wired',
                'networkSubnet': '192.168.1.0/24',
                'defaultGateway': '192.168.1.1',
                'ipScheme': 'dhcp',
                'routingProtocol': 'rip',
                'vlanConfig': '10 | Management | 192.168.10.0/24\n20 | Users | 192.168.20.0/24',
                'enableStp': False,
                'enableServers': True,
                'enableFirewall': True,
                'enableAcl': False,
                'enableNat': False,
                'firewallRules': 'ALLOW | 192.168.20.0/24 | 192.168.30.0/24 | HTTP\nDENY | ANY | 192.168.30.0/24 | SSH'
            }
        
        return jsonify({
            'success': True,
            'network_config': network_config,
            'simulation_id': simulation_id
        })
        
    except Exception as e:
        print(f"Error getting network configuration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/network-config', methods=['POST'])
@user_login_required
def save_network_config_api(simulation_id):
    """Save network configuration for a simulation"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        
        # Check if user has access to this simulation
        simulation = Simulation.query.get_or_404(simulation_id)
        
        network_config = data.get('network_config', {})
        if not network_config:
            return jsonify({
                'success': False,
                'error': 'Network configuration required'
            }), 400
        
        # Validate configuration
        validation_result = validate_network_config(network_config)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': 'Invalid network configuration',
                'validation_errors': validation_result['errors']
            }), 400
        
        # Get or create simulation attempt
        attempt = SimulationAttempt.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id
        ).order_by(SimulationAttempt.created_at.desc()).first()
        
        if not attempt:
            # Create new attempt
            attempt = SimulationAttempt(
                user_id=user.id,
                simulation_id=simulation_id,
                progress_data={'network_config': network_config}
            )
            db.session.add(attempt)
        else:
            # Update existing attempt
            try:
                progress = json.loads(attempt.progress_data) if isinstance(attempt.progress_data, str) else attempt.progress_data or {}
            except (json.JSONDecodeError, KeyError):
                progress = {}
            
            progress['network_config'] = network_config
            attempt.progress_data = json.dumps(progress) if not isinstance(progress, str) else progress
            attempt.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        # Log the save operation
        print(f"🌐 Network configuration saved for simulation {simulation_id} by user {user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Network configuration saved successfully',
            'simulation_id': simulation_id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving network configuration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/network-config/validate', methods=['POST'])
@user_login_required
def validate_network_config_api(simulation_id):
    """Validate network configuration for a simulation"""
    try:
        user = get_user_from_session()
        data = request.get_json() or {}
        
        # Check if user has access to this simulation
        simulation = Simulation.query.get_or_404(simulation_id)
        
        network_config = data.get('network_config', {})
        if not network_config:
            return jsonify({
                'success': False,
                'error': 'Network configuration required'
            }), 400
        
        # Perform validation
        validation_result = validate_network_config(network_config)
        
        return jsonify({
            'success': True,
            'valid': validation_result['valid'],
            'errors': validation_result['errors'],
            'warnings': validation_result.get('warnings', []),
            'simulation_id': simulation_id
        })
        
    except Exception as e:
        print(f"Error validating network configuration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def validate_network_config(config):
    """Validate network configuration data"""
    errors = []
    warnings = []
    
    try:
        # Required fields
        required_fields = ['networkType', 'networkSubnet', 'defaultGateway']
        for field in required_fields:
            if not config.get(field):
                errors.append(f'Missing required field: {field}')
        
        # IP address validation
        if config.get('networkSubnet'):
            subnet = config['networkSubnet']
            if '/' not in subnet:
                errors.append('Network subnet must include CIDR notation (e.g., /24)')
            else:
                ip_part = subnet.split('/')[0]
                import re
                ip_regex = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
                if not re.match(ip_regex, ip_part):
                    errors.append('Invalid network subnet IP format')
        
        if config.get('defaultGateway'):
            gateway = config['defaultGateway']
            import re
            ip_regex = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            if not re.match(ip_regex, gateway):
                errors.append('Invalid gateway IP format')
        
        # VLAN configuration validation
        if config.get('vlanConfig'):
            vlan_lines = config['vlanConfig'].strip().split('\n')
            for i, line in enumerate(vlan_lines):
                if line.strip():
                    parts = [part.strip() for part in line.split('|')]
                    if len(parts) < 3:
                        errors.append(f'Invalid VLAN configuration on line {i+1}: expected format "ID | Name | Subnet"')
                    else:
                        # Validate VLAN ID
                        try:
                            vlan_id = int(parts[0])
                            if vlan_id < 1 or vlan_id > 4094:
                                errors.append(f'Invalid VLAN ID {vlan_id}: must be between 1-4094')
                        except ValueError:
                            errors.append(f'Invalid VLAN ID on line {i+1}: must be numeric')
        
        # Security warnings
        if config.get('enableFirewall') is False:
            warnings.append('Firewall is disabled - security risk')
        
        if config.get('enableAcl') is False and config.get('enableFirewall') is False:
            warnings.append('No access controls enabled - high security risk')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
        
    except Exception as e:
        return {
            'valid': False,
            'errors': [f'Validation error: {str(e)}'],
            'warnings': []
        }

# ===== END NETWORK CONFIGURATION API ROUTES =====

# ===== AUTOMATIC TASK VERIFICATION ROUTES =====

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/check-command', methods=['POST'])
@user_login_required
def check_command_execution(simulation_id):
    """Check if a command executed by the user matches task requirements"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No command data provided'}), 400
        
        user = get_user_from_session()
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Get task configuration
        simulation_config = simulation.simulation_config or {}
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except Exception:
                simulation_config = {}
        
        task_config = simulation_config.get('task_config', {})
        command_requirements = task_config.get('commandRequirements', {})
        
        if not command_requirements.get('enabled', False):
            return jsonify({
                'checking_enabled': False,
                'message': 'Automatic command checking is not enabled for this simulation'
            })
        
        # Get command details from request
        executed_command = data.get('command', '').strip()
        device_type = data.get('deviceType', 'unknown').lower()
        device_name = data.get('deviceName', '')
        
        if not executed_command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Check against required commands
        required_commands = command_requirements.get('commands', [])
        matches = []
        
        for req_cmd in required_commands:
            if not req_cmd.get('required', True):
                continue  # Skip optional commands
                
            req_device_type = req_cmd.get('deviceType', 'any').lower()
            req_command_text = req_cmd.get('commandText', '').strip()
            req_command_type = req_cmd.get('commandType', 'exact').lower()
            
            # Check device type match
            device_match = (req_device_type == 'any' or 
                          req_device_type == device_type or
                          device_type == 'any')
            
            if not device_match:
                continue
            
            # Check command match based on type
            command_match = False
            if req_command_type == 'exact':
                command_match = executed_command.lower() == req_command_text.lower()
            elif req_command_type == 'contains':
                command_match = req_command_text.lower() in executed_command.lower()
            elif req_command_type == 'pattern':
                try:
                    import re
                    command_match = bool(re.search(req_command_text, executed_command, re.IGNORECASE))
                except re.error:
                    command_match = False
            
            if command_match:
                matches.append({
                    'commandId': req_cmd.get('id', len(matches)),
                    'description': req_cmd.get('description', ''),
                    'commandText': req_command_text,
                    'deviceType': req_device_type
                })
        
        # Get or create user progress tracking
        progress = get_user_task_progress(user.id, simulation_id)
        
        # Update progress with new matches
        if matches:
            for match in matches:
                if match['commandId'] not in progress.get('completed_commands', []):
                    progress['completed_commands'].append(match['commandId'])
        
        # Save progress
        save_user_task_progress(user.id, simulation_id, progress)
        
        # Calculate completion status
        total_required = len([cmd for cmd in required_commands if cmd.get('required', True)])
        completed_count = len(progress.get('completed_commands', []))
        
        completion_mode = command_requirements.get('completionMode', 'all-commands')
        is_complete = False
        
        if completion_mode == 'all-commands':
            is_complete = completed_count >= total_required
        elif completion_mode == 'percentage':
            required_percentage = command_requirements.get('completionPercentage', 80)
            is_complete = (completed_count / max(total_required, 1)) * 100 >= required_percentage
        elif completion_mode == 'minimum-count':
            minimum_commands = command_requirements.get('minimumCommands', 3)
            is_complete = completed_count >= minimum_commands
        
        return jsonify({
            'checking_enabled': True,
            'matches': matches,
            'match_count': len(matches),
            'progress': {
                'completed_commands': progress.get('completed_commands', []),
                'total_required': total_required,
                'completed_count': completed_count,
                'completion_percentage': (completed_count / max(total_required, 1)) * 100,
                'is_complete': is_complete
            },
            'show_progress': command_requirements.get('showProgress', True)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to check command: {str(e)}'}), 500


@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/task-progress', methods=['GET'])
@user_login_required
def get_task_progress(simulation_id):
    """Get current task progress for the user"""
    try:
        user = get_user_from_session()
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Get task configuration
        simulation_config = simulation.simulation_config or {}
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except Exception:
                simulation_config = {}
        
        task_config = simulation_config.get('task_config', {})
        
        # Get user progress
        progress = get_user_task_progress(user.id, simulation_id)
        
        # Calculate progress metrics
        command_requirements = task_config.get('commandRequirements', {})
        required_commands = command_requirements.get('commands', [])
        total_required = len([cmd for cmd in required_commands if cmd.get('required', True)])
        completed_count = len(progress.get('completed_commands', []))
        
        # Device requirements check
        device_requirements = task_config.get('deviceRequirements', {})
        device_count_met = check_device_count_requirement(user.id, simulation_id, device_requirements)
        
        return jsonify({
            'task_config': task_config,
            'progress': {
                'completed_commands': progress.get('completed_commands', []),
                'total_required': total_required,
                'completed_count': completed_count,
                'completion_percentage': (completed_count / max(total_required, 1)) * 100,
                'device_count_met': device_count_met,
                'last_updated': progress.get('last_updated')
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get task progress: {str(e)}'}), 500


@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/check-devices', methods=['POST'])
@user_login_required
def check_device_requirements(simulation_id):
    """Check if device count and type requirements are met"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No device data provided'}), 400
        
        user = get_user_from_session()
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Get task configuration
        simulation_config = simulation.simulation_config or {}
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except Exception:
                simulation_config = {}
        
        task_config = simulation_config.get('task_config', {})
        device_requirements = task_config.get('deviceRequirements', {})
        
        devices = data.get('devices', [])
        
        # Check device count requirement
        required_count = device_requirements.get('deviceCount', 0)
        actual_count = len(devices)
        count_met = actual_count >= required_count
        
        # Check device type requirements
        type_requirements_met = True
        type_details = {}
        
        if device_requirements.get('enforceDeviceTypes', False):
            required_types = device_requirements.get('requiredDeviceTypes', {})
            actual_types = {}
            
            # Count actual device types
            for device in devices:
                device_type = device.get('type', '').lower()
                if device_type.endswith('s'):
                    device_type = device_type[:-1]  # Remove plural 's'
                actual_types[device_type] = actual_types.get(device_type, 0) + 1
            
            # Check each required type
            for req_type, req_count in required_types.items():
                actual_type_count = actual_types.get(req_type, 0)
                type_met = actual_type_count >= req_count
                type_details[req_type] = {
                    'required': req_count,
                    'actual': actual_type_count,
                    'met': type_met
                }
                if not type_met:
                    type_requirements_met = False
        
        return jsonify({
            'device_count': {
                'required': required_count,
                'actual': actual_count,
                'met': count_met
            },
            'device_types': {
                'enforce_types': device_requirements.get('enforceDeviceTypes', False),
                'requirements_met': type_requirements_met,
                'details': type_details
            },
            'overall_met': count_met and type_requirements_met
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to check device requirements: {str(e)}'}), 500


def get_user_task_progress(user_id, simulation_id):
    """Get user's task progress from session or database"""
    session_key = f'task_progress_{simulation_id}'
    
    # Try to get from session first
    if session_key in session:
        return session[session_key]
    
    # Fallback: create new progress tracking
    return {
        'completed_commands': [],
        'device_count_met': False,
        'last_updated': datetime.utcnow().isoformat()
    }


def save_user_task_progress(user_id, simulation_id, progress):
    """Save user's task progress to session"""
    session_key = f'task_progress_{simulation_id}'
    progress['last_updated'] = datetime.utcnow().isoformat()
    session[session_key] = progress


def check_device_count_requirement(user_id, simulation_id, device_requirements):
    """Check if device count requirement is met (stub for now)"""
    # This would need to be implemented to check current canvas state
    # For now, return True as devices are checked in real-time via check_device_requirements
    return True

# ===== END AUTOMATIC TASK VERIFICATION ROUTES =====

# Export the blueprint for direct import
__all__ = ['dynamic_sim_bp', 'register_dynamic_routes']
