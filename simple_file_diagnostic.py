#!/usr/bin/env python3
"""
Simple diagnostic test for file creation issues
"""

import os
import sys
import traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from admin.services.enhanced_class_template_generator import enhanced_template_generator

def simple_file_creation_test():
    """Test file creation capabilities"""
    print("🔍 Simple File Creation Diagnostic")
    print("=" * 50)
    
    app = Flask(__name__)
    
    with app.app_context():
        print("1. Testing Flask App Context...")
        print("   ✅ App context created successfully")
        
        print("\n2. Testing Enhanced Template Generator...")
        try:
            # Initialize directories
            enhanced_template_generator._ensure_app_context_directories()
            
            templates_dir = enhanced_template_generator.templates_dir
            routes_dir = enhanced_template_generator.routes_dir
            
            print(f"   ✅ Templates directory: {templates_dir}")
            print(f"   ✅ Routes directory: {routes_dir}")
            
            # Check if directories exist
            if not os.path.exists(templates_dir):
                print(f"   ❌ Templates directory doesn't exist: {templates_dir}")
                return False
            
            if not os.path.exists(routes_dir):
                print(f"   ❌ Routes directory doesn't exist: {routes_dir}")
                return False
            
        except Exception as e:
            print(f"   ❌ Template generator initialization failed: {e}")
            traceback.print_exc()
            return False
        
        print("\n3. Testing File Creation Permissions...")
        try:
            # Test creating a template file
            test_template_content = """
<!DOCTYPE html>
<html>
<head><title>Test Template</title></head>
<body><h1>Test Template</h1></body>
</html>
"""
            
            test_template_path = os.path.join(templates_dir, "test_template.html")
            with open(test_template_path, 'w', encoding='utf-8') as f:
                f.write(test_template_content)
            
            print(f"   ✅ Template file created: {test_template_path}")
            
            # Test creating a routes file
            test_routes_content = """
from flask import Blueprint

test_bp = Blueprint('test', __name__)

@test_bp.route('/test')
def test_route():
    return 'Test route working'
"""
            
            test_routes_path = os.path.join(routes_dir, "test_routes.py")
            with open(test_routes_path, 'w', encoding='utf-8') as f:
                f.write(test_routes_content)
            
            print(f"   ✅ Routes file created: {test_routes_path}")
            
            # Clean up test files
            os.remove(test_template_path)
            os.remove(test_routes_path)
            
            print("   ✅ Test files cleaned up successfully")
            
        except Exception as e:
            print(f"   ❌ File creation failed: {e}")
            traceback.print_exc()
            return False
        
        print("\n4. Testing Mock Class Template Generation...")
        try:
            # Create a mock class object
            class MockClass:
                def __init__(self):
                    self.id = 999
                    self.name = "Test Networking Class"
                    self.code = "TEST999"
                    self.section = "A"
                    self.description = "Test class for diagnostics"
                    self.question_groups = []
            
            mock_class = MockClass()
            
            # Test template data preparation
            template_data = enhanced_template_generator._prepare_template_data(mock_class)
            print(f"   ✅ Template data prepared with {len(template_data)} keys")
            
            # Test class type detection
            class_type = enhanced_template_generator._detect_class_type(mock_class)
            print(f"   ✅ Class type detected: {class_type}")
            
            # Test template content generation
            template_content = enhanced_template_generator._generate_enhanced_template_content(template_data)
            print(f"   ✅ Template content generated ({len(template_content)} characters)")
            
            # Test actual file creation
            template_filename = f"class_{mock_class.id}_{mock_class.code.lower()}.html"
            template_path = os.path.join(templates_dir, template_filename)
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            print(f"   ✅ Template file created: {template_filename}")
            
            # Test routes generation
            routes_data = enhanced_template_generator._prepare_routes_data(mock_class)
            routes_content = enhanced_template_generator._generate_enhanced_routes_content(routes_data)
            
            routes_filename = f"class_{mock_class.id}_routes.py"
            routes_path = os.path.join(routes_dir, routes_filename)
            
            with open(routes_path, 'w', encoding='utf-8') as f:
                f.write(routes_content)
            
            print(f"   ✅ Routes file created: {routes_filename}")
            
            # Show where files are located
            print(f"\n   📁 Files created at:")
            print(f"      Template: {template_path}")
            print(f"      Routes: {routes_path}")
            
            # Clean up
            os.remove(template_path)
            os.remove(routes_path)
            print("   ✅ Mock files cleaned up")
            
        except Exception as e:
            print(f"   ❌ Mock template generation failed: {e}")
            traceback.print_exc()
            return False
        
        print("\n5. Testing Static Template Integration...")
        try:
            static_templates = enhanced_template_generator.static_templates_map
            print(f"   ✅ Static templates loaded: {len(static_templates)} types")
            
            for class_type, config in static_templates.items():
                print(f"      - {class_type}: {len(config['simulations'])} simulations")
            
        except Exception as e:
            print(f"   ❌ Static template integration failed: {e}")
            return False
        
        print("\n🎉 All File Creation Tests Passed!")
        
        print("\n📍 File Locations:")
        print(f"   Templates: {templates_dir}")
        print(f"   Routes: {routes_dir}")
        
        print("\n📝 What happens when admin creates a class:")
        print("   1. Class object is created in database")
        print("   2. enhanced_template_generator.generate_all_class_resources(class_id) is called")
        print("   3. Template and routes files are created in the above directories")
        print("   4. route_registry.register_class_routes(class_id) registers the routes")
        print("   5. Students can access the class at /class/{id}/")
        
        return True

if __name__ == "__main__":
    success = simple_file_creation_test()
    
    if success:
        print("\n✅ File creation system is working correctly!")
        print("\nIf admin still can't create files, the issue might be:")
        print("1. Database connection problems")
        print("2. Missing Flask application context")
        print("3. Import errors in the main application")
        print("4. Route registration issues")
    else:
        print("\n❌ File creation system has issues!")
        print("Please check the errors above.")
    
    sys.exit(0 if success else 1)
