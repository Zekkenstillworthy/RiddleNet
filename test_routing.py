#!/usr/bin/env python3

import sys
sys.path.append('.')

try:
    from flask import Flask, url_for
    from user.views import user_bp
    from admin.controllers.auth_controller import auth_bp
    
    app = Flask(__name__)
    app.register_blueprint(user_bp, url_prefix='')
    app.register_blueprint(auth_bp, url_prefix='/admin')
    
    with app.test_request_context():
        print('=== URL ROUTING TEST ===')
        print('User logout URL:', url_for('user.logout'))
        print('Admin logout URL:', url_for('auth.logout'))
        print('User index URL:', url_for('user.index'))
        print('========================')
        
        # Verify the correct routing
        user_logout = url_for('user.logout')
        admin_logout = url_for('auth.logout')
        
        if user_logout == '/logout':
            print('✅ User logout correctly routes to /logout')
        else:
            print(f'❌ User logout routes to {user_logout}')
            
        if admin_logout == '/admin/logout':
            print('✅ Admin logout correctly routes to /admin/logout')
        else:
            print(f'❌ Admin logout routes to {admin_logout}')
            
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")
