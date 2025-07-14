"""
Simple script to add quiz questions to the database
This script creates sample quiz questions for Class 7 (Networking)
"""

from run import app
from admin.models.question import Question
from admin.models.question_group import QuestionGroup
from __init__ import db
import json

def add_quiz_questions():
    """Add sample quiz questions to the database"""
    with app.app_context():
        try:
            # Sample questions for networking quiz
            sample_questions = [
                {
                    "question": "What does OSI stand for in networking?",
                    "correct_answer": "Open Systems Interconnection",
                    "options": [
                        {"text": "Open Systems Interconnection", "correct": True},
                        {"text": "Optical Signal Interface", "correct": False},
                        {"text": "Operating System Integration", "correct": False},
                        {"text": "Open Source Implementation", "correct": False}
                    ]
                },
                {
                    "question": "Which layer of the OSI model is responsible for routing?",
                    "correct_answer": "Network Layer",
                    "options": [
                        {"text": "Physical Layer", "correct": False},
                        {"text": "Data Link Layer", "correct": False},
                        {"text": "Network Layer", "correct": True},
                        {"text": "Transport Layer", "correct": False}
                    ]
                },
                {
                    "question": "What is the default subnet mask for a Class C network?",
                    "correct_answer": "255.255.255.0",
                    "options": [
                        {"text": "255.0.0.0", "correct": False},
                        {"text": "255.255.0.0", "correct": False},
                        {"text": "255.255.255.0", "correct": True},
                        {"text": "255.255.255.255", "correct": False}
                    ]
                },
                {
                    "question": "Which protocol is used for web browsing?",
                    "correct_answer": "HTTP",
                    "options": [
                        {"text": "FTP", "correct": False},
                        {"text": "HTTP", "correct": True},
                        {"text": "SMTP", "correct": False},
                        {"text": "SNMP", "correct": False}
                    ]
                },
                {
                    "question": "What is the maximum data rate of Ethernet 10Base-T?",
                    "correct_answer": "10 Mbps",
                    "options": [
                        {"text": "10 Mbps", "correct": True},
                        {"text": "100 Mbps", "correct": False},
                        {"text": "1 Gbps", "correct": False},
                        {"text": "10 Gbps", "correct": False}
                    ]
                }
            ]
            
            # Get the current maximum question number
            max_numb = db.session.query(db.func.max(Question.numb)).scalar() or 0
            print(f"Current max question number: {max_numb}")
            
            created_count = 0
            for i, q_data in enumerate(sample_questions):
                # Check if question already exists
                existing_q = Question.query.filter_by(question=q_data["question"]).first()
                if existing_q:
                    print(f"⚠️  Question already exists: {q_data['question'][:50]}...")
                    continue
                
                # Create new question
                question = Question(
                    numb=max_numb + i + 1,
                    question=q_data["question"],
                    answer=q_data["correct_answer"],
                    question_type="multiple_choice",
                    options=q_data["options"],
                    category="networking",
                    explanation=f"Networking fundamentals question about {q_data['question'][:30]}..."
                )
                
                db.session.add(question)
                created_count += 1
                print(f"✅ Created question: {q_data['question'][:50]}...")
            
            # Commit all questions at once
            db.session.commit()
            print(f"\n🎉 Successfully created {created_count} quiz questions!")
            
            # Show total questions in database
            total_questions = Question.query.count()
            print(f"📊 Total questions in database: {total_questions}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating questions: {e}")
            return False

if __name__ == "__main__":
    success = add_quiz_questions()
    if success:
        print("\n✅ Quiz questions added successfully!")
        print("🎯 You can now test the quiz functionality in Class 7")
    else:
        print("\n❌ Failed to add quiz questions!")
