"""
Add activity_log column to task_assignments table
Run this migration to add activity tracking support
"""

from __init__ import db, create_app
from sqlalchemy import text

def add_activity_log_column():
    """Add activity_log column to task_assignments table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='task_assignments' 
                AND column_name='activity_log'
            """))
            
            if result.fetchone():
                print("✅ activity_log column already exists")
                return
            
            # Add the column
            print("📋 Adding activity_log column to task_assignments...")
            db.session.execute(text("""
                ALTER TABLE task_assignments 
                ADD COLUMN activity_log JSONB DEFAULT '[]'::jsonb NOT NULL
            """))
            
            db.session.commit()
            print("✅ Successfully added activity_log column")
            
        except Exception as e:
            print(f"❌ Error adding column: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    add_activity_log_column()
    print("\n✅ Migration complete!")
