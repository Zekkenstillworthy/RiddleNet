"""
Migration: Ensure live quiz session table has the columns expected by the ORM model.

This migration adds any missing fields to the live_quiz_sessions table and
applies sensible defaults so newer backend code can interact with the table
without hitting column-missing errors.

Run with:  python migrations/008_update_live_quiz_session_columns.py upgrade
"""
import sys
import os

# Allow importing the application factory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import inspect, text

from __init__ import create_app, db


LIVE_QUIZ_TABLE = 'live_quiz_sessions'


def upgrade():
    """Add any missing columns used by LiveQuizSession."""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        if LIVE_QUIZ_TABLE not in inspector.get_table_names():
            print(f"[ERROR] Table '{LIVE_QUIZ_TABLE}' does not exist; aborting upgrade.")
            return False

        existing_columns = {column['name'] for column in inspector.get_columns(LIVE_QUIZ_TABLE)}

        statements = []

        # Timing fields
        if 'started_at' not in existing_columns:
            statements.append("ALTER TABLE live_quiz_sessions ADD COLUMN started_at TIMESTAMP NULL")
        if 'ended_at' not in existing_columns:
            statements.append("ALTER TABLE live_quiz_sessions ADD COLUMN ended_at TIMESTAMP NULL")

        # Progress fields
        if 'current_question_index' not in existing_columns:
            statements.append("ALTER TABLE live_quiz_sessions ADD COLUMN current_question_index INTEGER DEFAULT 0")
        else:
            statements.append("ALTER TABLE live_quiz_sessions ALTER COLUMN current_question_index SET DEFAULT 0")

        if 'time_per_question' not in existing_columns:
            statements.append("ALTER TABLE live_quiz_sessions ADD COLUMN time_per_question INTEGER DEFAULT 30")
        else:
            statements.append("ALTER TABLE live_quiz_sessions ALTER COLUMN time_per_question SET DEFAULT 30")

        # Settings flags
        if 'show_leaderboard' not in existing_columns:
            statements.append("ALTER TABLE live_quiz_sessions ADD COLUMN show_leaderboard BOOLEAN DEFAULT TRUE")
        else:
            statements.append("ALTER TABLE live_quiz_sessions ALTER COLUMN show_leaderboard SET DEFAULT TRUE")

        if 'allow_join_after_start' not in existing_columns:
            statements.append("ALTER TABLE live_quiz_sessions ADD COLUMN allow_join_after_start BOOLEAN DEFAULT TRUE")
        else:
            statements.append("ALTER TABLE live_quiz_sessions ALTER COLUMN allow_join_after_start SET DEFAULT TRUE")

        if 'randomize_questions' not in existing_columns:
            statements.append("ALTER TABLE live_quiz_sessions ADD COLUMN randomize_questions BOOLEAN DEFAULT FALSE")
        else:
            statements.append("ALTER TABLE live_quiz_sessions ALTER COLUMN randomize_questions SET DEFAULT FALSE")

        if 'randomize_answers' not in existing_columns:
            statements.append("ALTER TABLE live_quiz_sessions ADD COLUMN randomize_answers BOOLEAN DEFAULT TRUE")
        else:
            statements.append("ALTER TABLE live_quiz_sessions ALTER COLUMN randomize_answers SET DEFAULT TRUE")

        # Metadata
        if 'created_by' not in existing_columns:
            statements.append("ALTER TABLE live_quiz_sessions ADD COLUMN created_by INTEGER NULL")
        if 'created_at' not in existing_columns:
            statements.append("ALTER TABLE live_quiz_sessions ADD COLUMN created_at TIMESTAMP DEFAULT NOW()")
        if 'updated_at' not in existing_columns:
            statements.append("ALTER TABLE live_quiz_sessions ADD COLUMN updated_at TIMESTAMP DEFAULT NOW()")

        for stmt in statements:
            db.session.execute(text(stmt))

        # Apply defaults for any existing rows so new code reads sensible values
        update_stmt = text(
            """
            UPDATE live_quiz_sessions
            SET
                current_question_index = COALESCE(current_question_index, 0),
                time_per_question = COALESCE(time_per_question, 30),
                show_leaderboard = COALESCE(show_leaderboard, TRUE),
                allow_join_after_start = COALESCE(allow_join_after_start, TRUE),
                randomize_questions = COALESCE(randomize_questions, FALSE),
                randomize_answers = COALESCE(randomize_answers, TRUE),
                created_at = COALESCE(created_at, NOW()),
                updated_at = COALESCE(updated_at, NOW())
            """
        )
        db.session.execute(update_stmt)

        db.session.commit()
        print("[OK] live_quiz_sessions table is aligned with the ORM model.")
        return True


def downgrade():
    """Downgrade by dropping newly added columns (if they exist)."""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        if LIVE_QUIZ_TABLE not in inspector.get_table_names():
            print(f"[WARNING] Table '{LIVE_QUIZ_TABLE}' does not exist; nothing to downgrade.")
            return True

        existing_columns = {column['name'] for column in inspector.get_columns(LIVE_QUIZ_TABLE)}

        drop_order = [
            'updated_at',
            'created_at',
            'created_by',
            'randomize_answers',
            'randomize_questions',
            'allow_join_after_start',
            'show_leaderboard',
            'time_per_question',
            'current_question_index',
            'ended_at',
            'started_at',
        ]

        for column in drop_order:
            if column in existing_columns:
                db.session.execute(text(f"ALTER TABLE live_quiz_sessions DROP COLUMN {column}"))

        db.session.commit()
        print("[OK] Downgrade completed, columns removed where present.")
        return True


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Update live quiz session columns migration')
    parser.add_argument('action', choices=['upgrade', 'downgrade'], help='Migration action to perform')

    args = parser.parse_args()

    if args.action == 'upgrade':
        upgrade()
    elif args.action == 'downgrade':
        downgrade()
