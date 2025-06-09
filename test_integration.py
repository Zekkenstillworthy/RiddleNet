#!/usr/bin/env python3
"""
Test script to verify the integration of extracted module content.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_module_loader():
    """Test the module loader functionality."""
    print("Testing module loader...")
    
    try:
        from module_loader import get_module_lesson_content, get_available_lesson_ids
        
        # Test getting all content
        content = get_module_lesson_content()
        print(f"✓ Successfully loaded {len(content)} lessons")
        
        # Test getting available IDs
        lesson_ids = get_available_lesson_ids()
        print(f"✓ Available lesson IDs: {lesson_ids}")
        
        # Test specific lesson content
        if "1.1" in content:
            lesson = content["1.1"]
            print(f"✓ Lesson 1.1 title: {lesson['title']}")
            print(f"✓ Lesson 1.1 content length: {len(lesson['content'])} characters")
            
            # Check if content contains HTML
            if "<div" in lesson['content'] and "</div>" in lesson['content']:
                print("✓ Content appears to be properly formatted HTML")
            else:
                print("⚠ Content may not be properly formatted")
        else:
            print("✗ Lesson 1.1 not found in content")
            
    except Exception as e:
        print(f"✗ Error testing module loader: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_flask_integration():
    """Test the Flask route integration."""
    print("\nTesting Flask integration...")
    
    try:
        # Import Flask app components
        from user.views import get_networking_lesson
        from flask import session
        
        print("✓ Successfully imported Flask components")
        
        # Note: We can't test the actual route without a Flask app context
        # But we can verify the function exists and imports work
        
    except Exception as e:
        print(f"✗ Error testing Flask integration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Run all tests."""
    print("=== Module Content Integration Test ===")
    
    success = True
    
    # Test module loader
    if not test_module_loader():
        success = False
    
    # Test Flask integration
    if not test_flask_integration():
        success = False
    
    print("\n=== Test Results ===")
    if success:
        print("✓ All tests passed! Integration appears to be working.")
        print("\nNext steps:")
        print("1. Visit http://localhost:5000/learning/networking-1 in your browser")
        print("2. Click on any lesson to see the extracted content")
        print("3. Verify that the content displays properly")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
