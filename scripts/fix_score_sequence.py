"""
Fix the score table sequence to match the maximum ID in the database.
This resolves the UniqueViolation error when inserting new scores.
"""
import psycopg2
import os

def fix_score_sequence():
    """Reset the score_id_seq to match the maximum ID in the score table"""
    
    # Database connection details from environment
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'RiddleNet')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'admin')
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        
        # Get the current max ID from the score table
        cursor.execute('SELECT MAX(id) FROM score')
        max_id = cursor.fetchone()[0]
        
        if max_id is None:
            max_id = 0
        
        print(f"Current maximum ID in score table: {max_id}")
        
        # Get the current sequence value
        cursor.execute('SELECT last_value FROM score_id_seq')
        current_seq = cursor.fetchone()[0]
        print(f"Current sequence value: {current_seq}")
        
        # Reset the sequence to max_id + 1
        new_seq_value = max_id + 1
        cursor.execute(f"ALTER SEQUENCE score_id_seq RESTART WITH {new_seq_value}")
        conn.commit()
        
        print(f"[OK] Sequence reset to: {new_seq_value}")
        
        # Verify the fix
        cursor.execute('SELECT last_value FROM score_id_seq')
        updated_seq = cursor.fetchone()[0]
        print(f"Verified new sequence value: {updated_seq}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Error fixing sequence: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_score_sequence()
