#!/usr/bin/env python3

import sys
import os
import traceback

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing API import...")

try:
    print("Importing Flask and other dependencies...")
    from flask import Flask
    print("✅ Flask imported")
    
    print("Importing user.api...")
    from user.api import api_blueprint
    print("✅ API blueprint imported successfully")
    
    # Check if /classes route is defined
    has_classes_route = False
    print("Available routes:")
    for rule in api_blueprint.url_map.iter_rules():
        print(f"  Route: {rule.endpoint} -> {rule.rule} [{', '.join(rule.methods)}]")
        if '/classes' in rule.rule:
            has_classes_route = True
    
    if has_classes_route:
        print("✅ /classes route found in API blueprint")
    else:
        print("❌ /classes route NOT found in API blueprint")
        
except ImportError as e:
    print(f"❌ Failed to import API blueprint: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()

# Test database connection
try:
    print("\nTesting database imports...")
    import sys
    import os
    # Make sure we're importing from the main __init__.py
    main_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, main_dir)
    from __init__ import db
    print("✅ db imported")
    from admin.models.class_model import Class, class_students
    print("✅ Class model imported")
    from user.models.user import User
    print("✅ User model imported")
    print("✅ Database models imported successfully")
except ImportError as e:
    print(f"❌ Failed to import database models: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"❌ Database error: {e}")
    traceback.print_exc()
