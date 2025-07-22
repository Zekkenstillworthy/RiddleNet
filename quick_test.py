#!/usr/bin/env python3
"""
Simplified test to check the activity feed endpoint directly
"""
import requests
import json
import time

def quick_test():
    """Quick test of the activity feed"""
    url = "http://localhost:5001/admin/api/analytics/activity-feed?limit=3"
    
    try:
        print("🔍 Testing activity feed...")
        response = requests.get(url, timeout=5)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running on localhost:5001")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
