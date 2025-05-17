import sys
import os
from __init__ import create_app, db
from admin.models.class_model import Class

app = create_app()

# Create an application context
with app.app_context():
    try:
        # Try to get class with ID 4
        test_class = Class.query.get(4)
        if test_class:
            print(f"Class {test_class.name} has {len(test_class.students)} students")
            print("Class ID 4 details successfully retrieved!")
            
            # Print student information
            for i, student in enumerate(test_class.students):
                print(f"Student {i+1}: {student.username} (ID: {student.id})")
                
            # Test the to_dict method works
            class_dict = test_class.to_dict()
            print(f"Class dictionary has {len(class_dict)} fields")
            print(f"Student count in dict: {class_dict.get('studentCount')}")
            
        else:
            print("Class with ID 4 not found")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
