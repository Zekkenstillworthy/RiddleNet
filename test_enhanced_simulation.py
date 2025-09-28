#!/usr/bin/env python3
"""
Test script for Enhanced Network Simulation System
Run this to verify the validation enhancements are working correctly.
"""

import json
import sys
import os

# Add the RiddleNet directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_validation_function():
    """Test the enhanced validate_network_configuration function"""
    
    # Import the validation function from our updated routes file
    try:
        from user.dynamic_simulation_routes import validate_network_configuration
        print("✅ Successfully imported validate_network_configuration")
    except ImportError as e:
        print(f"❌ Failed to import validation function: {e}")
        return False
    
    # Test case 1: Simple PC configuration
    print("\n🧪 Test 1: PC IP Configuration")
    network_state = {
        'devices': [
            {
                'name': 'PC1',
                'type': 'pc',
                'config': {
                    'ip': '192.168.1.10/24',
                    'gateway': '192.168.1.1'
                }
            }
        ]
    }
    
    expected_config = {
        'devices': {
            'PC1': {
                'ip': '192.168.1.10/24',
                'gateway': '192.168.1.1'
            }
        }
    }
    
    result = validate_network_configuration(network_state, expected_config)
    if result['valid']:
        print("✅ PC configuration validation passed")
    else:
        print(f"❌ PC configuration validation failed: {result['errors']}")
        return False
    
    # Test case 2: Router interface configuration
    print("\n🧪 Test 2: Router Interface Configuration")
    network_state = {
        'devices': [
            {
                'name': 'Router1',
                'type': 'router',
                'config': {
                    'interfaces': {
                        'GigabitEthernet0/0': {
                            'ip': '192.168.1.1/24',
                            'status': 'up'
                        }
                    }
                }
            }
        ]
    }
    
    expected_config = {
        'devices': {
            'Router1': {
                'interfaces': {
                    'GigabitEthernet0/0': {
                        'ip': '192.168.1.1/24',
                        'status': 'up'
                    }
                }
            }
        }
    }
    
    result = validate_network_configuration(network_state, expected_config)
    if result['valid']:
        print("✅ Router interface validation passed")
    else:
        print(f"❌ Router interface validation failed: {result['errors']}")
        return False
    
    # Test case 3: Wireless AP configuration
    print("\n🧪 Test 3: Wireless Access Point Configuration")
    network_state = {
        'devices': [
            {
                'name': 'AP1',
                'type': 'access_point',
                'config': {
                    'wireless': {
                        'ssid': 'HomeLab',
                        'psk': 'lab12345'
                    }
                }
            }
        ]
    }
    
    expected_config = {
        'devices': {
            'AP1': {
                'wireless': {
                    'ssid': 'HomeLab',
                    'psk': 'lab12345'
                }
            }
        }
    }
    
    result = validate_network_configuration(network_state, expected_config)
    if result['valid']:
        print("✅ Wireless AP validation passed")
    else:
        print(f"❌ Wireless AP validation failed: {result['errors']}")
        return False
    
    # Test case 4: Failed validation (incorrect IP)
    print("\n🧪 Test 4: Failed Validation (Incorrect IP)")
    network_state = {
        'devices': [
            {
                'name': 'PC1',
                'type': 'pc',
                'config': {
                    'ip': '192.168.1.20/24',  # Wrong IP
                    'gateway': '192.168.1.1'
                }
            }
        ]
    }
    
    expected_config = {
        'devices': {
            'PC1': {
                'ip': '192.168.1.10/24',  # Expected IP
                'gateway': '192.168.1.1'
            }
        }
    }
    
    result = validate_network_configuration(network_state, expected_config)
    if not result['valid'] and len(result['errors']) > 0:
        print("✅ Failed validation correctly detected")
        print(f"📋 Error message: {result['errors'][0]}")
    else:
        print("❌ Failed validation was not detected properly")
        return False
    
    return True

def test_step_definitions():
    """Test the step definition format"""
    print("\n🧪 Testing Step Definition Format")
    
    sample_steps = [
        {
            "title": "Configure PC1",
            "type": "network_config",
            "description": "Set IP 192.168.1.10/24 and gateway 192.168.1.1 on PC1.",
            "validation": {
                "type": "network_config",
                "expected_config": {
                    "devices": {
                        "PC1": { 
                            "ip": "192.168.1.10/24", 
                            "gateway": "192.168.1.1" 
                        }
                    }
                },
                "score": 10
            }
        },
        {
            "title": "Wire the LAN",
            "type": "connectivity",
            "description": "Connect PC1 to Switch1 and Switch1 to Router1.",
            "validation": {
                "type": "connectivity",
                "expected_topology": {
                    "expected_connections": [
                        ["PC1","Switch1"],
                        ["Switch1","Router1"]
                    ]
                },
                "score": 10
            }
        }
    ]
    
    # Validate JSON structure
    try:
        json_str = json.dumps(sample_steps, indent=2)
        parsed_back = json.loads(json_str)
        print("✅ Step definitions JSON structure is valid")
        print(f"📋 Sample has {len(parsed_back)} steps")
        return True
    except json.JSONEncodeError as e:
        print(f"❌ Step definitions JSON is invalid: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced Network Simulation System - Test Suite")
    print("="*60)
    
    all_tests_passed = True
    
    # Test validation function
    if not test_validation_function():
        all_tests_passed = False
    
    # Test step definitions
    if not test_step_definitions():
        all_tests_passed = False
    
    print("\n" + "="*60)
    if all_tests_passed:
        print("🎉 All tests passed! Enhanced simulation system is working correctly.")
        print("\n📋 Next steps:")
        print("1. Admin: Add step definitions to simulation in admin editor")
        print("2. User: Open simulation and test the 'Validate Network' button")
        print("3. Verify real-time step validation feedback")
    else:
        print("❌ Some tests failed. Check the validation logic.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)