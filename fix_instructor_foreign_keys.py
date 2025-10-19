"""
Database Migration Script: Fix Foreign Keys from admin_users to instructor_users
This script updates all foreign key constraints that still reference the old admin_users table
"""

from application import create_app
from __init__ import db
from sqlalchemy import text
import sys

# Create app instance
app = create_app()

def fix_foreign_keys():
    """Fix foreign keys in database tables"""
    with app.app_context():
        try:
            print("🔧 Starting foreign key migration...")
            print("=" * 60)
            
            # Check if we're using PostgreSQL or SQLite
            db_url = str(db.engine.url)
            is_postgres = 'postgresql' in db_url.lower()
            
            if is_postgres:
                print("✅ PostgreSQL database detected")
                
                # Drop and recreate foreign keys for PostgreSQL
                tables_to_fix = [
                    ('class_content', 'created_by'),
                    ('class_assignments', 'created_by'),
                    ('class_materials', 'created_by'),
                    ('class_simulations', 'created_by'),
                    ('modules', 'created_by'),
                    ('instructor_scores', 'user_id'),
                    ('simulations', 'created_by'),
                ]
                
                for table_name, column_name in tables_to_fix:
                    try:
                        # Find existing constraint name
                        constraint_query = text(f"""
                            SELECT constraint_name 
                            FROM information_schema.table_constraints 
                            WHERE table_name = '{table_name}' 
                            AND constraint_type = 'FOREIGN KEY'
                            AND constraint_name LIKE '%{column_name}%'
                        """)
                        
                        result = db.session.execute(constraint_query).fetchone()
                        
                        if result:
                            constraint_name = result[0]
                            print(f"  🔍 Found constraint: {constraint_name} on {table_name}.{column_name}")
                            
                            # Drop old constraint
                            drop_query = text(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name}")
                            db.session.execute(drop_query)
                            print(f"  ✅ Dropped old constraint: {constraint_name}")
                            
                            # Add new constraint
                            add_query = text(f"""
                                ALTER TABLE {table_name} 
                                ADD CONSTRAINT {constraint_name} 
                                FOREIGN KEY ({column_name}) 
                                REFERENCES instructor_users(id)
                            """)
                            db.session.execute(add_query)
                            print(f"  ✅ Created new constraint: {constraint_name} -> instructor_users(id)")
                        else:
                            print(f"  ⚠️  No constraint found for {table_name}.{column_name}")
                            
                    except Exception as e:
                        print(f"  ❌ Error fixing {table_name}.{column_name}: {str(e)}")
                
                # Commit all changes
                db.session.commit()
                print("\n" + "=" * 60)
                print("✅ Foreign key migration completed successfully!")
                
            else:
                print("ℹ️  SQLite database detected - foreign keys will be updated on table recreation")
                print("ℹ️  Run 'db.drop_all()' and 'db.create_all()' to apply changes")
                
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    print("\n🔄 Foreign Key Migration Tool")
    print("=" * 60)
    print("This will update all foreign keys from admin_users to instructor_users")
    
    response = input("\nProceed with migration? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        fix_foreign_keys()
    else:
        print("❌ Migration cancelled")
        sys.exit(0)
