#!/usr/bin/env python3
"""
Fix OSI completion status for users who have completed both levels
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_osi_completion():
    """Fix OSI completion status"""
    from application import create_app
    from user.models.challenge_score import ChallengeScore
    from __init__ import db
    
    app = create_app()
    
    with app.app_context():
        print(f"\n{'='*80}")
        print(f"Fixing OSI Completion Status")
        print(f"{'='*80}\n")
        
        # Find all OSI challenges where both levels are complete but is_completed is False
        osi_challenges = ChallengeScore.query.filter_by(challenge_type='osi').all()
        
        fixed_count = 0
        for challenge in osi_challenges:
            metadata = challenge.challenge_metadata or {}
            challenge_data = metadata.get('challenge_data', {})
            
            level1_score = challenge_data.get('level1_score', 0)
            level2_score = challenge_data.get('level2_score', 0)
            both_levels_complete = challenge_data.get('both_levels_complete', False)
            
            # Check if both levels are at 100% but challenge is not marked complete
            if level1_score == 100 and level2_score == 100 and not challenge.is_completed:
                print(f"User ID {challenge.user_id}:")
                print(f"  Current Status: is_completed = {challenge.is_completed}")
                print(f"  Level 1: {level1_score}%, Level 2: {level2_score}%")
                print(f"  Both Complete Flag: {both_levels_complete}")
                
                # Update completion status
                challenge.is_completed = True
                if not challenge.first_completed_at:
                    challenge.first_completed_at = challenge.updated_at
                challenge.last_completed_at = challenge.updated_at
                
                # Also update the both_levels_complete flag in metadata if not set
                if not both_levels_complete:
                    challenge_data['both_levels_complete'] = True
                    metadata['challenge_data'] = challenge_data
                    challenge.challenge_metadata = metadata
                
                print(f"  ✅ Fixed: is_completed = True")
                print()
                fixed_count += 1
        
        if fixed_count > 0:
            db.session.commit()
            print(f"✅ Fixed {fixed_count} OSI challenge(s)")
        else:
            print(f"✅ No OSI challenges needed fixing")
        
        print(f"\n{'='*80}\n")

if __name__ == '__main__':
    fix_osi_completion()
