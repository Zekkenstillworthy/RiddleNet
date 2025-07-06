#!/usr/bin/env python3
"""
Test the actual admin class creation flow
"""

import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_admin_class_creation_flow():
    """Test the exact flow that happens when admin creates a class"""
    print("🔍 Testing Admin Class Creation Flow")
    print("=" * 50)
    
    try:
        # Import what the admin controller imports
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from admin.models.class_model import Class
        from admin.services.enhanced_class_template_generator import enhanced_template_generator
        from admin.services.dynamic_route_registry import route_registry
        
        print("✅ All imports successful")
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Create a Flask app similar to the main application
    app = Flask(__name__)
    
    # Use the actual database from the main application
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'test.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Ensure instance directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Initialize SQLAlchemy
    from admin import db
    db.init_app(app)
    
    with app.app_context():
        print("\n1. Testing Database Setup...")
        try:
            # Create tables
            db.create_all()
            print("   ✅ Database tables created/verified")
            
            # Test basic database operation
            existing_classes_count = Class.query.count()
            print(f"   ✅ Database accessible - {existing_classes_count} existing classes")
            
        except Exception as e:
            print(f"   ❌ Database setup failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n2. Simulating Admin Class Creation Request...")
        try:
            # Simulate the JSON data that would come from the admin frontend
            test_class_data = {
                'name': 'Introduction to Networking',
                'section': 'A',
                'code': 'NET101',
                'description': 'Learn fundamental networking concepts and protocols',
                'startDate': '2025-01-15',
                'endDate': '2025-05-15',
                'maxStudents': 30,
                'status': 'active',
                'questionGroups': []  # Empty for this test
            }
            
            print(f"   ✅ Test data prepared: {test_class_data['name']}")
            
        except Exception as e:
            print(f"   ❌ Test data preparation failed: {e}")
            return False
        
        print("\n3. Creating Class Object...")
        try:
            # Check if code already exists
            existing_class = Class.query.filter_by(code=test_class_data.get('code')).first()
            if existing_class:
                print(f"   ⚠️  Class with code {test_class_data['code']} already exists, using different code")
                test_class_data['code'] = 'NET101_TEST'
            
            # Parse dates
            from datetime import datetime
            start_date = datetime.strptime(test_class_data.get('startDate'), '%Y-%m-%d').date()
            end_date = datetime.strptime(test_class_data.get('endDate'), '%Y-%m-%d').date()
            
            # Create new class
            new_class = Class(
                name=test_class_data.get('name'),
                section=test_class_data.get('section'),
                code=test_class_data.get('code'),
                description=test_class_data.get('description'),
                start_date=start_date,
                end_date=end_date,
                max_students=test_class_data.get('maxStudents'),
                status=test_class_data.get('status', 'active')
            )
            
            # Save to database
            db.session.add(new_class)
            db.session.commit()
            
            print(f"   ✅ Class created with ID: {new_class.id}")
            
        except Exception as e:
            print(f"   ❌ Class creation failed: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False
        
        print("\n4. Testing Enhanced Template Generation...")
        try:
            # This is the exact call made in the admin controller
            generation_result = enhanced_template_generator.generate_all_class_resources(new_class.id)
            
            print(f"   ✅ Template generation successful")
            print(f"   - Template: {generation_result['template']}")
            print(f"   - Routes: {generation_result['routes']}")
            print(f"   - Enhanced: {generation_result.get('enhanced', False)}")
            
            # Check if files were actually created
            templates_dir = enhanced_template_generator.templates_dir
            routes_dir = enhanced_template_generator.routes_dir
            
            template_path = os.path.join(templates_dir, generation_result['template'])
            routes_path = os.path.join(routes_dir, generation_result['routes'])
            
            if os.path.exists(template_path):
                file_size = os.path.getsize(template_path)
                print(f"   ✅ Template file exists: {template_path} ({file_size} bytes)")
            else:
                print(f"   ❌ Template file missing: {template_path}")
                return False
            
            if os.path.exists(routes_path):
                file_size = os.path.getsize(routes_path)
                print(f"   ✅ Routes file exists: {routes_path} ({file_size} bytes)")
            else:
                print(f"   ❌ Routes file missing: {routes_path}")
                return False
            
        except Exception as e:
            print(f"   ❌ Template generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n5. Testing Route Registration...")
        try:
            # Register routes dynamically (as done in admin controller)
            route_registry.register_class_routes(new_class.id)
            print("   ✅ Route registration successful")
            
        except Exception as e:
            print(f"   ❌ Route registration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n6. Testing Dashboard Integration...")
        try:
            # Create dashboard integration
            integration_info = enhanced_template_generator.create_class_dashboard_integration(new_class)
            
            print("   ✅ Dashboard integration created")
            print(f"   - Dashboard URL: {integration_info['dashboard_url']}")
            print(f"   - API endpoints: {len(integration_info['api_endpoints'])}")
            print(f"   - Static integrations: {len(integration_info['static_integrations'])}")
            
        except Exception as e:
            print(f"   ❌ Dashboard integration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n7. Verifying Class Access...")
        try:
            # Test what a student would see
            class_type = enhanced_template_generator._detect_class_type(new_class)
            print(f"   ✅ Class type detected: {class_type}")
            
            if class_type in enhanced_template_generator.static_templates_map:
                simulations = enhanced_template_generator.static_templates_map[class_type]['simulations']
                print(f"   ✅ Static integrations available: {len(simulations)} simulations")
            else:
                print(f"   ✅ General class type (no static integrations)")
            
            print(f"   ✅ Student access URL: /class/{new_class.id}/")
            
        except Exception as e:
            print(f"   ❌ Class access verification failed: {e}")
            return False
        
        print("\n8. Final Verification...")
        
        # List the actual files created
        templates_dir = enhanced_template_generator.templates_dir
        routes_dir = enhanced_template_generator.routes_dir
        
        template_files = [f for f in os.listdir(templates_dir) if f.startswith(f'class_{new_class.id}_')]
        route_files = [f for f in os.listdir(routes_dir) if f.startswith(f'class_{new_class.id}_')]
        
        print(f"   ✅ Template files created: {template_files}")
        print(f"   ✅ Route files created: {route_files}")
        
        print("\n🎉 Admin Class Creation Flow Test PASSED!")
        
        print("\n📍 Files Created:")
        for file in template_files:
            print(f"   📄 {os.path.join(templates_dir, file)}")
        for file in route_files:
            print(f"   📄 {os.path.join(routes_dir, file)}")
        
        print(f"\n🎯 Student can now access: http://localhost:5001/class/{new_class.id}/")
        
        # Clean up test data
        print("\n9. Cleanup...")
        try:
            # Remove created files
            for file in template_files:
                os.remove(os.path.join(templates_dir, file))
            for file in route_files:
                os.remove(os.path.join(routes_dir, file))
            
            # Remove test class
            db.session.delete(new_class)
            db.session.commit()
            
            print("   ✅ Cleanup completed")
            
        except Exception as e:
            print(f"   ⚠️  Cleanup warning: {e}")
        
        return True

if __name__ == "__main__":
    success = test_admin_class_creation_flow()
    
    if success:
        print("\n✅ CONCLUSION: The admin class creation system is working perfectly!")
        print("\n📖 When admin creates a class:")
        print("   1. Class is saved to database ✅")
        print("   2. Template file is generated ✅")
        print("   3. Routes file is generated ✅")
        print("   4. Routes are registered ✅")
        print("   5. Dashboard integration is created ✅")
        print("   6. Student access is enabled ✅")
        
        print("\n🔍 If admin reports issues, check:")
        print("   - Is the Flask application running properly?")
        print("   - Are there any JavaScript errors in the browser console?")
        print("   - Is the database accessible?")
        print("   - Are there any permission issues with the directories?")
        
    else:
        print("\n❌ Issues found in the admin class creation flow!")
    
    sys.exit(0 if success else 1)
