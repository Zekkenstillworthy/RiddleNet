"""
Cleanup Script: Remove badges awarded under old 75% threshold
Keep only badges that align with new 100% requirement
"""
from __init__ import db
from user.models.user_badge import UserBadge
from user.models.challenge_score import ChallengeScore

def cleanup_old_badges():
    """
    Remove rare-tier badges that were awarded under the old 75% threshold.
    Only keep badges where the user actually scored 100%.
    """
    print("🧹 Starting badge cleanup...")
    
    # Get all badges
    all_badges = UserBadge.query.all()
    removed_count = 0
    kept_count = 0
    
    for badge in all_badges:
        user_id = badge.user_id
        challenge_type = badge.challenge_type
        badge_id = badge.badge_id
        earned_score = badge.earned_score
        
        print(f"\n📋 Checking badge: {badge.badge_name} (User {user_id})")
        print(f"   Challenge: {challenge_type}, Score: {earned_score}%, Rarity: {badge.badge_rarity}")
        
        # Check if this badge should be removed
        should_remove = False
        reason = ""
        
        # Rule 1: Rare badges require 100% now (quiz_master, crimping_expert, layer_master, network_detective)
        if badge.badge_rarity == 'rare' and earned_score < 100:
            should_remove = True
            reason = f"Rare badge with {earned_score}% (needs 100%)"
        
        # Rule 2: Legendary badges always required 100%, but verify
        elif badge.badge_rarity == 'legendary' and earned_score < 100:
            should_remove = True
            reason = f"Legendary badge with {earned_score}% (invalid)"
        
        # Rule 3: Check against actual challenge score in database
        challenge_score = ChallengeScore.query.filter_by(
            user_id=user_id,
            challenge_type=challenge_type
        ).first()
        
        if challenge_score and challenge_score.best_score < 100:
            # Special case: If best score is < 100%, remove ALL badges for this challenge
            should_remove = True
            reason = f"Challenge best score is {challenge_score.best_score}% (needs 100%)"
        
        if should_remove:
            print(f"   ❌ REMOVING: {reason}")
            db.session.delete(badge)
            removed_count += 1
        else:
            print(f"   ✅ KEEPING: Valid badge")
            kept_count += 1
    
    # Commit all changes
    db.session.commit()
    
    print(f"\n{'='*60}")
    print(f"✅ Cleanup complete!")
    print(f"   Removed: {removed_count} badges")
    print(f"   Kept: {kept_count} badges")
    print(f"{'='*60}")

if __name__ == '__main__':
    with db.app.app_context():
        cleanup_old_badges()
