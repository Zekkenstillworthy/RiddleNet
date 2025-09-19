#!/usr/bin/env python3
"""
Check students in class 7 and their relationships
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app, db
from admin.models.class_model import Class, class_students
from user.models.user import User

def check_class_7_students():
    app = create_app()
    
    with app.app_context():
        try:
            # Get class 7
            class_7 = Class.query.get(7)
            if not class_7:
                print("❌ Class 7 not found!")
                return
            
            print(f"✅ Found Class 7: {class_7.name} ({class_7.code})")
            print(f"   Description: {class_7.description}")
            print(f"   Status: {class_7.status}")
            print(f"   Created by: {class_7.created_by}")
            print(f"   Max students: {class_7.max_students}")
            
            # Check students using the relationship
            print(f"\n🔍 Checking students using class.students relationship:")
            students_via_relationship = class_7.students.all()
            print(f"   Students count via relationship: {len(students_via_relationship)}")
            
            for student in students_via_relationship:
                print(f"   - Student: {student.username} ({student.first_name} {student.last_name})")
                print(f"     Email: {student.email}")
                print(f"     ID: {student.id}")
            
            # Check students using raw query
            print(f"\n🔍 Checking students using raw query on class_students table:")
            raw_query = db.session.query(class_students).filter(class_students.c.class_id == 7).all()
            print(f"   Students count via raw query: {len(raw_query)}")
            
            for row in raw_query:
                user = User.query.get(row.user_id)
                if user:
                    print(f"   - Student: {user.username} ({user.first_name} {user.last_name})")
                    print(f"     Email: {user.email}")
                    print(f"     User ID: {user.id}")
                    print(f"     Join Date: {row.joined_date}")
                    print(f"     Status: {row.status}")
                else:
                    print(f"   - User ID {row.user_id} not found in users table!")
            
            # Check class.students.count()
            print(f"\n🔍 class_7.students.count(): {class_7.students.count()}")
            
            # Check if there are any users at all
            print(f"\n🔍 Total users in database: {User.query.count()}")
            
            # Check if there are any class-student relationships at all
            print(f"🔍 Total class-student relationships: {db.session.query(class_students).count()}")
            
            # Check all classes and their student counts
            print(f"\n🔍 All classes and their student counts:")
            all_classes = Class.query.all()
            for cls in all_classes:
                student_count = cls.students.count()
                print(f"   Class {cls.id} ({cls.name}): {student_count} students")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_class_7_students()