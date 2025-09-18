#!/usr/bin/env python3
"""
Test the forgot password routes accessibility
"""

import requests
import sys

def test_forgot_password_access():
    """Test that the forgot password routes are accessible without authentication"""
    
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 Testing admin forgot password route accessibility...")
    print()
    
    # Test 1: Check forgot password page accessibility
    try:
        response = requests.get(f"{base_url}/admin/forgot-password", timeout=5)
        print(f"📝 GET /admin/forgot-password:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS: Forgot password page is accessible!")
            if "Forgot Password" in response.text:
                print("   ✅ Page contains 'Forgot Password' content")
            else:
                print("   ⚠️  Page might not be the correct forgot password form")
        elif response.status_code == 302:
            print("   ❌ REDIRECTED: Still being redirected to login")
            print(f"   Location header: {response.headers.get('Location', 'Not found')}")
        else:
            print(f"   ❌ ERROR: Unexpected status code {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CONNECTION ERROR: {str(e)}")
        print("   Make sure the application is running on port 5001")
        return False
    
    print()
    
    # Test 2: Check reset password page accessibility (with dummy token)
    try:
        dummy_token = "test_token_123"
        response = requests.get(f"{base_url}/admin/reset-password/{dummy_token}", timeout=5)
        print(f"📝 GET /admin/reset-password/{dummy_token}:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS: Reset password page is accessible!")
            if "Reset Password" in response.text:
                print("   ✅ Page contains 'Reset Password' content")
        elif response.status_code == 302:
            # Expected if token is invalid, but route should be accessible
            print("   ✅ ACCESSIBLE: Route is accessible (redirect due to invalid token is expected)")
        else:
            print(f"   Status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CONNECTION ERROR: {str(e)}")
    
    print()
    
    # Test 3: Test login page for comparison
    try:
        response = requests.get(f"{base_url}/admin/login", timeout=5)
        print(f"📝 GET /admin/login:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login page is accessible")
            if "Forgot password?" in response.text:
                print("   ✅ Login page contains 'Forgot password?' link")
            else:
                print("   ⚠️  Login page might be missing the forgot password link")
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CONNECTION ERROR: {str(e)}")
    
    print()
    print("🎯 Test Summary:")
    print("   - If forgot password page shows status 200, the route protection fix worked!")
    print("   - If you still see redirects to login, the application might need a restart")
    print()

if __name__ == "__main__":
    test_forgot_password_access()