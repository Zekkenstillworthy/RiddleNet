#!/usr/bin/env python3
"""
Simple verification that simulation routes are properly defined
"""

def test_simulation_routes():
    print("🔍 Checking simulation routes definition...")
    
    # Test if we can read the routes from the views file
    try:
        with open('user/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for our simulation route definitions
        simulation_routes = [
            'networking1_simulations',
            'networking1_components_simulation',
            'networking1_osi_simulation',
            'networking1_tcpip_simulation', 
            'networking1_ethernet_simulation',
            'networking1_application_simulation',
            'networking1_datalink_simulation'
        ]
        
        found_routes = []
        missing_routes = []
        
        for route in simulation_routes:
            if f'def {route}()' in content:
                found_routes.append(route)
            else:
                missing_routes.append(route)
        
        print(f"✅ Found {len(found_routes)} simulation route definitions:")
        for route in found_routes:
            print(f"   ✓ {route}")
        
        if missing_routes:
            print(f"❌ Missing {len(missing_routes)} route definitions:")
            for route in missing_routes:
                print(f"   ✗ {route}")
            return False
        
        # Check if routes are using correct decorators
        correct_decorators = True
        for route in simulation_routes:
            route_def_start = content.find(f'def {route}()')
            if route_def_start > 0:
                # Look backwards for the route decorator
                route_section = content[max(0, route_def_start-200):route_def_start]
                if f"@user_bp.route('/{route.replace('_', '-')}')" not in route_section:
                    print(f"❌ Route {route} missing correct decorator")
                    correct_decorators = False
        
        if correct_decorators:
            print("✅ All routes have correct decorators")
        
        # Check for URL generation fixes
        if "url_for('user.simulation." in content:
            print("❌ Found old simulation blueprint references - still needs fixing")
            return False
        
        print("✅ No old blueprint references found")
        print("🎉 All simulation routes properly configured!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking routes: {e}")
        return False

if __name__ == "__main__":
    test_simulation_routes()
