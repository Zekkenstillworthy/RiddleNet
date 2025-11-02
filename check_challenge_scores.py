#!/usr/bin/env python3
"""
Check challenge scores for a specific user on production
"""
import sys
import os

# Add the parent directory to the path to import application
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_scores(user_id=1):
    """Check challenge scores for a user"""
    from application import create_app
    from user.models.challenge_score import ChallengeScore
    
    app = create_app()
    
    with app.app_context():
        print(f"\n{'='*80}")
        print(f"Challenge Scores for User ID: {user_id}")
        print(f"{'='*80}\n")
        
        # Query all challenge scores for the user
        scores = ChallengeScore.query.filter_by(user_id=user_id).all()
        
        if not scores:
            print(f"❌ No challenge scores found for user {user_id}")
            return
        
        print(f"✅ Found {len(scores)} challenge score(s):\n")
        
        for score in scores:
            print(f"Challenge Type: {score.challenge_type}")
            print(f"  Best Score: {score.best_score}%")
            print(f"  Latest Score: {score.latest_score}%")
            print(f"  Is Completed: {score.is_completed}")
            print(f"  Total Attempts: {score.total_attempts}")
            print(f"  Updated At: {score.updated_at}")
            
            # Print metadata if available
            if score.challenge_metadata:
                print(f"  Metadata:")
                metadata = score.challenge_metadata
                if isinstance(metadata, dict):
                    for key, value in metadata.items():
                        if key == 'challenge_data':
                            print(f"    {key}:")
                            if isinstance(value, dict):
                                for k, v in value.items():
                                    print(f"      {k}: {v}")
                        else:
                            print(f"    {key}: {value}")
                else:
                    print(f"    {metadata}")
            print()
        
        print(f"{'='*80}\n")

if __name__ == '__main__':
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    check_scores(user_id)
