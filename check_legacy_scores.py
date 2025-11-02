#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from application import create_app
from user.models.score import Score

app = create_app()
with app.app_context():
    print("\n=== LEGACY SCORES FOR USER 1 (UserScore table) ===")
    scores = Score.query.filter_by(user_id=1).all()
    print(f"Total legacy scores: {len(scores)}")
    
    # Group by category
    by_category = {}
    for s in scores:
        cat = s.category or 'unknown'
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(s.score)
    
    for cat, score_list in by_category.items():
        best = max(score_list) if score_list else 0
        print(f"\n{cat}:")
        print(f"  Best score: {best}")
        print(f"  Total attempts: {len(score_list)}")
