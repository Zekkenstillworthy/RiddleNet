"""
Migration: Add missing columns to live_quiz_responses table

This migration adds the answered_at column and ensures all expected fields
are present in the live_quiz_responses table to match the ORM model.

Run with: python migrations/011_update_live_quiz_responses_columns.py upgrade
"""
import os
import sys

# Allow importing the application factory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import inspect, text
from __init__ import create_app, db


RESPONSES_TABLE = 'live_quiz_responses'


def upgrade():
    """Add missing columns to live_quiz_responses table."""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        if RESPONSES_TABLE not in inspector.get_table_names():
            print(f"[ERROR] Table '{RESPONSES_TABLE}' does not exist; aborting upgrade.")
            return False

        existing_columns = {column['name'] for column in inspector.get_columns(RESPONSES_TABLE)}

        statements = []

        # Add answered_at column if missing
        if 'answered_at' not in existing_columns:
            statements.append(
                "ALTER TABLE live_quiz_responses ADD COLUMN answered_at TIMESTAMP DEFAULT NOW()"
            )
            print("📝 Adding answered_at column")

        # Ensure other expected columns exist
        if 'response_time' not in existing_columns:
            statements.append(
                "ALTER TABLE live_quiz_responses ADD COLUMN response_time DOUBLE PRECISION DEFAULT 0"
            )
            print("📝 Adding response_time column")

        if 'points_awarded' not in existing_columns:
            statements.append(
                "ALTER TABLE live_quiz_responses ADD COLUMN points_awarded INTEGER DEFAULT 0"
            )
            print("📝 Adding points_awarded column")

        if 'question_text' not in existing_columns:
            statements.append(
                "ALTER TABLE live_quiz_responses ADD COLUMN question_text VARCHAR(500)"
            )
            print("📝 Adding question_text column")

        if 'correct_answer' not in existing_columns:
            statements.append(
                "ALTER TABLE live_quiz_responses ADD COLUMN correct_answer VARCHAR(1000)"
            )
            print("📝 Adding correct_answer column")

        if 'created_at' not in existing_columns:
            statements.append(
                "ALTER TABLE live_quiz_responses ADD COLUMN created_at TIMESTAMP DEFAULT NOW()"
            )
            print("📝 Adding created_at column")

        # Execute all ALTER TABLE statements
        for stmt in statements:
            db.session.execute(text(stmt))

        # Set defaults for existing rows
        update_stmt = text(
            """
            UPDATE live_quiz_responses
            SET
                answered_at = COALESCE(answered_at, created_at, NOW()),
                response_time = COALESCE(response_time, 0),
                points_awarded = COALESCE(points_awarded, 0),
                created_at = COALESCE(created_at, NOW())
            WHERE answered_at IS NULL 
               OR response_time IS NULL 
               OR points_awarded IS NULL 
               OR created_at IS NULL
            """
        )
        db.session.execute(update_stmt)

        # Apply NOT NULL constraints where appropriate
        not_null_statements = [
            "ALTER TABLE live_quiz_responses ALTER COLUMN participant_id SET NOT NULL",
            "ALTER TABLE live_quiz_responses ALTER COLUMN session_id SET NOT NULL",
            "ALTER TABLE live_quiz_responses ALTER COLUMN question_id SET NOT NULL",
            "ALTER TABLE live_quiz_responses ALTER COLUMN selected_answer SET NOT NULL",
            "ALTER TABLE live_quiz_responses ALTER COLUMN is_correct SET NOT NULL",
            "ALTER TABLE live_quiz_responses ALTER COLUMN response_time SET NOT NULL",
        ]

        for stmt in not_null_statements:
            try:
                db.session.execute(text(stmt))
            except Exception as e:
                print(f"⚠️ Warning: Could not set NOT NULL constraint - {e}")

        db.session.commit()
        print("[OK] live_quiz_responses table is aligned with ORM model.")
        return True


def downgrade():
    """Remove added columns (if safe to do so)."""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        if RESPONSES_TABLE not in inspector.get_table_names():
            print(f"[WARNING] Table '{RESPONSES_TABLE}' does not exist; nothing to downgrade.")
            return True

        existing_columns = {column['name'] for column in inspector.get_columns(RESPONSES_TABLE)}

        # Drop added columns in reverse order
        drop_columns = [
            'created_at',
            'correct_answer',
            'question_text',
            'points_awarded',
            'response_time',
            'answered_at',
        ]

        for column in drop_columns:
            if column in existing_columns:
                db.session.execute(text(f"ALTER TABLE live_quiz_responses DROP COLUMN {column}"))
                print(f"🗑️ Dropped column {column}")

        db.session.commit()
        print("[OK] Downgrade completed for live_quiz_responses table.")
        return True


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Update live quiz responses columns migration')
    parser.add_argument('action', choices=['upgrade', 'downgrade'], help='Migration action to perform')

    args = parser.parse_args()

    if args.action == 'upgrade':
        success = upgrade()
        sys.exit(0 if success else 1)
    elif args.action == 'downgrade':
        success = downgrade()
        sys.exit(0 if success else 1)
