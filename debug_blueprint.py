#!/usr/bin/env python3
"""Debug script to check blueprint registration"""

try:
    from run import app
    from admin.routes.device_sync_api import device_sync_bp
    print(f'Blueprint name: {device_sync_bp.name}')
    print(f'Blueprint URL prefix: {device_sync_bp.url_prefix}')
    print(f'App blueprints: {list(app.blueprints.keys())}')
    
    # Check if device_sync_bp is in registered blueprints
    if 'device_sync_bp' in app.blueprints:
        print('✅ device_sync_bp is registered')
        blueprint = app.blueprints['device_sync_bp']
        print(f'Blueprint URL prefix: {blueprint.url_prefix}')
        print(f'Blueprint routes: {[rule.rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith("device_sync_bp.")]}')
    else:
        print('❌ device_sync_bp is NOT registered')
    
    print('✅ Blueprint registration check complete')
    
    # Check all routes containing device-sync
    device_sync_routes = [rule for rule in app.url_map.iter_rules() if 'device-sync' in rule.rule]
    print(f'Device sync routes: {[rule.rule for rule in device_sync_routes]}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()