"""
Enhanced Simulation Configuration
Centralized configuration for network validation across all simulation editors
"""

class ValidationConfig:
    """Configuration class for enhanced simulation validation"""
    
    # State machine for simulation validation
    VALIDATION_STATES = {
        'DISCONNECTED': 'disconnected',
        'CONFIGURED': 'configured', 
        'CONNECTED': 'connected',
        'VALIDATED': 'validated',
        'WORKING': 'working'
    }
    
    # Device configuration requirements by type
    DEVICE_CONFIG_REQUIREMENTS = {
        'pc': {
            'required': ['ip_address', 'subnet_mask', 'default_gateway'],
            'optional': ['dns_server', 'hostname'],
            'validation_rules': {
                'ip_address': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                'subnet_mask': r'^(?:(?:255\.){3}(?:255|254|252|248|240|224|192|128|0))|(?:\/(?:[0-9]|[1-2][0-9]|3[0-2]))$'
            }
        },
        'server': {
            'required': ['ip_address', 'subnet_mask', 'default_gateway', 'services'],
            'optional': ['dns_server', 'hostname'],
            'validation_rules': {
                'ip_address': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                'services': ['dhcp', 'dns', 'web', 'ftp', 'email']
            }
        },
        'router': {
            'required': ['interfaces', 'routing_protocol', 'default_route'],
            'optional': ['nat', 'acls', 'qos'],
            'validation_rules': {
                'routing_protocol': ['static', 'rip', 'ospf', 'eigrp'],
                'interfaces': 'list_of_interfaces'
            }
        },
        'switch': {
            'required': ['vlans', 'interfaces', 'spanning_tree'],
            'optional': ['port_security', 'trunk_ports'],
            'validation_rules': {
                'spanning_tree': ['stp', 'rstp', 'mstp'],
                'vlans': 'list_of_vlans'
            }
        },
        'access-point': {
            'required': ['ssid', 'security_type', 'ip_address', 'subnet_mask'],
            'optional': ['encryption', 'guest_network'],
            'validation_rules': {
                'security_type': ['wpa2', 'wpa3', 'open'],
                'ssid': r'^[a-zA-Z0-9_-]{1,32}$'
            }
        }
    }
    
    # Physical connection validation rules
    PHYSICAL_CONNECTION_RULES = {
        'pc': {
            'allowed_connections': ['switch', 'router', 'access-point'],
            'cable_types': ['ethernet', 'wireless'],
            'max_connections': 1
        },
        'server': {
            'allowed_connections': ['switch', 'router'],
            'cable_types': ['ethernet', 'fiber'],
            'max_connections': 2
        },
        'router': {
            'allowed_connections': ['switch', 'router', 'pc', 'server'],
            'cable_types': ['ethernet', 'fiber', 'serial'],
            'max_connections': 10
        },
        'switch': {
            'allowed_connections': ['pc', 'server', 'router', 'switch', 'access-point'],
            'cable_types': ['ethernet', 'fiber'],
            'max_connections': 48
        },
        'access-point': {
            'allowed_connections': ['switch', 'router', 'pc'],
            'cable_types': ['ethernet', 'wireless'],
            'max_connections': 1
        }
    }
    
    # Cable compatibility matrix
    CABLE_COMPATIBILITY = {
        'ethernet': {
            'straight': ['pc_to_switch', 'router_to_switch', 'server_to_switch'],
            'crossover': ['pc_to_pc', 'switch_to_switch', 'router_to_router'],
            'auto_mdix': ['any_to_any']  # Modern devices support auto MDI/MDIX
        },
        'fiber': {
            'single_mode': ['router_to_router', 'switch_to_switch', 'long_distance'],
            'multi_mode': ['server_to_switch', 'switch_to_switch', 'short_distance']
        },
        'wireless': {
            '802.11ac': ['ap_to_client'],
            '802.11ax': ['ap_to_client']
        }
    }
    
    # Default connectivity tests
    DEFAULT_CONNECTIVITY_TESTS = [
        {
            'name': 'basic_ping_test',
            'description': 'Test basic connectivity between end devices',
            'type': 'ping',
            'required': True
        },
        {
            'name': 'gateway_connectivity',
            'description': 'Test connectivity to default gateway',
            'type': 'ping_gateway',
            'required': True
        },
        {
            'name': 'routing_table_check',
            'description': 'Verify routing table configuration',
            'type': 'route_check',
            'required': False
        },
        {
            'name': 'dns_resolution',
            'description': 'Test DNS resolution if DNS server configured',
            'type': 'nslookup',
            'required': False
        }
    ]
    
    # Error messages for validation failures
    VALIDATION_MESSAGES = {
        'config_incomplete': 'Device configuration is incomplete. Required fields: {fields}',
        'invalid_ip': 'Invalid IP address format: {ip}',
        'invalid_connection': 'Invalid connection between {device1} and {device2}',
        'cable_incompatible': 'Cable type {cable} is not compatible with connection {connection}',
        'connectivity_failed': 'Connectivity test failed: {test} between {source} and {target}',
        'routing_error': 'Routing configuration error: {error}',
        'interface_error': 'Interface configuration error on {device}: {error}'
    }

    @classmethod
    def get_default_config(cls):
        """Get default enhanced validation configuration"""
        return {
            'enhanced_validation': {
                'enabled': True,
                'state_machine_enabled': True,
                'configuration_requirements': {
                    'require_ip_assignment': True,
                    'require_device_modes': True,
                    'require_cable_configuration': True,
                    'require_interface_config': True
                },
                'physical_validation': {
                    'enforce_compatible_connections': True,
                    'validate_device_capabilities': True,
                    'check_cable_types': True,
                    'max_connection_validation': True
                },
                'connectivity_tests': {
                    'require_ping_tests': True,
                    'require_route_validation': True,
                    'require_connectivity_matrix': True,
                    'auto_generate_tests': True,
                    'required_tests': []
                }
            }
        }
    
    @classmethod
    def validate_device_config(cls, device_type, config):
        """Validate device configuration against requirements"""
        if device_type not in cls.DEVICE_CONFIG_REQUIREMENTS:
            return False, f"Unknown device type: {device_type}"
        
        requirements = cls.DEVICE_CONFIG_REQUIREMENTS[device_type]
        missing_fields = []
        
        for field in requirements['required']:
            if field not in config or not config[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, "Configuration valid"
    
    @classmethod
    def validate_physical_connection(cls, device1_type, device2_type, cable_type):
        """Validate physical connection between two devices"""
        if device1_type not in cls.PHYSICAL_CONNECTION_RULES:
            return False, f"Unknown device type: {device1_type}"
        
        rules = cls.PHYSICAL_CONNECTION_RULES[device1_type]
        
        if device2_type not in rules['allowed_connections']:
            return False, f"Connection not allowed between {device1_type} and {device2_type}"
        
        if cable_type not in rules['cable_types']:
            return False, f"Cable type {cable_type} not supported by {device1_type}"
        
        return True, "Connection valid"