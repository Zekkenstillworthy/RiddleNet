#!/usr/bin/env python3
"""
Migration script to create the networking2_progress table
"""

import sys
import os

print("Starting migration script...")

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Importing modules...")
    from __init__ import create_app, db
    from user.models.networking2_progress import Networking2Progress
    print("Modules imported successfully!")
    
    # Create the Flask app instance
    print("Creating Flask app...")
    app = create_app()
    print("Flask app created successfully!")
    
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def create_networking2_table():
    """Create the networking2_progress table"""
    try:
        with app.app_context():
            print('Creating networking2_progress table...')
            
            # Create all tables (this will only create missing ones)
            db.create_all()
            
            print('✅ Table creation completed successfully!')
            
            # Verify the table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'networking2_progress' in tables:
                print('✅ networking2_progress table verified in database')
                print('\nTable columns:')
                for column in inspector.get_columns('networking2_progress'):
                    print(f'  - {column["name"]}: {column["type"]}')
                return True
            else:
                print('❌ networking2_progress table not found')
                return False
                
    except Exception as e:
        print(f'❌ Error creating table: {e}')
        return False

if __name__ == '__main__':
    success = create_networking2_table()
    if success:
        print('\n🎉 Database migration completed successfully!')
        print('You can now access the Networking 2 learning path.')
    else:
        print('\n💥 Database migration failed.')
        sys.exit(1)
