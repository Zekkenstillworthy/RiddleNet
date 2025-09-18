from admin.models.question import Question, StandardQuestion
from sqlalchemy import text
from __init__ import db
from run import app

with app.app_context():
    print('=== CHECKING ALL QUESTIONS IN DATABASE ===')
    
    # Check Question table
    questions = Question.query.all()
    print(f'Question table: Found {len(questions)} questions')
    for q in questions[:5]:  # Show first 5
        print(f'  - Q{q.numb} (ID: {q.id}): {q.question[:60]}... (category: {q.category})')
    
    # Check StandardQuestion table  
    std_questions = StandardQuestion.query.all()
    print(f'StandardQuestion table: Found {len(std_questions)} questions')
    for q in std_questions[:5]:  # Show first 5
        print(f'  - Q{q.numb} (ID: {q.id}): {q.question[:60]}... (category: {q.category})')
    
    print(f'Total questions: {len(questions) + len(std_questions)}')
    
    # Check unique categories
    question_categories = set([q.category for q in questions])
    std_question_categories = set([q.category for q in std_questions])
    all_categories = question_categories.union(std_question_categories)
    print(f'Categories found: {list(all_categories)}')