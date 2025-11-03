"""
Utility for synchronizing PostgreSQL sequences with actual table data.
Prevents duplicate key violations when sequences fall behind.
"""

from sqlalchemy import text
from __init__ import db


def sync_sequence(table_name: str, id_column: str = 'id') -> bool:
    """Synchronize PostgreSQL sequence for a table with the actual max ID.

    Args:
        table_name: Name of the table (e.g., 'simulation_assignments', 'modules')
        id_column: Name of the ID column (defaults to 'id')

    Returns:
        bool: True if sequence was synced successfully, False otherwise
    """
    try:
        # Get the maximum ID value from the table
        max_id_result = db.session.execute(
            text(f"SELECT COALESCE(MAX({id_column}), 0) FROM {table_name}")
        )
        max_id = max_id_result.scalar_one() or 0
        next_val = max_id if max_id > 0 else 1
        
        print(f"[FIX] Syncing sequence for {table_name}.{id_column} -> max_id={max_id}, setval={next_val}")

        # Get the sequence name for the table and column
        seq_name_result = db.session.execute(
            text(f"SELECT pg_get_serial_sequence('{table_name}', '{id_column}')")
        )
        seq_name = seq_name_result.scalar_one()
        
        if not seq_name:
            print(f"[WARNING]  No sequence found for {table_name}.{id_column}")
            return False
            
        print(f"[FIX] Resolved sequence name: {seq_name}")

        # Set the sequence value to the next safe value
        db.session.execute(
            text("SELECT setval(:seq, :val, true)"), 
            {"seq": seq_name, "val": next_val}
        )
        db.session.commit()
        
        print(f"[OK] Sequence synced successfully for {table_name}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to sync sequence for {table_name}: {e}")
        db.session.rollback()
        try:
            # Fallback: try to use ALTER SEQUENCE
            print(f"[REFRESH] Attempting ALTER SEQUENCE fallback for {table_name}")
            sequence_name = f"{table_name}_{id_column}_seq"
            db.session.execute(
                text(f"ALTER SEQUENCE {sequence_name} RESTART WITH {next_val + 1}")
            )
            db.session.commit()
            print(f"[OK] Sequence synced using ALTER SEQUENCE for {table_name}")
            return True
        except Exception as e2:
            print(f"[ERROR] ALTER SEQUENCE fallback also failed for {table_name}: {e2}")
            db.session.rollback()
            return False


def commit_with_sequence_retry(table_name: str, id_column: str = 'id', max_retries: int = 2):
    """Commit with automatic sequence synchronization on IntegrityError.
    
    Args:
        table_name: Name of the table that might have sequence issues
        id_column: Name of the ID column (defaults to 'id')
        max_retries: Maximum number of retry attempts
    """
    from sqlalchemy.exc import IntegrityError
    
    for attempt in range(max_retries + 1):
        try:
            db.session.commit()
            return  # Success!
        except IntegrityError as e:
            if 'duplicate key' in str(e).lower() and attempt < max_retries:
                print(f"[REFRESH] IntegrityError detected, syncing sequence for {table_name} (attempt {attempt + 1}/{max_retries + 1})")
                db.session.rollback()
                if sync_sequence(table_name, id_column):
                    continue  # Try commit again
            # If we can't fix it or max retries reached, re-raise
            raise e
