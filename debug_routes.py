"""Debug script to list all registered Flask routes"""
from application import application

print("=" * 80)
print("REGISTERED FLASK ROUTES")
print("=" * 80)

routes_list = []
for rule in application.url_map.iter_rules():
    routes_list.append({
        'endpoint': rule.endpoint,
        'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
        'path': rule.rule
    })

# Filter for live_quiz routes
print("\n[TARGET] LIVE QUIZ ROUTES:")
print("-" * 80)
live_quiz_routes = [r for r in routes_list if 'live_quiz' in r['endpoint'] or 'live-quiz' in r['path']]
if live_quiz_routes:
    for route in sorted(live_quiz_routes, key=lambda x: x['path']):
        print(f"{route['methods']:20} {route['path']:50} ({route['endpoint']})")
else:
    print("[ERROR] NO LIVE QUIZ ROUTES FOUND!")

print("\n[DATA] ALL API ROUTES:")
print("-" * 80)
api_routes = [r for r in routes_list if r['path'].startswith('/api')]
for route in sorted(api_routes, key=lambda x: x['path'])[:50]:  # First 50 API routes
    print(f"{route['methods']:20} {route['path']:50} ({route['endpoint']})")

print("\n" + "=" * 80)
print(f"Total routes: {len(routes_list)}")
print("=" * 80)
