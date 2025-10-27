"""
Production Fix for Live Quiz - One-Step Solution
Automatically detects missing sessions and creates them
Safe to run multiple times (won't create duplicates)
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import create_app, db
from user.models.live_quiz import LiveQuizSession
from instructor.models.class_model import Class
from instructor.models.module import Module
from instructor.models.user import Instructor
from instructor.models.question_group import QuestionGroup
import random
import string

def generate_session_code():
    """Generate a unique 6-character session code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not LiveQuizSession.query.filter_by(session_code=code).first():
            return code

def fix_production_live_quiz():
    """
    One-step production fix:
    1. Check current session state
    2. Create missing sessions automatically
    3. Report what was done
    """
    
    app = create_app()
    with app.app_context():
        print("=" * 80)
        print("LIVE QUIZ PRODUCTION FIX - AUTOMATED REPAIR")
        print("=" * 80)
        print()
        
        # Get first instructor (or report error)
        instructor = Instructor.query.first()
        if not instructor:
            print("❌ CRITICAL: No instructor accounts found!")
            print("   You must create an instructor account first.")
            print("   Run: flask shell")
            print("   >>> from instructor.models.user import Instructor")
            print("   >>> # Create instructor...")
            return False
        
        print(f"✅ Using instructor: {instructor.username} (ID: {instructor.id})")
        print()
        
        # Get all active classes
        classes = Class.query.all()
        if not classes:
            print("❌ No classes found in database")
            return False
        
        print(f"📚 Found {len(classes)} classes")
        print()
        
        # Track what we do
        modules_checked = 0
        modules_with_sessions = 0
        modules_without_sessions = 0
        sessions_created = 0
        
        # Check each module
        for class_obj in classes:
            modules = Module.query.filter_by(
                class_id=class_obj.id, 
                is_active=True, 
                is_published=True
            ).all()
            
            if not modules:
                print(f"⚠️  Class '{class_obj.name}' has no published modules")
                continue
            
            print(f"🎓 Class: {class_obj.name} (ID: {class_obj.id})")
            
            for module in modules:
                modules_checked += 1
                
                # Check for existing active/waiting sessions
                existing_sessions = LiveQuizSession.query.filter_by(
                    class_id=class_obj.id,
                    module_id=module.id
                ).filter(
                    LiveQuizSession.status.in_(['active', 'waiting'])
                ).all()
                
                if existing_sessions:
                    modules_with_sessions += 1
                    print(f"   ✅ Module '{module.title}': {len(existing_sessions)} sessions exist")
                    for session in existing_sessions:
                        print(f"      - {session.title} ({session.status}) Code: {session.session_code}")
                else:
                    modules_without_sessions += 1
                    print(f"   ⚠️  Module '{module.title}': NO sessions found")
                    
                    # Try to find a question group for this class
                    question_groups = [qg for qg in class_obj.question_groups.all()]
                    
                    if not question_groups:
                        print(f"      ❌ Cannot create session: No question groups for this class")
                        continue
                    
                    # Use first question group
                    question_group = question_groups[0]
                    
                    # Create a waiting session
                    session_code = generate_session_code()
                    session = LiveQuizSession(
                        question_group_id=question_group.id,
                        class_id=class_obj.id,
                        module_id=module.id,
                        lesson_id=None,  # Module-level quiz
                        session_code=session_code,
                        title=f"{module.title} - Live Quiz",
                        time_per_question=30,
                        status='waiting',  # Create as waiting, instructor can start it
                        created_by=instructor.id,
                        show_leaderboard=True,
                        allow_join_after_start=True,
                        randomize_questions=False,
                        randomize_answers=True
                    )
                    
                    db.session.add(session)
                    sessions_created += 1
                    
                    print(f"      ✅ Created session: {session.title}")
                    print(f"         Code: {session_code} | Status: waiting")
                    print(f"         Question Group: {question_group.name}")
            
            print()
        
        # Commit all changes
        if sessions_created > 0:
            try:
                db.session.commit()
                print("=" * 80)
                print("✅ DATABASE UPDATED SUCCESSFULLY")
                print("=" * 80)
                print()
                print(f"📊 SUMMARY:")
                print(f"   - Modules checked: {modules_checked}")
                print(f"   - Modules with sessions: {modules_with_sessions}")
                print(f"   - Modules without sessions: {modules_without_sessions}")
                print(f"   - Sessions created: {sessions_created}")
                print()
                
                if sessions_created > 0:
                    print("🎉 SUCCESS! Live Quiz buttons should now appear on module pages.")
                    print()
                    print("📋 NEXT STEPS:")
                    print("   1. Restart your application:")
                    print("      sudo systemctl restart riddlenet")
                    print()
                    print("   2. Navigate to any module page as a student")
                    print("      You should see 'Live Quiz Starting Soon' button")
                    print()
                    print("   3. Instructors can start sessions via:")
                    print("      POST /instructor/api/live-quiz/<session_id>/start")
                    print()
                
                return True
                
            except Exception as e:
                db.session.rollback()
                print("=" * 80)
                print("❌ ERROR COMMITTING TO DATABASE")
                print("=" * 80)
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("=" * 80)
            print("ℹ️  NO CHANGES NEEDED")
            print("=" * 80)
            print()
            print("All modules already have active or waiting quiz sessions.")
            print("If the button is still not appearing, check:")
            print("   1. Browser console for JavaScript errors")
            print("   2. Server logs for query errors")
            print("   3. Database permissions")
            print()
            return True

if __name__ == '__main__':
    success = fix_production_live_quiz()
    sys.exit(0 if success else 1)
