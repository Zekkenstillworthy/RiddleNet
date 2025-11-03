"""
Check assignment_submissions table for sequence issues
"""
from application import application
from __init__ import db
from instructor.models.assignment_submission import AssignmentSubmission

with application.app_context():
    # Check max ID
    max_id = db.session.query(db.func.max(AssignmentSubmission.id)).scalar()
    print(f"Max ID in assignment_submissions: {max_id}")
    
    # Check if there are any submissions
    count = AssignmentSubmission.query.count()
    print(f"Total submissions: {count}")
    
    # Check for duplicates or specific ID issues
    if count > 0:
        submissions = AssignmentSubmission.query.order_by(AssignmentSubmission.id.desc()).limit(5).all()
        print("\nLast 5 submissions:")
        for sub in submissions:
            print(f"  ID: {sub.id}, Assignment: {sub.assignment_id}, Student: {sub.student_id}, Status: {sub.status}")
    
    # Check sequence value (PostgreSQL specific)
    try:
        result = db.session.execute(db.text("SELECT last_value FROM assignment_submissions_id_seq"))
        sequence_val = result.scalar()
        print(f"\nSequence last_value: {sequence_val}")
        
        if max_id and sequence_val <= max_id:
            print(f"⚠️ SEQUENCE ISSUE: Sequence ({sequence_val}) <= Max ID ({max_id})")
            print(f"   This will cause duplicate key violations!")
            print(f"\n   Fix command:")
            print(f"   SELECT setval('assignment_submissions_id_seq', (SELECT MAX(id) FROM assignment_submissions));")
    except Exception as e:
        print(f"Could not check sequence: {e}")
