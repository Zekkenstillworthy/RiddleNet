from flask import Blueprint, jsonify, request
from __init__ import db
from instructor.models.topology import Topology

topology_api_bp = Blueprint('topology_api', __name__, url_prefix='/api/topology')

@topology_api_bp.route('/config/<topology_type>')
def get_topology_config(topology_type):
    """Endpoint to get topology configuration including scoring metrics and device requirements"""
    try:
        # First try to get from database
        topology = Topology.query.filter_by(topology_type=topology_type).first()
        
        if topology:
            return jsonify({
                'topology_type': topology.topology_type,
                'base_score': topology.base_score,
                'time_bonus': topology.time_bonus,
                'perfect_match_bonus': topology.perfect_match_bonus,
                'scoring_metrics': topology.scoring_metrics,
                'device_requirements': topology.device_requirements,
                'validation_rules': topology.validation_rules if hasattr(topology, 'validation_rules') else None
            })
        
        # Fallback to default configuration if not in database
        default_scoring = {
            'time_efficiency': 10,
            'config_process': 25,
            'design_layout': 20,
            'completeness': 20,
            'correctness': 25
        }
        
        default_requirements = {
            'point-to-point': {'pc': 2, 'router': 0, 'switch': 0, 'server': 0},
            'star': {'pc': 3, 'router': 0, 'switch': 1, 'server': 0},
            'mesh': {'pc': 0, 'router': 4, 'switch': 0, 'server': 0},
            'bus': {'pc': 4, 'router': 0, 'switch': 0, 'server': 0},
            'ring': {'pc': 0, 'router': 0, 'switch': 4, 'server': 0},
            'tree': {'pc': 4, 'router': 1, 'switch': 2, 'server': 0},
            'hybrid': {'pc': 3, 'router': 1, 'switch': 2, 'server': 1}
        }
        
        return jsonify({
            'topology_type': topology_type,
            'base_score': 10,
            'time_bonus': 5,
            'perfect_match_bonus': 5,
            'scoring_metrics': default_scoring,
            'device_requirements': default_requirements.get(topology_type, {'pc': 2, 'router': 0, 'switch': 0, 'server': 0}),
            'validation_rules': {'rules': []}
        })
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving topology configuration: {str(e)}'
        }), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@topology_api_bp.route('/types')
def get_topology_types():
    """Get all available topology types"""
    try:
        # Get topology types from the database
        topologies = Topology.query.with_entities(Topology.topology_type).distinct().all()
        topology_types = [t[0] for t in topologies]
        
        # If no types found in database, use default list
        if not topology_types:
            topology_types = ['point-to-point', 'mesh', 'star', 'bus', 'ring', 'tree', 'hybrid']
            
        return jsonify({
            'status': 'success',
            'topology_types': topology_types
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@topology_api_bp.route('/validate', methods=['POST'])
def validate_topology():
    """Endpoint to validate a user-created topology against requirements"""
    try:
        data = request.json
        
        if not data or 'topology_type' not in data or 'devices' not in data or 'connections' not in data:
            return jsonify({
                'valid': False,
                'message': 'Missing required data: topology_type, devices, and connections are required'
            }), 400
        
        # Get topology configuration
        topology_type = data['topology_type']
        topology = Topology.query.filter_by(topology_type=topology_type).first()
        
        if not topology:
            # Use default requirements
            device_requirements = {
                'point-to-point': {'pc': 2, 'router': 0, 'switch': 0, 'server': 0},
                'star': {'pc': 3, 'router': 0, 'switch': 1, 'server': 0},
                'mesh': {'pc': 0, 'router': 4, 'switch': 0, 'server': 0},
                'bus': {'pc': 4, 'router': 0, 'switch': 0, 'server': 0},
                'ring': {'pc': 0, 'router': 0, 'switch': 4, 'server': 0},
                'tree': {'pc': 4, 'router': 1, 'switch': 2, 'server': 0},
                'hybrid': {'pc': 3, 'router': 1, 'switch': 2, 'server': 1}
            }.get(topology_type, {'pc': 2, 'router': 0, 'switch': 0, 'server': 0})
            
            validation_rules = {'rules': []}
        else:
            device_requirements = topology.device_requirements
            validation_rules = topology.validation_rules if hasattr(topology, 'validation_rules') else {'rules': []}
        
        # Check device requirements
        devices = data['devices']
        connections = data['connections']
        
        # Count devices by type
        device_counts = {}
        for device in devices:
            device_type = device.get('type', '').lower()
            device_counts[device_type] = device_counts.get(device_type, 0) + 1
        
        # Check if requirements are met
        missing_devices = []
        for req_type, req_count in device_requirements.items():
            if device_counts.get(req_type, 0) < req_count:
                missing_devices.append(f"{req_count - device_counts.get(req_type, 0)} more {req_type}")
        
        if missing_devices:
            return jsonify({
                'valid': False,
                'message': f"Missing required devices: {', '.join(missing_devices)}"
            })
        
        # Validate topology structure based on topology type
        valid, message = validate_topology_structure(topology_type, devices, connections)
        if not valid:
            return jsonify({
                'valid': False,
                'message': message
            })
        
        # Check custom validation rules if any
        if validation_rules and 'rules' in validation_rules and validation_rules['rules']:
            for rule in validation_rules['rules']:
                valid, message = evaluate_validation_rule(rule, devices, connections)
                if not valid:
                    return jsonify({
                        'valid': False,
                        'message': message
                    })
        
        return jsonify({
            'valid': True,
            'message': "Topology meets all requirements"
        })
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': f'Error validating topology: {str(e)}'
        }), 500

@topology_api_bp.route('/debug-json', methods=['POST'])
def debug_topology_json():
    """Debug endpoint for troubleshooting topology configuration"""
    try:
        data = request.json
        
        results = {
            'initial_config': check_json_structure(data.get('initial_config')),
            'expected_config': check_json_structure(data.get('expected_config')),
            'validation_rules': check_json_structure(data.get('validation_rules')),
            'scoring_metrics': check_scoring_metrics(data.get('scoring_metrics')),
            'device_requirements': check_device_requirements(data.get('device_requirements'))
        }
        
        return jsonify({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def check_json_structure(config):
    """Helper function to validate JSON structure"""
    if not config:
        return "Missing or empty"
    
    if isinstance(config, dict):
        required_keys = []
        if 'devices' in config:
            required_keys.append('devices')
        if 'connections' in config:
            required_keys.append('connections')
        if 'rules' in config:
            required_keys.append('rules')
        
        if not required_keys:
            return "Valid but unknown structure"
        
        missing = [key for key in required_keys if key not in config]
        if missing:
            return f"Missing required keys: {', '.join(missing)}"
        
        return "Valid structure"
    
    return "Invalid structure - not a dictionary"

def check_scoring_metrics(metrics):
    """Helper function to validate scoring metrics"""
    if not metrics or not isinstance(metrics, dict):
        return "Missing or invalid format"
    
    expected_keys = ['time_efficiency', 'config_process', 'design_layout', 'completeness', 'correctness']
    missing = [key for key in expected_keys if key not in metrics]
    
    if missing:
        return f"Missing metrics: {', '.join(missing)}"
    
    total = sum(metrics.values())
    return f"Valid - Total weight: {total}"

def check_device_requirements(requirements):
    """Helper function to validate device requirements"""
    if not requirements or not isinstance(requirements, dict):
        return "Missing or invalid format"
    
    expected_keys = ['pc', 'router', 'switch', 'server']
    missing = [key for key in expected_keys if key not in requirements]
    
    if missing:
        return f"Missing device types: {', '.join(missing)}"
    
    total = sum(requirements.values())
    return f"Valid - Total devices required: {total}"

def validate_topology_structure(topology_type, devices, connections):
    """
    Validate a topology structure based on the topology type
    Returns (valid, message) tuple
    """
    if topology_type == 'point-to-point':
        # Point-to-point: Requires exactly 1 connection between 2 devices
        if len(devices) != 2:
            return False, "Point-to-point topology must have exactly 2 devices"
        if len(connections) != 1:
            return False, "Point-to-point topology must have exactly 1 connection"
        return True, "Point-to-point topology structure is valid"
        
    elif topology_type == 'star':
        # Star: Requires one central device connected to all other devices
        if len(devices) < 4:  # At least 1 central + 3 peripheral devices
            return False, "Star topology must have at least 4 devices (1 central + 3 peripheral)"
            
        # Find potential central devices (those connected to 3+ other devices)
        device_connections = {}
        for conn in connections:
            source = conn.get('source', '')
            target = conn.get('target', '')
            device_connections[source] = device_connections.get(source, 0) + 1
            device_connections[target] = device_connections.get(target, 0) + 1
            
        # Check if at least one device is connected to all others
        central_devices = [d for d, count in device_connections.items() if count >= len(devices) - 1]
        if not central_devices:
            return False, "Star topology must have one central device connected to all other devices"
        return True, "Star topology structure is valid"
        
    elif topology_type == 'mesh':
        # Mesh: Requires each device to be connected to every other device
        if len(devices) < 3:
            return False, "Mesh topology must have at least 3 devices"
            
        # Required connections for a full mesh = n(n-1)/2
        required_connections = len(devices) * (len(devices) - 1) // 2
        if len(connections) < required_connections:
            return False, f"Mesh topology must have at least {required_connections} connections"
            
        # Check if each device is connected to every other device
        device_connections = {}
        for conn in connections:
            source = conn.get('source', '')
            target = conn.get('target', '')
            
            if source not in device_connections:
                device_connections[source] = set()
            if target not in device_connections:
                device_connections[target] = set()
                
            device_connections[source].add(target)
            device_connections[target].add(source)
            
        for device_id in [d.get('id') for d in devices]:
            if device_id not in device_connections:
                return False, f"Device {device_id} is not connected to any other device"
            
            if len(device_connections[device_id]) < len(devices) - 1:
                return False, f"Device {device_id} is not connected to all other devices"
                
        return True, "Mesh topology structure is valid"
        
    elif topology_type == 'ring':
        # Ring: Requires each device to be connected to exactly 2 other devices, forming a circle
        if len(devices) < 3:
            return False, "Ring topology must have at least 3 devices"
            
        # Check if each device has exactly 2 connections
        device_connections = {}
        for conn in connections:
            source = conn.get('source', '')
            target = conn.get('target', '')
            
            device_connections[source] = device_connections.get(source, 0) + 1
            device_connections[target] = device_connections.get(target, 0) + 1
            
        for device_id, count in device_connections.items():
            if count != 2:
                return False, f"In a ring topology, device {device_id} must have exactly 2 connections"
                
        # Check if the ring is closed (this is a simplified check)
        if len(connections) != len(devices):
            return False, "Ring topology must form a closed loop"
            
        return True, "Ring topology structure is valid"
        
    elif topology_type == 'bus':
        # Bus: Requires devices to be connected in a linear arrangement
        if len(devices) < 3:
            return False, "Bus topology must have at least 3 devices"
            
        # Check if devices form a linear connection (simplified)
        if len(connections) != len(devices) - 1:
            return False, "Bus topology must have exactly (n-1) connections for n devices"
            
        # Count connections per device (ends should have 1, others should have 2)
        device_connections = {}
        for conn in connections:
            source = conn.get('source', '')
            target = conn.get('target', '')
            
            device_connections[source] = device_connections.get(source, 0) + 1
            device_connections[target] = device_connections.get(target, 0) + 1
            
        end_points = sum(1 for count in device_connections.values() if count == 1)
        if end_points != 2:
            return False, "Bus topology must have exactly 2 end points"
            
        return True, "Bus topology structure is valid"
        
    elif topology_type == 'tree':
        # Tree: Requires a hierarchical structure with parent-child relationships
        if len(devices) < 3:
            return False, "Tree topology must have at least 3 devices"
            
        # Check for no cycles (number of connections should be n-1 for n devices)
        if len(connections) != len(devices) - 1:
            return False, "Tree topology must have exactly (n-1) connections for n devices"
            
        # Simplified check for tree structure
        device_connections = {}
        for conn in connections:
            source = conn.get('source', '')
            target = conn.get('target', '')
            
            device_connections[source] = device_connections.get(source, 0) + 1
            device_connections[target] = device_connections.get(target, 0) + 1
            
        # At least one device should have more than 2 connections (the root)
        has_root = any(count > 2 for count in device_connections.values())
        if not has_root:
            return False, "Tree topology must have at least one root device with multiple children"
            
        return True, "Tree topology structure is valid"
        
    elif topology_type == 'hybrid':
        # Hybrid: Combines elements of multiple topology types
        # For hybrid, we only do basic validation
        if len(devices) < 5:
            return False, "Hybrid topology must have at least 5 devices"
            
        if len(connections) < 4:
            return False, "Hybrid topology must have at least 4 connections"
            
        return True, "Hybrid topology structure is valid"
        
    else:
        # For unknown topology types, just return true
        return True, f"Unknown topology type: {topology_type}"

def evaluate_validation_rule(rule, devices, connections):
    """
    Evaluate a custom validation rule against topology
    Returns (valid, message) tuple
    """
    rule_type = rule.get('type', '')
    rule_params = rule.get('parameters', {})
    
    if rule_type == 'connection_count':
        # Check for minimum or exact connection count
        min_count = rule_params.get('min', 0)
        max_count = rule_params.get('max', float('inf'))
        exact_count = rule_params.get('exact')
        
        if exact_count is not None:
            if len(connections) != exact_count:
                return False, f"Connection count must be exactly {exact_count}"
        elif len(connections) < min_count:
            return False, f"Connection count must be at least {min_count}"
        elif len(connections) > max_count:
            return False, f"Connection count must not exceed {max_count}"
            
    elif rule_type == 'device_connection':
        # Check for device connection requirements
        device_type = rule_params.get('device_type', '')
        min_connections = rule_params.get('min_connections', 0)
        max_connections = rule_params.get('max_connections', float('inf'))
        
        # Find devices of specified type
        target_devices = [d.get('id') for d in devices if d.get('type', '').lower() == device_type.lower()]
        
        # Count connections for each device
        device_connection_counts = {}
        for conn in connections:
            source = conn.get('source', '')
            target = conn.get('target', '')
            
            if source in target_devices:
                device_connection_counts[source] = device_connection_counts.get(source, 0) + 1
            if target in target_devices:
                device_connection_counts[target] = device_connection_counts.get(target, 0) + 1
                
        # Check if all devices of the specified type meet connection requirements
        for device_id in target_devices:
            count = device_connection_counts.get(device_id, 0)
            if count < min_connections:
                return False, f"Device {device_id} ({device_type}) must have at least {min_connections} connections"
            if count > max_connections:
                return False, f"Device {device_id} ({device_type}) must not exceed {max_connections} connections"
                
    elif rule_type == 'custom':
        # Placeholder for custom rule evaluation logic
        return True, "Custom rule validation not implemented yet"
        
    # If we got here, the rule is either satisfied or not recognized
    return True, f"Rule '{rule_type}' passed validation"
