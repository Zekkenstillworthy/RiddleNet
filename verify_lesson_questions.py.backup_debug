#!/usr/bin/env python3
"""
Test if lesson questions are now available for modules
"""
from application import create_app
from instructor.models.module import Module
from instructor.models.question_group import QuestionGroup

app = create_app()

with app.app_context():
    print("=" * 80)
    print("TEST: Verify lesson_questions will be populated")
    print("=" * 80)
    
    # Test Module 1 (Computer Network Fundamentals)
    test_module_ids = [1, 2, 5, 6, 7, 8, 12, 15]
    
    for module_id in test_module_ids:
        module = Module.query.get(module_id)
        if not module:
            print(f"❌ Module {module_id} not found")
            continue
        
        print(f"\n📘 Module {module_id}: '{module.title}'")
        
        # Simulate the code from universal_class_routes.py lines 775-782
        lesson_questions = []
        try:
            module_question_groups = module.question_groups.filter(QuestionGroup.is_active == True).all()
        except Exception:
            module_question_groups = list(module.question_groups) if hasattr(module, 'question_groups') else []
        
        assigned_question_groups = []
        seen_question_group_ids = set()
        
        for qg in module_question_groups:
            if not qg or getattr(qg, 'id', None) is None:
                continue
            if qg.id in seen_question_group_ids:
                continue
            if hasattr(qg, 'is_active') and not qg.is_active:
                continue
            assigned_question_groups.append(qg)
            seen_question_group_ids.add(qg.id)
        
        for qg in assigned_question_groups:
            questions_in_group = getattr(qg, 'questions', []) or []
            for question in questions_in_group:
                if not question:
                    continue
                question_dict = {
                    'id': getattr(question, 'id', None),
                    'question': getattr(question, 'question', ''),
                    'answer': getattr(question, 'answer', ''),
                    'options': list(question.options) if hasattr(question, 'options') else [],
                    'explanation': getattr(question, 'explanation', None),
                    'numb': getattr(question, 'numb', None),
                }
                lesson_questions.append(question_dict)
        
        print(f"   Question Groups: {len(assigned_question_groups)}")
        print(f"   Total Questions: {len(lesson_questions)}")
        
        if lesson_questions:
            print(f"   ✅ __lessonQuestions will be populated with {len(lesson_questions)} questions")
            print(f"   Sample questions:")
            for q in lesson_questions[:2]:
                print(f"      - Q{q['id']}: {q['question'][:50]}...")
        else:
            print(f"   ❌ __lessonQuestions will be EMPTY - Live Quiz will fail!")
    
    print(f"\n" + "=" * 80)
    print(f"✅ FIX VERIFICATION COMPLETE")
    print(f"=" * 80)
