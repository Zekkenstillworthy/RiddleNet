#!/usr/bin/env python3
"""
Setup sample quiz questions for testing the quiz system
"""

import os
import sys
import json

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from admin.models.question import Question
from admin.models.question_group import QuestionGroup
from admin.models.class_model import Class
from run import db, app

def setup_sample_quiz():
    """Setup sample quiz questions for Class 7 (Networking 1)"""
    
    with app.app_context():
        # Get or create Class 7
        class_7 = Class.query.get(7)
        if not class_7:
            print("Class 7 not found. Creating it...")
            class_7 = Class(
                id=7,
                name="Networking 1",
                description="Introduction to computer networking concepts",
                class_code="NET101"
            )
            db.session.add(class_7)
            db.session.commit()
            print("✅ Class 7 created")
        
        # Create a question group for this class
        existing_group = QuestionGroup.query.filter_by(name="Networking Fundamentals").first()
        if existing_group:
            print("✅ Question group already exists")
            question_group = existing_group
        else:
            question_group = QuestionGroup(
                name="Networking Fundamentals",
                description="Basic networking concepts and terminology"
            )
            db.session.add(question_group)
            db.session.commit()
            print("✅ Question group created")
        
        # Sample networking questions
        sample_questions = [
            {
                "question": "What does OSI stand for in networking?",
                "type": "multiple_choice",
                "options": [
                    {"text": "Open Systems Interconnection", "correct": True},
                    {"text": "Optical Signal Interface", "correct": False},
                    {"text": "Operating System Integration", "correct": False},
                    {"text": "Open Source Implementation", "correct": False}
                ],
                "difficulty": "easy"
            },
            {
                "question": "How many layers are in the OSI model?",
                "type": "multiple_choice",
                "options": [
                    {"text": "5", "correct": False},
                    {"text": "6", "correct": False},
                    {"text": "7", "correct": True},
                    {"text": "8", "correct": False}
                ],
                "difficulty": "easy"
            },
            {
                "question": "Which layer of the OSI model is responsible for routing?",
                "type": "multiple_choice",
                "options": [
                    {"text": "Physical Layer", "correct": False},
                    {"text": "Data Link Layer", "correct": False},
                    {"text": "Network Layer", "correct": True},
                    {"text": "Transport Layer", "correct": False}
                ],
                "difficulty": "medium"
            },
            {
                "question": "What is the default subnet mask for a Class C network?",
                "type": "multiple_choice",
                "options": [
                    {"text": "255.0.0.0", "correct": False},
                    {"text": "255.255.0.0", "correct": False},
                    {"text": "255.255.255.0", "correct": True},
                    {"text": "255.255.255.255", "correct": False}
                ],
                "difficulty": "medium"
            },
            {
                "question": "Which protocol operates at the Transport layer?",
                "type": "multiple_choice",
                "options": [
                    {"text": "HTTP", "correct": False},
                    {"text": "IP", "correct": False},
                    {"text": "TCP", "correct": True},
                    {"text": "Ethernet", "correct": False}
                ],
                "difficulty": "medium"
            },
            {
                "question": "What does DHCP stand for?",
                "type": "multiple_choice",
                "options": [
                    {"text": "Dynamic Host Configuration Protocol", "correct": True},
                    {"text": "Direct Hardware Communication Protocol", "correct": False},
                    {"text": "Distributed Host Control Protocol", "correct": False},
                    {"text": "Digital Hardware Configuration Process", "correct": False}
                ],
                "difficulty": "easy"
            },
            {
                "question": "Which topology connects all devices to a central hub?",
                "type": "multiple_choice",
                "options": [
                    {"text": "Bus", "correct": False},
                    {"text": "Ring", "correct": False},
                    {"text": "Star", "correct": True},
                    {"text": "Mesh", "correct": False}
                ],
                "difficulty": "easy"
            },
            {
                "question": "What is the maximum data rate of Ethernet 10Base-T?",
                "type": "multiple_choice",
                "options": [
                    {"text": "10 Mbps", "correct": True},
                    {"text": "100 Mbps", "correct": False},
                    {"text": "1 Gbps", "correct": False},
                    {"text": "10 Gbps", "correct": False}
                ],
                "difficulty": "medium"
            },
            {
                "question": "Which cable type is most commonly used for Ethernet connections?",
                "type": "multiple_choice",
                "options": [
                    {"text": "Coaxial", "correct": False},
                    {"text": "Fiber Optic", "correct": False},
                    {"text": "Twisted Pair", "correct": True},
                    {"text": "Parallel", "correct": False}
                ],
                "difficulty": "easy"
            },
            {
                "question": "What does NAT stand for in networking?",
                "type": "multiple_choice",
                "options": [
                    {"text": "Network Access Translation", "correct": False},
                    {"text": "Network Address Translation", "correct": True},
                    {"text": "Network Application Transfer", "correct": False},
                    {"text": "Network Authentication Token", "correct": False}
                ],
                "difficulty": "medium"
            }
        ]
        
        # Create questions
        created_count = 0
        for q_data in sample_questions:
            # Check if question already exists
            existing_q = Question.query.filter_by(question=q_data["question"]).first()
            if existing_q:
                print(f"⚠️  Question already exists: {q_data['question'][:50]}...")
                continue
            
            # Find the correct answer from options
            correct_answer = None
            for option in q_data["options"]:
                if option["correct"]:
                    correct_answer = option["text"]
                    break
            
            if not correct_answer:
                print(f"⚠️  No correct answer found for: {q_data['question'][:50]}...")
                continue
            
            # Get the next question number
            max_numb = db.session.query(db.func.max(Question.numb)).scalar() or 0
            
            question = Question(
                numb=max_numb + 1,
                question=q_data["question"],
                answer=correct_answer,
                question_type=q_data["type"],
                options=q_data["options"],
                category="networking",
                explanation=f"This is a {q_data.get('difficulty', 'medium')} level networking question."
            )
            db.session.add(question)
            db.session.flush()  # Get the question ID
            
            # Add question to the group
            question_group.questions.append(question)
            created_count += 1
        
        db.session.commit()
        
        print(f"✅ Created {created_count} new questions")
        print(f"✅ Total questions in group: {len(question_group.questions)}")
        print(f"✅ Quiz setup complete for Class 7!")
        
        return True

if __name__ == "__main__":
    success = setup_sample_quiz()
    if success:
        print("\n🎉 Sample quiz setup completed successfully!")
        print("You can now test the quiz functionality in Class 7")
    else:
        print("\n❌ Setup failed!")
