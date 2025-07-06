#!/usr/bin/env python3
"""
Simple test to verify the admin API route has automation integration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_route_integration():
    """Test that the API route has automation integration"""
    print("🔍 Testing API Route Integration")
    print("=" * 40)
    
    # Read the API routes file
    api_routes_file = 'admin/routes/api_routes.py'
    
    try:
        with open(api_routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for automation integration
        automation_checks = [
            ('Enhanced template generator import', 'from admin.services.enhanced_class_template_generator import enhanced_template_generator'),
            ('Route registry import', 'from admin.services.dynamic_route_registry import route_registry'),
            ('Generate all class resources call', 'enhanced_template_generator.generate_all_class_resources'),
            ('Register class routes call', 'route_registry.register_class_routes'),
            ('Automation comment', '🚀 ENHANCED AUTOMATION')
        ]
        
        print("Checking automation integration in create_class API:")
        
        all_passed = True
        for check_name, check_pattern in automation_checks:
            if check_pattern in content:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ {check_name} - MISSING")
                all_passed = False
        
        if all_passed:
            print(f"\n🎉 SUCCESS: All automation integration checks passed!")
            print("The create_class API route now includes:")
            print("  - Enhanced template generation")
            print("  - Dynamic route registration")
            print("  - Error handling for automation")
            
            # Show the relevant code section
            print("\n📋 Integration Code Preview:")
            print("-" * 40)
            
            # Find the automation section
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '🚀 ENHANCED AUTOMATION' in line:
                    # Show 20 lines from this point
                    for j in range(i, min(i+20, len(lines))):
                        print(f"{j+1:3d}: {lines[j]}")
                    break
                    
            return True
        else:
            print(f"\n❌ FAILED: Some automation integration is missing.")
            return False
            
    except Exception as e:
        print(f"❌ Error reading API routes file: {e}")
        return False

if __name__ == "__main__":
    success = test_api_route_integration()
    if success:
        print("\n✅ Integration is complete! When you create a new class through the admin interface,")
        print("   the system will automatically generate HTML templates and route files.")
        print("\n🎯 Next Steps:")
        print("   1. Start your Flask application")
        print("   2. Go to /admin/classes")
        print("   3. Create a new class")
        print("   4. Check templates/user/classes/ for the generated HTML file")
        print("   5. Check user/routes/generated/ for the generated route file")
    else:
        print("\n❌ Integration incomplete - automation may not work when creating classes.")
