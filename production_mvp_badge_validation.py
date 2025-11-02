#!/usr/bin/env python3
"""
🔍 MVP Production Badge & Progress Validation Script
====================================================

This script validates that the badge distribution and progress percentage 
calculations are accurate and complementing each other in production.

Run on production server:
    ssh -i riddlenetv1.pem ubuntu@54.66.229.118
    cd /home/ubuntu/RiddleNet
    python3 production_mvp_badge_validation.py
"""

import sys
import os

# Add the application directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application import create_app
from user.models.challenge_score import ChallengeScore
from user.models.user_badge import UserBadge
from user.models import User as UserModel
from sqlalchemy import func


def validate_badge_logic():
    """Validate badge distribution and progress percentage accuracy"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*100)
        print("🎯 MVP BADGE & PROGRESS VALIDATION - PRODUCTION SERVER")
        print("="*100)
        
        # Get all users with badges or challenge scores
        users_with_data = UserModel.query.join(
            UserBadge, UserModel.id == UserBadge.user_id, isouter=True
        ).join(
            ChallengeScore, UserModel.id == ChallengeScore.user_id, isouter=True
        ).distinct().all()
        
        print(f"\n📊 Total users with badges or challenge data: {len(users_with_data)}")
        
        issues_found = []
        
        for user in users_with_data:
            print(f"\n{'─'*100}")
            print(f"👤 USER: {user.username} (ID: {user.id})")
            print(f"{'─'*100}")
            
            # Get user's challenges
            challenges = ChallengeScore.query.filter_by(user_id=user.id).all()
            badges = UserBadge.query.filter_by(user_id=user.id).all()
            
            print(f"\n  📈 CHALLENGE PROGRESS:")
            challenge_status = {}
            
            for challenge_type in ['crimping', 'osi', 'troubleshooting', 'quiz']:
                challenge = ChallengeScore.query.filter_by(
                    user_id=user.id, 
                    challenge_type=challenge_type
                ).first()
                
                if challenge:
                    if challenge_type == 'troubleshooting':
                        # Link Up! - calculate from sub-items
                        if challenge.challenge_metadata:
                            completed = challenge.challenge_metadata.get('completed_challenges', [])
                            counts = challenge.challenge_metadata.get('challenge_counts', {})
                            TOTAL = 12  # Foundation (3) + Easy (3) + Medium (3) + Hard (3)
                            completed_count = len(completed)
                            progress = (completed_count / TOTAL) * 100
                            is_complete = completed_count >= TOTAL
                            
                            print(f"    🔧 Link Up! (Troubleshooting):")
                            print(f"       Completed: {completed_count}/{TOTAL} sub-items")
                            print(f"       Foundation: {counts.get('foundation', 0)}/3")
                            print(f"       Easy: {counts.get('easy', 0)}/3")
                            print(f"       Medium: {counts.get('medium', 0)}/3")
                            print(f"       Hard: {counts.get('hard', 0)}/3")
                            print(f"       Progress: {progress:.1f}%")
                            print(f"       Complete: {'✅ YES' if is_complete else '❌ NO'}")
                            
                            challenge_status[challenge_type] = {
                                'progress': progress,
                                'is_complete': is_complete,
                                'completed_count': completed_count,
                                'total': TOTAL
                            }
                        else:
                            print(f"    🔧 Link Up! (Troubleshooting): No metadata found")
                            challenge_status[challenge_type] = {'progress': 0, 'is_complete': False}
                    
                    elif challenge_type == 'crimping':
                        # Crimping - score-based
                        score = ChallengeScore.effective_best_score(challenge)
                        is_complete = score >= 100
                        
                        print(f"    🔌 Crimping Simulation:")
                        print(f"       Score: {score:.1f}%")
                        print(f"       Complete: {'✅ YES' if is_complete else '❌ NO'}")
                        
                        challenge_status[challenge_type] = {
                            'progress': score,
                            'is_complete': is_complete
                        }
                    
                    elif challenge_type == 'osi':
                        # OSI - two-level challenge
                        score = ChallengeScore.effective_best_score(challenge)
                        is_complete = ChallengeScore.is_effectively_completed(challenge) and score >= 100
                        
                        metadata = challenge.challenge_metadata or {}
                        challenge_data = metadata.get('challenge_data', {})
                        level1 = challenge_data.get('level1_score', 0)
                        level2 = challenge_data.get('level2_score', 0)
                        both = challenge_data.get('both_levels_complete', False)
                        
                        print(f"    🌐 OSI Model & TCP/IP:")
                        print(f"       Level 1 (OSI): {level1}%")
                        print(f"       Level 2 (TCP/IP): {level2}%")
                        print(f"       Both Complete: {both}")
                        print(f"       Effective Score: {score:.1f}%")
                        print(f"       Complete: {'✅ YES' if is_complete else '❌ NO'}")
                        
                        challenge_status[challenge_type] = {
                            'progress': score,
                            'is_complete': is_complete
                        }
                    
                    elif challenge_type == 'quiz':
                        # Quiz - score-based
                        score = challenge.best_score or 0
                        is_complete = score >= 100
                        
                        print(f"    📝 Quiz Challenge:")
                        print(f"       Score: {score:.1f}%")
                        print(f"       Complete: {'✅ YES' if is_complete else '❌ NO'}")
                        
                        challenge_status[challenge_type] = {
                            'progress': score,
                            'is_complete': is_complete
                        }
            
            # Validate badges
            print(f"\n  🏆 BADGES:")
            if badges:
                print(f"    Total in database: {len(badges)}")
                
                for badge in badges:
                    challenge_type = badge.challenge_type
                    status = challenge_status.get(challenge_type, {})
                    is_complete = status.get('is_complete', False)
                    progress = status.get('progress', 0)
                    
                    # Check if badge should exist
                    if is_complete:
                        print(f"    ✅ VALID: {badge.badge_name} ({challenge_type}) - Challenge at 100%")
                    else:
                        print(f"    ❌ INVALID: {badge.badge_name} ({challenge_type})")
                        print(f"       ⚠️ Badge exists but challenge is only {progress:.1f}% complete!")
                        
                        # Add to issues list
                        issue = {
                            'user_id': user.id,
                            'username': user.username,
                            'badge_id': badge.badge_id,
                            'badge_name': badge.badge_name,
                            'challenge_type': challenge_type,
                            'progress': progress,
                            'is_complete': is_complete
                        }
                        
                        if challenge_type == 'troubleshooting':
                            issue['completed_count'] = status.get('completed_count', 0)
                            issue['total'] = status.get('total', 12)
                        
                        issues_found.append(issue)
            else:
                print(f"    No badges awarded")
            
            # Check for missing badges
            print(f"\n  🔍 MISSING BADGES CHECK:")
            completed_without_badge = []
            for challenge_type, status in challenge_status.items():
                if status.get('is_complete', False):
                    has_badge = any(b.challenge_type == challenge_type for b in badges)
                    if not has_badge:
                        print(f"    ⚠️ {challenge_type}: 100% complete but NO BADGE!")
                        completed_without_badge.append({
                            'user_id': user.id,
                            'username': user.username,
                            'challenge_type': challenge_type,
                            'progress': status.get('progress', 0)
                        })
                    else:
                        print(f"    ✅ {challenge_type}: Badge exists")
            
            # Dashboard consistency check
            completed_challenges = sum(1 for s in challenge_status.values() if s.get('is_complete', False))
            valid_badges = sum(1 for b in badges if challenge_status.get(b.challenge_type, {}).get('is_complete', False))
            
            print(f"\n  📊 DASHBOARD CONSISTENCY:")
            print(f"    Challenges Complete: {completed_challenges}/4")
            print(f"    Valid Badges: {valid_badges}")
            print(f"    Total Badges in DB: {len(badges)}")
            
            if completed_challenges != valid_badges:
                print(f"    ⚠️ INCONSISTENCY: Challenges complete ({completed_challenges}) != Valid badges ({valid_badges})")
            else:
                print(f"    ✅ CONSISTENT: Challenges and badges match")
        
        # Summary Report
        print(f"\n{'='*100}")
        print("📋 VALIDATION SUMMARY")
        print(f"{'='*100}")
        
        if issues_found:
            print(f"\n❌ ISSUES FOUND: {len(issues_found)} invalid badges")
            print("\nInvalid badges (should be removed):")
            for issue in issues_found:
                if issue['challenge_type'] == 'troubleshooting':
                    print(f"  • User: {issue['username']} (ID: {issue['user_id']})")
                    print(f"    Badge: {issue['badge_name']} ({issue['challenge_type']})")
                    print(f"    Progress: {issue['completed_count']}/{issue['total']} ({issue['progress']:.1f}%)")
                else:
                    print(f"  • User: {issue['username']} (ID: {issue['user_id']})")
                    print(f"    Badge: {issue['badge_name']} ({issue['challenge_type']})")
                    print(f"    Progress: {issue['progress']:.1f}%")
        else:
            print("\n✅ NO ISSUES FOUND: All badges are valid!")
        
        if issues_found:
            print(f"\n🔧 TO FIX ISSUES, RUN:")
            print(f"    python3 cleanup_invalid_badges.py")
        
        print(f"\n{'='*100}\n")


if __name__ == "__main__":
    validate_badge_logic()
