#!/usr/bin/env python3
"""
Test script to verify the simulation save functionality
"""
import requests
import json
import sys

def test_simulation_save():
    base_url = "http://127.0.0.1:5001"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("🔍 Testing simulation save functionality...")
    
    # Test 1: Try to access the edit page directly (should redirect to login)
    print("\n📍 Step 1: Testing access to simulation edit page...")
    response = session.get(f"{base_url}/admin/simulation/edit/1")
    
    if response.status_code == 200:
        print("✅ Successfully accessed simulation edit page (already logged in)")
        return test_save_endpoint(session, base_url)
    elif response.url.endswith('/admin/login') or 'login' in response.url:
        print("🔐 Redirected to login page - authentication required")
        return test_login_and_save(session, base_url)
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        return False

def test_login_and_save(session, base_url):
    print("\n📍 Step 2: Attempting admin login...")
    
    # Get login page to extract any CSRF tokens
    login_response = session.get(f"{base_url}/admin/login")
    if login_response.status_code != 200:
        print(f"❌ Failed to access login page: {login_response.status_code}")
        return False
    
    # Try common admin credentials (you'll need to adjust these)
    login_data = {
        'username': 'admin',
        'password': 'admin'
    }
    
    # Attempt login
    login_response = session.post(f"{base_url}/admin/login", data=login_data, allow_redirects=False)
    
    if login_response.status_code in [302, 303]:
        print("✅ Login appears successful (redirect received)")
        return test_save_endpoint(session, base_url)
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print("   You may need to log in manually through the browser")
        return False

def test_save_endpoint(session, base_url):
    print("\n📍 Step 3: Testing save endpoint...")
    
    # Test data for simulation save
    test_data = {
        "title": "Test Simulation Save",
        "description": "Testing the save functionality",
        "difficulty": "Medium",
        "problem_type": "network",
        "scenario": "Test scenario",
        "solution": "Test solution",
        "time_limit": 15,
        "base_score": 50,
        "time_bonus": 10,
        "hints": [],
        "initial_topology": {
            "devices": [],
            "connections": []
        },
        "solution_topology": {
            "devices": [],
            "connections": []
        },
        "required_steps": [],
        "is_active": True,
        "cli_rules": {}
    }
    
    # Attempt to save
    headers = {'Content-Type': 'application/json'}
    response = session.post(
        f"{base_url}/admin/simulation/edit/1/save",
        headers=headers,
        json=test_data
    )
    
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get('success'):
                print("✅ Save successful!")
                print(f"   Message: {result.get('message', 'No message')}")
                return True
            else:
                print(f"❌ Save failed: {result.get('message', 'Unknown error')}")
                return False
        except json.JSONDecodeError:
            print("❌ Invalid JSON response from server")
            print(f"   Response text: {response.text[:200]}...")
            return False
    else:
        print(f"❌ HTTP error: {response.status_code}")
        if response.status_code == 401:
            print("   Authentication required - please log in through the browser first")
        elif response.status_code == 404:
            print("   Simulation not found")
        elif response.status_code == 500:
            print("   Server error - check application logs")
        
        print(f"   Response: {response.text[:200]}...")
        return False

def check_application_status():
    print("🏥 Checking application health...")
    try:
        response = requests.get("http://127.0.0.1:5001/", timeout=5)
        if response.status_code == 200:
            print("✅ Application is running and responding")
            return True
        else:
            print(f"⚠️ Application responding with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Application is not running or not accessible on port 5001")
        return False
    except requests.exceptions.Timeout:
        print("❌ Application is not responding (timeout)")
        return False

if __name__ == "__main__":
    print("🧪 RiddleNet Simulation Save Functionality Test")
    print("=" * 50)
    
    if not check_application_status():
        print("\n💡 Make sure the RiddleNet application is running:")
        print("   python run.py")
        sys.exit(1)
    
    success = test_simulation_save()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Save functionality is working.")
    else:
        print("❌ Tests failed. Check the issues above.")
        print("\n💡 Possible solutions:")
        print("   1. Log in to the admin panel through your browser first")
        print("   2. Check if simulation ID 1 exists in the database")
        print("   3. Check application logs for detailed error messages")
        print("   4. Verify database connectivity and permissions")