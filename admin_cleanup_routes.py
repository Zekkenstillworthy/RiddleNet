"""
Badge Cleanup Admin Route
Add to your Flask app temporarily to clean up old badges
"""
from flask import Blueprint, jsonify
from user.models.user_badge import UserBadge
from user.models.challenge_score import ChallengeScore
from __init__ import db

# Create admin blueprint for one-time cleanup
admin_cleanup_bp = Blueprint('admin_cleanup', __name__)

@admin_cleanup_bp.route('/admin/cleanup-badges')
def cleanup_badges():
    """
    One-time cleanup: Remove badges awarded under old 75% threshold
    Access via: http://localhost:5000/admin/cleanup-badges
    """
    try:
        removed_badges = []
        
        # Find all rare badges with < 100% scores
        rare_badges = UserBadge.query.filter(
            UserBadge.badge_rarity == 'rare',
            UserBadge.earned_score < 100
        ).all()
        
        for badge in rare_badges:
            removed_badges.append({
                'badge_name': badge.badge_name,
                'user_id': badge.user_id,
                'score': badge.earned_score,
                'challenge': badge.challenge_type
            })
            db.session.delete(badge)
        
        # Also check for badges where the user's best score is < 100%
        all_badges = UserBadge.query.all()
        for badge in all_badges:
            challenge_score = ChallengeScore.query.filter_by(
                user_id=badge.user_id,
                challenge_type=badge.challenge_type
            ).first()
            
            if challenge_score and challenge_score.best_score < 100:
                removed_badges.append({
                    'badge_name': badge.badge_name,
                    'user_id': badge.user_id,
                    'score': badge.earned_score,
                    'challenge': badge.challenge_type,
                    'reason': f'Best score only {challenge_score.best_score}%'
                })
                db.session.delete(badge)
        
        # Remove duplicates (safety check)
        all_badges_after = UserBadge.query.all()
        seen = {}
        duplicates = []
        
        for badge in all_badges_after:
            key = f"{badge.user_id}_{badge.badge_id}"
            if key in seen:
                duplicates.append({
                    'badge_name': badge.badge_name,
                    'user_id': badge.user_id,
                    'reason': 'Duplicate'
                })
                db.session.delete(badge)
            else:
                seen[key] = badge
        
        # Commit all deletions
        db.session.commit()
        
        # Get remaining badges
        remaining_badges = UserBadge.query.all()
        remaining_list = [{
            'badge_name': b.badge_name,
            'user_id': b.user_id,
            'score': b.earned_score,
            'rarity': b.badge_rarity
        } for b in remaining_badges]
        
        return jsonify({
            'success': True,
            'removed_count': len(removed_badges) + len(duplicates),
            'removed_badges': removed_badges,
            'duplicates_removed': duplicates,
            'remaining_count': len(remaining_badges),
            'remaining_badges': remaining_list
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Register this blueprint in your application.py temporarily
