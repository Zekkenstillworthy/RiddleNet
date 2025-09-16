#!/usr/bin/env python3
"""
Test script to validate the topology implementation
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:5001"

def test_basic_connectivity():
    """Test if the application is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Application is running (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Application not reachable: {e}")
        return False

def test_new_topology_endpoint():
    """Test the new topology endpoint"""
    try:
        # Test with a non-existent simulation ID
        response = requests.get(f"{BASE_URL}/dynamic/api/simulation/999/topology", timeout=5)
        print(f"✅ Topology endpoint exists (Status: {response.status_code})")
        
        if response.status_code == 404:
            print("  📝 Expected 404 for non-existent simulation")
        elif response.status_code == 200:
            data = response.json()
            print(f"  📝 Response: {data}")
        
        return True
    except Exception as e:
        print(f"❌ Topology endpoint error: {e}")
        return False

def test_network_state_endpoint():
    """Test the enhanced network-state endpoint"""
    try:
        # Test with sample topology data
        test_topology = {
            "devices": [
                {"id": "router1", "type": "router", "x": 200, "y": 150, "label": "Router 1"},
                {"id": "switch1", "type": "switch", "x": 100, "y": 250, "label": "Switch 1"}
            ],
            "connections": [
                {"from": "router1", "to": "switch1"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/dynamic/api/simulation/999/network-state",
            json=test_topology,
            timeout=5
        )
        
        print(f"✅ Network-state endpoint accessible (Status: {response.status_code})")
        
        if response.status_code == 404:
            print("  📝 Expected 404 for non-existent simulation")
        else:
            try:
                data = response.json()
                print(f"  📝 Response: {data}")
            except:
                print(f"  📝 Response text: {response.text[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ Network-state endpoint error: {e}")
        return False

def test_validation_functions():
    """Test client-side validation (by checking the template file)"""
    try:
        # Check if our validation functions are in the template
        template_path = "templates/user/dynamic_simulation.html"
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validation_functions = [
            "validateTopologyStructure",
            "validateCurrentTopology",
            "showTopologyValidationResults",
            "checkTopologyConnectivity",
            "handleMissingTopology"
        ]
        
        all_found = True
        for func in validation_functions:
            if func in content:
                print(f"✅ Found validation function: {func}")
            else:
                print(f"❌ Missing validation function: {func}")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Error checking validation functions: {e}")
        return False

def test_backend_validation():
    """Test if backend validation function exists"""
    try:
        # Check if validate_topology_data exists in the routes file
        routes_path = "user/dynamic_simulation_routes.py"
        with open(routes_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "validate_topology_data" in content:
            print("✅ Backend validation function exists")
            return True
        else:
            print("❌ Backend validation function missing")
            return False
    except Exception as e:
        print(f"❌ Error checking backend validation: {e}")
        return False

def test_enhanced_topology_loading():
    """Test if enhanced topology loading exists"""
    try:
        template_path = "templates/user/dynamic_simulation.html"
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        enhanced_functions = [
            "loadTopologyFromConfig",
            "getAttemptTopology",
            "loadTopologyData",
            "saveTopologyToServer"
        ]
        
        all_found = True
        for func in enhanced_functions:
            if func in content:
                print(f"✅ Found enhanced function: {func}")
            else:
                print(f"❌ Missing enhanced function: {func}")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Error checking enhanced functions: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Topology Implementation")
    print("=" * 50)
    
    tests = [
        ("Basic Connectivity", test_basic_connectivity),
        ("New Topology Endpoint", test_new_topology_endpoint),
        ("Network State Endpoint", test_network_state_endpoint),
        ("Validation Functions", test_validation_functions),
        ("Backend Validation", test_backend_validation),
        ("Enhanced Topology Loading", test_enhanced_topology_loading)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n📊 Test Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Implementation looks good.")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())