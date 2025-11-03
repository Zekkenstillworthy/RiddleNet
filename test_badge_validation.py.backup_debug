#!/usr/bin/env python3
"""
Quick Badge Validation Test - Production
Tests badge logic without making any changes
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import db, create_app
from user.models.user_badge import UserBadge
from user.models.challenge_score import ChallengeScore
from user.models import User

def test_badge_validation():
    """Test badge validation logic"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("BADGE VALIDATION TEST (READ-ONLY)")
        print("="*80)
        
        # Get all users with badges
        users_with_badges = db.session.query(User.id, User.username).join(
            UserBadge, User.id == UserBadge.user_id
        ).distinct().all()
        
        print(f"\n📊 Users with badges: {len(users_with_badges)}")
        
        for user_id, username in users_with_badges:
            print(f"\n" + "-"*80)
            print(f"👤 User: {username} (ID: {user_id})")
            print("-"*80)
            
            # Get user's badges
            badges = UserBadge.query.filter_by(user_id=user_id).all()
            print(f"Total badges: {len(badges)}")
            
            # Get user's challenges
            challenges = ChallengeScore.query.filter_by(user_id=user_id).all()
            print(f"Total challenges attempted: {len(challenges)}")
            
            # Check each badge
            for badge in badges:
                challenge_type = badge.challenge_type
                challenge = ChallengeScore.query.filter_by(
                    user_id=user_id,
                    challenge_type=challenge_type
                ).first()
                
                if challenge:
                    is_completed = ChallengeScore.is_effectively_completed(challenge)
                    effective_score = ChallengeScore.effective_best_score(challenge)
                    
                    status = "✅ VALID" if (is_completed and effective_score >= 100) else "❌ INVALID"
                    
                    print(f"\n  {status} Badge: {badge.badge_name}")
                    print(f"    Challenge: {challenge_type}")
                    print(f"    Effective Score: {effective_score}%")
                    print(f"    Is Completed: {is_completed}")
                    print(f"    Badge Earned Score: {badge.earned_score}%")
                    
                    if challenge_type == 'osi':
                        metadata = challenge.challenge_metadata or {}
                        challenge_data = metadata.get('challenge_data', {})
                        level1 = challenge_data.get('level1_score', 0)
                        level2 = challenge_data.get('level2_score', 0)
                        both = challenge_data.get('both_levels_complete', False)
                        print(f"    OSI L1: {level1}% | L2: {level2}% | Both: {both}")
                else:
                    print(f"\n  ❌ INVALID Badge: {badge.badge_name}")
                    print(f"    Challenge: {challenge_type}")
                    print(f"    ERROR: No challenge record found!")
            
            # Show completed challenges
            completed = [c for c in challenges if ChallengeScore.is_effectively_completed(c)]
            print(f"\n  📈 Challenges 100% Complete: {len(completed)}")
            for c in completed:
                score = ChallengeScore.effective_best_score(c)
                print(f"    ✅ {c.challenge_type}: {score}%")
        
        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80 + "\n")

if __name__ == '__main__':
    print("\n🔍 Running badge validation test...")
    try:
        test_badge_validation()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
