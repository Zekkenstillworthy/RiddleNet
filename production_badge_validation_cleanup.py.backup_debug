#!/usr/bin/env python3
"""
Production Badge Validation and Cleanup Script
Removes badges that were incorrectly awarded when challenge completion was < 100%
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import db, create_app
from user.models.user_badge import UserBadge
from user.models.challenge_score import ChallengeScore

def validate_and_cleanup_badges():
    """Remove badges where the associated challenge is not 100% complete"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("PRODUCTION BADGE VALIDATION & CLEANUP")
        print("="*80)
        
        # Get all badges
        all_badges = UserBadge.query.all()
        print(f"\n📊 Total badges in database: {len(all_badges)}")
        
        invalid_badges = []
        valid_badges = []
        
        # Check each badge against its challenge completion status
        for badge in all_badges:
            user_id = badge.user_id
            challenge_type = badge.challenge_type
            
            # Get the corresponding challenge score
            challenge = ChallengeScore.query.filter_by(
                user_id=user_id,
                challenge_type=challenge_type
            ).first()
            
            if not challenge:
                print(f"\n⚠️  Badge without challenge data:")
                print(f"   User: {user_id}, Badge: {badge.badge_id} ({badge.badge_name})")
                print(f"   Challenge Type: {challenge_type}")
                invalid_badges.append(badge)
                continue
            
            # Check if challenge is TRULY completed
            is_completed = ChallengeScore.is_effectively_completed(challenge)
            effective_score = ChallengeScore.effective_best_score(challenge)
            
            # Badge should only exist if challenge is 100% complete
            if not is_completed or effective_score < 100:
                print(f"\n❌ INVALID BADGE:")
                print(f"   User: {user_id}, Badge: {badge.badge_id} ({badge.badge_name})")
                print(f"   Challenge Type: {challenge_type}")
                print(f"   Effective Score: {effective_score}%")
                print(f"   Is Completed: {is_completed}")
                print(f"   Earned Score (badge): {badge.earned_score}%")
                
                # For OSI, show level breakdown
                if challenge_type == 'osi':
                    metadata = challenge.challenge_metadata or {}
                    challenge_data = metadata.get('challenge_data', {})
                    level1 = challenge_data.get('level1_score', 0)
                    level2 = challenge_data.get('level2_score', 0)
                    both_complete = challenge_data.get('both_levels_complete', False)
                    print(f"   OSI Level 1: {level1}%")
                    print(f"   OSI Level 2: {level2}%")
                    print(f"   Both Complete Flag: {both_complete}")
                
                invalid_badges.append(badge)
            else:
                valid_badges.append(badge)
        
        print(f"\n" + "="*80)
        print(f"📊 VALIDATION SUMMARY")
        print(f"="*80)
        print(f"✅ Valid badges: {len(valid_badges)}")
        print(f"❌ Invalid badges: {len(invalid_badges)}")
        
        if invalid_badges:
            print(f"\n" + "="*80)
            print("CLEANUP PLAN")
            print("="*80)
            print("\nThe following badges will be DELETED:")
            
            for badge in invalid_badges:
                print(f"  • User {badge.user_id}: {badge.badge_name} ({badge.badge_id}) - {badge.challenge_type}")
            
            # Ask for confirmation
            response = input(f"\n⚠️  DELETE {len(invalid_badges)} invalid badges? (yes/no): ").strip().lower()
            
            if response == 'yes':
                print("\n🗑️  Deleting invalid badges...")
                for badge in invalid_badges:
                    print(f"   Deleting: User {badge.user_id} - {badge.badge_name}")
                    db.session.delete(badge)
                
                db.session.commit()
                print(f"\n✅ Successfully deleted {len(invalid_badges)} invalid badges")
                print("✅ Database updated successfully!")
            else:
                print("\n❌ Cleanup cancelled. No changes made.")
        else:
            print("\n✅ All badges are valid! No cleanup needed.")
        
        print("\n" + "="*80)
        print("CLEANUP COMPLETE")
        print("="*80 + "\n")

if __name__ == '__main__':
    print("\n🔧 Starting Production Badge Validation...")
    try:
        validate_and_cleanup_badges()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
