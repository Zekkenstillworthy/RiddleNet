#!/usr/bin/env python3
"""
Fix the simulations table sequence to prevent duplicate key violations
"""
import psycopg2
from psycopg2 import sql
import os

# Database configuration
DB_CONFIG = {
    'dbname': 'riddlenet_db',
    'user': 'ubuntu',
    'password': os.environ.get('DB_PASSWORD', 'your_password_here'),  # Update if needed
    'host': 'localhost',
    'port': 5432
}

def fix_simulation_sequence():
    """Sync the simulations_id_seq sequence with the actual max ID"""
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get current max ID
        print("🔍 Checking max simulation ID...")
        cursor.execute("SELECT MAX(id) FROM simulations;")
        max_id = cursor.fetchone()[0]
        print(f"📊 Current max ID in simulations table: {max_id}")
        
        # Get current sequence value
        cursor.execute("SELECT last_value FROM simulations_id_seq;")
        seq_value = cursor.fetchone()[0]
        print(f"📊 Current sequence value: {seq_value}")
        
        if max_id is None:
            print("⚠️ No simulations found in table")
            new_value = 1
        elif seq_value <= max_id:
            print(f"⚠️ Sequence is behind! Setting to {max_id}")
            new_value = max_id
        else:
            print("✅ Sequence is already correct")
            cursor.close()
            conn.close()
            return
        
        # Reset sequence
        print(f"🔧 Resetting sequence to {new_value}...")
        cursor.execute(
            sql.SQL("SELECT setval('simulations_id_seq', %s);"),
            [new_value]
        )
        conn.commit()
        
        # Verify
        cursor.execute("SELECT last_value FROM simulations_id_seq;")
        new_seq_value = cursor.fetchone()[0]
        print(f"✅ Sequence reset complete! New value: {new_seq_value}")
        
        cursor.close()
        conn.close()
        print("✅ Done!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_simulation_sequence()
