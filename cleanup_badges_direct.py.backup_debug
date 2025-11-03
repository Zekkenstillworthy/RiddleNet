"""
Direct Database Badge Cleanup
Run this from Flask shell: flask shell < cleanup_badges_direct.py
Or manually in Python shell
"""

# Delete all rare badges that were awarded with < 100% score
print("🧹 Cleaning up badges awarded under old 75% threshold...")

from user.models.user_badge import UserBadge
from __init__ import db

# Find and remove rare badges with < 100% scores
rare_badges_to_remove = UserBadge.query.filter(
    UserBadge.badge_rarity == 'rare',
    UserBadge.earned_score < 100
).all()

print(f"Found {len(rare_badges_to_remove)} rare badges with < 100% scores:")
for badge in rare_badges_to_remove:
    print(f"  - {badge.badge_name} (User {badge.user_id}, Score: {badge.earned_score}%)")
    db.session.delete(badge)

# Also remove any duplicate badges (safety check)
all_badges = UserBadge.query.all()
seen = {}
duplicates = []

for badge in all_badges:
    key = f"{badge.user_id}_{badge.badge_id}"
    if key in seen:
        # Keep the first one (most recent), remove duplicates
        duplicates.append(badge)
        print(f"  - Duplicate: {badge.badge_name} (User {badge.user_id})")
    else:
        seen[key] = badge

for dup in duplicates:
    db.session.delete(dup)

# Commit changes
db.session.commit()

print(f"✅ Removed {len(rare_badges_to_remove)} rare badges with < 100%")
print(f"✅ Removed {len(duplicates)} duplicate badges")
print(f"✅ Cleanup complete!")

# Show remaining badges
remaining = UserBadge.query.all()
print(f"\n📊 Remaining badges: {len(remaining)}")
for badge in remaining:
    print(f"  ✓ {badge.badge_name} ({badge.badge_rarity}, {badge.earned_score}%)")
