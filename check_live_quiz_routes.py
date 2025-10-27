"""Check if live quiz routes are registered"""
from application import application

print("=== CHECKING LIVE QUIZ ROUTES ===\n")

# Get all routes
live_quiz_routes = []
all_routes = []

for rule in application.url_map.iter_rules():
    all_routes.append(str(rule))
    if 'live' in str(rule).lower() or 'quiz' in str(rule).lower():
        live_quiz_routes.append({
            'rule': str(rule),
            'methods': ','.join(rule.methods - {'HEAD', 'OPTIONS'}),
            'endpoint': rule.endpoint
        })

print(f"Total routes registered: {len(all_routes)}\n")

if live_quiz_routes:
    print(f"Found {len(live_quiz_routes)} live quiz routes:\n")
    for route in sorted(live_quiz_routes, key=lambda x: x['rule']):
        print(f"  {route['methods']:8} {route['rule']:60} ({route['endpoint']})")
else:
    print("[ERROR] NO LIVE QUIZ ROUTES FOUND!\n")
    print("Searching for any routes containing 'api':")
    api_routes = [r for r in all_routes if '/api/' in r]
    for route in sorted(api_routes)[:20]:  # Show first 20
        print(f"  {route}")

print("\n=== END ===")
