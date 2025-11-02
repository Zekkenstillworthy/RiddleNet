#!/usr/bin/env python3
"""
🔧 Cleanup Invalid Badges Script
================================

Removes badges where the associated challenge is not 100% complete.
This ensures dashboard consistency between progress and badge display.

Run on production server:
    ssh -i riddlenetv1.pem ubuntu@54.66.229.118
    cd /home/ubuntu/RiddleNet
    python3 cleanup_invalid_badges.py
"""

import sys
import os

# Add the application directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application import create_app
from user.models.challenge_score import ChallengeScore
from user.models.user_badge import UserBadge
from user.models import db


def cleanup_invalid_badges():
    """Remove badges where the challenge is not 100% complete"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*100)
        print("🔧 CLEANUP INVALID BADGES - PRODUCTION")
        print("="*100)
        
        # Get all badges
        all_badges = UserBadge.query.all()
        print(f"\n📊 Total badges in database: {len(all_badges)}")
        
        invalid_badges = []
        valid_badges = []
        
        # Check each badge against challenge completion
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
                print(f"   User ID: {user_id}")
                print(f"   Badge: {badge.badge_id} ({badge.badge_name})")
                print(f"   Challenge Type: {challenge_type}")
                invalid_badges.append(badge)
                continue
            
            # Check if challenge is TRULY completed
            is_truly_completed = False
            
            if challenge_type == 'troubleshooting':
                # Link Up! - check sub-item completion (all 12 items must be complete)
                if challenge.challenge_metadata:
                    completed_count = len(challenge.challenge_metadata.get('completed_challenges', []))
                    TOTAL_LINK_UP_ITEMS = 12  # Foundation (3) + Easy (3) + Medium (3) + Hard (3)
                    is_truly_completed = completed_count >= TOTAL_LINK_UP_ITEMS
                    
                    if not is_truly_completed:
                        counts = challenge.challenge_metadata.get('challenge_counts', {})
                        print(f"\n❌ INVALID BADGE:")
                        print(f"   User ID: {user_id}")
                        print(f"   Badge: {badge.badge_id} ({badge.badge_name})")
                        print(f"   Challenge Type: {challenge_type}")
                        print(f"   Completed: {completed_count}/{TOTAL_LINK_UP_ITEMS} sub-items")
                        print(f"   Foundation: {counts.get('foundation', 0)}/3")
                        print(f"   Easy: {counts.get('easy', 0)}/3")
                        print(f"   Medium: {counts.get('medium', 0)}/3")
                        print(f"   Hard: {counts.get('hard', 0)}/3")
                        invalid_badges.append(badge)
                else:
                    print(f"\n❌ INVALID BADGE:")
                    print(f"   User ID: {user_id}")
                    print(f"   Badge: {badge.badge_id} ({badge.badge_name})")
                    print(f"   Challenge Type: {challenge_type}")
                    print(f"   No metadata found")
                    invalid_badges.append(badge)
            else:
                # For other challenges (crimping, osi, quiz), check completion status
                is_truly_completed = ChallengeScore.is_effectively_completed(challenge)
                effective_score = ChallengeScore.effective_best_score(challenge)
                is_truly_completed = is_truly_completed and effective_score >= 100
                
                if not is_truly_completed:
                    print(f"\n❌ INVALID BADGE:")
                    print(f"   User ID: {user_id}")
                    print(f"   Badge: {badge.badge_id} ({badge.badge_name})")
                    print(f"   Challenge Type: {challenge_type}")
                    print(f"   Effective Score: {effective_score:.1f}%")
                    print(f"   Is Completed: {ChallengeScore.is_effectively_completed(challenge)}")
                    
                    if challenge_type == 'osi' and challenge.challenge_metadata:
                        challenge_data = challenge.challenge_metadata.get('challenge_data', {})
                        level1 = challenge_data.get('level1_score', 0)
                        level2 = challenge_data.get('level2_score', 0)
                        both = challenge_data.get('both_levels_complete', False)
                        print(f"   OSI Level 1: {level1}% | Level 2: {level2}% | Both: {both}")
                    
                    invalid_badges.append(badge)
            
            if is_truly_completed:
                valid_badges.append(badge)
                print(f"✅ VALID: {badge.badge_id} ({badge.badge_name}) for User {user_id}")
        
        # Summary
        print(f"\n{'='*100}")
        print("📋 CLEANUP SUMMARY")
        print(f"{'='*100}")
        print(f"\n✅ Valid badges: {len(valid_badges)}")
        print(f"❌ Invalid badges: {len(invalid_badges)}")
        
        if invalid_badges:
            print(f"\n⚠️  The following badges will be DELETED:")
            for badge in invalid_badges:
                print(f"  • Badge ID: {badge.badge_id} ({badge.badge_name})")
                print(f"    User ID: {badge.user_id}")
                print(f"    Challenge Type: {badge.challenge_type}")
            
            # Confirm deletion
            confirm = input(f"\n❓ Delete {len(invalid_badges)} invalid badge(s)? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                print(f"\n🗑️  Deleting invalid badges...")
                for badge in invalid_badges:
                    print(f"  Deleting: {badge.badge_id} ({badge.badge_name}) - User {badge.user_id}")
                    db.session.delete(badge)
                
                db.session.commit()
                print(f"\n✅ Successfully deleted {len(invalid_badges)} invalid badge(s)")
                print(f"✅ Remaining badges: {len(valid_badges)}")
            else:
                print(f"\n❌ Deletion cancelled. No changes made.")
        else:
            print(f"\n🎉 All badges are valid! No cleanup needed.")
        
        print(f"\n{'='*100}\n")


if __name__ == "__main__":
    cleanup_invalid_badges()
