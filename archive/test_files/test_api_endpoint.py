"""
Quick test script to diagnose the 500 error
"""
from flask import Flask
from __init__ import db
from user.models.challenge_progress import ChallengeProgress
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///riddlenet.db'  # Adjust if different
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    try:
        print("🔍 Testing ChallengeProgress query...")
        
        # Test query (use user_id = 1 or adjust as needed)
        user_id = 1
        challenge_type = 'linkup'
        
        progress = ChallengeProgress.query.filter_by(
            user_id=user_id,
            challenge_type=challenge_type
        ).first()
        
        if progress:
            print(f"✅ Found progress record for user {user_id}")
            print(f"📊 State data keys: {list(progress.state_data.keys()) if progress.state_data else 'None'}")
            print(f"📅 Last updated: {progress.last_updated}")
            print(f"📅 Last updated type: {type(progress.last_updated)}")
            
            if progress.last_updated:
                try:
                    iso_date = progress.last_updated.isoformat()
                    print(f"✅ Datetime serialization works: {iso_date}")
                except Exception as e:
                    print(f"❌ Datetime serialization failed: {e}")
            else:
                print(f"⚠️ last_updated is None")
                
            if progress.state_data:
                if 'completed_scenarios' in progress.state_data:
                    scenarios = progress.state_data['completed_scenarios']
                    print(f"✅ Found {len(scenarios)} completed scenarios")
                elif 'scenario_id' in progress.state_data:
                    print(f"✅ Found legacy scenario_id: {progress.state_data['scenario_id']}")
        else:
            print(f"ℹ️ No progress record found for user {user_id}, type {challenge_type}")
            
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ ERROR during test:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
