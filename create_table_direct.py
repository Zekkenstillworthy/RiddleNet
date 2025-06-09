#!/usr/bin/env python3
"""
Simple migration script to create the networking2_progress table
"""

import sys
import os
import sqlite3

# Path to the database
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'test.db')

def create_table_directly():
    """Create the networking2_progress table directly using SQLite"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'test.db')
        print(f"Connecting to database: {db_path}")
        
        # Check if database file exists
        if not os.path.exists(db_path):
            print(f"Database file not found at: {db_path}")
            # Check for alternative locations
            alt_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user', 'app.db')
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    print(f"Found database at: {alt_path}")
                    db_path = alt_path
                    break
            else:
                print("No database file found. Creating new one...")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='networking2_progress';")
        if cursor.fetchone():
            print("✅ networking2_progress table already exists!")
            conn.close()
            return True
        
        # Create the table (based on the model structure we saw earlier)
        create_table_sql = """
        CREATE TABLE networking2_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            progress FLOAT DEFAULT 0.0,
            last_accessed DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id),
            UNIQUE(user_id, lesson_id)
        );
        """
        
        print("Creating networking2_progress table...")
        cursor.execute(create_table_sql)
        conn.commit()
        
        # Verify the table was created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='networking2_progress';")
        if cursor.fetchone():
            print("✅ networking2_progress table created successfully!")
            
            # Show table structure
            cursor.execute("PRAGMA table_info(networking2_progress);")
            columns = cursor.fetchall()
            print("\nTable columns:")
            for col in columns:
                print(f"  - {col[1]}: {col[2]}")
            
            conn.close()
            return True
        else:
            print("❌ Failed to create table")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("Starting direct SQLite migration...")
    success = create_table_directly()
    if success:
        print('\n🎉 Database migration completed successfully!')
        print('You can now access the Networking 2 learning path.')
    else:
        print('\n💥 Database migration failed.')
        sys.exit(1)
