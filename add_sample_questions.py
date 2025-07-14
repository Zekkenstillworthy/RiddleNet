#!/usr/bin/env python3
"""
Add sample questions to Quiz 1 for testing
"""

from run import app
from admin.models.question_group import QuestionGroup
from admin.models.question import Question
from admin import db

def add_sample_questions():
    with app.app_context():
        # Get Quiz 1
        quiz_1 = QuestionGroup.query.get(1)
        if not quiz_1:
            print("Quiz 1 not found!")
            return
            
        # Check if questions already exist
        if hasattr(quiz_1, 'questions') and quiz_1.questions:
            print(f"Quiz 1 already has {len(quiz_1.questions)} questions")
            return
            
        # Create sample networking questions
        sample_questions = [
            {
                'question': 'Which layer of the OSI model is responsible for routing?',
                'options': ['Physical', 'Data Link', 'Network', 'Transport'],
                'correct_answer': 'Network',
                'explanation': 'The Network layer (Layer 3) is responsible for routing packets between different networks.',
                'category': 'OSI Model',
                'type': 'multiple_choice'
            },
            {
                'question': 'What is the default subnet mask for a Class C network?',
                'options': ['255.0.0.0', '255.255.0.0', '255.255.255.0', '255.255.255.255'],
                'correct_answer': '255.255.255.0',
                'explanation': 'Class C networks use a /24 subnet mask, which is 255.255.255.0.',
                'category': 'IP Addressing',
                'type': 'multiple_choice'
            },
            {
                'question': 'Which protocol operates at the Transport layer?',
                'options': ['HTTP', 'TCP', 'IP', 'Ethernet'],
                'correct_answer': 'TCP',
                'explanation': 'TCP (Transmission Control Protocol) operates at the Transport layer (Layer 4).',
                'category': 'Protocols',
                'type': 'multiple_choice'
            },
            {
                'question': 'What does MAC stand for in networking?',
                'options': ['Media Access Control', 'Multiple Access Control', 'Machine Access Code', 'Memory Access Controller'],
                'correct_answer': 'Media Access Control',
                'explanation': 'MAC stands for Media Access Control, which is used for hardware addressing.',
                'category': 'Hardware',
                'type': 'multiple_choice'
            },
            {
                'question': 'Which port number is commonly used for HTTP?',
                'options': ['21', '23', '80', '443'],
                'correct_answer': '80',
                'explanation': 'HTTP commonly uses port 80, while HTTPS uses port 443.',
                'category': 'Ports',
                'type': 'multiple_choice'
            }
        ]
        
        created_questions = []
        
        for i, q_data in enumerate(sample_questions, 1):
            # Create new question
            question = Question(
                numb=i,
                question=q_data['question'],
                answer=q_data['correct_answer'],
                explanation=q_data['explanation'],
                category=q_data['category'],
                question_type=q_data['type']
            )
            
            # Set options using the property setter
            question.options = q_data['options']
            
            db.session.add(question)
            created_questions.append(question)
            
        try:
            # Commit questions first
            db.session.commit()
            print(f"Created {len(created_questions)} questions")
            
            # Add questions to the quiz group
            for question in created_questions:
                quiz_1.questions.append(question)
            
            # Commit the associations
            db.session.commit()
            print(f"Successfully added {len(created_questions)} questions to Quiz 1")
            
            # Verify
            print(f"Quiz 1 now has {len(quiz_1.questions)} questions:")
            for i, q in enumerate(quiz_1.questions, 1):
                print(f"  {i}. {q.question[:60]}...")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error adding questions: {e}")

if __name__ == "__main__":
    add_sample_questions()
