"""
Check Live Quiz Sessions in Database
Diagnostic script to verify live quiz sessions exist and their current status
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import create_app, db
from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant, LiveQuizResponse
from instructor.models.class_model import Class
from instructor.models.module import Module
from instructor.models.user import Instructor
from sqlalchemy import func

def check_live_quiz_sessions():
    """Check the current state of live quiz sessions in the database"""
    
    app = create_app()
    with app.app_context():
        print("=" * 80)
        print("LIVE QUIZ SESSION DATABASE CHECK")
        print("=" * 80)
        print()
        
        # Check if tables exist
        try:
            session_count = LiveQuizSession.query.count()
            print(f"✅ LiveQuizSession table exists with {session_count} total sessions")
        except Exception as e:
            print(f"❌ LiveQuizSession table error: {e}")
            return
        
        # Get all sessions
        all_sessions = LiveQuizSession.query.all()
        
        if not all_sessions:
            print("\n⚠️  NO LIVE QUIZ SESSIONS FOUND IN DATABASE")
            print("   This is why the Live Quiz button is not appearing!")
            print()
            print("📋 SOLUTION:")
            print("   1. Instructors need to create sessions via: POST /instructor/api/live-quiz/create")
            print("   2. Or run the seed script to create test sessions")
            print()
        else:
            print(f"\n📊 FOUND {len(all_sessions)} SESSIONS:")
            print()
            
            # Group by status
            status_counts = {}
            for session in all_sessions:
                status_counts[session.status] = status_counts.get(session.status, 0) + 1
            
            print("Status Distribution:")
            for status, count in status_counts.items():
                print(f"  - {status}: {count}")
            print()
            
            # Show active/waiting sessions (these will appear in UI)
            active_sessions = [s for s in all_sessions if s.status in ['active', 'waiting']]
            if active_sessions:
                print(f"✅ {len(active_sessions)} ACTIVE/WAITING SESSIONS (will show in UI):")
                print()
                for session in active_sessions:
                    print(f"  Session #{session.id}: {session.title}")
                    print(f"    Status: {session.status}")
                    print(f"    Code: {session.session_code}")
                    print(f"    Class ID: {session.class_id}")
                    print(f"    Module ID: {session.module_id}")
                    print(f"    Lesson ID: {session.lesson_id}")
                    print(f"    Created: {session.created_at}")
                    
                    # Get class and module names
                    try:
                        class_obj = Class.query.get(session.class_id)
                        module_obj = Module.query.get(session.module_id)
                        print(f"    Class: {class_obj.name if class_obj else 'N/A'}")
                        print(f"    Module: {module_obj.title if module_obj else 'N/A'}")
                    except:
                        pass
                    
                    # Get participant count
                    participant_count = LiveQuizParticipant.query.filter_by(
                        session_id=session.id,
                        is_active=True
                    ).count()
                    print(f"    Participants: {participant_count}")
                    print()
            else:
                print("⚠️  NO ACTIVE OR WAITING SESSIONS")
                print("   All sessions are completed/paused - button will not appear")
                print()
            
            # Show completed sessions
            completed_sessions = [s for s in all_sessions if s.status == 'completed']
            if completed_sessions:
                print(f"📝 {len(completed_sessions)} COMPLETED SESSIONS:")
                for session in completed_sessions:
                    print(f"  - Session #{session.id}: {session.title} (Code: {session.session_code})")
                print()
        
        # Check for classes and modules that could have sessions
        print("\n📚 AVAILABLE CLASSES & MODULES:")
        classes = Class.query.all()
        for class_obj in classes:
            modules = Module.query.filter_by(class_id=class_obj.id, is_active=True).all()
            print(f"  Class {class_obj.id}: {class_obj.name} ({len(modules)} modules)")
            for module in modules:
                # Check if this module has any sessions
                module_sessions = LiveQuizSession.query.filter_by(
                    class_id=class_obj.id,
                    module_id=module.id
                ).count()
                status = "✅" if module_sessions > 0 else "  "
                print(f"    {status} Module {module.id}: {module.title} ({module_sessions} sessions)")
        
        print()
        print("=" * 80)
        print("DIAGNOSIS COMPLETE")
        print("=" * 80)

if __name__ == '__main__':
    check_live_quiz_sessions()
