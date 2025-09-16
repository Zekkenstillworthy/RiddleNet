#!/usr/bin/env python3

from user.dynamic_simulation_routes import validate_topology_data
import json

def test_enhanced_validation():
    """Test enhanced device schema validation"""
    
    # Test enhanced device schema validation
    test_topology = {
        'devices': [
            {
                'id': 'device1',
                'type': 'pc',
                'interfaces': [
                    {'name': 'eth0', 'type': 'ethernet'}
                ],
                'position': {'x': 100, 'y': 200},
                'ip': '192.168.1.10',
                'meta': {'hostname': 'workstation1'}
            },
            {
                'id': 'device2', 
                'type': 'switch',
                'interfaces': [
                    {'name': 'FastEthernet0/1'},
                    {'name': 'FastEthernet0/2'}
                ],
                'position': {'x': 300, 'y': 200}
            }
        ],
        'connections': [
            {
                'from': {'deviceId': 'device1', 'port': 'eth0'},
                'to': {'deviceId': 'device2', 'port': 'FastEthernet0/1'},
                'cable': 'ethernet'
            }
        ]
    }

    result = validate_topology_data(test_topology)
    print('Enhanced Validation Test:')
    print(json.dumps(result, indent=2))
    print()
    
    # Test invalid topology
    invalid_topology = {
        'devices': [
            {
                'id': 'device1',
                'type': 'pc',
                'interfaces': 'not_array',  # Should be array
                'position': 'not_object',   # Should be object
                'ip': '999.999.999.999'     # Invalid IP
            }
        ],
        'connections': [
            {
                'from': {'deviceId': 'nonexistent', 'port': 'eth0'},
                'to': {'deviceId': 'device1', 'port': 'eth0'},
                'cable': 'unknown_cable'
            }
        ]
    }
    
    result2 = validate_topology_data(invalid_topology)
    print('Invalid Topology Test:')
    print(json.dumps(result2, indent=2))

if __name__ == '__main__':
    test_enhanced_validation()