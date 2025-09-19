#!/usr/bin/env python3
"""
Test script to verify user topology API endpoint
"""

import requests
import json

def test_user_topology_api():
    """Test the user topology API endpoint that should return admin-placed devices"""
    base_url = "http://127.0.0.1:5001"
    
    # Test the topology API endpoint
    topology_url = f"{base_url}/dynamic/api/simulation/1/topology"
    
    print("Testing User Topology API...")
    print(f"URL: {topology_url}")
    print("=" * 50)
    
    try:
        response = requests.get(topology_url)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
                
                # Check if topology data exists
                if 'topology' in data:
                    topology = data['topology']
                    print(f"\n✅ Topology found in response!")
                    print(f"   - Topology type: {type(topology)}")
                    
                    if isinstance(topology, dict):
                        print(f"   - Devices: {len(topology.get('devices', []))}")
                        print(f"   - Connections: {len(topology.get('connections', []))}")
                        
                        if topology.get('devices'):
                            print(f"   - First device: {topology['devices'][0].get('id', 'No ID')}")
                    elif isinstance(topology, str):
                        try:
                            parsed_topology = json.loads(topology)
                            print(f"   - Devices: {len(parsed_topology.get('devices', []))}")
                            print(f"   - Connections: {len(parsed_topology.get('connections', []))}")
                        except json.JSONDecodeError:
                            print(f"   - Topology is string but not valid JSON")
                            
                else:
                    print("❌ No topology field in response")
            else:
                print(f"❌ Response is HTML, not JSON")
                print(f"Content-Type: {content_type}")
                html_content = response.text
                print(f"HTML snippet (first 500 chars): {html_content[:500]}")
                
                # Check for login page indicators
                if 'login' in html_content.lower() or 'unauthorized' in html_content.lower():
                    print("❌ Likely redirected to login page - authentication required")
                elif 'error' in html_content.lower():
                    print("❌ Likely an error page")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running on port 5001?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_user_topology_api()