"""Test database connection"""
import psycopg2
from psycopg2 import OperationalError

# Test connection parameters
db_params = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'admin'
}

print("Testing PostgreSQL connection...")
print(f"Host: {db_params['host']}")
print(f"Port: {db_params['port']}")
print(f"User: {db_params['user']}")
print()

# First, try connecting to postgres database to list all databases
try:
    print("1. Connecting to 'postgres' database to check available databases...")
    conn = psycopg2.connect(
        host=db_params['host'],
        port=db_params['port'],
        user=db_params['user'],
        password=db_params['password'],
        database='postgres'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    databases = cursor.fetchall()
    print("✅ Available databases:")
    for db in databases:
        print(f"   - {db[0]}")
    cursor.close()
    conn.close()
    print()
except OperationalError as e:
    print(f"❌ Error connecting to postgres database: {e}")
    print()

# Now try connecting to riddlenet database
try:
    print("2. Connecting to 'riddlenet' database...")
    conn = psycopg2.connect(
        host=db_params['host'],
        port=db_params['port'],
        user=db_params['user'],
        password=db_params['password'],
        database='riddlenet'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Successfully connected to 'riddlenet' database!")
    print(f"   PostgreSQL version: {version[0]}")
    
    # Check if Admin table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'admin'
        );
    """)
    admin_exists = cursor.fetchone()[0]
    print(f"   Admin table exists: {admin_exists}")
    
    if admin_exists:
        cursor.execute("SELECT COUNT(*) FROM admin;")
        admin_count = cursor.fetchone()[0]
        print(f"   Number of admin records: {admin_count}")
    
    cursor.close()
    conn.close()
except OperationalError as e:
    print(f"❌ Error connecting to 'riddlenet' database: {e}")
    print()

# Test with SQLAlchemy (what Flask uses)
try:
    print("3. Testing SQLAlchemy connection (what Flask uses)...")
    from sqlalchemy import create_engine, text
    
    database_uri = f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/riddlenet"
    print(f"   URI: postgresql+psycopg2://{db_params['user']}:***@{db_params['host']}:{db_params['port']}/riddlenet")
    
    engine = create_engine(database_uri)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_database();"))
        current_db = result.fetchone()[0]
        print(f"✅ SQLAlchemy connection successful!")
        print(f"   Connected to database: {current_db}")
except Exception as e:
    print(f"❌ SQLAlchemy connection error: {e}")
