#!/usr/bin/env python3

"""
Test script to verify the class 7 serialization fix
"""

import requests
import json

def test_class_7_serialization():
    """Test that class 7 page loads without JSON serialization errors"""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # First, let's try to access the login page to get any necessary cookies
    login_url = "http://127.0.0.1:5001/login"
    response = session.get(login_url)
    print(f"Login page status: {response.status_code}")
    
    # Now try to login (we can use Gilbert's credentials)
    login_data = {
        'email': 'gilbertrequitud@gmail.com',
        'password': 'your_password_here'  # You'll need to set this
    }
    
    # For now, let's try to access the class page directly
    # Since the issue is in the template rendering, not authentication
    
    class_url = "http://127.0.0.1:5001/class/7/"
    print(f"Attempting to access: {class_url}")
    
    try:
        response = session.get(class_url, allow_redirects=True)
        print(f"Response status: {response.status_code}")
        print(f"Final URL: {response.url}")
        
        # Check if we get a 500 error or if the page loads
        if response.status_code == 500:
            print("❌ Error 500 - JSON serialization issue still exists")
            if "Object of type QuestionGroup is not JSON serializable" in response.text:
                print("❌ Confirmed: QuestionGroup serialization error")
            else:
                print("❌ Different 500 error")
        elif response.status_code == 302 or "login" in response.url:
            print("🔄 Redirected to login (expected for unauthenticated request)")
        elif response.status_code == 200:
            print("✅ Page loads successfully - serialization fix works!")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_class_7_serialization()
