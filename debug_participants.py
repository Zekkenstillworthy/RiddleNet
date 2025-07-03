#!/usr/bin/env python3
"""
Debug script to test participant joining events
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from services.troubleshooting_lobbies import LobbyManager
from flask import Flask
from flask_socketio import SocketIO, emit
from unittest.mock import MagicMock
import json

def test_participant_joining():
    """Test the participant joining flow"""
    print("🔍 Testing participant joining flow...")
    
    # Create lobby manager
    lobby_manager = LobbyManager()
    
    # Create a test lobby
    creator_info = {
        'username': 'Alice',
        'email': 'alice@test.com'
    }
    
    result = lobby_manager.create_lobby(
        creator_id='user_1',
        creator_info=creator_info,
        scenario_id='networking1',
        max_participants=4
    )
    
    if result['success']:
        lobby_id = result['lobby'].id
        print(f"✅ Created lobby {lobby_id}")
        
        # Try to join with another user
        joiner_info = {
            'username': 'Bob',
            'email': 'bob@test.com'
        }
        
        join_result = lobby_manager.join_lobby(
            lobby_id=lobby_id,
            user_id='user_2',
            user_info=joiner_info
        )
        
        if join_result['success']:
            print(f"✅ User Bob joined lobby")
            print(f"📋 Participants: {list(join_result['lobby'].participants.keys())}")
            
            # Check participant data
            participants = join_result['lobby'].participants
            for user_id, participant in participants.items():
                print(f"   👤 {user_id}: {participant['username']} (role: {participant['role']})")
                
            return True
        else:
            print(f"❌ Failed to join lobby: {join_result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ Failed to create lobby: {result.get('error', 'Unknown error')}")
        return False

def test_participant_data_structure():
    """Test the participant data structure"""
    print("\n🔍 Testing participant data structure...")
    
    lobby_manager = LobbyManager()
    
    # Create lobby
    result = lobby_manager.create_lobby(
        creator_id='user_1',
        creator_info={'username': 'Alice', 'email': 'alice@test.com'},
        scenario_id='networking1'
    )
    
    if result['success']:
        lobby = result['lobby']
        print("✅ Lobby created successfully")
        
        # Check participant data structure
        participant_data = lobby.participants['user_1']
        required_fields = ['user_id', 'username', 'joined_at', 'cursor_position', 'selected_device', 'is_active', 'color', 'role', 'score']
        
        print(f"📋 Participant data structure:")
        for field in required_fields:
            if field in participant_data:
                print(f"   ✅ {field}: {participant_data[field]}")
            else:
                print(f"   ❌ {field}: MISSING")
                
        return True
    else:
        print(f"❌ Failed to create lobby")
        return False

if __name__ == "__main__":
    print("🚀 Starting participant joining debug test...")
    
    test1_result = test_participant_joining()
    test2_result = test_participant_data_structure()
    
    if test1_result and test2_result:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
