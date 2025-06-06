#!/usr/bin/env python3
"""
Test script to verify all user dashboard routes work correctly
"""

import requests
import sys

# Base URL for the application
BASE_URL = "http://localhost:5000"

# Test routes
routes_to_test = [
    "/user/dashboard",
    "/user/leaderboard", 
    "/user/classes",
    "/user/profile",
    "/user/scores",
    "/user/about_us"
]

def test_routes():
    """Test all routes to ensure they respond correctly"""
    print("Testing RiddleNet User Dashboard Routes...")
    print("=" * 50)
    
    success_count = 0
    total_routes = len(routes_to_test)
    
    for route in routes_to_test:
        url = BASE_URL + route
        try:
            response = requests.get(url, allow_redirects=True, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {route} - OK (200)")
                success_count += 1
            elif response.status_code == 302:
                print(f"🔄 {route} - Redirect (302) - likely to login")
                success_count += 1
            else:
                print(f"❌ {route} - Error ({response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {route} - Connection Error (Server not running?)")
        except requests.exceptions.Timeout:
            print(f"❌ {route} - Timeout Error")
        except Exception as e:
            print(f"❌ {route} - Unexpected Error: {e}")
    
    print("=" * 50)
    print(f"Results: {success_count}/{total_routes} routes working")
    
    if success_count == total_routes:
        print("🎉 All routes are working correctly!")
        return True
    else:
        print("⚠️  Some routes need attention")
        return False

if __name__ == "__main__":
    test_routes()
