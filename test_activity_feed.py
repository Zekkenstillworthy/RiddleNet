#!/usr/bin/env python3
"""
Test script to check if the activity feed percentages are fixed
"""
import requests
import json
import time

def test_activity_feed():
    """Test the activity feed API and check percentages"""
    url = "http://localhost:5001/admin/api/analytics/activity-feed?limit=5"
    
    try:
        # Wait a moment for server to be ready
        time.sleep(2)
        
        print("Testing activity feed API...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response successful")
            print(f"📊 Activity feed data:")
            print(json.dumps(data, indent=2))
            
            # Check for percentage values > 100
            if isinstance(data, list):
                high_percentages = []
                for item in data:
                    if isinstance(item, dict):
                        # Look for percentage-like fields
                        for key, value in item.items():
                            if isinstance(value, (int, float)) and value > 100:
                                if 'percent' in key.lower() or 'score' in key.lower():
                                    high_percentages.append(f"{key}: {value}")
                
                if high_percentages:
                    print(f"❌ Found high percentages: {high_percentages}")
                else:
                    print("✅ No percentages above 100% found!")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server may not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_activity_feed()
