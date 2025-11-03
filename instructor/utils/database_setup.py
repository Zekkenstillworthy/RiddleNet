from __init__ import db
from instructor.models.question import Question
from werkzeug.security import generate_password_hash
from instructor.models.user import Instructor
from instructor.utils.questions_data import get_networking_questions
import os
from sqlalchemy import text

def setup_database():
    """Set up the database with initial tables and data."""
    from __init__ import db    
    from instructor.models.user import InstructorUser, Instructor
    from instructor.models.question import Question
    from instructor.models.score import InstructorScore  # Updated to use the renamed model
    from instructor.models.class_model import Class
    from instructor.models.question_group import QuestionGroup
    from instructor.models.essay_response import EssayResponse
    from instructor.models.activity_log import ActivityLog
    from instructor.models.topology import Topology
    
    # Import performance feedback models
    from user.models.performance_feedback import PerformanceFeedback, FeedbackSession
    
    from werkzeug.security import generate_password_hash
    
    print("Creating database tables...")
    
    # Create all database tables
    db.create_all()
    
    # Check for admin account and create if not exists
    admin_exists = Instructor.query.filter_by(username="admin").first()
    if not admin_exists:
        print("Creating admin account...")
        admin = Instructor(
            username="admin", 
            password_hash=generate_password_hash("admin"),
            email="admin@riddlenet.com"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin account created successfully!")
    
    # Migrate existing tables to add missing columns
    migrate_existing_tables()
    
    # One-time safety: ensure PostgreSQL sequences are in sync with MAX(id)
    sequences_to_fix = [
        ('simulation_assignments', 'simulation_assignments.id'),
        ('assignment_submissions', 'assignment_submissions.id')
    ]
    
    for table_name, description in sequences_to_fix:
        try:
            print(f"[database_setup] Syncing {description} sequence with MAX(id)...")
            max_id_result = db.session.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}"))
            max_id = max_id_result.scalar_one() or 0
            # Set to max_id so next nextval() returns max_id + 1
            next_val = max_id
            seq_name_result = db.session.execute(text(f"SELECT pg_get_serial_sequence('{table_name}','id')"))
            seq_name = seq_name_result.scalar_one()
            if seq_name:
                # setval with is_called=true means "last value returned was next_val, so nextval() returns next_val+1"
                db.session.execute(text("SELECT setval(:seq, :val, true)"), {"seq": seq_name, "val": next_val})
                db.session.commit()
                print(f"[database_setup] [OK] {description} sequence synced (next insert will use {next_val + 1})")
            else:
                print(f"[database_setup] [SKIP] No sequence found for {table_name}")
        except Exception as e:
            db.session.rollback()
            print(f"[database_setup] [WARNING] {description} sequence sync failed: {e}")
    
    print("Database setup complete!")
    print("[OK] Performance feedback tables created successfully!")

def migrate_existing_tables():
    """Previously performed ad-hoc SQLite PRAGMA based migrations.

    With PostgreSQL now mandated, structural changes should be handled via
    proper Alembic migrations (flask db migrate/upgrade). This function is
    retained as a no-op to avoid import errors from legacy calls.
    """
    print("[database_setup] Skipping legacy SQLite PRAGMA migrations (PostgreSQL in use)")

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

def create_default_instructor():
    """Create a default instructor user if no admin exists."""
    if Instructor.query.count() == 0:
        default_admin = Instructor(
            username="admin",
            password_hash=generate_password_hash("admin"),
            email="admin@example.com",
            role="admin"
        )
        try:
            db.session.add(default_admin)
            db.session.commit()
            print("Created default instructor user. Username: 'admin', Password: 'admin'")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating default admin: {e}")
