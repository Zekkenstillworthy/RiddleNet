#!/usr/bin/env python3
"""
Direct test of the student progress API
"""

import requests
import json

# Test with admin authentication simulation
url = "http://127.0.0.1:5001/admin/api/classes/7/students/2/progress"

# Create a session to maintain cookies
session = requests.Session()

# First, try to access the admin login page
login_page = session.get("http://127.0.0.1:5001/admin/login")
print(f"Login page status: {login_page.status_code}")

# Try the API directly 
response = session.get(url)
print(f"API Response Status: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Content Type: {response.headers.get('content-type', 'Unknown')}")

if response.status_code == 200:
    try:
        data = response.json()
        print("✅ JSON Response:")
        print(json.dumps(data, indent=2))
    except:
        print("❌ Response is not JSON:")
        print(response.text[:500])  # First 500 chars
else:
    print(f"❌ Error Response:")
    print(response.text[:500])  # First 500 chars