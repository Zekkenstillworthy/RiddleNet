#!/usr/bin/env python3
"""Quick script to check students in class 7"""

from application import create_app
from admin.models.class_model import Class

def check_class_students():
    app = create_app()
    with app.app_context():
        cls = Class.query.get(7)
        if cls:
            print(f"Class: {cls.name}")
            print(f"Students count: {cls.students.count()}")
            students = cls.students.all()
            if students:
                print("Students:")
                for student in students:
                    print(f"  - ID: {student.id}, Username: {student.username}, Email: {getattr(student, 'email', 'N/A')}")
            else:
                print("No students enrolled in this class")
        else:
            print("Class 7 not found")

if __name__ == "__main__":
    check_class_students()