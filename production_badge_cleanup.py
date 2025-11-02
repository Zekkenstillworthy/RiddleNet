#!/usr/bin/env python3
"""
Production Badge Cleanup Script
Removes badges awarded under old 75% threshold
Run on production server via Flask shell
"""

def cleanup_production_badges():
    """Clean up badges on production server"""
    from user.models.user_badge import UserBadge
    from user.models.challenge_score import ChallengeScore
    from __init__ import db
    
    print("=" * 80)
    print("🧹 PRODUCTION BADGE CLEANUP")
    print("=" * 80)
    
    # Step 1: Find all rare badges with < 100% scores
    print("\n[STEP 1] Finding rare badges with < 100% scores...")
    rare_badges = UserBadge.query.filter(
        UserBadge.badge_rarity == 'rare',
        UserBadge.earned_score < 100
    ).all()
    
    print(f"Found {len(rare_badges)} rare badges to remove:")
    for badge in rare_badges:
        print(f"  ❌ {badge.badge_name} - User {badge.user_id} - Score: {badge.earned_score}%")
    
    # Step 2: Find badges where user's best score is < 100%
    print("\n[STEP 2] Checking all badges against current best scores...")
    all_badges = UserBadge.query.all()
    invalid_badges = []
    
    for badge in all_badges:
        challenge_score = ChallengeScore.query.filter_by(
            user_id=badge.user_id,
            challenge_type=badge.challenge_type
        ).first()
        
        if challenge_score and challenge_score.best_score < 100:
            invalid_badges.append(badge)
            print(f"  ❌ {badge.badge_name} - User {badge.user_id} - Best: {challenge_score.best_score}%")
    
    # Step 3: Find duplicate badges
    print("\n[STEP 3] Checking for duplicate badges...")
    seen = {}
    duplicates = []
    
    for badge in all_badges:
        key = f"{badge.user_id}_{badge.badge_id}"
        if key in seen:
            duplicates.append(badge)
            print(f"  ❌ DUPLICATE: {badge.badge_name} - User {badge.user_id}")
        else:
            seen[key] = badge
    
    # Step 4: Perform cleanup
    print("\n[STEP 4] Removing invalid badges...")
    total_removed = 0
    
    # Remove rare badges with < 100%
    for badge in rare_badges:
        db.session.delete(badge)
        total_removed += 1
    
    # Remove badges with invalid best scores
    for badge in invalid_badges:
        if badge not in rare_badges:  # Avoid double-delete
            db.session.delete(badge)
            total_removed += 1
    
    # Remove duplicates
    for badge in duplicates:
        if badge not in rare_badges and badge not in invalid_badges:  # Avoid double-delete
            db.session.delete(badge)
            total_removed += 1
    
    # Commit changes
    try:
        db.session.commit()
        print(f"\n✅ Successfully removed {total_removed} badges")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR: {e}")
        return False
    
    # Step 5: Show remaining badges
    print("\n[STEP 5] Remaining badges after cleanup:")
    remaining = UserBadge.query.all()
    
    if remaining:
        user_badge_count = {}
        for badge in remaining:
            if badge.user_id not in user_badge_count:
                user_badge_count[badge.user_id] = []
            user_badge_count[badge.user_id].append(badge)
        
        for user_id, badges in sorted(user_badge_count.items()):
            print(f"\n  User {user_id}: {len(badges)} badges")
            for badge in badges:
                print(f"    ✓ {badge.badge_name} ({badge.badge_rarity}, {badge.earned_score}%)")
    else:
        print("  No badges remaining")
    
    print("\n" + "=" * 80)
    print(f"✅ CLEANUP COMPLETE - Removed {total_removed} badges")
    print("=" * 80)
    
    return True

if __name__ == '__main__':
    # Run cleanup within Flask application context
    import sys
    sys.path.insert(0, '/home/ubuntu/RiddleNet')
    
    from application import application
    with application.app_context():
        cleanup_production_badges()
