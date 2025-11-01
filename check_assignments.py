#!/usr/bin/env python
"""Quick script to check assignments in the database"""
from application import create_app
from __init__ import db
from instructor.models.class_content import ClassAssignment
from instructor.models.module import Module

app = create_app()
with app.app_context():
    # Check ClassAssignment table
    print("=" * 60)
    print("ClassAssignment Table (for deadlines)")
    print("=" * 60)
    assignments = ClassAssignment.query.filter_by(class_id=7).all()
    print(f'Total ClassAssignments: {len(assignments)}')
    for a in assignments:
        print(f'  - ID: {a.id}, Title: {a.title}, Published: {a.is_published}, Due: {a.due_date}')
    
    print("\n" + "=" * 60)
    print("Module Table (check for assignments)")
    print("=" * 60)
    modules = Module.query.filter_by(class_id=7).all()
    print(f'Total Modules for class 7: {len(modules)}')
    for m in modules:
        print(f'  - Module ID: {m.id}, Title: {m.title}')
        if hasattr(m, 'assignments'):
            try:
                count = m.assignments.count()
            except Exception:
                count = len(list(m.assignments))
            print(f'    Assignments: {count}')
