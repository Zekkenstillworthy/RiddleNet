#!/usr/bin/env python3
"""
Test script to validate the student progress modal implementation
"""

import requests
import json

# Test configuration
BASE_URL = "http://127.0.0.1:5001"
CLASS_ID = 7
STUDENT_ID = 2  # Assuming student ID 2 exists

def test_progress_api():
    """Test the student progress API endpoint"""
    print("🧪 Testing Student Progress API...")
    
    # Test the progress API
    url = f"{BASE_URL}/admin/api/classes/{CLASS_ID}/students/{STUDENT_ID}/progress"
    
    try:
        response = requests.get(url)
        print(f"📊 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response received successfully!")
            
            # Print structured data
            if data.get('success'):
                student = data.get('student', {})
                progress = data.get('progress', {})
                
                print(f"\n👤 Student Info:")
                print(f"   Name: {student.get('name', 'Unknown')}")
                print(f"   Email: {student.get('email', 'No email')}")
                
                print(f"\n📈 Progress Overview:")
                overview = progress.get('overview', {})
                print(f"   Overall Progress: {overview.get('overall_progress', 0)}%")
                print(f"   Modules: {overview.get('modules_completed', '0/0')}")
                print(f"   Lessons: {overview.get('lessons_completed', '0/0')}")
                print(f"   Assignments: {overview.get('assignments_submitted', '0/0')}")
                print(f"   Average Score: {overview.get('average_score', 0)}%")
                print(f"   Time Spent: {overview.get('total_time_spent_hours', 0)} hours")
                
                print(f"\n📚 Modules ({len(progress.get('modules', []))}):")
                for i, module in enumerate(progress.get('modules', [])[:3]):  # Show first 3
                    print(f"   {i+1}. {module.get('title', 'Unknown')} - {module.get('progress_percentage', 0)}%")
                
                print(f"\n📝 Recent Activity ({len(progress.get('recent_activity', []))}):")
                for i, activity in enumerate(progress.get('recent_activity', [])[:3]):  # Show first 3
                    print(f"   {i+1}. {activity.get('title', 'Unknown')}")
                
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_class_content_page():
    """Test that the class content manager page loads"""
    print("\n🌐 Testing Class Content Manager Page...")
    
    url = f"{BASE_URL}/admin/class-content-manager/{CLASS_ID}"
    
    try:
        response = requests.get(url)
        print(f"📄 Page Response Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for key modal elements
            modal_checks = [
                ('studentProgressModal', 'Student Progress Modal'),
                ('progressLoadingState', 'Loading State'),
                ('progressContent', 'Progress Content'),
                ('viewStudentProgress', 'View Progress Function'),
                ('fetchStudentProgress', 'Fetch Progress Function')
            ]
            
            print("\n🔍 Modal Implementation Checks:")
            for element, description in modal_checks:
                if element in content:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description} - Missing")
        
        else:
            print(f"❌ Page load failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Student Progress Modal Implementation")
    print("=" * 50)
    
    test_progress_api()
    test_class_content_page()
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")
    print("\n💡 To test the modal manually:")
    print(f"   1. Go to: {BASE_URL}/admin/class-content-manager/{CLASS_ID}")
    print("   2. Look for the Students section")
    print("   3. Click the 'View Progress' button (chart icon)")
    print("   4. The modal should open and display student progress data")