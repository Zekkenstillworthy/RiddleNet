import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 Starting route verification test...")

try:
    print("📦 Importing Flask app...")
    from run import app
    print("✅ App imported successfully")
    
    with app.app_context():
        print("🔍 Checking for simulation routes...")
        simulation_routes = []
        all_routes = []
        
        for rule in app.url_map.iter_rules():
            all_routes.append(f'{rule.endpoint}: {rule.rule}')
            if 'networking1' in rule.rule:
                simulation_routes.append(f'{rule.endpoint}: {rule.rule}')
        
        print(f"📊 Total routes found: {len(all_routes)}")
        print(f"🎯 Networking1 routes found: {len(simulation_routes)}")
        
        if simulation_routes:
            print('📍 Networking1 simulation routes:')
            for route in simulation_routes:
                print(f'   ✓ {route}')
        else:
            print('❌ No networking1 simulation routes found!')
            print("🔍 All available routes:")
            for route in all_routes[:10]:  # Show first 10 routes
                print(f'   - {route}')
            if len(all_routes) > 10:
                print(f'   ... and {len(all_routes) - 10} more routes')
        
    print('🎉 Route verification completed!')
    
except Exception as e:
    print(f'❌ Error during route verification: {e}')
    import traceback
    traceback.print_exc()
