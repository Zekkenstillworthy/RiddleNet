"""
Debug script to check what challenge statistics are being calculated
"""
from __init__ import db, create_app
from user.models.challenge_score import ChallengeScore

app = create_app()

with app.app_context():
    # Get user Gilbert's (ID: 1) challenge scores
    user_id = 1
    
    print("=" * 60)
    print("🔍 DEBUGGING DASHBOARD STATISTICS FOR USER ID:", user_id)
    print("=" * 60)
    
    # Get ALL challenge records
    all_challenges = ChallengeScore.query.filter_by(user_id=user_id).all()
    print(f"\n📊 Total Challenge Records in Database: {len(all_challenges)}")
    
    for challenge in all_challenges:
        print(f"\n  Challenge Type: {challenge.challenge_type}")
        print(f"    - Best Score: {challenge.best_score}%")
        print(f"    - Is Completed: {challenge.is_completed}")
        print(f"    - Total Attempts: {challenge.total_attempts}")
    
    # Get stats using the fixed method
    print("\n" + "=" * 60)
    print("✅ USING FIXED get_user_stats() METHOD")
    print("=" * 60)
    
    stats = ChallengeScore.get_user_stats(user_id)
    
    print(f"\n📈 Calculated Statistics:")
    print(f"  - Completed Challenges: {stats['total_challenges_completed']}/{stats['total_challenges']}")
    print(f"  - Average Score: {stats['average_score']:.1f}%")
    print(f"  - Total Attempts: {stats['total_attempts']}")
    print(f"  - Completion Rate: {stats['completion_rate']:.1f}%")
    
    # Show which challenges were counted
    MAIN_CHALLENGE_TYPES = ['crimping', 'osi', 'troubleshooting', 'quiz']
    filtered_challenges = ChallengeScore.query.filter_by(user_id=user_id).filter(
        ChallengeScore.challenge_type.in_(MAIN_CHALLENGE_TYPES)
    ).all()
    
    print(f"\n🎯 Main Challenge Types Found: {len(filtered_challenges)}")
    total_best_scores = 0
    for challenge in filtered_challenges:
        print(f"  - {challenge.challenge_type}: {challenge.best_score}% (Completed: {challenge.is_completed})")
        total_best_scores += challenge.best_score
    
    print(f"\n🧮 Calculation Breakdown:")
    print(f"  Sum of best scores: {total_best_scores}")
    print(f"  Divided by 4 (total challenges): {total_best_scores} / 4 = {total_best_scores / 4:.1f}%")
    
    print("\n" + "=" * 60)
    print("✅ DEBUG COMPLETE")
    print("=" * 60)
