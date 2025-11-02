"""
Invalid Troubleshooting Badge Cleanup Script

This script removes troubleshooting badges from users who haven't completed
all 9 Link Up! challenges. 

Under the old system, badges were awarded after completing just one challenge.
Under the new system, badges are only awarded after completing ALL 9 challenges.

This script:
1. Finds users with troubleshooting badges
2. Checks their actual progress (completed challenges)
3. Removes badges if progress < 9/9
4. Provides a detailed report

Usage:
    python cleanup_invalid_troubleshooting_badges.py [--dry-run]
    
Options:
    --dry-run    Show what would be removed without actually removing
"""

import sys
from __init__ import db, create_app
from user.models.challenge_score import ChallengeScore
from user.models.user_badge import UserBadge


def cleanup_invalid_badges(dry_run=False):
    """Remove troubleshooting badges from users who haven't completed all 9 challenges"""
    
    print("=" * 80)
    print("Invalid Troubleshooting Badge Cleanup Script")
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    print("=" * 80)
    print()
    
    # Get all users with troubleshooting badges
    troubleshooting_badges = UserBadge.query.filter_by(
        challenge_type='troubleshooting'
    ).all()
    
    if not troubleshooting_badges:
        print("✅ No troubleshooting badges found in database")
        return
    
    print(f"📊 Found {len(troubleshooting_badges)} troubleshooting badge(s)")
    print()
    
    # Track statistics
    stats = {
        'total_badges': len(troubleshooting_badges),
        'valid_badges': 0,
        'invalid_badges': 0,
        'removed_badges': 0
    }
    
    badges_to_remove = []
    
    # Check each badge
    for badge in troubleshooting_badges:
        user_id = badge.user_id
        badge_id = badge.badge_id
        
        print(f"\n{'─' * 80}")
        print(f"👤 User ID: {user_id} | Badge: {badge_id}")
        print(f"{'─' * 80}")
        
        # Get user's troubleshooting progress
        progress = ChallengeScore.get_troubleshooting_progress(user_id)
        
        total_completed = progress['challenge_counts']['total']
        is_complete = progress['is_complete']
        
        print(f"  Progress: {total_completed}/9 challenges complete")
        print(f"    Easy: {progress['challenge_counts']['easy']}/3")
        print(f"    Medium: {progress['challenge_counts']['medium']}/3")
        print(f"    Hard: {progress['challenge_counts']['hard']}/3")
        print(f"  Completed challenges: {progress['completed_challenges']}")
        
        # Check if badge is valid (requires 9/9 completion)
        if is_complete:
            print(f"  ✅ VALID BADGE - User has completed all 9 challenges")
            stats['valid_badges'] += 1
        else:
            print(f"  ❌ INVALID BADGE - User has only completed {total_completed}/9 challenges")
            stats['invalid_badges'] += 1
            badges_to_remove.append(badge)
    
    # Remove invalid badges
    print(f"\n{'=' * 80}")
    
    if not badges_to_remove:
        print("✅ All troubleshooting badges are valid!")
        print("   No cleanup needed.")
    else:
        print(f"⚠️  Found {len(badges_to_remove)} invalid badge(s) to remove:")
        print()
        
        for badge in badges_to_remove:
            print(f"  - User ID: {badge.user_id} | Badge: {badge.badge_id} ({badge.badge_name})")
        
        print()
        
        if dry_run:
            print("🔍 DRY RUN MODE - Badges would be removed, but no changes were made")
        else:
            # Ask for confirmation
            print("❓ Do you want to remove these invalid badges? (yes/no): ", end="")
            response = input().strip().lower()
            
            if response == 'yes':
                for badge in badges_to_remove:
                    db.session.delete(badge)
                    stats['removed_badges'] += 1
                
                db.session.commit()
                print(f"\n✅ Removed {stats['removed_badges']} invalid badge(s)")
            else:
                print("\n❌ Cleanup cancelled - no badges were removed")
    
    # Print final statistics
    print(f"\n{'=' * 80}")
    print("📊 CLEANUP STATISTICS")
    print(f"{'=' * 80}")
    print(f"  Total badges checked: {stats['total_badges']}")
    print(f"  Valid badges: {stats['valid_badges']}")
    print(f"  Invalid badges: {stats['invalid_badges']}")
    print(f"  Badges removed: {stats['removed_badges']}")
    print(f"{'=' * 80}")


if __name__ == '__main__':
    # Check for --dry-run flag
    dry_run = '--dry-run' in sys.argv
    
    app = create_app()
    with app.app_context():
        try:
            cleanup_invalid_badges(dry_run=dry_run)
            print("\n✅ Cleanup completed successfully!")
        except Exception as e:
            print(f"\n❌ Error during cleanup: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
