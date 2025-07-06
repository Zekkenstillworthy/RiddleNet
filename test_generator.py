#!/usr/bin/env python3
"""
Test the enhanced template generator in Flask app context
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def create_test_app():
    """Create a minimal Flask app for testing"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    db = SQLAlchemy(app)
    
    return app, db

def test_enhanced_generator():
    """Test the enhanced generator in app context"""
    print("🧪 Testing Enhanced Generator in Flask Context")
    print("=" * 60)
    
    app, db = create_test_app()
    
    with app.app_context():
        print("✅ Flask app context created")
        
        # Test 1: Import the enhanced generator
        try:
            from admin.services.enhanced_class_template_generator import enhanced_template_generator
            print("✅ Enhanced generator imported successfully")
        except Exception as e:
            print(f"❌ Enhanced generator import failed: {e}")
            return False
        
        # Test 2: Initialize directories
        try:
            enhanced_template_generator._ensure_app_context_directories()
            print(f"✅ Directories initialized:")
            print(f"   Templates: {enhanced_template_generator.templates_dir}")
            print(f"   Routes: {enhanced_template_generator.routes_dir}")
        except Exception as e:
            print(f"❌ Directory initialization failed: {e}")
            return False
        
        # Test 3: Create a mock class for testing
        try:
            class MockClass:
                def __init__(self):
                    self.id = 123
                    self.name = "Test Introduction to Networking"
                    self.code = "TEST123"
                    self.section = "A"
                    self.description = "Test class for automation"
                    self.question_groups = []
            
            mock_class = MockClass()
            print(f"✅ Mock class created: {mock_class.name}")
        except Exception as e:
            print(f"❌ Mock class creation failed: {e}")
            return False
        
        # Test 4: Test class type detection
        try:
            class_type = enhanced_template_generator._detect_class_type(mock_class)
            print(f"✅ Class type detected: {class_type}")
        except Exception as e:
            print(f"❌ Class type detection failed: {e}")
            return False
        
        # Test 5: Test template data preparation
        try:
            template_data = enhanced_template_generator._prepare_template_data(mock_class)
            print(f"✅ Template data prepared ({len(template_data)} keys)")
        except Exception as e:
            print(f"❌ Template data preparation failed: {e}")
            return False
        
        # Test 6: Test template content generation
        try:
            template_content = enhanced_template_generator._generate_enhanced_template_content(template_data)
            print(f"✅ Template content generated ({len(template_content)} chars)")
        except Exception as e:
            print(f"❌ Template content generation failed: {e}")
            return False
        
        # Test 7: Test actual file creation
        try:
            template_filename = enhanced_template_generator.generate_class_template(mock_class)
            print(f"✅ Template file created: {template_filename}")
            
            # Check if file actually exists
            template_path = os.path.join(enhanced_template_generator.templates_dir, template_filename)
            if os.path.exists(template_path):
                print(f"✅ Template file verified on disk")
                
                # Read and verify content
                with open(template_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                print(f"✅ Template file readable ({len(file_content)} chars)")
                
            else:
                print(f"❌ Template file not found: {template_path}")
                return False
                
        except Exception as e:
            print(f"❌ Template file creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 8: Test routes generation
        try:
            routes_filename = enhanced_template_generator.generate_class_routes(mock_class)
            print(f"✅ Routes file created: {routes_filename}")
            
            # Check if file actually exists
            routes_path = os.path.join(enhanced_template_generator.routes_dir, routes_filename)
            if os.path.exists(routes_path):
                print(f"✅ Routes file verified on disk")
                
                # Read and verify content
                with open(routes_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                print(f"✅ Routes file readable ({len(file_content)} chars)")
                
            else:
                print(f"❌ Routes file not found: {routes_path}")
                return False
                
        except Exception as e:
            print(f"❌ Routes file creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 9: Test complete resource generation from object
        try:
            resources = enhanced_template_generator.generate_class_resources_from_object(mock_class)
            print(f"✅ Complete resource generation successful:")
            for key, value in resources.items():
                print(f"   {key}: {value}")
        except Exception as e:
            print(f"❌ Complete resource generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 10: Test dashboard integration
        try:
            integration = enhanced_template_generator.create_class_dashboard_integration(mock_class)
            print(f"✅ Dashboard integration created:")
            print(f"   Dashboard URL: {integration['dashboard_url']}")
            print(f"   API endpoints: {len(integration['api_endpoints'])}")
            print(f"   Static integrations: {len(integration['static_integrations'])}")
        except Exception as e:
            print(f"❌ Dashboard integration failed: {e}")
            return False
        
        print("\n🎉 All tests passed! Enhanced generator is working correctly.")
        
        # Show file locations
        print(f"\n📂 Generated Files:")
        print(f"   Template: {template_path}")
        print(f"   Routes: {routes_path}")
        
        return True

if __name__ == "__main__":
    success = test_enhanced_generator()
    
    if success:
        print("\n✅ Enhanced generator is working correctly!")
        print("The issue is not with the generator itself.")
    else:
        print("\n❌ Enhanced generator has issues that need to be fixed.")
    
    sys.exit(0 if success else 1)
