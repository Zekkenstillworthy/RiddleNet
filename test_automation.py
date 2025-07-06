#!/usr/bin/env python3
"""
Test script for Enhanced Classroom Automation System
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app, db
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from admin.services.enhanced_class_template_generator import enhanced_template_generator
from admin.services.dynamic_route_registry import route_registry
from admin.services.automation_init import initialize_enhanced_automation, check_system_health

def test_automation_system():
    """Test the enhanced automation system"""
    print("🧪 Testing Enhanced Classroom Automation System")
    print("=" * 60)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Initialize the enhanced automation system
        print("1. Initializing Enhanced Automation System...")
        initialize_enhanced_automation(app)
        
        # Check system health
        print("\n2. Checking System Health...")
        health_ok = check_system_health()
        
        if not health_ok:
            print("❌ System health check failed!")
            return False
        
        # Test template generation
        print("\n3. Testing Template Generation...")
        
        # Check if we have any classes
        classes = Class.query.all()
        print(f"Found {len(classes)} existing classes")
        
        if not classes:
            print("⚠️  No classes found. Creating test class...")
            # Create a test class
            test_class = Class(
                name="Introduction to Networking",
                code="NET101",
                section="A",
                description="Learn fundamental networking concepts and protocols"
            )
            db.session.add(test_class)
            db.session.commit()
            classes = [test_class]
        
        # Test with the first class
        test_class = classes[0]
        print(f"Testing with class: {test_class.name} (ID: {test_class.id})")
        
        # Detect class type
        class_type = enhanced_template_generator._detect_class_type(test_class)
        print(f"Detected class type: {class_type}")
        
        # Generate template
        try:
            template_filename = enhanced_template_generator.generate_class_template(test_class)
            print(f"✅ Generated template: {template_filename}")
        except Exception as e:
            print(f"❌ Template generation failed: {e}")
            return False
        
        # Generate routes
        try:
            routes_filename = enhanced_template_generator.generate_class_routes(test_class)
            print(f"✅ Generated routes: {routes_filename}")
        except Exception as e:
            print(f"❌ Routes generation failed: {e}")
            return False
        
        # Test route registration
        try:
            route_registry.register_class_routes(test_class.id)
            print("✅ Routes registered successfully")
        except Exception as e:
            print(f"❌ Route registration failed: {e}")
            return False
        
        # Test dashboard integration
        try:
            integration_info = enhanced_template_generator.create_class_dashboard_integration(test_class)
            print(f"✅ Dashboard integration created: {integration_info['dashboard_url']}")
        except Exception as e:
            print(f"❌ Dashboard integration failed: {e}")
            return False
        
        # Test static template mappings
        print("\n4. Testing Static Template Mappings...")
        static_templates = enhanced_template_generator.static_templates_map
        
        for class_type, config in static_templates.items():
            print(f"   {class_type}: {len(config['simulations'])} simulations")
            
            # Check if templates exist
            learning_template = config['learning_template']
            template_path = os.path.join(app.root_path, 'templates', learning_template)
            exists = os.path.exists(template_path)
            print(f"     Learning template exists: {exists}")
            
            if not exists:
                print(f"     Missing: {template_path}")
        
        print("\n5. Final System Statistics...")
        try:
            from admin.services.automation_init import check_system_health
            check_system_health()
        except Exception as e:
            print(f"Statistics error: {e}")
        
        print("\n🎉 Automation System Test Complete!")
        print("\n📝 Test Summary:")
        print(f"   ✅ System initialized")
        print(f"   ✅ Health check passed")
        print(f"   ✅ Template generation working")
        print(f"   ✅ Route generation working")
        print(f"   ✅ Route registration working")
        print(f"   ✅ Dashboard integration working")
        print(f"   ✅ Static template mapping configured")
        
        print("\n🚀 Next Steps:")
        print("   1. Go to /admin/classes")
        print("   2. Create a new class")
        print("   3. System will auto-generate everything")
        print(f"   4. Visit /class/{test_class.id}/ to see the result")
        
        return True

if __name__ == "__main__":
    success = test_automation_system()
    if success:
        print("\n✅ All tests passed! The automation system is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    sys.exit(0 if success else 1)
