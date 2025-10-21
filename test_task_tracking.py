"""
Quick Test Script for Task Assignment Tracking

Tests the following:
1. Task config can be loaded from student view
2. Task progress can be saved
3. Activity tracking is functioning
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:5001"
SIMULATION_ID = 70

# Login session (you'll need to have a logged-in session)
session = requests.Session()

def test_task_config():
    """Test task config endpoint"""
    print("\n🧪 Testing Task Config Endpoint...")
    url = f"{BASE_URL}/dynamic/api/{SIMULATION_ID}/task-config"
    
    try:
        response = session.get(url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                task_config = data.get('task_config')
                if task_config:
                    print(f"   ✅ Task config loaded")
                    print(f"   📋 Enabled: {task_config.get('enabled')}")
                    print(f"   📋 Devices: {len(task_config.get('device_requirements', []))}")
                    print(f"   📋 Connections: {len(task_config.get('connection_requirements', []))}")
                    return True
                else:
                    print(f"   ⚠️ Task config not enabled")
                    return False
        print(f"   ❌ Failed to load task config")
        print(f"   Response: {response.text}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_task_assignment():
    """Test task assignment endpoint"""
    print("\n🧪 Testing Task Assignment Endpoint...")
    url = f"{BASE_URL}/dynamic/api/{SIMULATION_ID}/task-assignment"
    
    try:
        response = session.get(url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                assignment = data.get('assignment')
                if assignment:
                    print(f"   ✅ Assignment found")
                    print(f"   📋 Status: {assignment.get('status')}")
                    print(f"   📋 Completion: {assignment.get('completion_percentage')}%")
                    return True
                else:
                    print(f"   ⚠️ No assignment yet (will be created on first action)")
                    return True
        print(f"   ❌ Failed to load assignment")
        print(f"   Response: {response.text}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_save_progress():
    """Test saving task progress"""
    print("\n🧪 Testing Task Progress Save...")
    url = f"{BASE_URL}/dynamic/api/{SIMULATION_ID}/task-progress"
    
    test_data = {
        "devices_placed": ["router1", "switch1"],
        "devices_configured": {
            "router1": {
                "hostname": "R1",
                "configured_at": "2025-10-20T15:00:00.000Z"
            }
        },
        "connections_made": [
            {
                "source_device": "router1",
                "target_device": "switch1",
                "created_at": "2025-10-20T15:01:00.000Z"
            }
        ],
        "cli_history": [
            {
                "device_id": "router1",
                "command": "enable",
                "executed_at": "2025-10-20T15:02:00.000Z"
            }
        ],
        "activity_log": [
            {
                "type": "device_placed",
                "timestamp": "2025-10-20T15:00:00.000Z",
                "data": {"device_id": "router1"}
            }
        ]
    }
    
    try:
        response = session.post(url, json=test_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Progress saved successfully")
                print(f"   📋 Completion: {data.get('completion_percentage')}%")
                return True
        print(f"   ❌ Failed to save progress")
        print(f"   Response: {response.text}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 Task Assignment Tracking Test Suite")
    print("=" * 60)
    print(f"\nSimulation ID: {SIMULATION_ID}")
    print(f"Base URL: {BASE_URL}")
    
    results = {
        "task_config": test_task_config(),
        "task_assignment": test_task_assignment(),
        "save_progress": test_save_progress()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Task assignment tracking is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
        print("\nNote: You may need to:")
        print("1. Be logged in (session authentication)")
        print("2. Have task mode enabled for simulation 70")
        print("3. Ensure the server is running")

if __name__ == "__main__":
    main()
