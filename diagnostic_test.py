#!/usr/bin/env python3
"""
Diagnostic script to test file creation permissions and paths
"""

import os
import sys
import tempfile
from pathlib import Path

def test_directory_permissions():
    """Test directory creation and file writing permissions"""
    print("🔧 Testing Directory Permissions and File Creation")
    print("=" * 60)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    print(f"Base path: {base_path}")
    
    # Test directories to check
    test_dirs = [
        'templates/user/classes',
        'user/routes/generated',
        'static/css/user'
    ]
    
    print("\n1. Testing Directory Creation...")
    for test_dir in test_dirs:
        full_path = os.path.join(base_path, test_dir)
        print(f"\nTesting: {full_path}")
        
        try:
            # Check if directory exists
            if os.path.exists(full_path):
                print(f"   ✅ Directory exists")
                
                # Test if we can write to it
                test_file = os.path.join(full_path, 'test_write.tmp')
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    print(f"   ✅ Write permission OK")
                    os.remove(test_file)
                    print(f"   ✅ Delete permission OK")
                except Exception as e:
                    print(f"   ❌ Write/Delete failed: {e}")
                    
            else:
                print(f"   ⚠️  Directory doesn't exist, trying to create...")
                try:
                    os.makedirs(full_path, exist_ok=True)
                    print(f"   ✅ Directory created successfully")
                    
                    # Test write after creation
                    test_file = os.path.join(full_path, 'test_write.tmp')
                    with open(test_file, 'w') as f:
                        f.write("test")
                    print(f"   ✅ Write permission OK")
                    os.remove(test_file)
                    print(f"   ✅ Delete permission OK")
                    
                except Exception as e:
                    print(f"   ❌ Directory creation failed: {e}")
                    
        except Exception as e:
            print(f"   ❌ Error testing directory: {e}")
    
    print("\n2. Testing Template File Creation...")
    try:
        templates_dir = os.path.join(base_path, 'templates', 'user', 'classes')
        test_template = os.path.join(templates_dir, 'test_class_template.html')
        
        template_content = """
{% extends "user/base.html" %}
{% block title %}Test Class{% endblock %}
{% block content %}
<h1>Test Class Template</h1>
<p>This is a test template to verify file creation works.</p>
{% endblock %}
"""
        
        with open(test_template, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"   ✅ Template file created: {test_template}")
        
        # Verify file exists and is readable
        if os.path.exists(test_template):
            with open(test_template, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"   ✅ Template file readable ({len(content)} chars)")
            
            # Clean up
            os.remove(test_template)
            print(f"   ✅ Template file deleted")
        else:
            print(f"   ❌ Template file not found after creation")
            
    except Exception as e:
        print(f"   ❌ Template creation failed: {e}")
    
    print("\n3. Testing Routes File Creation...")
    try:
        routes_dir = os.path.join(base_path, 'user', 'routes', 'generated')
        test_route = os.path.join(routes_dir, 'test_class_routes.py')
        
        routes_content = """
from flask import Blueprint
test_bp = Blueprint('test', __name__)

@test_bp.route('/')
def test_route():
    return "Test route working"
"""
        
        with open(test_route, 'w', encoding='utf-8') as f:
            f.write(routes_content)
        
        print(f"   ✅ Routes file created: {test_route}")
        
        # Verify file exists and is readable
        if os.path.exists(test_route):
            with open(test_route, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"   ✅ Routes file readable ({len(content)} chars)")
            
            # Clean up
            os.remove(test_route)
            print(f"   ✅ Routes file deleted")
        else:
            print(f"   ❌ Routes file not found after creation")
            
    except Exception as e:
        print(f"   ❌ Routes creation failed: {e}")
    
    print("\n4. Testing Path Handling...")
    try:
        # Test various path formats
        test_paths = [
            'templates\\user\\classes',  # Windows backslash
            'templates/user/classes',    # Unix forward slash
            os.path.join('templates', 'user', 'classes')  # OS-specific
        ]
        
        for path_format in test_paths:
            full_path = os.path.join(base_path, path_format)
            normalized_path = os.path.normpath(full_path)
            exists = os.path.exists(normalized_path)
            print(f"   Path: {path_format} -> {exists}")
            
    except Exception as e:
        print(f"   ❌ Path testing failed: {e}")
    
    print("\n5. Testing with Temp Directory...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"   Temp dir: {temp_dir}")
            
            # Create subdirectories
            test_subdir = os.path.join(temp_dir, 'test', 'subdir')
            os.makedirs(test_subdir, exist_ok=True)
            print(f"   ✅ Subdirectory created")
            
            # Create test file
            test_file = os.path.join(test_subdir, 'test.html')
            with open(test_file, 'w') as f:
                f.write('<h1>Test</h1>')
            print(f"   ✅ File created in temp subdirectory")
            
            print(f"   ✅ Temp directory test successful")
            
    except Exception as e:
        print(f"   ❌ Temp directory test failed: {e}")
    
    print("\n6. System Information...")
    print(f"   Python version: {sys.version}")
    print(f"   Platform: {sys.platform}")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"   User: {os.environ.get('USERNAME', 'Unknown')}")
    
    print("\n✅ Diagnostic complete!")

if __name__ == "__main__":
    test_directory_permissions()
