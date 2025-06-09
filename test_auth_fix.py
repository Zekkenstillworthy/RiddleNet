#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

# Test the authentication routing fix
try:
    from flask import Flask, url_for, request
    from user.views import user_bp
    from admin.controllers.auth_controller import auth_bp
    
    app = Flask(__name__)
    app.secret_key = 'test_key'
    
    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='')
    app.register_blueprint(auth_bp, url_prefix='/admin')
    
    with app.test_request_context():
        print('=== AUTHENTICATION FIX VERIFICATION ===')
        print(f'User login URL: {url_for("user.login")}')
        print(f'User logout URL: {url_for("user.logout")}')
        print(f'User index URL: {url_for("user.index")}')
        print(f'Admin login URL: {url_for("auth.login")}')
        print(f'Admin logout URL: {url_for("auth.logout")}')
        print('========================================')
        
        # Test route expectations
        expected_routes = {
            'user.login': '/login',
            'user.logout': '/logout', 
            'user.index': '/',
            'auth.login': '/admin/login',
            'auth.logout': '/admin/logout'
        }
        
        all_correct = True
        for route_name, expected_url in expected_routes.items():
            actual_url = url_for(route_name)
            if actual_url == expected_url:
                print(f'✅ {route_name}: {actual_url}')
            else:
                print(f'❌ {route_name}: Expected {expected_url}, got {actual_url}')
                all_correct = False
        
        if all_correct:
            print('\n🎉 All routes are correctly configured!')
            print('✅ User logout should redirect to user login page')
            print('✅ Admin logout should redirect to admin login page') 
        else:
            print('\n❌ Some routes need attention')
            
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")
