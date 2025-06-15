#!/usr/bin/env python3
"""
Quick verification script to check if users were deleted
"""

import sqlite3
import os
from tabulate import tabulate

def verify_deletion():
    # Connect to the database
    db_path = os.path.join('instance', 'test.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("=== VERIFICATION: Checking if Zekken4 and Zekken2 were deleted ===\n")
        
        # Check user table
        print("Checking 'user' table:")
        cursor.execute("SELECT id, username, email FROM user ORDER BY id")
        users = cursor.fetchall()
        if users:
            headers = ["ID", "Username", "Email"]
            print(tabulate(users, headers=headers, tablefmt="grid"))
        else:
            print("No users found in 'user' table")
        
        print("\n" + "="*60 + "\n")
        
        # Check users table
        print("Checking 'users' table:")
        cursor.execute("SELECT id, username, email FROM users ORDER BY id")
        users_alt = cursor.fetchall()
        if users_alt:
            headers = ["ID", "Username", "Email"]
            print(tabulate(users_alt, headers=headers, tablefmt="grid"))
        else:
            print("No users found in 'users' table")
        
        print("\n" + "="*60 + "\n")
        
        # Check for any remaining references
        print("Checking for any remaining references to user IDs 2 and 3:")
        
        tables_to_check = [
            'networking_progress', 'networking2_progress', 'topic_progress',
            'troubleshooting_progress', 'topology_progress', 'essay_response',
            'essay_responses', 'essay', 'score', 'activity_log', 'activity_logs',
            'class_students', 'user_classes'
        ]
        
        found_references = False
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id IN (2, 3)")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"⚠️  Found {count} remaining references in table '{table}'")
                    found_references = True
            except sqlite3.Error as e:
                # Table might not exist or have user_id column
                pass
        
        if not found_references:
            print("✓ No remaining references found - deletion was complete!")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    verify_deletion()
