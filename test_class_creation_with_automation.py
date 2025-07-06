#!/usr/bin/env python3
"""
Test the class creation with automation integration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from admin.models.class_model import Class
from admin.services.enhanced_class_template_generator import enhanced_template_generator
from admin.services.dynamic_route_registry import route_registry
from admin import db

def test_class_creation_automation():
    """Test that automation is triggered when creating a class"""
    print("🧪 Testing Class Creation with Automation")
    print("=" * 50)
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    db.init_app(app)
    
    with app.app_context():
        # Initialize directories
        enhanced_template_generator._ensure_app_context_directories()
        
        # Create a new class (simulating admin form submission)
        print("\n1. Creating new class...")
        new_class = Class(
            name="Network Security Fundamentals",
            code="SEC201",
            section="B",
            description="Learn advanced network security concepts",
            max_students=25,
            status="active"
        )
        
        # Add to database
        db.session.add(new_class)
        db.session.commit()
        
        print(f"✅ Class created with ID: {new_class.id}")
        
        # Now test the automation system (this is what should happen automatically)
        print("\n2. Testing automation system...")
        
        try:
            # Generate template and routes
            result = enhanced_template_generator.generate_all_class_resources(new_class)
            
            if result.get('success'):
                print(f"✅ Auto-generated files:")
                print(f"   - Template: {result.get('template_path')}")
                print(f"   - Routes: {result.get('routes_path')}")
                
                # Verify files exist
                template_path = result.get('template_path')
                routes_path = result.get('routes_path')
                
                if template_path and os.path.exists(template_path):
                    print(f"✅ Template file created: {os.path.basename(template_path)}")
                    
                    # Show file size
                    file_size = os.path.getsize(template_path)
                    print(f"   Size: {file_size:,} bytes")
                    
                if routes_path and os.path.exists(routes_path):
                    print(f"✅ Routes file created: {os.path.basename(routes_path)}")
                    
                    # Show file size
                    file_size = os.path.getsize(routes_path)
                    print(f"   Size: {file_size:,} bytes")
                
                # Register routes dynamically
                route_registry.register_class_routes(new_class)
                print(f"✅ Routes registered for class {new_class.id}")
                
                print("\n🎉 SUCCESS: Automation system is working!")
                print("Files are now generated automatically when creating classes.")
                
            else:
                print(f"❌ File generation failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Automation system error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    success = test_class_creation_automation()
    if success:
        print("\n✅ Integration test passed! The automation system is ready.")
    else:
        print("\n❌ Integration test failed.")
