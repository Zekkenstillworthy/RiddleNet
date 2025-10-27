"""
Production Deployment Script for Live Quiz
Ensures production server has active quiz sessions
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import create_app, db
from user.models.live_quiz import LiveQuizSession
from instructor.models.class_model import Class
from instructor.models.module import Module
from instructor.models.user import Instructor
from sqlalchemy import func

def production_deployment_check():
    """
    Complete production deployment checklist for Live Quiz
    """
    
    app = create_app()
    with app.app_context():
        print("=" * 80)
        print("LIVE QUIZ PRODUCTION DEPLOYMENT CHECK")
        print("=" * 80)
        print()
        
        issues = []
        warnings = []
        
        # 1. Check if tables exist
        print("1. Database Tables Check")
        try:
            session_count = LiveQuizSession.query.count()
            print(f"   ✅ LiveQuizSession table exists ({session_count} sessions)")
        except Exception as e:
            print(f"   ❌ LiveQuizSession table error: {e}")
            issues.append("Database tables not migrated")
            return
        
        # 2. Check for active/waiting sessions
        print("\n2. Active/Waiting Sessions Check")
        active_count = LiveQuizSession.query.filter_by(status='active').count()
        waiting_count = LiveQuizSession.query.filter_by(status='waiting').count()
        
        if active_count > 0:
            print(f"   ✅ {active_count} active sessions found")
        else:
            print(f"   ⚠️  No active sessions (button will show with pulse animation)")
        
        if waiting_count > 0:
            print(f"   ✅ {waiting_count} waiting sessions found")
        else:
            print(f"   ⚠️  No waiting sessions (button will show 'Starting Soon')")
        
        if active_count == 0 and waiting_count == 0:
            issues.append("No active or waiting sessions - button will be hidden")
        
        # 3. Check session distribution across classes/modules
        print("\n3. Session Distribution Check")
        
        classes = Class.query.all()
        modules_without_sessions = []
        
        for class_obj in classes:
            modules = Module.query.filter_by(class_id=class_obj.id, is_active=True, is_published=True).all()
            
            if not modules:
                continue
            
            print(f"   Class {class_obj.id}: {class_obj.name}")
            
            for module in modules:
                session_count = LiveQuizSession.query.filter_by(
                    class_id=class_obj.id,
                    module_id=module.id
                ).filter(
                    LiveQuizSession.status.in_(['active', 'waiting'])
                ).count()
                
                if session_count > 0:
                    print(f"      ✅ Module {module.id}: {module.title} ({session_count} sessions)")
                else:
                    print(f"      ⚠️  Module {module.id}: {module.title} (NO sessions)")
                    modules_without_sessions.append({
                        'class_id': class_obj.id,
                        'class_name': class_obj.name,
                        'module_id': module.id,
                        'module_title': module.title
                    })
        
        if modules_without_sessions:
            warnings.append(f"{len(modules_without_sessions)} modules have no sessions")
        
        # 4. Check for orphaned sessions (no lesson_id)
        print("\n4. Session Configuration Check")
        orphaned_sessions = LiveQuizSession.query.filter(
            LiveQuizSession.lesson_id.is_(None),
            LiveQuizSession.status.in_(['active', 'waiting'])
        ).count()
        
        if orphaned_sessions > 0:
            print(f"   ℹ️  {orphaned_sessions} sessions have no lesson_id (this is OK)")
        else:
            print(f"   ✅ All sessions properly linked to lessons")
        
        # 5. Check for instructors
        print("\n5. Instructor Account Check")
        instructor_count = Instructor.query.count()
        if instructor_count > 0:
            print(f"   ✅ {instructor_count} instructor accounts found")
        else:
            print(f"   ❌ No instructor accounts found")
            issues.append("No instructors to create/manage sessions")
        
        # 6. Check for question groups
        print("\n6. Question Group Check")
        from instructor.models.question_group import QuestionGroup
        
        for class_obj in classes:
            # QuestionGroup uses many-to-many relationship with classes
            qg_count = len([qg for qg in class_obj.question_groups.all()])
            if qg_count > 0:
                print(f"   ✅ Class {class_obj.name}: {qg_count} question groups")
            else:
                print(f"   ⚠️  Class {class_obj.name}: No question groups")
                warnings.append(f"Class {class_obj.name} has no question groups")
        
        # Summary
        print("\n" + "=" * 80)
        print("DEPLOYMENT SUMMARY")
        print("=" * 80)
        
        if not issues:
            print("\n✅ DEPLOYMENT READY")
            print("   Live Quiz feature is properly configured")
        else:
            print("\n❌ DEPLOYMENT ISSUES FOUND:")
            for issue in issues:
                print(f"   - {issue}")
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"   - {warning}")
        
        # Recommendations
        print("\n📋 RECOMMENDATIONS:")
        
        if modules_without_sessions:
            print(f"\n   Create sessions for {len(modules_without_sessions)} modules:")
            for mod in modules_without_sessions[:5]:  # Show first 5
                print(f"   - {mod['class_name']} > {mod['module_title']}")
            
            if len(modules_without_sessions) > 5:
                print(f"   ... and {len(modules_without_sessions) - 5} more")
        
        if active_count == 0:
            print("\n   Start at least one session to enable immediate student access:")
            print("   POST /instructor/api/live-quiz/<session_id>/start")
        
        print("\n" + "=" * 80)

if __name__ == '__main__':
    production_deployment_check()
