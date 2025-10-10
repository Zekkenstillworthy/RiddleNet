"""
Database Migration Script - Challenge Progress MVP
Adds challenge_progress table for resumable challenges

Run this script to add the new table to your existing database:
    python migrate_challenge_progress.py
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application import create_app
from __init__ import db
from user.models.challenge_progress import ChallengeProgress


def migrate_challenge_progress():
    """Create the challenge_progress table"""
    print("=" * 70)
    print("Challenge Progress Table Migration - MVP")
    print("=" * 70)
    print()
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if table already exists
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'challenge_progress' in existing_tables:
                print("⚠️  Table 'challenge_progress' already exists!")
                print()
                response = input("Do you want to recreate it? (yes/no): ").lower()
                
                if response == 'yes':
                    print()
                    print("🗑️  Dropping existing table...")
                    ChallengeProgress.__table__.drop(db.engine)
                    print("✅ Table dropped")
                else:
                    print()
                    print("❌ Migration cancelled")
                    return
            
            # Create the table
            print()
            print("📦 Creating challenge_progress table...")
            ChallengeProgress.__table__.create(db.engine)
            print("✅ Table created successfully!")
            
            # Print table structure
            print()
            print("📋 Table Structure:")
            print("-" * 70)
            print("  • id (Integer, Primary Key)")
            print("  • user_id (Integer, Foreign Key to users.id)")
            print("  • challenge_type (String(50), Indexed)")
            print("  • state_data (JSON)")
            print("  • last_updated (DateTime)")
            print("  • is_completed (Boolean)")
            print("  • created_at (DateTime)")
            print()
            print("  Unique Constraint: (user_id, challenge_type)")
            print("-" * 70)
            
            # Verify table was created
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('challenge_progress')]
            
            print()
            print("✅ Migration completed successfully!")
            print(f"   Columns created: {', '.join(columns)}")
            print()
            print("🎮 The system is now ready for challenge progress tracking!")
            print()
            print("Next steps:")
            print("  1. Add continue modal to challenge templates")
            print("  2. Include challenge-progress-manager.js script")
            print("  3. Initialize progress manager in challenge JavaScript")
            print()
            
        except Exception as e:
            print()
            print("❌ Migration failed!")
            print(f"   Error: {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    migrate_challenge_progress()
