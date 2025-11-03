#!/usr/bin/env python3
"""
Fix Link Up! Progress Data Migration Script

Problem: Older Link Up completions stored scenario_id in metadata root,
         but new code expects completed_challenges array.

Solution: Migrate existing scenario_id to completed_challenges array.
"""

import sys
import os

# Add the RiddleNet directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application import create_app, db
from user.models.challenge_score import ChallengeScore
from sqlalchemy.orm.attributes import flag_modified

def fix_linkup_progress():
    """Migrate Link Up progress data to new completed_challenges format"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("🔧 LINK UP! PROGRESS DATA MIGRATION")
        print("=" * 80)
        
        # Get all troubleshooting challenge scores
        linkup_scores = ChallengeScore.query.filter_by(
            challenge_type='troubleshooting'
        ).all()
        
        print(f"\n📊 Found {len(linkup_scores)} Link Up! challenge records")
        
        fixed_count = 0
        already_correct = 0
        
        for score in linkup_scores:
            user_id = score.user_id
            print(f"\n👤 User ID: {user_id}")
            
            if not score.challenge_metadata:
                print(f"   ⚠️  No metadata - skipping")
                continue
            
            metadata = score.challenge_metadata
            
            # Check if already has completed_challenges array
            if 'completed_challenges' in metadata:
                completed = metadata.get('completed_challenges', [])
                print(f"   ✅ Already has completed_challenges array: {len(completed)} items")
                print(f"      Items: {completed}")
                already_correct += 1
                continue
            
            # Check if has old scenario_id format
            if 'scenario_id' in metadata:
                scenario_id = metadata.get('scenario_id')
                print(f"   🔧 MIGRATING: Found scenario_id='{scenario_id}'")
                
                # Create completed_challenges array with this scenario
                metadata['completed_challenges'] = [scenario_id]
                
                # Mark as modified for SQLAlchemy
                flag_modified(score, 'challenge_metadata')
                
                print(f"   ✅ MIGRATED: Created completed_challenges=['{scenario_id}']")
                fixed_count += 1
            else:
                print(f"   ℹ️  No scenario_id found - empty progress")
        
        if fixed_count > 0:
            print(f"\n💾 Committing {fixed_count} changes to database...")
            db.session.commit()
            print(f"✅ Database updated successfully!")
        else:
            print(f"\n✅ No migration needed - all records already correct")
        
        print("\n" + "=" * 80)
        print("📊 MIGRATION SUMMARY:")
        print("=" * 80)
        print(f"Total records: {len(linkup_scores)}")
        print(f"✅ Already correct: {already_correct}")
        print(f"🔧 Migrated: {fixed_count}")
        print(f"ℹ️  Empty progress: {len(linkup_scores) - already_correct - fixed_count}")
        print("=" * 80)
        
        return fixed_count

if __name__ == '__main__':
    try:
        fixed = fix_linkup_progress()
        print(f"\n🎉 Migration complete! Fixed {fixed} records.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
