#!/usr/bin/env python3
"""Check Quiz challenge data in database"""

from application import create_app
from models import db, ChallengeScore

app = create_app()

with app.app_context():
    score = ChallengeScore.query.filter_by(user_id=1, challenge_type='quiz').first()
    
    if score:
        print(f"Quiz Challenge Score for User 1:")
        print(f"  best_score: {score.best_score}")
        print(f"  latest_score: {score.latest_score}")
        print(f"  is_completed: {score.is_completed}")
        
        if score.challenge_metadata:
            print(f"  completedSets: {score.challenge_metadata.get('completedSets')}")
            print(f"  in_progress: {score.challenge_metadata.get('in_progress')}")
            
            if 'progress' in score.challenge_metadata:
                progress = score.challenge_metadata['progress']
                print(f"  progress.completedSets: {progress.get('completedSets')}")
                print(f"  progress.currentSet: {progress.get('currentSet')}")
                print(f"  progress.currentQuestion: {progress.get('currentQuestion')}")
    else:
        print("No Quiz challenge score found for User 1")
