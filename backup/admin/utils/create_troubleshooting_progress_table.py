# filepath: c:\Users\gilbe\Documents\Flask_Main_Official_2 - Copy\admin\utils\create_troubleshooting_progress_table.py
import sys
import os
# Adjust the path to include the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from __init__ import db
from admin.models.troubleshooting_progress import TroubleshootingProgress
from admin.models.troubleshooting import Troubleshooting
from admin.models.user import User

def create_troubleshooting_progress_table():
    """
    Create the troubleshooting_progress table in the database if it doesn't exist.
    """
    try:
        print("Creating troubleshooting_progress table...")
        db.create_all()
        print("Troubleshooting progress table created successfully.")
    except Exception as e:
        print(f"Error creating troubleshooting progress table: {e}")
        
def check_tables():
    """
    Check if the required tables exist and create them if they don't.
    """
    try:
        # Check if the troubleshooting table exists
        Troubleshooting.__table__.create(db.engine, checkfirst=True)
        print("Troubleshooting table exists or was created.")
        
        # Check if the troubleshooting progress table exists
        TroubleshootingProgress.__table__.create(db.engine, checkfirst=True)
        print("TroubleshootingProgress table exists or was created.")
        
        # Check for user table
        User.__table__.create(db.engine, checkfirst=True)
        print("User table exists or was created.")
        
        print("All required tables exist in the database.")
    except Exception as e:
        print(f"Error checking tables: {e}")

if __name__ == "__main__":
    create_troubleshooting_progress_table()
    check_tables()
    print("Database setup complete.")