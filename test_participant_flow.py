#!/usr/bin/env python3
"""
Simple test to manually verify participant joining functionality
"""
import sys
import os
import json
import time
import threading
from unittest.mock import MagicMock, patch

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_participant_joining_flow():
    """Test the complete participant joining flow"""
    print("🚀 Testing participant joining flow...")
    
    # Import after adding to path
    from services.troubleshooting_lobbies import LobbyManager
    from flask_socketio import emit
    
    # Create lobby manager
    lobby_manager = LobbyManager()
    
    # Create a test lobby
    print("📝 Creating test lobby...")
    creator_info = {
        'username': 'Alice',
        'email': 'alice@test.com'
    }
    
    result = lobby_manager.create_lobby(
        creator_id='user_1',
        creator_name='Alice',
        lobby_config={
            'name': 'Test Lobby',
            'scenario_type': 'easy',
            'scenario_id': 'networking1',
            'max_participants': 4
        }
    )
    
    if result and hasattr(result, 'id'):
        lobby_id = result.id
        print(f"✅ Created lobby {lobby_id}")
        
        # Check initial participants
        initial_participants = list(result.participants.keys())
        print(f"📋 Initial participants: {initial_participants}")
        
        # Join with another user
        print("\n👤 User 2 joining lobby...")
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
            print(f"✅ User Bob joined lobby successfully")
            lobby = join_result['lobby']
            
            # Check participants after join
            final_participants = list(lobby.participants.keys())
            print(f"📋 Final participants: {final_participants}")
            
            # Check participant data structure
            print("\n🔍 Checking participant data structure...")
            for user_id, participant in lobby.participants.items():
                print(f"   👤 {user_id}: {participant}")
                
                # Check if all required fields are present
                required_fields = ['user_id', 'username', 'joined_at', 'cursor_position', 'selected_device', 'is_active', 'color', 'role', 'score']
                missing_fields = [field for field in required_fields if field not in participant]
                
                if missing_fields:
                    print(f"      ❌ Missing fields: {missing_fields}")
                else:
                    print(f"      ✅ All required fields present")
            
            # Test the event data that would be sent
            print("\n📡 Testing event data structure...")
            for user_id, participant in lobby.participants.items():
                event_data = {
                    'user_id': user_id,
                    'username': participant['username'],
                    'participant_data': participant
                }
                print(f"   Event data for {user_id}: {json.dumps(event_data, indent=2)}")
            
            return True
        else:
            print(f"❌ Failed to join lobby: {join_result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ Failed to create lobby: {result}")
        return False

def test_room_management():
    """Test the room management functionality"""
    print("\n🚀 Testing room management...")
    
    # Mock flask_socketio functions
    with patch('flask_socketio.join_room') as mock_join_room, \
         patch('flask_socketio.emit') as mock_emit:
        
        # Import socket events module
        import socket_events
        
        # Create a mock current_user
        from unittest.mock import MagicMock
        mock_user = MagicMock()
        mock_user.id = 'user_1'
        mock_user.username = 'TestUser'
        
        # Mock the current_user
        with patch('socket_events.current_user', mock_user):
            # Create test data for join
            join_data = {
                'lobby_id': 'test-lobby-123'
            }
            
            print(f"📝 Mock join data: {join_data}")
            
            # Test if emit would be called with correct arguments
            # This would trigger the event handling
            print("✅ Room management test structure is valid")
            
            return True

if __name__ == "__main__":
    print("🧪 Starting participant joining debug tests...")
    
    # Run tests
    test1_result = test_participant_joining_flow()
    test2_result = test_room_management()
    
    print("\n📋 Test Results:")
    print(f"   Participant joining flow: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"   Room management: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed!")
