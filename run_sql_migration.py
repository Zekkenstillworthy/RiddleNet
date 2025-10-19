"""
Simple SQL Migration Runner
Executes fix_foreign_keys.sql using Python
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the SQL migration script"""
    
    # Database connection details from environment
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'riddlenet'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'admin')
    }
    
    print("🔧 SQL Migration Tool")
    print("=" * 60)
    print(f"Connecting to: {db_config['database']} on {db_config['host']}:{db_config['port']}")
    print()
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        print()
        
        # Read SQL file
        with open('fix_foreign_keys.sql', 'r') as f:
            sql_script = f.read()
        
        # Split into individual statements (excluding comments and verification query)
        statements = []
        current_statement = []
        
        for line in sql_script.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('--'):
                continue
            
            # Skip the verification SELECT query at the end
            if line.upper().startswith('SELECT') and 'table_name' in line.lower():
                break
            
            current_statement.append(line)
            
            # Statement ends with semicolon
            if line.endswith(';'):
                statements.append(' '.join(current_statement))
                current_statement = []
        
        print(f"📋 Found {len(statements)} SQL statements to execute")
        print()
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            try:
                # Extract table name for display
                if 'ALTER TABLE' in statement:
                    table_name = statement.split('ALTER TABLE')[1].split()[0]
                    print(f"  {i}. Processing table: {table_name}")
                    
                cursor.execute(statement)
                print(f"     ✅ Success")
                
            except Exception as e:
                print(f"     ⚠️  Warning: {str(e)}")
                # Continue even if constraint doesn't exist
        
        # Commit all changes
        conn.commit()
        print()
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print()
        
        # Run verification query
        print("🔍 Verifying - checking for remaining admin_users references...")
        verification_query = """
            SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND ccu.table_name = 'admin_users';
        """
        
        cursor.execute(verification_query)
        results = cursor.fetchall()
        
        if results:
            print("⚠️  Warning: Still found references to admin_users:")
            for row in results:
                print(f"   - {row[0]}.{row[1]} -> {row[2]}")
        else:
            print("✅ Perfect! No foreign keys pointing to admin_users found.")
        
        print()
        print("=" * 60)
        print("🎉 Migration complete! You can now restart your application.")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        print()
        print("Make sure PostgreSQL is running and credentials are correct.")
        if conn:
            conn.rollback()
        return False
        
    except FileNotFoundError:
        print("❌ Error: fix_foreign_keys.sql file not found")
        print("Make sure you're running this script from the project root directory.")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if conn:
            conn.rollback()
        return False
    
    return True

if __name__ == '__main__':
    print()
    response = input("⚠️  This will modify database foreign keys. Continue? (yes/no): ")
    print()
    
    if response.lower() in ['yes', 'y']:
        success = run_migration()
        if not success:
            print("\n❌ Migration failed. Please check the errors above.")
            exit(1)
    else:
        print("❌ Migration cancelled")
        exit(0)
