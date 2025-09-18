#!/usr/bin/env python3
"""
Create the password reset table for admin users
"""

import eventlet
eventlet.monkey_patch()

from __init__ import create_app, db
from admin.models.user import AdminPasswordReset, Admin
import os

# Create app with template directory
template_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app = create_app({'TEMPLATE_FOLDER': template_dir})

with app.app_context():
    try:
        # Create all tables (including the new AdminPasswordReset table)
        db.create_all()
        print("✅ Database tables created successfully!")
        print("✅ AdminPasswordReset table is now available for admin password resets")
        
        # Check if admin users exist
        admin_count = Admin.query.count()
        print(f"📊 Current admin users in database: {admin_count}")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        import traceback
        traceback.print_exc()
