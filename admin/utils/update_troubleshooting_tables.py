"""
This script adds the new fields to the troubleshooting table and creates 
the troubleshooting_progress table for tracking user progress
"""
from admin import db
from admin.models.troubleshooting import Troubleshooting
from admin.models.troubleshooting_progress import TroubleshootingProgress
from sqlalchemy import inspect, Column, Integer, String, Text, Boolean, DateTime, Float
import sys
from datetime import datetime

def add_column(engine, table_name, column):
    """Add a column to a table if it doesn't exist"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    if column.name not in columns:
        column_type = column.type.compile(engine.dialect)
        default = getattr(column, 'default', None)
        nullable = '' if column.nullable else ' NOT NULL'
        default_str = f" DEFAULT {default.arg}" if default else ''
        engine.execute(f'ALTER TABLE {table_name} ADD COLUMN {column.name} {column_type}{nullable}{default_str}')
        print(f"Added column {column.name} to {table_name}")
    else:
        print(f"Column {column.name} already exists in {table_name}")

def check_table_exists(engine, table_name):
    """Check if a table exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def run_migration():
    """Run the migration to update the troubleshooting tables"""
    try:
        engine = db.engine
        
        # Add new columns to troubleshooting table if needed
        if check_table_exists(engine, 'troubleshootings'):
            print("Updating troubleshootings table...")
            add_column(engine, 'troubleshootings', Column('required_steps', Text))
            add_column(engine, 'troubleshootings', Column('time_limit', Integer, default=15))
        else:
            print("Creating troubleshootings table...")
            Troubleshooting.__table__.create(engine)
            print("Created troubleshootings table")
        
        # Create troubleshooting_progress table if it doesn't exist
        if not check_table_exists(engine, 'troubleshooting_progress'):
            print("Creating troubleshooting_progress table...")
            TroubleshootingProgress.__table__.create(engine)
            print("Created troubleshooting_progress table")
        else:
            print("troubleshooting_progress table already exists")
            
        print("Migration completed successfully!")
        return True
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    if not success:
        sys.exit(1)
