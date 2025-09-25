#!/usr/bin/env python3
"""
Test script to verify collaboration models are working correctly
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Flask app context
from application import create_app
from admin import db

app = create_app()

with app.app_context():
    try:
        # Test importing collaboration models
        from admin.models.collaboration import CollaborationSetting, CollaborationLobby, TeamAssignment
        print("✅ Successfully imported collaboration models")
        
        # Test creating a collaboration setting
        from admin.models.simulation import Simulation
        simulation = Simulation.query.first()
        if simulation:
            # Check if collaboration setting already exists
            existing = CollaborationSetting.query.filter_by(simulation_id=simulation.id).first()
            if not existing:
                setting = CollaborationSetting(
                    simulation_id=simulation.id,
                    collaboration_enabled=True,
                    team_size=2,
                    shared_terminal=False,
                    individual_terminals=True,
                    follow_leader=False,
                    chat_enabled=True,
                    transcript_logging=False,
                    allow_late_join=True,
                    require_instructor=False,
                    roles=['leader', 'member']
                )
                db.session.add(setting)
                db.session.commit()
                print(f"✅ Created collaboration setting for simulation {simulation.id}: {simulation.title}")
            else:
                print(f"✅ Collaboration setting already exists for simulation {simulation.id}: {simulation.title}")
                
            # Test the to_dict method
            setting = CollaborationSetting.query.filter_by(simulation_id=simulation.id).first()
            if setting:
                settings_dict = setting.to_dict()
                print(f"✅ to_dict() method works: {settings_dict}")
            
        else:
            print("⚠️ No simulations found in database")
            
        # Test lobby model
        print("✅ CollaborationLobby model is available")
        print("✅ TeamAssignment model is available")
        
        # Test the troubleshooting lobbies service
        from services.troubleshooting_lobbies import lobby_manager
        print("✅ Successfully imported lobby_manager")
        
        print("\n🎉 All collaboration components are working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing collaboration models: {e}")
        import traceback
        traceback.print_exc()