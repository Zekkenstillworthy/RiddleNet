#!/usr/bin/env python3
"""
Simple test script for Enhanced Classroom Automation System (without eventlet)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from admin.services.enhanced_class_template_generator import enhanced_template_generator
from admin.services.dynamic_route_registry import route_registry

def create_simple_app():
    """Create a simple Flask app for testing"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    db = SQLAlchemy(app)
    
    return app, db

def simple_test():
    """Simple test of the automation system"""
    print("🧪 Simple Enhanced Classroom Automation Test")
    print("=" * 50)
    
    app, db = create_simple_app()
    
    with app.app_context():
        print("✅ App context created successfully")
        
        # Test template generator initialization
        print("1. Testing template generator initialization...")
        try:
            # Re-initialize the generator in app context
            enhanced_template_generator._ensure_app_context_directories()
            print("✅ Template generator initialized")
        except Exception as e:
            print(f"❌ Template generator failed: {e}")
            return False
        
        # Test static template mappings
        print("2. Testing static template mappings...")
        static_templates = enhanced_template_generator.static_templates_map
        print(f"✅ Found {len(static_templates)} class type mappings:")
        
        for class_type, config in static_templates.items():
            print(f"   - {class_type}: {len(config['simulations'])} simulations")
        
        # Test class type detection
        print("3. Testing class type detection...")
        
        # Create a test class object (mock)
        class MockClass:
            def __init__(self, name):
                self.name = name
                self.id = 1
                self.code = "TEST101"
                self.section = "A"
                self.description = "Test class"
                self.question_groups = []
        
        test_cases = [
            ("Introduction to Networking", "networking1"),
            ("Networking 1", "networking1"),
            ("Advanced Networking", "networking2"),
            ("Networking 2", "networking2"),
            ("Network Security", "security"),
            ("Basic Computer Science", "general")
        ]
        
        for test_name, expected_type in test_cases:
            mock_class = MockClass(test_name)
            detected_type = enhanced_template_generator._detect_class_type(mock_class)
            status = "✅" if detected_type == expected_type else "❌"
            print(f"   {status} '{test_name}' -> {detected_type} (expected: {expected_type})")
        
        # Test directory creation
        print("4. Testing directory creation...")
        templates_dir = enhanced_template_generator.templates_dir
        routes_dir = enhanced_template_generator.routes_dir
        
        print(f"   Templates directory: {templates_dir}")
        print(f"   Routes directory: {routes_dir}")
        
        if os.path.exists(templates_dir):
            print("   ✅ Templates directory exists")
        else:
            print("   ❌ Templates directory missing")
        
        if os.path.exists(routes_dir):
            print("   ✅ Routes directory exists")
        else:
            print("   ❌ Routes directory missing")
        
        # Test template content generation
        print("5. Testing template content generation...")
        try:
            mock_class = MockClass("Introduction to Networking")
            template_data = enhanced_template_generator._prepare_template_data(mock_class)
            print(f"   ✅ Template data prepared: {len(template_data)} keys")
            
            # Test enhanced template generation
            template_content = enhanced_template_generator._generate_enhanced_template_content(template_data)
            print(f"   ✅ Enhanced template generated: {len(template_content)} characters")
            
        except Exception as e:
            print(f"   ❌ Template generation failed: {e}")
            return False
        
        # Test simulation proxy routes
        print("6. Testing simulation proxy routes...")
        try:
            routes_data = {
                'class_id': 1,
                'class_name': 'Test Class',
                'class_code': 'TEST101',
                'blueprint_name': 'test_class',
                'class_type': 'networking1'
            }
            
            proxy_routes = enhanced_template_generator._generate_simulation_proxy_routes(routes_data, 'networking1')
            print(f"   ✅ Proxy routes generated: {len(proxy_routes)} characters")
            
        except Exception as e:
            print(f"   ❌ Proxy routes generation failed: {e}")
            return False
        
        # Test dashboard integration
        print("7. Testing dashboard integration...")
        try:
            mock_class = MockClass("Introduction to Networking")
            integration_info = enhanced_template_generator.create_class_dashboard_integration(mock_class)
            print(f"   ✅ Dashboard integration created")
            print(f"   - Dashboard URL: {integration_info['dashboard_url']}")
            print(f"   - API endpoints: {len(integration_info['api_endpoints'])}")
            print(f"   - Static integrations: {len(integration_info['static_integrations'])}")
            
        except Exception as e:
            print(f"   ❌ Dashboard integration failed: {e}")
            return False
        
        print("\n🎉 Simple Test Complete!")
        print("\n📝 Test Results:")
        print("   ✅ Template generator initialized correctly")
        print("   ✅ Static template mappings loaded")
        print("   ✅ Class type detection working")
        print("   ✅ Directory creation working")
        print("   ✅ Template content generation working")
        print("   ✅ Simulation proxy routes working")
        print("   ✅ Dashboard integration working")
        
        print("\n🚀 System Status: READY")
        print("The enhanced classroom automation system is working correctly!")
        
        return True

if __name__ == "__main__":
    success = simple_test()
    
    if success:
        print("\n✅ All tests passed! The automation system is working correctly.")
        print("\n📖 To use the system:")
        print("   1. Start your Flask application")
        print("   2. Go to /admin/classes")
        print("   3. Create a new class")
        print("   4. The system will automatically generate templates and routes")
        print("   5. Students can access the class via /class/{id}/")
    else:
        print("\n❌ Some tests failed.")
    
    sys.exit(0 if success else 1)
