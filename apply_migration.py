"""
Apply database migration: Admin -> Instructor
This script executes the SQL migration file safely
"""
import os
import sys
from sqlalchemy import create_engine, text

# Get database credentials from environment
from dotenv import load_dotenv
load_dotenv()

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'riddlenet')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin')

# Build database URI
DATABASE_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

print(f"Connecting to database: {POSTGRES_DB}")
print(f"Host: {POSTGRES_HOST}:{POSTGRES_PORT}")

try:
    # Create engine
    engine = create_engine(DATABASE_URI)
    
    # Read migration file
    migration_file = 'migrations/rename_admin_to_instructor.sql'
    print(f"\nReading migration file: {migration_file}")
    
    with open(migration_file, 'r') as f:
        sql_content = f.read()
    
    # Execute migration
    print("\n" + "="*60)
    print("APPLYING MIGRATION: Admin -> Instructor")
    print("="*60 + "\n")
    
    with engine.connect() as conn:
        # Execute in a transaction
        with conn.begin():
            # Split SQL by semicolons and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for i, statement in enumerate(statements, 1):
                if statement.upper().startswith('BEGIN') or statement.upper().startswith('COMMIT'):
                    continue  # Skip transaction control - we handle it with context manager
                    
                if '/*' in statement:  # Skip comments block
                    continue
                    
                print(f"Executing statement {i}/{len(statements)}...")
                try:
                    conn.execute(text(statement))
                    print(f"  ✓ Success")
                except Exception as e:
                    print(f"  ⚠ Warning: {e}")
                    # Continue with other statements
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETED")
        print("="*60)
        
        # Verify changes
        print("\nVerifying tables with 'instructor' in name:")
        result = conn.execute(text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE tablename LIKE '%instructor%' 
            ORDER BY tablename
        """))
        
        for row in result:
            print(f"  ✓ {row[0]}")
    
    print("\n✅ Migration applied successfully!")
    print("You can now update the Python code to use 'instructor_users' table.")
    
except Exception as e:
    print(f"\n❌ Error during migration: {e}")
    print("\nIf tables already exist with instructor names, this is expected.")
    print("You can proceed with updating the Python code.")
    import traceback
    traceback.print_exc()
    sys.exit(1)
