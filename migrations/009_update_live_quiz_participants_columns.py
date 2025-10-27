"""
Migration: Align live quiz participant table with ORM model fields.

This migration renames legacy columns, adds any missing fields, and ensures
sensible defaults so the backend can load participant records without
UndefinedColumn errors.

Run with:  python migrations/009_update_live_quiz_participants_columns.py upgrade
"""
import os
import sys

# Allow importing the application factory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import inspect, text

from __init__ import create_app, db


PARTICIPANT_TABLE = 'live_quiz_participants'


def upgrade():
    """Rename legacy columns and add any missing participant fields."""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        if PARTICIPANT_TABLE not in inspector.get_table_names():
            print(f"[ERROR] Table '{PARTICIPANT_TABLE}' does not exist; aborting upgrade.")
            return False

        existing_columns = {column['name'] for column in inspector.get_columns(PARTICIPANT_TABLE)}

        # Rename columns if the legacy name exists and the new name is absent
        rename_pairs = {
            'username': 'display_name',
            'correct_answers': 'total_correct',
            'total_questions_answered': 'total_answered',
            'current_rank': 'rank',
        }

        renamed = False
        for old_name, new_name in rename_pairs.items():
            if old_name in existing_columns and new_name not in existing_columns:
                db.session.execute(text(f"ALTER TABLE {PARTICIPANT_TABLE} RENAME COLUMN {old_name} TO {new_name}"))
                existing_columns.remove(old_name)
                existing_columns.add(new_name)
                renamed = True
                print(f"🔁 Renamed column {old_name} -> {new_name}")

        if renamed:
            db.session.commit()
            inspector = inspect(db.engine)
            existing_columns = {column['name'] for column in inspector.get_columns(PARTICIPANT_TABLE)}

        # Add columns introduced by the ORM model when missing
        add_statements = []
        if 'average_response_time' not in existing_columns:
            add_statements.append(
                "ALTER TABLE live_quiz_participants ADD COLUMN average_response_time DOUBLE PRECISION DEFAULT 0"
            )
        if 'total_time' not in existing_columns:
            add_statements.append(
                "ALTER TABLE live_quiz_participants ADD COLUMN total_time DOUBLE PRECISION DEFAULT 0"
            )
        if 'completed_at' not in existing_columns:
            add_statements.append(
                "ALTER TABLE live_quiz_participants ADD COLUMN completed_at TIMESTAMP NULL"
            )

        for stmt in add_statements:
            db.session.execute(text(stmt))

        # Ensure sensible defaults for numeric columns used by the ORM
        default_statements = [
            "ALTER TABLE live_quiz_participants ALTER COLUMN total_score SET DEFAULT 0",
            "ALTER TABLE live_quiz_participants ALTER COLUMN total_correct SET DEFAULT 0",
            "ALTER TABLE live_quiz_participants ALTER COLUMN total_answered SET DEFAULT 0",
            "ALTER TABLE live_quiz_participants ALTER COLUMN is_active SET DEFAULT TRUE",
            "ALTER TABLE live_quiz_participants ALTER COLUMN average_response_time SET DEFAULT 0",
            "ALTER TABLE live_quiz_participants ALTER COLUMN total_time SET DEFAULT 0",
        ]

        for stmt in default_statements:
            db.session.execute(text(stmt))

        # Backfill NULL values so NOT NULL constraints can be applied safely
        backfill_stmt = text(
            """
            UPDATE live_quiz_participants
            SET
                display_name = COALESCE(display_name, 'Participant'),
                total_score = COALESCE(total_score, 0),
                total_correct = COALESCE(total_correct, 0),
                total_answered = COALESCE(total_answered, 0),
                average_response_time = COALESCE(average_response_time, 0),
                total_time = COALESCE(total_time, 0),
                is_active = COALESCE(is_active, TRUE)
            """
        )
        db.session.execute(backfill_stmt)

        # Enforce NOT NULL constraints expected by the ORM
        not_null_statements = [
            "ALTER TABLE live_quiz_participants ALTER COLUMN session_id SET NOT NULL",
            "ALTER TABLE live_quiz_participants ALTER COLUMN user_id SET NOT NULL",
            "ALTER TABLE live_quiz_participants ALTER COLUMN display_name SET NOT NULL",
        ]

        for stmt in not_null_statements:
            db.session.execute(text(stmt))

        db.session.commit()
        print("[OK] live_quiz_participants table aligned with ORM model.")
        return True


def downgrade():
    """Attempt to revert the participant table changes."""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        if PARTICIPANT_TABLE not in inspector.get_table_names():
            print(f"[WARNING] Table '{PARTICIPANT_TABLE}' does not exist; nothing to downgrade.")
            return True

        existing_columns = {column['name'] for column in inspector.get_columns(PARTICIPANT_TABLE)}

        rename_pairs = {
            'display_name': 'username',
            'total_correct': 'correct_answers',
            'total_answered': 'total_questions_answered',
            'rank': 'current_rank',
        }

        # Drop NOT NULL constraints to match legacy schema
        drop_not_null = [
            "ALTER TABLE live_quiz_participants ALTER COLUMN session_id DROP NOT NULL",
            "ALTER TABLE live_quiz_participants ALTER COLUMN user_id DROP NOT NULL",
            "ALTER TABLE live_quiz_participants ALTER COLUMN display_name DROP NOT NULL",
        ]
        for stmt in drop_not_null:
            db.session.execute(text(stmt))

        # Remove added columns when present
        drop_columns = []
        if 'average_response_time' in existing_columns:
            drop_columns.append("ALTER TABLE live_quiz_participants DROP COLUMN average_response_time")
        if 'total_time' in existing_columns:
            drop_columns.append("ALTER TABLE live_quiz_participants DROP COLUMN total_time")
        if 'completed_at' in existing_columns:
            drop_columns.append("ALTER TABLE live_quiz_participants DROP COLUMN completed_at")

        for stmt in drop_columns:
            db.session.execute(text(stmt))

        # Rename columns back to their legacy names when applicable
        for new_name, old_name in rename_pairs.items():
            if new_name in existing_columns:
                db.session.execute(text(f"ALTER TABLE {PARTICIPANT_TABLE} RENAME COLUMN {new_name} TO {old_name}"))

        db.session.commit()
        print("[OK] Downgrade completed for live_quiz_participants table.")
        return True


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Update live quiz participant columns migration')
    parser.add_argument('action', choices=['upgrade', 'downgrade'], help='Migration action to perform')

    args = parser.parse_args()

    if args.action == 'upgrade':
        upgrade()
    elif args.action == 'downgrade':
        downgrade()
