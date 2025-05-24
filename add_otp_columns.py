import sqlite3

def add_otp_columns():
    try:
        # Connect to the database
        conn = sqlite3.connect('instance/test.db')
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute('PRAGMA table_info(user)')
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Add OTP column if it doesn't exist
        if 'otp' not in existing_columns:
            cursor.execute('ALTER TABLE user ADD COLUMN otp VARCHAR(6)')
            print("Added otp column")
        
        # Add OTP timestamp column if it doesn't exist
        if 'otp_generated_at' not in existing_columns:
            cursor.execute('ALTER TABLE user ADD COLUMN otp_generated_at TIMESTAMP')
            print("Added otp_generated_at column")
        
        # Commit changes and close connection
        conn.commit()
        print("Database updated successfully!")
        
    except Exception as e:
        print(f"Error updating database: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_otp_columns()
