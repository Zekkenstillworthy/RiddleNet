#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from application import create_app
from user.models.challenge_score import ChallengeScore

app = create_app()
with app.app_context():
    scores = ChallengeScore.query.filter_by(user_id=1).all()
    print("\nUser 1 Challenge Status:")
    for s in scores:
        print(f"  {s.challenge_type}: {s.best_score}% - Completed: {s.is_completed}")
