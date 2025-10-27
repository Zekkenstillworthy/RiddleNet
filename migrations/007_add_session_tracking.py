"""
Migration: Add session tracking tables for concurrent login prevention

This migration creates two new tables:
1. user_sessions - Tracks active user sessions
2. instructor_sessions - Tracks active instructor sessions

Run this script to add session tracking to the database.
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from __init__ import db, create_app
from user.models.user_session import UserSession
from instructor.models.instructor_session import InstructorSession


def upgrade():
    """Create session tracking tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating session tracking tables...")
        
        # Create the tables
        try:
            db.create_all()
            print("[OK] Successfully created session tracking tables:")
            print("   - user_sessions")
            print("   - instructor_sessions")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'user_sessions' in tables:
                print("[OK] user_sessions table verified")
            else:
                print("[ERROR] user_sessions table not found")
            
            if 'instructor_sessions' in tables:
                print("[OK] instructor_sessions table verified")
            else:
                print("[ERROR] instructor_sessions table not found")
            
            print("\nMigration completed successfully!")
            
        except Exception as e:
            print(f"[ERROR] Error during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True


def downgrade():
    """Drop session tracking tables"""
    app = create_app()
    
    with app.app_context():
        print("Dropping session tracking tables...")
        
        try:
            # Drop the tables
            UserSession.__table__.drop(db.engine, checkfirst=True)
            InstructorSession.__table__.drop(db.engine, checkfirst=True)
            
            print("[OK] Successfully dropped session tracking tables")
            print("\nDowngrade completed successfully!")
            
        except Exception as e:
            print(f"[ERROR] Error during downgrade: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Session Tracking Migration')
    parser.add_argument('action', choices=['upgrade', 'downgrade'], 
                       help='Migration action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'upgrade':
        upgrade()
    elif args.action == 'downgrade':
        downgrade()
