"""Test script to verify live quiz blueprint registration"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from __init__ import create_app

# Create the app
app = create_app()

# Import and register the blueprint
import importlib

module_path = 'instructor.api.live_quiz_api'
blueprint_name = 'live_quiz_instructor_bp'

try:
    module = importlib.import_module(module_path)
    blueprint = getattr(module, blueprint_name)
    
    print(f"[OK] Blueprint imported successfully")
    print(f"   Name: {blueprint.name}")
    print(f"   URL Prefix: {blueprint.url_prefix}")
    print(f"   Import Name: {blueprint.import_name}")
    
    # Check if already registered
    if blueprint.name in app.blueprints:
        print(f"[WARNING]  Blueprint already registered!")
    else:
        app.register_blueprint(blueprint, url_prefix=None)
        print(f"[OK] Blueprint registered successfully!")
    
    # List all routes for this blueprint
    print(f"\n[DATA] Routes for {blueprint.name}:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint.startswith(blueprint.name):
            print(f"   {rule.endpoint:50} {rule.rule}")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
