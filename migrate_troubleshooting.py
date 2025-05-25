#!/usr/bin/env python3
"""
Migration script to add missing columns to the troubleshootings table
"""
import sqlite3
import sys
import os
from datetime import datetime

def backup_database():
    """Create a backup of the current database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'instance/test_backup_{timestamp}.db'
    
    try:
        # Copy the database file
        import shutil
        shutil.copy2('instance/test.db', backup_path)
        print(f"Database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False

def migrate_troubleshooting_table():
    """Add missing columns to the troubleshootings table"""
    db_path = 'instance/test.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist!")
        return False
    
    # Create backup first
    if not backup_database():
        print("Failed to create backup. Aborting migration.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List of columns to add with their definitions
        new_columns = [
            ("problem_type", "VARCHAR(50)", "'network'"),  # Default to 'network'
            ("scoring_metrics", "TEXT", "NULL"),
            ("initial_topology", "TEXT", "NULL"),
            ("solution_topology", "TEXT", "NULL"),
            ("required_steps", "TEXT", "NULL"),
            ("time_limit", "INTEGER", "15"),  # Default 15 minutes
            ("base_score", "INTEGER", "10"),  # Default base score
            ("time_bonus", "INTEGER", "5"),   # Default time bonus
            ("solution_bonus", "INTEGER", "5"), # Default solution bonus
            ("required_devices", "TEXT", "NULL"),
            ("topology_config", "TEXT", "NULL"),
            ("expected_topology", "TEXT", "NULL"),
            ("tasks", "TEXT", "NULL"),
            ("perfect_match_bonus", "INTEGER", "10"), # Default perfect match bonus
            ("topology_type", "VARCHAR(50)", "NULL")
        ]
        
        print("Adding missing columns to troubleshootings table...")
        
        for col_name, col_type, default_value in new_columns:
            try:
                # Check if column already exists
                cursor.execute('PRAGMA table_info(troubleshootings)')
                existing_columns = [col[1] for col in cursor.fetchall()]
                
                if col_name not in existing_columns:
                    sql = f"ALTER TABLE troubleshootings ADD COLUMN {col_name} {col_type}"
                    if default_value != "NULL":
                        sql += f" DEFAULT {default_value}"
                    
                    cursor.execute(sql)
                    print(f"  ✓ Added column: {col_name}")
                else:
                    print(f"  - Column already exists: {col_name}")
                    
            except Exception as e:
                print(f"  ✗ Error adding column {col_name}: {e}")
        
        conn.commit()
        conn.close()
        
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

def verify_migration():
    """Verify that all columns were added successfully"""
    print("\nVerifying migration...")
    
    try:
        conn = sqlite3.connect('instance/test.db')
        cursor = conn.cursor()
        
        cursor.execute('PRAGMA table_info(troubleshootings)')
        columns = cursor.fetchall()
        
        print(f"Table now has {len(columns)} columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error verifying migration: {e}")
        return False

if __name__ == "__main__":
    print("Starting troubleshootings table migration...")
    print("Current working directory:", os.getcwd())
    print("Database path exists:", os.path.exists('instance/test.db'))
    
    if migrate_troubleshooting_table():
        verify_migration()
        print("\nMigration completed! You can now test the troubleshooting API.")
    else:
        print("\nMigration failed! Please check the errors above.")
