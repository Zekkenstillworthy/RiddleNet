"""
Retroactive Badge Award Script
Awards badges to users who have already completed challenges but didn't receive badges
"""
from __init__ import db, create_app
from user.models.challenge_score import ChallengeScore
from user.models.user_badge import UserBadge
from user.services.badge_service import BadgeService

app = create_app()

with app.app_context():
    print("=" * 60)
    print("🏆 RETROACTIVE BADGE AWARD SCRIPT")
    print("=" * 60)
    
    # Get all challenge scores
    all_scores = ChallengeScore.query.all()
    
    print(f"\nFound {len(all_scores)} challenge score records")
    print("\nProcessing each score for badge eligibility...\n")
    
    total_badges_awarded = 0
    
    for score_record in all_scores:
        user_id = score_record.user_id
        challenge_type = score_record.challenge_type
        score = score_record.best_score
        metadata = score_record.challenge_metadata or {}
        
        print(f"\n📊 Checking User {user_id} - {challenge_type} (Score: {score}%)")
        
        # Check and award badges
        try:
            newly_earned = BadgeService.check_and_award_badges(
                user_id=user_id,
                challenge_type=challenge_type,
                score=score,
                metadata=metadata
            )
            
            if newly_earned:
                print(f"   ✅ Awarded {len(newly_earned)} badge(s):")
                for badge in newly_earned:
                    print(f"      - {badge['badge_name']} ({badge['badge_rarity']})")
                    total_badges_awarded += 1
            else:
                print(f"   ℹ️  No new badges (already earned or score too low)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Commit all changes
    try:
        db.session.commit()
        print("\n" + "=" * 60)
        print(f"✅ SUCCESS: Awarded {total_badges_awarded} badge(s) total!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ ERROR committing to database: {e}")
        db.session.rollback()
    
    # Show summary
    print("\n📈 BADGE SUMMARY BY USER:")
    print("-" * 60)
    
    from user.models.user import User
    users_with_badges = db.session.query(User.id, User.username).join(UserBadge).distinct().all()
    
    for user_id, username in users_with_badges:
        badges = UserBadge.query.filter_by(user_id=user_id).all()
        print(f"\n👤 {username} (ID: {user_id}) - {len(badges)} badge(s):")
        for badge in badges:
            print(f"   🏆 {badge.badge_name} - {badge.badge_description}")
    
    print("\n" + "=" * 60)
    print("✅ Script complete!")
    print("=" * 60)
