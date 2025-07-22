#!/usr/bin/env python3
"""
Test admin login credentials
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from admin.models.user import Admin
from admin import db
from werkzeug.security import check_password_hash

def test_admin_credentials():
    """Test various admin credentials"""
    from admin.app import AdminApp
    
    admin_app = AdminApp()
    
    with admin_app.app.app_context():
        print("🔍 Testing admin credentials...")
        
        # Get all admin users
        admins = Admin.query.all()
        print(f"📊 Found {len(admins)} admin users:")
        
        for admin in admins:
            print(f"  - Username: {admin.username}")
            print(f"    Email: {admin.email}")
            print(f"    Role: {getattr(admin, 'role', 'N/A')}")
            print(f"    ID: {admin.id}")
            
            # Test different passwords
            test_passwords = ['admin', 'admin123', 'Zekken9103', 'password']
            
            for password in test_passwords:
                if admin.check_password(password):
                    print(f"    ✅ Password '{password}' works!")
                else:
                    print(f"    ❌ Password '{password}' failed")
            print()

if __name__ == "__main__":
    test_admin_credentials()
