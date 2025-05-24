"""
Run the troubleshooting database migration to add new fields and create the progress tracking table.
"""
import sys
from flask import Flask
from admin.utils.update_troubleshooting_tables import run_migration
from admin import db
from admin.models.troubleshooting import Troubleshooting
from admin.models.troubleshooting_progress import TroubleshootingProgress

# Create a minimal Flask app for running the migration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        print("Running troubleshooting database migration...")
        success = run_migration()
        if success:
            print("Migration completed successfully!")
            sys.exit(0)
        else:
            print("Migration failed!")
            sys.exit(1)