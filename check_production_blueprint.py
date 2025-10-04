#!/home/ubuntu/RiddleNet/venv/bin/python3
"""
Diagnostic script to check blueprint registration on production
Run this on the production server to verify the admin_user blueprint
RUN WITH: /home/ubuntu/RiddleNet/venv/bin/python3 check_production_blueprint.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/home/ubuntu/RiddleNet')

print("=" * 80)
print("PRODUCTION BLUEPRINT DIAGNOSTIC")
print("=" * 80)

# 1. Check if source code has the fix
print("\n1. Checking run.py for blueprint registration code...")
try:
    with open('/home/ubuntu/RiddleNet/run.py', 'r') as f:
        content = f.read()
        if "('admin.controllers.user_controller', 'user_bp', '/admin', None)" in content:
            print("   ✅ run.py contains correct registration (alias=None)")
        elif "('admin.controllers.user_controller', 'user_bp', '/admin', 'admin_user_bp')" in content:
            print("   ❌ run.py still has OLD registration (alias='admin_user_bp')")
            print("   🔄 Production code NOT updated! Need to pull from Git!")
        else:
            print("   ⚠️  Could not find user_controller registration line")
except Exception as e:
    print(f"   ❌ Error reading run.py: {e}")

# 2. Check user_controller.py blueprint name
print("\n2. Checking user_controller.py blueprint definition...")
try:
    with open('/home/ubuntu/RiddleNet/admin/controllers/user_controller.py', 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[10:20], start=11):  # Check around line 14
            if 'user_bp = Blueprint' in line:
                print(f"   Line {i}: {line.strip()}")
                if "'admin_user'" in line:
                    print("   ✅ Blueprint name is 'admin_user'")
                break
except Exception as e:
    print(f"   ❌ Error reading user_controller.py: {e}")

# 3. Test import and check blueprint
print("\n3. Testing import and blueprint registration...")
try:
    from admin.controllers.user_controller import user_bp
    print(f"   ✅ Successfully imported user_bp")
    print(f"   Blueprint name: {user_bp.name}")
    print(f"   Blueprint import_name: {user_bp.import_name}")
    
    # Count routes
    route_count = len([rule for rule in user_bp.deferred_functions])
    print(f"   Deferred functions: {route_count}")
    
    # List some key routes
    print("\n   Key routes in blueprint:")
    for func in user_bp.deferred_functions[:5]:
        print(f"      - {func}")
    
except Exception as e:
    print(f"   ❌ Error importing user_bp: {e}")
    import traceback
    traceback.print_exc()

# 4. Check if Flask app can be created
print("\n4. Testing Flask app creation and blueprint registration...")
try:
    from flask import Flask
    test_app = Flask(__name__)
    
    from admin.controllers.user_controller import user_bp
    test_app.register_blueprint(user_bp, url_prefix='/admin')
    
    print(f"   ✅ Blueprint registered successfully")
    
    # Check endpoints
    admin_user_endpoints = [rule.endpoint for rule in test_app.url_map.iter_rules() 
                           if 'admin_user' in rule.endpoint]
    
    print(f"   Found {len(admin_user_endpoints)} admin_user endpoints")
    
    if 'admin_user.admin_profile' in admin_user_endpoints:
        print("   ✅ admin_user.admin_profile endpoint exists!")
    else:
        print("   ❌ admin_user.admin_profile endpoint NOT FOUND")
        print(f"   Available admin_user endpoints: {admin_user_endpoints[:10]}")
    
except Exception as e:
    print(f"   ❌ Error creating test app: {e}")
    import traceback
    traceback.print_exc()

# 5. Check for .pyc files in APPLICATION code (not venv)
print("\n5. Checking for remaining .pyc files in application code...")
import subprocess
result = subprocess.run(['find', '/home/ubuntu/RiddleNet', '-name', '*.pyc', '-type', 'f', 
                        '-not', '-path', '*/venv/*'], 
                       capture_output=True, text=True)
pyc_files = result.stdout.strip().split('\n')
pyc_count = len([f for f in pyc_files if f])
print(f"   Found {pyc_count} .pyc files in application code")
if pyc_count > 0:
    print("   ⚠️  WARNING: .pyc files found in application code:")
    for f in pyc_files[:20]:
        if f:
            print(f"      {f}")
else:
    print("   ✅ No .pyc files in application code")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
