#!/usr/bin/env python3
"""
Test Flask app startup with simulation routes
"""
import sys
import os

print("🚀 Testing Flask app startup...")

try:
    # Try importing the app
    print("📦 Importing run module...")
    from run import app
    print("✅ App module imported successfully")
    
    # Test in app context
    with app.app_context():
        print("🔍 Testing app context...")
        
        # Get route count
        total_routes = len(list(app.url_map.iter_rules()))
        print(f"📊 Total routes registered: {total_routes}")
        
        # Look for simulation routes specifically
        simulation_count = 0
        networking1_routes = []
        
        for rule in app.url_map.iter_rules():
            if 'networking1' in rule.rule:
                networking1_routes.append(f"{rule.endpoint} -> {rule.rule}")
                simulation_count += 1
        
        print(f"🎯 Networking1 routes found: {simulation_count}")
        
        if networking1_routes:
            print("📍 Networking1 routes:")
            for route in networking1_routes:
                print(f"   ✓ {route}")
        
        print("✅ Flask app startup test completed successfully!")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ General error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🎉 All tests passed!")
