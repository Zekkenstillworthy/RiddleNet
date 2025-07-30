#!/usr/bin/env python3
"""
Database fix script to recreate tables from current models
"""

import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from __init__ import create_app, db
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from admin.models.user import AdminUser
from user.models.user import User

def fix_database():
    """Fix database schema issues"""
    print("Starting database schema fix...")
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        try:
            # Print current Class model columns
            print("Current Class model columns:")
            for column in Class.__table__.columns:
                print(f"  {column.name}: {column.type}")
            
            # Check if we need to recreate tables
            print("\nChecking if tables need updates...")
            
            # Try to query the classes table
            try:
                classes = Class.query.limit(1).all()
                print(f"Successfully queried classes table. Found {len(classes)} classes.")
            except Exception as e:
                print(f"Error querying classes: {e}")
                print("Recreating classes table...")
                
                # Drop and recreate the classes table
                db.engine.execute('DROP TABLE IF EXISTS classes')
                Class.__table__.create(db.engine)
                print("Classes table recreated successfully.")
            
            print("Database schema fix completed successfully!")
            
        except Exception as e:
            print(f"Error during database fix: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = fix_database()
    if success:
        print("✅ Database fix completed successfully!")
    else:
        print("❌ Database fix failed!")
