#!/usr/bin/env python3
"""
Check which modules the Live Quiz sessions belong to
"""
from application import create_app
from user.models.live_quiz import LiveQuizSession
from instructor.models.module import Module

app = create_app()

with app.app_context():
    print("=" * 80)
    print("LIVE QUIZ SESSION TO MODULE MAPPING")
    print("=" * 80)
    
    sessions = LiveQuizSession.query.all()
    
    for session in sessions:
        module = Module.query.get(session.module_id) if session.module_id else None
        module_title = module.title if module else "N/A"
        
        # Check if this module has question groups assigned
        has_questions = False
        question_count = 0
        if module and hasattr(module, 'question_groups'):
            try:
                qgroups = list(module.question_groups)
                if qgroups:
                    has_questions = True
                    for qg in qgroups:
                        question_count += len(qg.questions or [])
            except Exception as e:
                pass
        
        status_emoji = "✅" if has_questions else "❌"
        print(f"{status_emoji} Session {session.id}: '{session.title}'")
        print(f"   Module: {session.module_id} - {module_title}")
        print(f"   Question Group ID: {session.question_group_id}")
        print(f"   Module has questions: {has_questions} ({question_count} questions)")
        print()
