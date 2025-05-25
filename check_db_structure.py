#!/usr/bin/env python3
import sqlite3
import sys
import os

def check_table_structure():
    """Check the current structure of the troubleshootings table"""
    db_path = 'instance/test.db'
    print(f"Checking database at: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if troubleshootings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='troubleshootings'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("troubleshootings table does not exist!")
            return
        
        # Get table structure
        cursor.execute('PRAGMA table_info(troubleshootings)')
        columns = cursor.fetchall()
        
        print('Current troubleshootings table columns:')
        for col in columns:
            print(f'  {col[1]} ({col[2]}) - {"NOT NULL" if col[3] else "NULL"} - Default: {col[4]}')
        
        print(f'\nTotal columns: {len(columns)}')
        
        # Get row count
        cursor.execute('SELECT COUNT(*) FROM troubleshootings')
        row_count = cursor.fetchone()[0]
        print(f'Total rows: {row_count}')
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_table_structure()
