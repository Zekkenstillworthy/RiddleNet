#!/usr/bin/env python3
"""
Test script to verify user topology API endpoint with authentication
"""

import requests
import json

def test_with_authentication():
    """Test the user topology API endpoint with authentication"""
    base_url = "http://127.0.0.1:5001"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("Testing User Topology API with Authentication...")
    print("=" * 60)
    
    # Step 1: Try to access the main simulation page to get redirected to login
    print("Step 1: Checking if we can access simulation page without login...")
    sim_url = f"{base_url}/dynamic/simulation/1"
    response = session.get(sim_url)
    print(f"Simulation page status: {response.status_code}")
    
    if 'login' in response.text.lower():
        print("✅ Correctly redirected to login page")
    
    # Step 2: Check if there's a way to create a test user or login
    # For now, let's see what the topology API returns without proper auth
    topology_url = f"{base_url}/dynamic/api/simulation/1/topology"
    
    print(f"\nStep 2: Testing topology API...")
    print(f"URL: {topology_url}")
    
    try:
        response = session.get(topology_url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                data = response.json()
                print(f"✅ Got JSON response!")
                print(f"Response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Got HTML instead of JSON - likely redirected to login")
                print(f"Content-Type: {content_type}")
        else:
            print(f"❌ Error status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 3: Try to understand the login process
    print(f"\nStep 3: Analyzing login process...")
    login_url = f"{base_url}/login"
    response = session.get(login_url)
    print(f"Login page status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Can access login page")
        # Look for CSRF tokens or form fields
        if 'csrf' in response.text.lower():
            print("   - CSRF token likely required")
        if 'username' in response.text.lower() or 'email' in response.text.lower():
            print("   - Username/email field found")
        if 'password' in response.text.lower():
            print("   - Password field found")

if __name__ == "__main__":
    test_with_authentication()