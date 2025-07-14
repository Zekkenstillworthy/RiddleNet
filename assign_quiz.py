#!/usr/bin/env python3
"""
Assign question group 1 to class 7
"""

from run import app
from admin.models.question_group import QuestionGroup
from admin.models.class_model import Class
from admin import db

def assign_quiz_to_class():
    with app.app_context():
        # Get class 7 and question group 1
        class_7 = Class.query.get(7)
        quiz_1 = QuestionGroup.query.get(1)
        
        if not class_7:
            print("Class 7 not found!")
            return
            
        if not quiz_1:
            print("Question group 1 not found!")
            return
            
        # Check if already assigned
        if quiz_1 in class_7.question_groups:
            print("Quiz 1 is already assigned to Class 7")
            return
            
        # Assign the question group to the class
        class_7.question_groups.append(quiz_1)
        
        try:
            db.session.commit()
            print(f"Successfully assigned '{quiz_1.name}' to '{class_7.name}'")
            
            # Verify the assignment
            print(f"Class 7 now has {class_7.question_groups.count()} question groups:")
            for qg in class_7.question_groups:
                print(f"  - {qg.name} (ID: {qg.id})")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error assigning quiz to class: {e}")

if __name__ == "__main__":
    assign_quiz_to_class()
