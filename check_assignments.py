"""Check which assignments exist in the database."""

from application import create_app
from instructor.models.class_content import ClassAssignment

app = create_app()

with app.app_context():
    assignments = ClassAssignment.query.order_by(ClassAssignment.id).all()
    
    if not assignments:
        print("❌ No assignments found in the database!")
    else:
        print(f"✅ Found {len(assignments)} assignment(s):\n")
        for assignment in assignments:
            print(f"  ID: {assignment.id}")
            print(f"  Title: {assignment.title}")
            print(f"  Class ID: {assignment.class_id}")
            print(f"  Module ID: {assignment.module_id if hasattr(assignment, 'module_id') else 'N/A'}")
            print(f"  Due Date: {assignment.due_date if hasattr(assignment, 'due_date') else 'N/A'}")
            print(f"  {'-' * 50}")
