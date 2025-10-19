"""
Test script to verify instructor simulation routes are properly registered
Run this with: python test_instructor_routes.py
"""
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the app
from run import app

def test_instructor_routes():
    """Test that instructor simulation routes are registered"""
    print("\n" + "="*80)
    print("TESTING INSTRUCTOR SIMULATION ROUTES")
    print("="*80 + "\n")
    
    # List of expected routes
    expected_routes = [
        '/instructor/simulation/edit/new',
        '/instructor/simulation/edit/<int:simulation_id>',
        '/instructor/simulation/<int:simulation_id>',
        '/instructor/simulation/api/list',
        '/instructor/simulation/api/<int:simulation_id>',
        '/instructor/simulation/api/create',
        '/instructor/simulation/edit/<int:simulation_id>/save',
        '/instructor/simulation/edit/save',
        '/instructor/simulation/api/assignments/explicit',
    ]
    
    # Get all registered routes
    registered_routes = []
    with app.app_context():
        for rule in app.url_map.iter_rules():
            if '/instructor/simulation' in rule.rule:
                registered_routes.append({
                    'rule': rule.rule,
                    'endpoint': rule.endpoint,
                    'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'}))
                })
    
    print(f"Found {len(registered_routes)} instructor simulation routes:\n")
    
    for route in sorted(registered_routes, key=lambda x: x['rule']):
        methods = ', '.join(route['methods'])
        print(f"  ✓ {route['rule']:<60} [{methods}]")
        print(f"    Endpoint: {route['endpoint']}")
        print()
    
    # Check if expected routes are present
    print("\n" + "-"*80)
    print("ROUTE VERIFICATION")
    print("-"*80 + "\n")
    
    registered_paths = [r['rule'] for r in registered_routes]
    
    all_found = True
    for expected in expected_routes:
        # Convert <int:simulation_id> to a testable pattern
        test_path = expected.replace('<int:simulation_id>', '1')
        
        # Check if route exists (either exact match or with variable)
        found = any(
            expected == registered or 
            expected.replace('<int:simulation_id>', '{simulation_id}') in registered.replace('<', '{').replace('>', '}')
            for registered in registered_paths
        )
        
        status = "✓" if found else "✗"
        print(f"  {status} {expected}")
        if not found:
            all_found = False
    
    print("\n" + "="*80)
    if all_found:
        print("SUCCESS: All expected routes are registered!")
    else:
        print("WARNING: Some routes are missing!")
    print("="*80 + "\n")
    
    return all_found

if __name__ == "__main__":
    try:
        result = test_instructor_routes()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
