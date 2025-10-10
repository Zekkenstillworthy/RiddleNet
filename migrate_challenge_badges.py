"""
Database Migration Script - MVP
Creates challenge_scores and user_badges tables

Run this script to add the new tables to your database:
    python migrate_challenge_badges.py
"""

from __init__ import db, create_app
from user.models.challenge_score import ChallengeScore
from user.models.user_badge import UserBadge


def run_migration():
    """
    Create challenge_scores and user_badges tables
    """
    print("=" * 60)
    print("MVP Database Migration: Challenge Scores & Badges")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            print("\n[1/3] Creating challenge_scores table...")
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'challenge_scores' in existing_tables:
                print("   ⚠️  Table 'challenge_scores' already exists, skipping...")
            else:
                # Create challenge_scores table
                ChallengeScore.__table__.create(db.engine, checkfirst=True)
                print("   ✅ Created 'challenge_scores' table")
            
            print("\n[2/3] Creating user_badges table...")
            
            if 'user_badges' in existing_tables:
                print("   ⚠️  Table 'user_badges' already exists, skipping...")
            else:
                # Create user_badges table
                UserBadge.__table__.create(db.engine, checkfirst=True)
                print("   ✅ Created 'user_badges' table")
            
            print("\n[3/3] Verifying tables...")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'challenge_scores' in existing_tables and 'user_badges' in existing_tables:
                print("   ✅ All tables created successfully!")
                print("\n" + "=" * 60)
                print("Migration Complete!")
                print("=" * 60)
                print("\nNew tables:")
                print("  • challenge_scores - Tracks challenge completions and scores")
                print("  • user_badges - Tracks badge awards")
                print("\nYou can now:")
                print("  1. Complete challenges to save scores")
                print("  2. Earn badges automatically based on performance")
                print("  3. View real-time stats on the dashboard")
                return True
            else:
                print("   ❌ Table verification failed")
                return False
                
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def rollback_migration():
    """
    Drop challenge_scores and user_badges tables (use with caution!)
    """
    print("=" * 60)
    print("Rollback: Dropping challenge_scores and user_badges tables")
    print("=" * 60)
    print("\n⚠️  WARNING: This will delete all challenge scores and badge data!")
    
    confirm = input("Type 'YES' to confirm rollback: ")
    
    if confirm != 'YES':
        print("Rollback cancelled.")
        return
    
    app = create_app()
    
    with app.app_context():
        try:
            print("\nDropping tables...")
            
            # Drop tables
            UserBadge.__table__.drop(db.engine, checkfirst=True)
            print("   ✅ Dropped 'user_badges' table")
            
            ChallengeScore.__table__.drop(db.engine, checkfirst=True)
            print("   ✅ Dropped 'challenge_scores' table")
            
            print("\n" + "=" * 60)
            print("Rollback Complete!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Rollback failed: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        rollback_migration()
    else:
        run_migration()
