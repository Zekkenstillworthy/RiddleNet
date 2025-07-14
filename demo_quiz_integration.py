#!/usr/bin/env python3
"""
Demo script to showcase the quiz integration in classes
"""

from run import app
from admin.models.question_group import QuestionGroup
from admin.models.class_model import Class
from admin.models.question import Question
from user.models.user import User
from admin import db

def demo_quiz_integration():
    """Demonstrate the quiz integration"""
    with app.app_context():
        print("🎯 RiddleNet Quiz Integration Demo")
        print("=" * 50)
        
        # Show classes and their quizzes
        classes = Class.query.all()
        for cls in classes:
            print(f"\n📚 Class: {cls.name} (ID: {cls.id})")
            print(f"   Code: {cls.code}")
            print(f"   Question Groups: {cls.question_groups.count()}")
            
            for qg in cls.question_groups:
                print(f"   └── 📝 {qg.name}")
                print(f"       ├── Questions: {len(qg.questions)}")
                print(f"       ├── Description: {qg.description or 'N/A'}")
                print(f"       └── Route: /class/{cls.id}/assessment/{qg.id}")
                
                # Show sample questions
                for i, q in enumerate(qg.questions[:2], 1):
                    print(f"           Question {i}: {q.question[:50]}...")
        
        print("\n🌐 Available Endpoints:")
        print("   • /class/7/ - Class 7 Portal (with Assessment tab)")
        print("   • /class/9/ - Class 9 Portal (with Assessment tab)")
        print("   • /class/7/api/assessments - Quiz data API")
        print("   • /class/7/assessment/1 - Quiz interface")
        print("   • /class/9/assessment/1 - Quiz interface")
        
        print("\n✨ Features Integrated:")
        print("   ✅ Assessment tab in class navigation")
        print("   ✅ Quiz cards with metadata (questions, time)")
        print("   ✅ Click-to-start quiz functionality")
        print("   ✅ API endpoints for dynamic loading")
        print("   ✅ Quiz interface template")
        print("   ✅ Progress tracking integration")
        
        print("\n🎮 How to Test:")
        print("   1. Visit http://localhost:5001/class/7")
        print("   2. Click 'Assessments' tab in sidebar")
        print("   3. Click 'Start Assessment' on any quiz")
        print("   4. Quiz interface will load with questions")
        
        print("\n🔧 Technical Implementation:")
        print("   • Class templates: templates/user/classes/")
        print("   • Route files: user/routes/generated/")
        print("   • Quiz interface: templates/user/quiz_interface.html")
        print("   • Backend: QuestionGroup model with Class relationship")

if __name__ == "__main__":
    demo_quiz_integration()
