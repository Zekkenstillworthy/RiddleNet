#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from application import create_app
from user.models.challenge_score import ChallengeScore

app = create_app()
with app.app_context():
    print("\n=== ALL CHALLENGES FOR USER 1 ===")
    scores = ChallengeScore.query.filter_by(user_id=1).all()
    print(f"Total: {len(scores)}")
    for s in scores:
        print(f"\n{s.challenge_type}:")
        print(f"  Best: {s.best_score}%")
        print(f"  Latest: {s.latest_score}%")
        print(f"  Completed: {s.is_completed}")
        print(f"  Attempts: {s.total_attempts}")
    
    print("\n=== CHECKING CRIMPING SPECIFICALLY ===")
    crimping = ChallengeScore.query.filter_by(user_id=1, challenge_type='crimping').first()
    print(f"Crimping exists: {crimping is not None}")
    if crimping:
        print(f"  Best: {crimping.best_score}%")
        print(f"  Completed: {crimping.is_completed}")
