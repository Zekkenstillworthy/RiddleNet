#!/usr/bin/env python3
"""
Database Migration: Add priority and category fields to class_assignments table
"""

import sqlite3
import os
import sys

# Add the parent directory to the path so we can import from the admin module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_assignment_fields():
    """Add priority and category columns to class_assignments table"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'riddlenet.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(class_assignments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add priority column if it doesn't exist
        if 'priority' not in columns:
            print("Adding 'priority' column to class_assignments table...")
            cursor.execute("ALTER TABLE class_assignments ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'")
            print("✅ Priority column added successfully")
        else:
            print("⚠️ Priority column already exists")
        
        # Add category column if it doesn't exist
        if 'category' not in columns:
            print("Adding 'category' column to class_assignments table...")
            cursor.execute("ALTER TABLE class_assignments ADD COLUMN category VARCHAR(50) DEFAULT 'general'")
            print("✅ Category column added successfully")
        else:
            print("⚠️ Category column already exists")
        
        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting migration to add priority and category fields to class_assignments...")
    success = migrate_assignment_fields()
    
    if success:
        print("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("💥 Migration failed!")
        sys.exit(1)