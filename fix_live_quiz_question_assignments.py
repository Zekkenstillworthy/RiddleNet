#!/usr/bin/env python3
"""
Fix Live Quiz by assigning Question Group 1 to all modules that have Live Quiz sessions
"""
from application import create_app
from user.models.live_quiz import LiveQuizSession
from instructor.models.module import Module
from instructor.models.question_group import QuestionGroup
from __init__ import db

app = create_app()

with app.app_context():
    print("=" * 80)
    print("LIVE QUIZ FIX: Assign Question Group to Modules")
    print("=" * 80)
    
    # Get Question Group 1
    question_group = QuestionGroup.query.get(1)
    if not question_group:
        print("❌ ERROR: Question Group 1 not found!")
        exit(1)
    
    print(f"\n📚 Question Group: '{question_group.name}' (ID: {question_group.id})")
    print(f"   Questions: {len(question_group.questions or [])}")
    
    # Get all Live Quiz sessions
    sessions = LiveQuizSession.query.all()
    module_ids_to_fix = set()
    
    for session in sessions:
        if session.module_id:
            module = Module.query.get(session.module_id)
            if module and hasattr(module, 'question_groups'):
                try:
                    qgroups = list(module.question_groups)
                    qg_ids = [qg.id for qg in qgroups]
                    if 1 not in qg_ids:
                        module_ids_to_fix.add(session.module_id)
                except Exception:
                    module_ids_to_fix.add(session.module_id)
    
    print(f"\n🔍 Found {len(module_ids_to_fix)} modules that need Question Group 1 assigned")
    
    if module_ids_to_fix:
        print(f"\n📝 Assigning Question Group 1 to modules:")
        for module_id in sorted(module_ids_to_fix):
            module = Module.query.get(module_id)
            if module:
                try:
                    # Check if already assigned (double-check)
                    existing_qgroups = list(module.question_groups)
                    if question_group not in existing_qgroups:
                        module.question_groups.append(question_group)
                        print(f"   ✅ Module {module_id}: '{module.title}' - Question Group added")
                    else:
                        print(f"   ⏭️  Module {module_id}: '{module.title}' - Already has Question Group")
                except Exception as e:
                    print(f"   ❌ Module {module_id}: Error - {e}")
        
        # Commit changes
        try:
            db.session.commit()
            print(f"\n✅ SUCCESS: Changes committed to database!")
            print(f"   {len(module_ids_to_fix)} modules now have Question Group 1 assigned")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: Failed to commit changes: {e}")
    else:
        print("\n✅ All modules already have Question Group 1 assigned - nothing to fix")
    
    # Verify fix
    print(f"\n🔍 Verifying fix...")
    sessions = LiveQuizSession.query.all()
    fixed_count = 0
    still_broken = 0
    
    for session in sessions:
        if session.module_id:
            module = Module.query.get(session.module_id)
            if module and hasattr(module, 'question_groups'):
                try:
                    qgroups = list(module.question_groups)
                    question_count = sum(len(qg.questions or []) for qg in qgroups)
                    if question_count > 0:
                        fixed_count += 1
                    else:
                        still_broken += 1
                        print(f"   ⚠️  Session {session.id} (Module {module.id}): Still no questions!")
                except Exception:
                    still_broken += 1
    
    print(f"\n📊 Results:")
    print(f"   ✅ {fixed_count} sessions now have questions available")
    print(f"   ❌ {still_broken} sessions still have issues")
