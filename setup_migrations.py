#!/usr/bin/env python3
"""
Database Migration Setup for RiddleNet
This script initializes Flask-Migrate for proper database schema management
"""
import os
import sys
from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade

# Add the application directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def setup_migrations():
    """Initialize Flask-Migrate for the application"""
    
    # Import the app and db from your application
    from run import app, db
    
    # Initialize Flask-Migrate
    migrate_obj = Migrate(app, db)
    
    with app.app_context():
        migrations_dir = os.path.join(current_dir, 'migrations')
        
        # Check if migrations directory exists
        if not os.path.exists(migrations_dir):
            print("🔧 Initializing Flask-Migrate...")
            try:
                init()
                print("✅ Flask-Migrate initialized successfully")
                print(f"📁 Migrations directory created at: {migrations_dir}")
            except Exception as e:
                print(f"❌ Error initializing Flask-Migrate: {e}")
                return False
        else:
            print("✅ Flask-Migrate already initialized")
        
        # Create initial migration if none exist
        versions_dir = os.path.join(migrations_dir, 'versions')
        if os.path.exists(versions_dir):
            migration_files = [f for f in os.listdir(versions_dir) if f.endswith('.py')]
            if not migration_files:
                print("🔧 Creating initial migration...")
                try:
                    migrate(message='Initial migration')
                    print("✅ Initial migration created successfully")
                except Exception as e:
                    print(f"❌ Error creating initial migration: {e}")
                    return False
            else:
                print(f"✅ Found {len(migration_files)} existing migrations")
        
        return True

def apply_migrations():
    """Apply all pending migrations"""
    from run import app, db
    
    migrate_obj = Migrate(app, db)
    
    with app.app_context():
        try:
            print("🔧 Applying database migrations...")
            upgrade()
            print("✅ Database migrations applied successfully")
            return True
        except Exception as e:
            print(f"❌ Error applying migrations: {e}")
            return False

def main():
    """Main function to set up and apply migrations"""
    print("🗄️  RiddleNet Database Migration Setup")
    print("=" * 40)
    
    # Setup migrations
    if not setup_migrations():
        print("❌ Failed to setup migrations")
        sys.exit(1)
    
    # Apply migrations
    if not apply_migrations():
        print("❌ Failed to apply migrations")
        sys.exit(1)
    
    print("\n✅ Database migration setup completed successfully!")
    print("\n📋 Useful commands for future migrations:")
    print("  Create migration:  flask db migrate -m 'description'")
    print("  Apply migrations:  flask db upgrade")
    print("  Migration history: flask db history")
    print("  Current revision:  flask db current")

if __name__ == "__main__":
    main()