#!/usr/bin/env python3
"""
Verify that user_bp blueprint has the admin_profile route
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from admin.controllers.user_controller import user_bp
    
    print(f"Blueprint name: {user_bp.name}")
    print(f"\nRegistered routes:")
    
    # Get deferred functions (routes that will be registered)
    if hasattr(user_bp, 'deferred_functions'):
        print(f"Deferred functions: {len(user_bp.deferred_functions)}")
        for func in user_bp.deferred_functions:
            print(f"  - {func}")
    
    # Try to get registered routes
    print(f"\nBlueprint has {len(user_bp.deferred_functions if hasattr(user_bp, 'deferred_functions') else [])} deferred functions")
    
    # Check if admin_profile function exists
    from admin.controllers.user_controller import UserController
    if hasattr(UserController, 'admin_profile'):
        print(f"\n✓ UserController.admin_profile exists")
        print(f"  Function: {UserController.admin_profile}")
    else:
        print(f"\n✗ UserController.admin_profile NOT FOUND")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
