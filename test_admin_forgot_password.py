#!/usr/bin/env python3
"""
Test script to verify admin forgot password functionality
"""

import eventlet
eventlet.monkey_patch()

from __init__ import create_app, db
from admin.models.user import Admin, AdminPasswordReset
import os

# Create app with template directory
template_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app = create_app({'TEMPLATE_FOLDER': template_dir})

with app.app_context():
    try:
        # Test 1: Check if we have admin users with email addresses
        print("🔍 Testing admin forgot password functionality...")
        print()
        
        admins = Admin.query.all()
        print(f"📊 Found {len(admins)} admin users:")
        
        admins_with_email = []
        for admin in admins:
            has_email = bool(admin.email and admin.email.strip())
            status = "✅ Has email" if has_email else "❌ No email"
            print(f"   - {admin.username}: {status} ({admin.email if has_email else 'N/A'})")
            if has_email:
                admins_with_email.append(admin)
        
        print()
        
        if not admins_with_email:
            print("⚠️  No admin users have email addresses set!")
            print("📝 You'll need to add email addresses to admin accounts to test password reset.")
            print()
            print("Example SQL to add an email:")
            print("UPDATE admin SET email = 'admin@example.com' WHERE username = 'your_admin_username';")
        else:
            # Test 2: Create a test password reset token
            test_admin = admins_with_email[0]
            print(f"🧪 Creating test password reset token for: {test_admin.username}")
            
            # Create a password reset token
            reset_token = AdminPasswordReset.create_token(test_admin.id, expiry_hours=1)
            
            print(f"✅ Password reset token created!")
            print(f"   - Token: {reset_token.token}")
            print(f"   - Expires: {reset_token.expires_at}")
            print(f"   - Reset URL: http://localhost:5000/admin/reset-password/{reset_token.token}")
            
            # Test 3: Verify token validation
            retrieved_token = AdminPasswordReset.get_valid_token(reset_token.token)
            
            if retrieved_token:
                print("✅ Token validation test passed!")
            else:
                print("❌ Token validation test failed!")
        
        print()
        print("🎯 Admin Forgot Password Routes Available:")
        print("   - GET/POST /admin/forgot-password - Request password reset")
        print("   - GET/POST /admin/reset-password/<token> - Reset password with token")
        print()
        print("📋 To test manually:")
        print("   1. Go to http://localhost:5000/admin/login")
        print("   2. Click 'Forgot password?' link")
        print("   3. Enter an admin email address")
        print("   4. Check email for reset link (if email is configured)")
        print()
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()