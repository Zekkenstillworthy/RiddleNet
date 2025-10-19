"""
Create an instructor account and fix password hash column length
"""
import os
import psycopg2
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_instructor_account():
    """Create an instructor account after fixing the database schema"""
    
    # Database connection parameters
    db_params = {
        'dbname': 'riddlenet',
        'user': 'postgres',
        'password': 'admin',
        'host': 'localhost',
        'port': 5432
    }
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Step 1: Fix password_hash column length
        print("\n📝 Fixing password_hash column length...")
        alter_sql = """
        ALTER TABLE instructor 
        ALTER COLUMN password_hash TYPE VARCHAR(255);
        """
        cursor.execute(alter_sql)
        conn.commit()
        print("✅ Password hash column updated to VARCHAR(255)")
        
        # Step 2: Check if admin already exists
        print("\n🔍 Checking for existing admin account...")
        cursor.execute("SELECT id, email FROM instructor WHERE email = 'admin@riddlenet.com' OR username = 'admin'")
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  Admin account already exists (ID: {existing[0]}, Email: {existing[1]})")
            print("Skipping account creation")
            return
        
        # Step 3: Create instructor account
        print("\n👤 Creating instructor account...")
        
        # Instructor details
        username = 'admin'
        email = 'admin@riddlenet.com'
        password = 'admin123'  # Change this to your preferred password
        role = 'instructor'
        
        # Generate password hash
        password_hash = generate_password_hash(password, method='scrypt')
        created_at = datetime.now()
        
        insert_sql = """
        INSERT INTO instructor (username, password_hash, email, role, created_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        
        cursor.execute(insert_sql, (username, password_hash, email, role, created_at))
        instructor_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"✅ Instructor account created successfully!")
        print(f"\n📋 Account Details:")
        print(f"   ID: {instructor_id}")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Role: {role}")
        print(f"\n🔐 Login URL: http://127.0.0.1:5001/instructor/login")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    print("=" * 60)
    print("  CREATE INSTRUCTOR ACCOUNT")
    print("=" * 60)
    create_instructor_account()
    print("\n" + "=" * 60)
    print("  DONE!")
    print("=" * 60)
