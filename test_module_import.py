#!/usr/bin/env python3
"""
Test script to verify module_loader import works correctly
"""
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {current_dir}")
    print(f"Python path includes script dir: {current_dir in sys.path}")
    
    # Test the import
    from module_loader import get_module_lesson_content
    print("✅ Successfully imported module_loader")
    
    # Test the function
    content = get_module_lesson_content()
    print(f"✅ Successfully loaded {len(content)} lessons")
    
    # Test a specific lesson
    if "1.1" in content:
        lesson = content["1.1"]
        print(f"✅ Lesson 1.1 found: {lesson['title']}")
        print(f"   Content length: {len(lesson['content'])} characters")
    else:
        print("❌ Lesson 1.1 not found")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
