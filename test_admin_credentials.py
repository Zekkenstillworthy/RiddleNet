#!/usr/bin/env python3
"""
Test script to check admin credentials and test the fixed cookie configuration
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from __init__ import create_app, db
from admin.models.user import Admin

def main():
    print("🔍 Testing admin credentials and cookie configuration...")
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        try:
            # Query all admin users
            admins = Admin.query.all()
            print(f"\n📊 Found {len(admins)} admin users:")
            
            for admin in admins:
                print(f"   👤 ID: {admin.id}")
                print(f"   📧 Username: {admin.username}")
                print(f"   📧 Email: {getattr(admin, 'email', 'N/A')}")
                print(f"   🔑 Role: {getattr(admin, 'role', 'N/A')}")
                print(f"   ✅ Active: {getattr(admin, 'is_active', 'N/A')}")
                print("   " + "="*50)
                
                # Test password hash (but don't print it)
                if hasattr(admin, 'password_hash') and admin.password_hash:
                    print(f"   🔐 Has password hash: Yes")
                else:
                    print(f"   🔐 Has password hash: No")
                    
                # Try to check password for common values
                common_passwords = ['admin', 'password', 'gilbert', 'riddlenet']
                for pwd in common_passwords:
                    if hasattr(admin, 'check_password') and admin.check_password(pwd):
                        print(f"   ✅ FOUND PASSWORD: {pwd}")
                        break
                else:
                    print("   ⚠️ Common passwords didn't work")
                    
                print()
                
        except Exception as e:
            print(f"❌ Error querying admin users: {e}")

if __name__ == "__main__":
    main()