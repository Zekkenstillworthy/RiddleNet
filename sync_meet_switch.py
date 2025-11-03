#!/usr/bin/env python3
"""
Sync 'meet-switch' completion to backend database
"""
from application import create_app, db
from user.models.challenge_score import ChallengeScore
from sqlalchemy.orm.attributes import flag_modified

app = create_app()
with app.app_context():
    # Get Gilbert's Link Up! challenge score
    cs = ChallengeScore.query.filter_by(
        user_id=1,
        challenge_type='troubleshooting'
    ).first()
    
    if not cs:
        print("❌ No challenge score found for user 1")
        exit(1)
    
    # Get existing completed_challenges
    completed = cs.challenge_metadata.get('completed_challenges', [])
    print(f"📊 Current completed_challenges: {completed}")
    print(f"📊 Current count: {len(completed)}/26")
    print(f"📊 Current progress: {cs.best_score:.1f}%")
    
    # Add meet-switch if not already present
    if 'meet-switch' not in completed:
        completed.append('meet-switch')
        cs.challenge_metadata['completed_challenges'] = completed
        cs.best_score = (len(completed) / 26) * 100.0
        flag_modified(cs, 'challenge_metadata')
        db.session.commit()
        print(f"\n✅ Added 'meet-switch' to completed_challenges")
        print(f"✅ New count: {len(completed)}/26")
        print(f"✅ New progress: {cs.best_score:.1f}%")
    else:
        print(f"\nℹ️ 'meet-switch' already in completed_challenges")
