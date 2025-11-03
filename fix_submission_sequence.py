"""
Fix assignment_submissions sequence to prevent duplicate key violations
"""
from application import application
from __init__ import db

with application.app_context():
    try:
        # Fix the sequence by setting it to MAX(id) + 1
        result = db.session.execute(db.text("""
            SELECT setval('assignment_submissions_id_seq', 
                         COALESCE((SELECT MAX(id) FROM assignment_submissions), 0) + 1, 
                         false);
        """))
        
        new_sequence = result.scalar()
        print(f"✅ Sequence fixed! Next value will be: {new_sequence}")
        
        # Verify the fix
        max_id_result = db.session.execute(db.text("SELECT MAX(id) FROM assignment_submissions"))
        max_id = max_id_result.scalar() or 0
        
        sequence_result = db.session.execute(db.text("SELECT last_value FROM assignment_submissions_id_seq"))
        sequence_val = sequence_result.scalar()
        
        print(f"\nVerification:")
        print(f"  Max ID in table: {max_id}")
        print(f"  Sequence value: {sequence_val}")
        
        if sequence_val > max_id:
            print(f"  ✅ Sequence is now ahead of max ID - safe to insert!")
        else:
            print(f"  ⚠️ Issue still exists!")
        
        db.session.commit()
        
    except Exception as e:
        print(f"❌ Error fixing sequence: {e}")
        db.session.rollback()
