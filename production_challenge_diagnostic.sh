#!/bin/bash
# Production Badge Diagnostic Script
# Checks for duplicate badges and validates badge display

echo "🔍 RiddleNet Badge Diagnostic - Production Server"
echo "=================================================="

cd ~/RiddleNet || exit 1

# Run Python diagnostic
python3 << 'EOF'
import os
import sys

# Set up the application context
from application import create_app, db
from user.models.user_badge import UserBadge
from user.models.challenge_score import ChallengeScore

app = create_app()

with app.app_context():
    print("\n📊 Checking User ID 1 (Gilbert):")
    print("=" * 60)
    
    # Get all badges
    badges = UserBadge.query.filter_by(user_id=1).all()
    print(f"\n🏆 Total badges in database: {len(badges)}")
    
    # Group by challenge_type
    from collections import defaultdict
    badges_by_type = defaultdict(list)
    for badge in badges:
        badges_by_type[badge.challenge_type].append({
            'badge_id': badge.badge_id,
            'badge_name': badge.badge_name,
            'score': badge.score
        })
    
    print(f"\n📋 Badges grouped by challenge type:")
    for challenge_type, badge_list in badges_by_type.items():
        print(f"\n  {challenge_type.upper()}:")
        for b in badge_list:
            print(f"    - {b['badge_name']} (ID: {b['badge_id']}, Score: {b['score']}%)")
        if len(badge_list) > 1:
            print(f"    ⚠️  DUPLICATE DETECTED: {len(badge_list)} badges for same challenge!")
    
    # Get challenge completion status
    print(f"\n✅ Challenge Completion Status:")
    print("=" * 60)
    challenges = ChallengeScore.query.filter_by(user_id=1).all()
    for c in challenges:
        status = "✓ COMPLETED" if c.is_completed else "✗ INCOMPLETE"
        print(f"  {status:15} | {c.challenge_type:20} | {c.best_score:.1f}%")
    
    # Count unique challenge types with badges
    unique_types = set(badge.challenge_type for badge in badges)
    print(f"\n📊 Summary:")
    print(f"  Total badge records: {len(badges)}")
    print(f"  Unique challenge types: {len(unique_types)}")
    print(f"  Completed challenges: {sum(1 for c in challenges if c.is_completed)}")
    
    # Expected display
    print(f"\n🎯 Expected Dashboard Display:")
    completed_challenges = [c for c in challenges if c.is_completed]
    valid_badge_count = len(set(c.challenge_type for c in completed_challenges))
    print(f"  Badge Count: {valid_badge_count}")
    print(f"  Challenges Complete: {len(completed_challenges)}/{len(challenges)}")
    
    # Check for issues
    if len(badges) != len(unique_types):
        print(f"\n⚠️  WARNING: Duplicate badges detected!")
        print(f"  Found {len(badges)} badge records but only {len(unique_types)} unique challenge types")
        print(f"  Recommendation: Clean up duplicate badges")

EOF

echo ""
echo "✅ Diagnostic complete!"
echo ""
