#!/usr/bin/env python3
"""
Check assessments for class 7
"""

from run import app
from admin.models.question_group import QuestionGroup
from admin.models.class_model import Class

def check_assessments():
    with app.app_context():
        # Get class 7
        class_7 = Class.query.get(7)
        if not class_7:
            print("Class 7 not found!")
            return
            
        print(f"Class 7: {class_7.name} ({class_7.code})")
        print("Question groups for class 7:")
        
        qgs = class_7.question_groups.all()
        for qg in qgs:
            print(f"ID: {qg.id}, Name: {qg.name}")
            if hasattr(qg, 'questions'):
                print(f"  Questions: {len(qg.questions) if qg.questions else 0}")
        
        print(f"\nTotal question groups: {len(qgs)}")
        
        # Also check all question groups in the system
        print("\nAll question groups in system:")
        all_qgs = QuestionGroup.query.all()
        for qg in all_qgs:
            print(f"ID: {qg.id}, Name: {qg.name}, Classes: {[c.name for c in qg.classes]}")

if __name__ == "__main__":
    check_assessments()
