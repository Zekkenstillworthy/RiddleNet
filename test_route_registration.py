#!/usr/bin/env python3
"""
Test script to verify dynamic route registration is working
"""

import os
import sys
import traceback

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_route_registration():
    """Test the dynamic route registration system"""
    print("🔍 Testing Dynamic Route Registration System")
    print("=" * 50)
    
    try:
        # Import the Flask app
        from run import app
        
        with app.app_context():
            print("✅ Flask app imported successfully")
            
            # Check if route registry is available
            try:
                from admin.services.dynamic_route_registry import route_registry
                print("✅ Route registry imported successfully")
                
                # Get statistics
                stats = route_registry.get_statistics()
                print(f"\n📊 Route Registry Statistics:")
                print(f"   Total classes: {stats.get('total_classes', 0)}")
                print(f"   Registered classes: {stats.get('registered_classes', 0)}")
                print(f"   Route files: {stats.get('route_files', 0)}")
                print(f"   Registration rate: {stats.get('registration_rate', 0):.1f}%")
                
                if stats.get('registered_class_ids'):
                    print(f"   Registered class IDs: {stats['registered_class_ids']}")
                
                # Test specific class routes
                test_class_ids = [1, 9, 26]  # Classes we know exist
                print(f"\n🧪 Testing specific class routes:")
                
                for class_id in test_class_ids:
                    if route_registry.is_class_registered(class_id):
                        print(f"   ✅ Class {class_id}: Routes registered")
                        
                        # Get route info
                        info = route_registry.get_class_routes_info(class_id)
                        if info.get('registered'):
                            print(f"      Blueprint: {info.get('blueprint_name')}")
                            print(f"      URL prefix: {info.get('url_prefix')}")
                    else:
                        print(f"   ❌ Class {class_id}: Routes NOT registered")
                
                # Check if routes are actually available in Flask
                print(f"\n🌐 Checking Flask routes:")
                class_routes = []
                for rule in app.url_map.iter_rules():
                    if rule.rule.startswith('/class/') and rule.rule.count('/') >= 2:
                        class_routes.append(str(rule.rule))
                
                if class_routes:
                    print(f"   Found {len(class_routes)} class routes:")
                    for route in sorted(class_routes):
                        print(f"      {route}")
                else:
                    print("   ❌ No class routes found in Flask URL map")
                
                return True
                
            except Exception as e:
                print(f"❌ Error with route registry: {e}")
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ Error importing Flask app: {e}")
        traceback.print_exc()
        return False

def test_manual_route_registration():
    """Test manual registration of a specific class route"""
    print(f"\n🔧 Testing Manual Route Registration")
    print("-" * 30)
    
    try:
        from run import app
        from admin.services.dynamic_route_registry import route_registry
        
        with app.app_context():
            # Try to manually register class 1 routes
            test_class_id = 1
            print(f"Attempting to register routes for class {test_class_id}...")
            
            result = route_registry.register_class_routes(test_class_id)
            if result:
                print(f"✅ Successfully registered routes for class {test_class_id}")
                
                # Check if the route is now available
                test_url = f"/class/{test_class_id}/"
                found_route = False
                for rule in app.url_map.iter_rules():
                    if str(rule.rule) == test_url:
                        found_route = True
                        print(f"✅ Route {test_url} found in Flask URL map")
                        break
                
                if not found_route:
                    print(f"❌ Route {test_url} not found in Flask URL map")
                    
            else:
                print(f"❌ Failed to register routes for class {test_class_id}")
                
    except Exception as e:
        print(f"❌ Error in manual route registration: {e}")
        traceback.print_exc()

def main():
    """Main test function"""
    print("🚀 Dynamic Route Registration Test")
    print("=" * 60)
    
    # Test 1: Basic route registration
    success1 = test_route_registration()
    
    # Test 2: Manual route registration
    test_manual_route_registration()
    
    print(f"\n{'=' * 60}")
    if success1:
        print("✅ Route registration system is working!")
    else:
        print("❌ Route registration system has issues!")
    
    print("\n💡 To fix 404 errors:")
    print("   1. Restart the Flask application")
    print("   2. Check that class route files exist in user/routes/generated/")
    print("   3. Verify route registry is initialized in run.py")
    print("   4. Check Flask console for route registration messages")

if __name__ == "__main__":
    main()
