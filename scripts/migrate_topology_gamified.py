#!/usr/bin/env python3
"""
Database Migration for Gamified Topology Features
================================================

This script adds the new columns needed for the gamified topology system
to the existing topologies table.

Usage:
    python scripts/migrate_topology_gamified.py
"""

import sys
import os

# Add the parent directory to the path so we can import from the main application
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from application import create_app
from user.models import db
from sqlalchemy import text

def migrate_topology_table():
    """Add new columns for gamified topology features"""
    
    migrations = [
        # Add time limit column
        {
            'name': 'time_limit',
            'sql': 'ALTER TABLE topologies ADD COLUMN time_limit INTEGER DEFAULT 300;'
        },
        # Add tutorial steps column
        {
            'name': 'tutorial_steps',
            'sql': 'ALTER TABLE topologies ADD COLUMN tutorial_steps TEXT;'
        },
        # Add hints column
        {
            'name': 'hints',
            'sql': 'ALTER TABLE topologies ADD COLUMN hints TEXT;'
        },
        # Add unlock requirement column
        {
            'name': 'unlock_requirement',
            'sql': 'ALTER TABLE topologies ADD COLUMN unlock_requirement VARCHAR(100);'
        },
        # Add prerequisite topology foreign key
        {
            'name': 'prerequisite_topology_id',
            'sql': 'ALTER TABLE topologies ADD COLUMN prerequisite_topology_id INTEGER REFERENCES topologies(id);'
        }
    ]
    
    print("Migrating topology table for gamified features...")
    
    for migration in migrations:
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='topologies' AND column_name=:column_name
            """), {'column_name': migration['name']})
            
            if result.fetchone():
                print(f"  ✓ Column '{migration['name']}' already exists, skipping...")
                continue
            
            # Add the column
            db.session.execute(text(migration['sql']))
            db.session.commit()
            print(f"  ✓ Added column '{migration['name']}'")
            
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Error adding column '{migration['name']}': {e}")
            # Continue with other migrations
            continue
    
    print("\n✓ Topology table migration completed!")

def check_table_structure():
    """Check the current structure of the topologies table"""
    try:
        result = db.session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name='topologies'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        
        print(f"\nTopologies table structure ({len(columns)} columns):")
        print("=" * 60)
        
        for column in columns:
            nullable = "NULL" if column[2] == 'YES' else "NOT NULL"
            default = f" DEFAULT {column[3]}" if column[3] else ""
            print(f"  {column[0]:<25} {column[1]:<15} {nullable}{default}")
        
        # Check for gamified columns specifically
        gamified_columns = ['time_limit', 'tutorial_steps', 'hints', 'unlock_requirement', 'prerequisite_topology_id']
        existing_gamified = [col[0] for col in columns if col[0] in gamified_columns]
        missing_gamified = [col for col in gamified_columns if col not in existing_gamified]
        
        print(f"\nGamified columns status:")
        print(f"  ✓ Existing: {', '.join(existing_gamified) if existing_gamified else 'None'}")
        print(f"  ✗ Missing:  {', '.join(missing_gamified) if missing_gamified else 'None'}")
        
        return len(missing_gamified) == 0
        
    except Exception as e:
        print(f"Error checking table structure: {e}")
        return False

def main():
    """Main migration function"""
    app = create_app()
    
    with app.app_context():
        print("Gamified Topology Database Migration")
        print("=" * 40)
        
        # Check current structure
        is_migrated = check_table_structure()
        
        if is_migrated:
            print("\n✓ All gamified columns already exist! No migration needed.")
            return
        
        # Ask user if they want to proceed with migration
        print("\nDo you want to proceed with the database migration?")
        response = input("This will modify the topologies table structure (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            migrate_topology_table()
            
            # Check final structure
            print("\nPost-migration table structure:")
            check_table_structure()
        else:
            print("Migration cancelled.")

if __name__ == '__main__':
    main()