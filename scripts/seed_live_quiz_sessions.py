"""
Seed Live Quiz Sessions for Production/Testing
Creates live quiz sessions to ensure the Live Quiz UI is visible

USAGE:
    python scripts/seed_live_quiz_sessions.py              # Seed all modules with waiting sessions
    python scripts/seed_live_quiz_sessions.py --active     # Create one active session immediately
    python scripts/seed_live_quiz_sessions.py --clean      # Remove all test sessions first
    python scripts/seed_live_quiz_sessions.py --class 7    # Seed only specific class
    python scripts/seed_live_quiz_sessions.py --module 1   # Seed only specific module
"""

import sys
import os
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import create_app, db
from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant, LiveQuizResponse
from instructor.models.class_model import Class
from instructor.models.module import Module, Lesson
from instructor.models.question_group import QuestionGroup
from instructor.models.user import Instructor
import random
import string

def generate_session_code():
    """Generate a unique 6-character session code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not LiveQuizSession.query.filter_by(session_code=code).first():
            return code

def clean_test_sessions():
    """Remove all existing test sessions"""
    app = create_app()
    with app.app_context():
        print("=" * 80)
        print("CLEANING EXISTING SESSIONS")
        print("=" * 80)
        print()
        
        # Count before deletion
        total = LiveQuizSession.query.count()
        active_count = LiveQuizSession.query.filter_by(status='active').count()
        waiting_count = LiveQuizSession.query.filter_by(status='waiting').count()
        
        print(f"Found {total} total sessions:")
        print(f"  - Active: {active_count}")
        print(f"  - Waiting: {waiting_count}")
        print()
        
        if total == 0:
            print("✅ No sessions to clean")
            return
        
        # Confirm deletion
        confirm = input("⚠️  Delete all sessions? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cleanup cancelled")
            return
        
        try:
            # Delete all sessions (cascade will handle participants/responses)
            LiveQuizSession.query.delete()
            db.session.commit()
            print(f"✅ Deleted {total} sessions")
            print()
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deleting sessions: {e}")


def seed_live_quiz_sessions(class_id_filter=None, module_id_filter=None, status_override=None):
    """Create test live quiz sessions for modules
    
    Args:
        class_id_filter: Only seed sessions for this class ID
        module_id_filter: Only seed sessions for this module ID  
        status_override: Override default 'waiting' status with 'active'
    """
    
    app = create_app()
    with app.app_context():
        print("=" * 80)
        print("SEEDING LIVE QUIZ SESSIONS")
        print("=" * 80)
        print()
        
        # Get first instructor (or create one if none exists)
        instructor = Instructor.query.first()
        if not instructor:
            print("❌ No instructors found in database!")
            print("   Please create an instructor first.")
            return 0
        
        print(f"Using instructor: {instructor.username} (ID: {instructor.id})")
        print()
        
        # Get all classes (or filter to specific class)
        if class_id_filter:
            classes = [Class.query.get(class_id_filter)]
            if not classes[0]:
                print(f"❌ Class ID {class_id_filter} not found!")
                return 0
        else:
            classes = Class.query.all()
        
        if not classes:
            print("❌ No classes found in database!")
            return 0
        
        sessions_created = 0
        default_status = status_override or 'waiting'
        
        for class_obj in classes:
            print(f"\n📚 Class: {class_obj.name} (ID: {class_obj.id})")
            
            # Get modules for this class (or filter to specific module)
            if module_id_filter:
                modules = [Module.query.get(module_id_filter)]
                if not modules[0] or modules[0].class_id != class_obj.id:
                    continue
            else:
                modules = Module.query.filter_by(class_id=class_obj.id, is_active=True).all()
            
            if not modules:
                print("   ⚠️  No modules found for this class")
                continue
            
            for module in modules:
                print(f"  📖 Module: {module.title} (ID: {module.id})")
                
                # Get first lesson in module
                lesson = Lesson.query.filter_by(module_id=module.id, is_active=True).first()
                
                if not lesson:
                    print("     ⚠️  No lessons found - creating session without lesson_id")
                
                # Get a question group for this class
                question_groups = class_obj.question_groups.all() if hasattr(class_obj, 'question_groups') else []
                
                if not question_groups:
                    print("     ⚠️  No question groups found for this class - skipping")
                    continue
                
                question_group = question_groups[0]
                
                # Check if session already exists for this module
                existing_session = LiveQuizSession.query.filter_by(
                    class_id=class_obj.id,
                    module_id=module.id,
                    status=default_status
                ).first()
                
                if existing_session:
                    print(f"     ℹ️  Session already exists: {existing_session.title} (Code: {existing_session.session_code}, Status: {existing_session.status})")
                    continue
                
                # Create a session
                session_code = generate_session_code()
                session = LiveQuizSession(
                    question_group_id=question_group.id,
                    class_id=class_obj.id,
                    module_id=module.id,
                    lesson_id=lesson.id if lesson else None,
                    session_code=session_code,
                    title=f"{module.title} - Live Quiz",
                    time_per_question=30,
                    status=default_status,
                    created_by=instructor.id,
                    show_leaderboard=True,
                    allow_join_after_start=True,
                    randomize_questions=False,
                    randomize_answers=True
                )
                
                # If creating active session, set started_at
                if default_status == 'active':
                    session.started_at = datetime.utcnow()
                
                db.session.add(session)
                sessions_created += 1
                
                status_emoji = "🔴" if default_status == 'active' else "⏳"
                print(f"     ✅ Created session: {session.title}")
                print(f"        Code: {session_code}")
                print(f"        Status: {default_status} {status_emoji}")
                print(f"        Question Group: {question_group.name}")
                if lesson:
                    print(f"        Lesson: {lesson.title}")
        
        # Commit all changes
        try:
            db.session.commit()
            print()
            print("=" * 80)
            print(f"✅ Successfully created {sessions_created} live quiz sessions!")
            print("=" * 80)
            print()
            
            if sessions_created > 0:
                print("📋 NEXT STEPS:")
                print("   1. Restart the application to pick up changes")
                print("   2. Navigate to a module page as a student")
                
                if default_status == 'waiting':
                    print("   3. You should see the 'Live Quiz Starting Soon' button")
                    print("   4. Start sessions via: POST /instructor/api/live-quiz/<id>/start")
                elif default_status == 'active':
                    print("   3. You should see the 'Join Live Quiz Now!' button (pulsing)")
                    print("   4. Click to join immediately")
                print()
            else:
                print("ℹ️  No new sessions created (sessions may already exist)")
                print()
            
            return sessions_created
            
        except Exception as e:
            db.session.rollback()
            print()
            print(f"❌ Error committing sessions: {e}")
            import traceback
            traceback.print_exc()
            return 0

def seed_active_session(class_id=None, module_id=None):
    """Create one active session for immediate testing
    
    Args:
        class_id: Specific class ID to use
        module_id: Specific module ID to use
    """
    
    app = create_app()
    with app.app_context():
        print("=" * 80)
        print("CREATING ACTIVE LIVE QUIZ SESSION")
        print("=" * 80)
        print()
        
        # Get first instructor
        instructor = Instructor.query.first()
        if not instructor:
            print("❌ No instructors found!")
            return 0
        
        # Get target class
        if class_id:
            class_obj = Class.query.get(class_id)
        else:
            class_obj = Class.query.first()
            
        if not class_obj:
            print("❌ No classes found!")
            return 0
        
        # Get target module
        if module_id:
            module = Module.query.get(module_id)
            if not module or module.class_id != class_obj.id:
                print(f"❌ Module {module_id} not found in class {class_obj.id}!")
                return 0
        else:
            module = Module.query.filter_by(class_id=class_obj.id, is_active=True).first()
            
        if not module:
            print("❌ No modules found!")
            return 0
        
        lesson = Lesson.query.filter_by(module_id=module.id, is_active=True).first()
        
        question_groups = class_obj.question_groups.all() if hasattr(class_obj, 'question_groups') else []
        if not question_groups:
            print("❌ No question groups found!")
            return 0
        
        question_group = question_groups[0]
        
        session_code = generate_session_code()
        session = LiveQuizSession(
            question_group_id=question_group.id,
            class_id=class_obj.id,
            module_id=module.id,
            lesson_id=lesson.id if lesson else None,
            session_code=session_code,
            title=f"ACTIVE TEST QUIZ - {module.title}",
            time_per_question=30,
            status='active',  # Create as active immediately
            created_by=instructor.id,
            started_at=datetime.utcnow(),
            show_leaderboard=True,
            allow_join_after_start=True,
            randomize_questions=False,
            randomize_answers=True
        )
        
        db.session.add(session)
        
        try:
            db.session.commit()
            print(f"✅ Created ACTIVE session!")
            print(f"   Title: {session.title}")
            print(f"   Code: {session_code}")
            print(f"   Class: {class_obj.name} (ID: {class_obj.id})")
            print(f"   Module: {module.title} (ID: {module.id})")
            if lesson:
                print(f"   Lesson: {lesson.title} (ID: {lesson.id})")
            print(f"   Status: ACTIVE 🔴")
            print()
            print("🎉 The Live Quiz button should now appear immediately!")
            print(f"   Navigate to: /class/{class_obj.id}/module/{module.id}")
            print()
            return 1
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Seed Live Quiz sessions for production/testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scripts/seed_live_quiz_sessions.py                    # Seed all modules
  python scripts/seed_live_quiz_sessions.py --active           # Create one active session
  python scripts/seed_live_quiz_sessions.py --clean            # Clean all sessions first
  python scripts/seed_live_quiz_sessions.py --class 7          # Seed only class 7
  python scripts/seed_live_quiz_sessions.py --module 1         # Seed only module 1
  python scripts/seed_live_quiz_sessions.py --class 7 --active # Active session for class 7
        '''
    )
    
    parser.add_argument('--active', action='store_true',
                        help='Create one active session instead of seeding all')
    parser.add_argument('--clean', action='store_true',
                        help='Remove all existing sessions first')
    parser.add_argument('--class', type=int, dest='class_id',
                        help='Only seed sessions for specific class ID')
    parser.add_argument('--module', type=int, dest='module_id',
                        help='Only seed sessions for specific module ID')
    parser.add_argument('--status', choices=['waiting', 'active'],
                        help='Override default status (default: waiting)')
    
    args = parser.parse_args()
    
    # Clean existing sessions if requested
    if args.clean:
        clean_test_sessions()
    
    # Create sessions
    if args.active:
        seed_active_session(class_id=args.class_id, module_id=args.module_id)
    else:
        seed_live_quiz_sessions(
            class_id_filter=args.class_id,
            module_id_filter=args.module_id,
            status_override=args.status
        )
