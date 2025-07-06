#!/usr/bin/env python3
"""
Diagnostic test for class creation issues
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
from admin import db

def create_test_app():
    """Create test app"""
    app = Flask(__name__)
    
    # Use the actual database path from the main application
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'test.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Ensure instance directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Initialize database
    db.init_app(app)
    
    return app

def diagnose_class_creation():
    """Diagnose class creation issues"""
    print("🔍 Diagnosing Class Creation Issues")
    print("=" * 50)
    
    app = create_test_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("1. Testing Database Connection...")
        try:
            # Test database connection
            existing_classes = Class.query.all()
            print(f"   ✅ Database connected - Found {len(existing_classes)} existing classes")
        except Exception as e:
            print(f"   ❌ Database connection failed: {e}")
            return False
        
        print("\n2. Testing Enhanced Template Generator...")
        try:
            # Test if enhanced template generator is accessible
            print(f"   ✅ Enhanced template generator available")
            print(f"   - Templates directory: {enhanced_template_generator.templates_dir}")
            print(f"   - Routes directory: {enhanced_template_generator.routes_dir}")
        except Exception as e:
            print(f"   ❌ Enhanced template generator error: {e}")
            return False
        
        print("\n3. Testing Directory Permissions...")
        try:
            # Test directory creation and write permissions
            templates_dir = enhanced_template_generator.templates_dir
            routes_dir = enhanced_template_generator.routes_dir
            
            if not templates_dir or not routes_dir:
                print("   ⚠️  Directories not initialized, initializing now...")
                enhanced_template_generator._ensure_app_context_directories()
                templates_dir = enhanced_template_generator.templates_dir
                routes_dir = enhanced_template_generator.routes_dir
            
            # Test write permissions
            test_file = os.path.join(templates_dir, 'test_write.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"   ✅ Write permissions OK for templates directory")
            
            test_file = os.path.join(routes_dir, 'test_write.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"   ✅ Write permissions OK for routes directory")
            
        except Exception as e:
            print(f"   ❌ Directory permissions error: {e}")
            return False
        
        print("\n4. Testing Class Creation...")
        try:
            # Create a test class
            test_class = Class(
                name="Test Networking Class",
                code="TEST001",
                section="A",
                description="Test class for diagnostics"
            )
            
            db.session.add(test_class)
            db.session.commit()
            
            print(f"   ✅ Test class created with ID: {test_class.id}")
            
        except Exception as e:
            print(f"   ❌ Class creation failed: {e}")
            return False
        
        print("\n5. Testing Template Generation...")
        try:
            # Test template generation
            result = enhanced_template_generator.generate_all_class_resources(test_class.id)
            print(f"   ✅ Template generation successful")
            print(f"   - Template: {result['template']}")
            print(f"   - Routes: {result['routes']}")
            print(f"   - Enhanced: {result.get('enhanced', False)}")
            
            # Check if files were actually created
            template_path = os.path.join(templates_dir, result['template'])
            routes_path = os.path.join(routes_dir, result['routes'])
            
            if os.path.exists(template_path):
                print(f"   ✅ Template file created: {template_path}")
            else:
                print(f"   ❌ Template file not found: {template_path}")
                return False
            
            if os.path.exists(routes_path):
                print(f"   ✅ Routes file created: {routes_path}")
            else:
                print(f"   ❌ Routes file not found: {routes_path}")
                return False
            
        except Exception as e:
            print(f"   ❌ Template generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n6. Testing Route Registration...")
        try:
            # Test route registration
            route_registry.register_class_routes(test_class.id)
            print(f"   ✅ Route registration successful")
            
        except Exception as e:
            print(f"   ❌ Route registration failed: {e}")
            return False
        
        print("\n7. Testing Dashboard Integration...")
        try:
            # Test dashboard integration
            integration_info = enhanced_template_generator.create_class_dashboard_integration(test_class)
            print(f"   ✅ Dashboard integration created")
            print(f"   - Dashboard URL: {integration_info['dashboard_url']}")
            
        except Exception as e:
            print(f"   ❌ Dashboard integration failed: {e}")
            return False
        
        print("\n8. Cleanup...")
        try:
            # Clean up test files
            template_path = os.path.join(templates_dir, result['template'])
            routes_path = os.path.join(routes_dir, result['routes'])
            
            if os.path.exists(template_path):
                os.remove(template_path)
            if os.path.exists(routes_path):
                os.remove(routes_path)
            
            # Remove test class
            db.session.delete(test_class)
            db.session.commit()
            
            print("   ✅ Cleanup successful")
            
        except Exception as e:
            print(f"   ⚠️  Cleanup warning: {e}")
        
        print("\n🎉 All Diagnostics Passed!")
        print("\nThe system should be working correctly.")
        print("If admin still can't create files, check:")
        print("1. Application is running with proper Flask context")
        print("2. Database is properly initialized")
        print("3. Admin has proper permissions")
        print("4. No conflicting imports or module issues")
        
        return True

if __name__ == "__main__":
    success = diagnose_class_creation()
    
    if success:
        print("\n✅ Diagnostics completed successfully!")
        print("The class creation system should be working.")
    else:
        print("\n❌ Issues found during diagnostics!")
        print("Please check the errors above and fix them.")
    
    sys.exit(0 if success else 1)
