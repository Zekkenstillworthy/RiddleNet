"""
Fix Leaderboard Score Normalization
This script normalizes scores in the ChallengeScore table that exceed 100%.
Scores above 100 are typically from hardcoded challenges where raw point values
(100-320) were saved instead of normalized percentages (0-100).
"""

import sys
import os
# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import application as app
from __init__ import db
from user.models.challenge_score import ChallengeScore

def fix_score_normalization():
    """Normalize all scores above 100% to proper 0-100 range"""
    with app.app_context():
        # Find all challenge scores above 100%
        high_scores = ChallengeScore.query.filter(ChallengeScore.best_score > 100).all()
        
        print(f"\n{'='*80}")
        print(f"[FIX] FIXING LEADERBOARD SCORE NORMALIZATION")
        print(f"{'='*80}\n")
        print(f"Found {len(high_scores)} scores above 100% that need normalization\n")
        
        if not high_scores:
            print("[OK] All scores are already properly normalized!")
            return
        
        fixed_count = 0
        for challenge_score in high_scores:
            old_score = challenge_score.best_score
            old_latest = challenge_score.latest_score
            old_avg = challenge_score.average_score
            
            # Determine the normalization factor based on challenge type
            # Easy challenges: max score = 120 (base 100 + 20 bonus)
            # Medium challenges: max score = 220 (base 200 + 20 bonus)
            # Hard challenges: max score = 320 (base 300 + 20 bonus)
            
            if 'easy' in challenge_score.challenge_type.lower():
                max_score = 120
            elif 'medium' in challenge_score.challenge_type.lower():
                max_score = 220
            elif 'hard' in challenge_score.challenge_type.lower():
                max_score = 320
            else:
                # For troubleshooting (general), if score is 100-120, treat as easy
                # If 200-220, treat as medium, if 300-320, treat as hard
                if old_score <= 120:
                    max_score = 120
                elif old_score <= 220:
                    max_score = 220
                else:
                    max_score = 320
            
            # Normalize scores to 0-100 range
            challenge_score.best_score = min((old_score / max_score) * 100, 100.0)
            challenge_score.latest_score = min((old_latest / max_score) * 100, 100.0)
            challenge_score.average_score = min((old_avg / max_score) * 100, 100.0)
            
            # Also fix total_score if it's been accumulated
            if challenge_score.total_score and challenge_score.total_score > 100 * challenge_score.total_attempts:
                challenge_score.total_score = (challenge_score.total_score / max_score) * 100
            
            print(f"[OK] Fixed {challenge_score.user.username} - {challenge_score.challenge_type}")
            print(f"   Best Score: {old_score:.1f} → {challenge_score.best_score:.1f}%")
            print(f"   Latest Score: {old_latest:.1f} → {challenge_score.latest_score:.1f}%")
            print(f"   Average Score: {old_avg:.1f} → {challenge_score.average_score:.1f}%")
            print()
            
            fixed_count += 1
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"{'='*80}")
            print(f"[OK] Successfully normalized {fixed_count} challenge scores!")
            print(f"{'='*80}\n")
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Error committing changes: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_score_normalization()
