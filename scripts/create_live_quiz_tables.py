"""
Simple script to create Live Quiz tables in production database.
Run this FIRST before running the fix script.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from __init__ import create_app, db
from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant, LiveQuizResponse


def create_tables():
    """Create all Live Quiz related tables."""
    print("=" * 80)
    print("CREATING LIVE QUIZ TABLES")
    print("=" * 80)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Import models to ensure they're registered
            from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant, LiveQuizResponse
            
            print("\n📋 Creating tables...")
            
            # Create all tables
            db.create_all()
            
            print("\n✅ Tables created successfully!")
            
            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\n📊 Verifying tables:")
            live_quiz_tables = [t for t in tables if 'live_quiz' in t.lower()]
            
            if live_quiz_tables:
                for table in live_quiz_tables:
                    print(f"   ✅ {table}")
            else:
                print("   ❌ No live_quiz tables found!")
                return False
            
            # Get column info for live_quiz_sessions
            if 'live_quiz_sessions' in tables:
                print("\n📝 live_quiz_sessions columns:")
                columns = inspector.get_columns('live_quiz_sessions')
                for col in columns:
                    print(f"   - {col['name']} ({col['type']})")
            
            print("\n" + "=" * 80)
            print("✅ SUCCESS! You can now run fix_production_live_quiz.py")
            print("=" * 80)
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    success = create_tables()
    sys.exit(0 if success else 1)
