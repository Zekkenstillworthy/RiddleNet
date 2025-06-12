#!/usr/bin/env python3
"""
Test script to verify Networking 2 API endpoints are working correctly
"""

import requests
import json
import sys

def test_networking2_api():
    base_url = "http://localhost:5000"
    
    print("Testing Networking 2 API endpoints...")
    print("=" * 50)
    
    # Test 1: Check lessons endpoint
    try:
        print("\n1. Testing /api/networking2/lessons")
        response = requests.get(f"{base_url}/api/networking2/lessons")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Number of lessons: {len(data)}")
            print(f"   Available lesson IDs: {list(data.keys())}")
            
            # Check if we have the expected lessons
            expected_lessons = ['net2_1.1', 'net2_2.1', 'net2_3.1', 'net2_4.1', 'net2_5.1', 'net2_7.1']
            missing_lessons = [lesson for lesson in expected_lessons if lesson not in data]
            if missing_lessons:
                print(f"   ⚠️  Missing lessons: {missing_lessons}")
            else:
                print("   ✅ All expected lessons are present")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: Check individual lesson endpoint
    try:
        print("\n2. Testing /api/networking2/lesson/net2_1.1")
        response = requests.get(f"{base_url}/api/networking2/lesson/net2_1.1")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Lesson Title: {data.get('title', 'N/A')}")
            content = data.get('content', '')
            print(f"   Content Length: {len(content)} characters")
            
            # Check for key content indicators
            content_lower = content.lower()
            if 'routing' in content_lower:
                print("   ✅ Contains routing content")
            if 'simulation' in content_lower:
                print("   ✅ Contains simulation references")
            if len(content) > 1000:
                print("   ✅ Has substantial content")
            else:
                print("   ⚠️  Content seems short")
                
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Check main Networking 2 page
    try:
        print("\n3. Testing main Networking 2 page")
        response = requests.get(f"{base_url}/learning/networking2")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for key HTML elements
            if 'Launch Simulation' in html_content:
                print("   ✅ Simulation button present")
            if 'Networking 2' in html_content:
                print("   ✅ Page title present")
            if 'loadLessonContent' in html_content:
                print("   ✅ JavaScript loader present")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_networking2_api()
