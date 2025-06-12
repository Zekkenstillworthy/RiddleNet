#!/usr/bin/env python3
"""
Quick verification of simulation files and routing structure
"""
import os

def test_simulation_files():
    print("🔍 Verifying simulation files and structure...")
    
    # Check if all simulation HTML templates exist
    template_dir = "templates/user"
    required_templates = [
        "networking1_simulations.html",
        "networking1-components-simulation.html", 
        "networking1-osi-simulation.html",
        "networking1-tcpip-simulation.html",
        "networking1-ethernet-simulation.html",
        "networking1-application-simulation.html",
        "networking1-datalink-simulation.html"
    ]
    
    print(f"📂 Checking templates in {template_dir}...")
    missing_templates = []
    found_templates = []
    
    for template in required_templates:
        template_path = os.path.join(template_dir, template)
        if os.path.exists(template_path):
            found_templates.append(template)
            # Get file size
            size = os.path.getsize(template_path)
            print(f"   ✓ {template} ({size:,} bytes)")
        else:
            missing_templates.append(template)
            print(f"   ✗ {template} - MISSING")
    
    if missing_templates:
        print(f"❌ Missing {len(missing_templates)} templates!")
        return False
    
    print(f"✅ All {len(found_templates)} simulation templates found!")
    
    # Check if user views file contains simulation routes
    print("\n🔍 Checking route definitions in user/views.py...")
    try:
        with open('user/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        route_functions = [
            'networking1_simulations',
            'networking1_components_simulation',
            'networking1_osi_simulation', 
            'networking1_tcpip_simulation',
            'networking1_ethernet_simulation',
            'networking1_application_simulation',
            'networking1_datalink_simulation'
        ]
        
        missing_routes = []
        found_routes = []
        
        for route_func in route_functions:
            if f'def {route_func}()' in content:
                found_routes.append(route_func)
                print(f"   ✓ {route_func}")
            else:
                missing_routes.append(route_func)
                print(f"   ✗ {route_func} - MISSING")
        
        if missing_routes:
            print(f"❌ Missing {len(missing_routes)} route functions!")
            return False
        
        print(f"✅ All {len(found_routes)} route functions found!")
        
        # Check for old blueprint references
        if 'user.simulation.' in content:
            print("❌ Found old blueprint references that need fixing!")
            return False
        
        print("✅ No old blueprint references found!")
        
    except Exception as e:
        print(f"❌ Error reading views file: {e}")
        return False
    
    print("\n🎉 All simulation files and routes verified successfully!")
    return True

if __name__ == "__main__":
    success = test_simulation_files()
    if success:
        print("\n🚀 Simulations are ready to test!")
        print("Next steps:")
        print("1. Start the Flask app: python run.py")
        print("2. Navigate to the Networking 1 course")
        print("3. Click 'Interactive Simulations' button")
        print("4. Test each simulation from the hub")
    else:
        print("\n❌ Issues found - check the output above")
