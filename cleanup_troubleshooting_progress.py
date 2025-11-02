"""
Troubleshooting Progress Recalculation Script

This script recalculates the progress tracking for all users who have attempted
Link Up! (troubleshooting) challenges. It:

1. Scans all troubleshooting-related challenge scores
2. Identifies which sub-challenges each user has completed at 100%
3. Updates the metadata to track completed challenges
4. Shows progress breakdown by difficulty

Run this after deploying the sub-item completion fix to update existing user data.

Usage:
    python cleanup_troubleshooting_progress.py
"""

from __init__ import db, create_app
from user.models.challenge_score import ChallengeScore
from user.models.user_badge import UserBadge
from datetime import datetime

# Challenge definitions
EASY_CHALLENGES = ['vlan-basics', 'default-gateway', 'default-gateway-setup', 'dhcp-client', 'dhcp-client-config']
MEDIUM_CHALLENGES = ['extended-ring-redundancy', 'hybrid-star-ring', 'partial-mesh-ospf']
HARD_CHALLENGES = ['mpls-vpn-complex', 'datacenter-fabric', 'sd-wan-overlay']

# Normalized challenge names (for alternative IDs)
EASY_CHALLENGES_NORMALIZED = ['vlan-basics', 'default-gateway', 'dhcp-client']

def normalize_scenario_id(scenario_id):
    """Normalize alternative scenario names"""
    if scenario_id in ['default-gateway', 'default-gateway-setup']:
        return 'default-gateway'
    elif scenario_id in ['dhcp-client', 'dhcp-client-config']:
        return 'dhcp-client'
    else:
        return scenario_id


def recalculate_troubleshooting_progress():
    """Recalculate progress for all users with troubleshooting challenges"""
    
    print("=" * 80)
    print("Troubleshooting Progress Recalculation Script")
    print("=" * 80)
    print()
    
    # Get all troubleshooting challenge scores (across all difficulty levels)
    all_scores = ChallengeScore.query.filter(
        ChallengeScore.challenge_type.in_(['linkup_easy', 'troubleshooting_medium', 'troubleshooting_hard', 'troubleshooting'])
    ).order_by(ChallengeScore.user_id, ChallengeScore.updated_at).all()
    
    if not all_scores:
        print("❌ No troubleshooting challenges found in database")
        return
    
    print(f"✅ Found {len(all_scores)} troubleshooting challenge records")
    print()
    
    # Group by user
    user_challenges = {}
    for score in all_scores:
        user_id = score.user_id
        if user_id not in user_challenges:
            user_challenges[user_id] = []
        user_challenges[user_id].append(score)
    
    print(f"📊 Processing {len(user_challenges)} users...")
    print()
    
    # Track statistics
    stats = {
        'users_processed': 0,
        'users_with_progress': 0,
        'users_with_invalid_badges': 0,
        'total_challenges_completed': 0,
        'users_at_100_percent': 0
    }
    
    # Process each user
    for user_id, scores in user_challenges.items():
        print(f"\n{'─' * 80}")
        print(f"👤 User ID: {user_id}")
        print(f"{'─' * 80}")
        
        # Extract completed scenarios (100% score)
        completed_scenarios = set()
        for score_record in scores:
            print(f"  Challenge: {score_record.challenge_type} | Score: {score_record.best_score}%")
            
            if score_record.best_score >= 100.0:  # Must be 100% to count
                metadata = score_record.challenge_metadata or {}
                scenario = metadata.get('scenario_id')
                if scenario:
                    normalized_scenario = normalize_scenario_id(scenario)
                    completed_scenarios.add(normalized_scenario)
                    print(f"    ✅ Completed: {scenario} (normalized: {normalized_scenario})")
        
        # Count by difficulty
        easy_count = sum(1 for s in completed_scenarios if s in EASY_CHALLENGES_NORMALIZED)
        medium_count = sum(1 for s in completed_scenarios if s in MEDIUM_CHALLENGES)
        hard_count = sum(1 for s in completed_scenarios if s in HARD_CHALLENGES)
        total_count = easy_count + medium_count + hard_count
        
        print(f"\n  📈 Progress Summary:")
        print(f"    Easy: {easy_count}/3 - {[s for s in completed_scenarios if s in EASY_CHALLENGES_NORMALIZED]}")
        print(f"    Medium: {medium_count}/3 - {[s for s in completed_scenarios if s in MEDIUM_CHALLENGES]}")
        print(f"    Hard: {hard_count}/3 - {[s for s in completed_scenarios if s in HARD_CHALLENGES]}")
        print(f"    Total: {total_count}/9 ({(total_count/9)*100:.1f}%)")
        
        # Update metadata for the latest score record (most recent)
        latest_score = scores[-1]
        
        # Ensure metadata exists
        if latest_score.challenge_metadata is None:
            latest_score.challenge_metadata = {}
        
        # Update with recalculated data
        latest_score.challenge_metadata['completed_challenges'] = list(completed_scenarios)
        latest_score.challenge_metadata['challenge_counts'] = {
            'easy': easy_count,
            'medium': medium_count,
            'hard': hard_count,
            'total': total_count
        }
        latest_score.challenge_metadata['recalculated_at'] = datetime.utcnow().isoformat()
        
        print(f"\n  ✅ Updated metadata for latest score record (ID: {latest_score.id})")
        
        # Update statistics
        stats['users_processed'] += 1
        if total_count > 0:
            stats['users_with_progress'] += 1
        stats['total_challenges_completed'] += total_count
        if total_count >= 9:
            stats['users_at_100_percent'] += 1
        
        # Check for invalid badges (users with badge but not all 9 challenges complete)
        user_badges = UserBadge.query.filter_by(
            user_id=user_id,
            challenge_type='troubleshooting'
        ).all()
        
        if user_badges and total_count < 9:
            print(f"\n  ⚠️  WARNING: User has troubleshooting badge but only {total_count}/9 challenges complete!")
            print(f"      Badges: {[b.badge_id for b in user_badges]}")
            stats['users_with_invalid_badges'] += 1
    
    # Commit all changes
    print(f"\n{'=' * 80}")
    print("💾 Saving changes to database...")
    db.session.commit()
    print("✅ All changes committed successfully!")
    
    # Print final statistics
    print(f"\n{'=' * 80}")
    print("📊 RECALCULATION STATISTICS")
    print(f"{'=' * 80}")
    print(f"  Users processed: {stats['users_processed']}")
    print(f"  Users with progress: {stats['users_with_progress']}")
    print(f"  Users at 100% (9/9): {stats['users_at_100_percent']}")
    print(f"  Total challenges completed: {stats['total_challenges_completed']}")
    print(f"  Users with invalid badges: {stats['users_with_invalid_badges']}")
    print(f"{'=' * 80}")
    
    if stats['users_with_invalid_badges'] > 0:
        print()
        print("⚠️  WARNING: Some users have troubleshooting badges but haven't completed all 9 challenges.")
        print("   These badges were likely awarded under the old system.")
        print("   Consider running: python cleanup_invalid_troubleshooting_badges.py")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        try:
            recalculate_troubleshooting_progress()
            print("\n✅ Recalculation completed successfully!")
        except Exception as e:
            print(f"\n❌ Error during recalculation: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
