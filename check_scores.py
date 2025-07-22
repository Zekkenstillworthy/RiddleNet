from __init__ import db, create_app
from user.models.score import Score

app = create_app()

with app.app_context():
    recent_scores = Score.query.order_by(Score.date_attempted.desc()).limit(10).all()
    print('Recent scores:')
    for score in recent_scores:
        print(f'ID: {score.id}, Score: {score.score}, Category: {score.category}, User: {score.user_id}, Date: {score.date_attempted}')
    
    # Check score ranges
    print('\nScore ranges:')
    min_score = db.session.query(db.func.min(Score.score)).scalar()
    max_score = db.session.query(db.func.max(Score.score)).scalar()
    avg_score = db.session.query(db.func.avg(Score.score)).scalar()
    print(f'Min: {min_score}, Max: {max_score}, Avg: {avg_score}')
    
    # Sample of different score values
    print('\nSample scores by category:')
    for category in ['riddle', 'topology', 'troubleshoot', 'crimping']:
        sample_scores = Score.query.filter(Score.category == category).limit(3).all()
        for score in sample_scores:
            print(f'{category}: {score.score}')
