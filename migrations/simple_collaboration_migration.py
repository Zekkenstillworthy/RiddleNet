#!/usr/bin/env python3
"""
Simple migration script to add collaboration_settings column to simulations table
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def add_collaboration_settings_column():
    """Add collaboration_settings JSON column to simulations table using psycopg2"""
    try:
        # Get database connection details from environment
        db_url = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'admin')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'RiddleNet')}"
        
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='simulations' AND column_name='collaboration_settings';
        """)
        
        if cursor.fetchone():
            print("[OK] collaboration_settings column already exists")
            return True
        
        # Add the column
        cursor.execute("""
            ALTER TABLE simulations 
            ADD COLUMN collaboration_settings JSON DEFAULT '{}';
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("[OK] Successfully added collaboration_settings column to simulations table")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error adding collaboration_settings column: {str(e)}")
        return False

if __name__ == "__main__":
    success = add_collaboration_settings_column()
    exit(0 if success else 1)