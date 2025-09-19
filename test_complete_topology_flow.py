#!/usr/bin/env python3
"""
Complete test script to verify topology data flow from admin to user
Creates a test user, logs in, and checks topology API
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from __init__ import create_app, db
from user.models.user import User as UserModel
from admin.models.simulation import Simulation
import requests
import json
import hashlib

def create_test_user():
    """Create a test user for testing"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if test user already exists
            test_user = UserModel.query.filter_by(username='testuser').first()
            
            if test_user:
                print("✅ Test user already exists")
                return True
                
            # Create new test user
            password_hash = hashlib.sha256('testpassword'.encode()).hexdigest()
            
            new_user = UserModel(
                username='testuser',
                email='test@example.com',
                password_hash=password_hash,
                is_active=True
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            print("✅ Test user created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            return False

def test_login_and_topology():
    """Test login and topology API"""
    base_url = "http://127.0.0.1:5001"
    
    # Create session
    session = requests.Session()
    
    print("\n🔐 Testing login and topology API...")
    
    # Step 1: Get login page to extract any CSRF tokens
    login_page = session.get(f"{base_url}/login")
    print(f"Login page status: {login_page.status_code}")
    
    # Step 2: Attempt login
    login_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    
    # Check if login page has a form with action
    if 'action=' in login_page.text:
        print("   - Found form action in login page")
    
    login_response = session.post(f"{base_url}/login", data=login_data)
    print(f"Login response status: {login_response.status_code}")
    
    # Check if login was successful (usually redirects or changes content)
    if login_response.status_code in [200, 302]:
        print("✅ Login request completed")
        
        # Check cookies
        cookies = session.cookies.get_dict()
        print(f"Cookies after login: {list(cookies.keys())}")
        
        if any('session' in cookie.lower() for cookie in cookies.keys()):
            print("✅ Session cookie found")
        
    # Step 3: Test topology API
    print(f"\n📡 Testing topology API...")
    topology_url = f"{base_url}/dynamic/api/simulation/1/topology"
    
    try:
        response = session.get(topology_url)
        print(f"Topology API status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                data = response.json()
                print(f"✅ Successfully got JSON response!")
                print(f"Response structure: {list(data.keys())}")
                
                if 'topology' in data:
                    topology = data['topology']
                    devices = topology.get('devices', [])
                    connections = topology.get('connections', [])
                    
                    print(f"🔧 Topology data:")
                    print(f"   - Source: {data.get('source', 'unknown')}")
                    print(f"   - Devices: {len(devices)}")
                    print(f"   - Connections: {len(connections)}")
                    
                    if devices:
                        first_device = devices[0]
                        print(f"   - First device ID: {first_device.get('id', 'No ID')}")
                        print(f"   - First device type: {first_device.get('type', 'No type')}")
                        
                        if data.get('source') == 'admin':
                            print("🎯 SUCCESS: Admin-placed devices are visible to user!")
                        else:
                            print(f"⚠️ Note: Topology source is '{data.get('source')}', not 'admin'")
                    else:
                        print("⚠️ No devices found in topology")
                else:
                    print("❌ No topology field in response")
                    
            else:
                print(f"❌ Got HTML instead of JSON - authentication may have failed")
                print(f"Content-Type: {content_type}")
                
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response snippet: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error testing topology API: {e}")

def verify_database_topology():
    """Verify that simulation 1 has topology data in database"""
    app = create_app()
    
    with app.app_context():
        try:
            simulation = Simulation.query.get(1)
            if not simulation:
                print("❌ Simulation 1 not found in database")
                return False
                
            print(f"\n📊 Database verification for simulation {simulation.id}:")
            print(f"   - Title: {simulation.title}")
            
            config = simulation.simulation_config
            if isinstance(config, str):
                try:
                    config = json.loads(config)
                except:
                    config = {}
            
            network_topology = config.get('network_topology', {})
            
            if network_topology:
                devices = network_topology.get('devices', [])
                connections = network_topology.get('connections', [])
                print(f"   - Admin topology devices: {len(devices)}")
                print(f"   - Admin topology connections: {len(connections)}")
                
                if devices:
                    print(f"   - First device: {devices[0].get('id', 'No ID')}")
                    return True
                else:
                    print("   - No devices in admin topology")
                    return False
            else:
                print("   - No network_topology field found")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying database: {e}")
            return False

def main():
    print("🧪 Complete Topology Data Flow Test")
    print("=" * 50)
    
    # Step 1: Verify database has topology data
    if not verify_database_topology():
        print("\n❌ Database verification failed - no topology data to test with")
        return
    
    # Step 2: Create test user
    if not create_test_user():
        print("\n❌ Test user creation failed")
        return
    
    # Step 3: Test login and topology API
    test_login_and_topology()

if __name__ == "__main__":
    main()