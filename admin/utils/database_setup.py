from admin import db
from admin.models.question import Question
from werkzeug.security import generate_password_hash
from admin.models.user import Admin
from admin.utils.questions_data import get_networking_questions
import sqlite3

def setup_database():
    """Set up the database with initial tables and data."""
    from admin import db    
    from admin.models.user import AdminUser, Admin
    from admin.models.question import Question
    from admin.models.score import AdminScore  # Updated to use the renamed model
    from admin.models.class_model import Class
    from admin.models.question_group import QuestionGroup
    from admin.models.essay_response import EssayResponse
    from admin.models.activity_log import ActivityLog
    from admin.models.topology import Topology
    from werkzeug.security import generate_password_hash
    
    print("Creating database tables...")
    
    # Create all database tables
    db.create_all()
    
    # Check for admin account and create if not exists
    admin_exists = Admin.query.filter_by(username="admin").first()
    if not admin_exists:
        print("Creating admin account...")
        admin = Admin(
            username="admin", 
            password_hash=generate_password_hash("admin"),
            email="admin@riddlenet.com"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin account created successfully!")
    
    # Migrate existing tables to add missing columns
    migrate_existing_tables()
    
    print("Database setup complete!")

def migrate_existing_tables():
    """Add missing columns to existing tables"""
    try:
        from sqlalchemy import text
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        
        # Fix activity_logs table column naming issue
        try:
            cursor.execute("PRAGMA table_info(activity_logs)")
            activity_columns = [column[1] for column in cursor.fetchall()]
            
            if 'admin_user_id' in activity_columns and 'user_id' not in activity_columns:
                print("Migrating activity_logs table: renaming admin_user_id to user_id...")
                # Create new table with correct schema
                cursor.execute('''
                CREATE TABLE activity_logs_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action_type VARCHAR(50) NOT NULL,
                    message VARCHAR(255) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    related_entity_type VARCHAR(50),
                    related_entity_id INTEGER
                )
                ''')
                
                # Copy data from old table to new table
                cursor.execute('''
                INSERT INTO activity_logs_new (id, user_id, action_type, message, timestamp, related_entity_type, related_entity_id)
                SELECT id, admin_user_id, action_type, message, timestamp, related_entity_type, related_entity_id
                FROM activity_logs
                ''')
                
                # Drop old table and rename new table
                cursor.execute('DROP TABLE activity_logs')
                cursor.execute('ALTER TABLE activity_logs_new RENAME TO activity_logs')
                connection.commit()
                print("Successfully migrated activity_logs table")
        except Exception as e:
            print(f"Activity logs table migration: {e}")
        
        # Check and add updated_at column to classes table
        cursor.execute("PRAGMA table_info(classes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'updated_at' not in columns:
            print("Adding updated_at column to classes table...")
            cursor.execute("ALTER TABLE classes ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            connection.commit()
            print("Successfully added updated_at column to classes table")
          # Check other tables that might need updated_at column
        tables_needing_updated_at = [
            'topologies', 'troubleshootings', 
            'troubleshooting_progress', 'question_groups'
        ]
        
        for table_name in tables_needing_updated_at:
            try:
                cursor.execute(f"PRAGMA table_info({table_name})")
                table_columns = [column[1] for column in cursor.fetchall()]
                
                if table_columns and 'updated_at' not in table_columns:
                    print(f"Adding updated_at column to {table_name} table...")
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    connection.commit()
                    print(f"Successfully added updated_at column to {table_name} table")
            except Exception as e:
                print(f"Table {table_name} might not exist yet: {e}")
                continue
        
        connection.close()
        print("Database migration completed successfully")
        
    except Exception as e:
        print(f"Error during database migration: {e}")

def import_default_questions():
    """Import default questions if the database is empty."""
    if Question.query.count() == 0:
        try:
            # Get default questions from questions_data.py
            default_questions = get_networking_questions()
            
            for q_data in default_questions:
                question = Question(
                    numb=q_data["numb"],
                    question=q_data["question"],
                    answer=q_data["answer"],
                    options=q_data["options"],
                    explanation=q_data.get("explanation", ""),
                    category="riddle"
                )
                db.session.add(question)
                
            db.session.commit()
            print("Imported default questions from questions_data.py")
        except Exception as e:
            db.session.rollback()
            print(f"Error importing default questions: {e}")

def create_default_admin():
    """Create a default admin user if no admin exists."""
    if Admin.query.count() == 0:
        default_admin = Admin(
            username="admin",
            password_hash=generate_password_hash("admin"),
            email="admin@example.com",
            role="admin"
        )
        try:
            db.session.add(default_admin)
            db.session.commit()
            print("Created default admin user. Username: 'admin', Password: 'admin'")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating default admin: {e}")
