#!/usr/bin/env python3
"""Check Live Quiz questions in database"""

from application import create_app
from instructor.models.question_group import QuestionGroup
from user.models.live_quiz import LiveQuizSession

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("LIVE QUIZ DATABASE DIAGNOSTICS")
    print("="*80)
    
    # Check question groups
    groups = QuestionGroup.query.all()
    print(f"\n📚 Total Question Groups: {len(groups)}")
    
    if groups:
        print("\nQuestion Groups:")
        for g in groups[:10]:
            title = getattr(g, 'title', getattr(g, 'name', f'Group {g.id}'))
            questions_count = len(g.questions) if hasattr(g, 'questions') and g.questions else 0
            print(f"  - Group {g.id}: '{title}' - {questions_count} questions")
            if hasattr(g, 'questions') and g.questions:
                for q in g.questions[:3]:
                    # Question model uses 'question' field
                    question_text = getattr(q, 'question', getattr(q, 'question_text', getattr(q, 'text', 'No text')))
                    print(f"      Q{q.id}: {question_text[:60] if question_text else 'EMPTY'}...")
                    # Show answer and options to check if question is complete
                    answer = getattr(q, 'answer', 'No answer')
                    options = getattr(q, 'options', [])
                    print(f"           Answer: {answer[:30] if answer else 'EMPTY'}, Options: {len(options) if isinstance(options, list) else 'N/A'}")
    else:
        print("  ⚠️ WARNING: No question groups found!")
    
    # Check live quiz sessions
    sessions = LiveQuizSession.query.all()
    print(f"\n🎯 Total Live Quiz Sessions: {len(sessions)}")
    
    if sessions:
        print("\nLive Quiz Sessions:")
        for s in sessions:
            print(f"  - Session {s.id}: '{s.title}'")
            print(f"    Status: {s.status}")
            print(f"    Question Group ID: {s.question_group_id}")
            
            # Check if question group exists
            qg = QuestionGroup.query.get(s.question_group_id)
            if qg:
                qg_title = getattr(qg, 'title', getattr(qg, 'name', f'Group {qg.id}'))
                questions_count = len(qg.questions) if hasattr(qg, 'questions') and qg.questions else 0
                print(f"    Question Group: '{qg_title}' ({questions_count} questions)")
            else:
                print(f"    ❌ ERROR: Question Group {s.question_group_id} not found!")
    else:
        print("  ⚠️ WARNING: No live quiz sessions found!")
    
    print("\n" + "="*80 + "\n")
