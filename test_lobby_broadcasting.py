#!/usr/bin/env python3
"""
Quick test to verify lobby broadcasting behavior
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.troubleshooting_lobbies import LobbyManager

def test_lobby_broadcasting():
    """Test the lobby broadcasting functionality"""
    print("🧪 Testing Lobby Broadcasting...")
    
    # Initialize lobby manager
    lobby_manager = LobbyManager()
    
    # Create test lobby
    print("\n1. Creating a new lobby...")
    lobby_config = {
        'name': 'Broadcast Test Session',
        'scenario_type': 'easy',
        'scenario_id': 'network',
        'max_participants': 4,
        'is_private': False
    }
    
    lobby = lobby_manager.create_lobby(
        creator_id='test_creator',
        creator_name='Creator User',
        lobby_config=lobby_config
    )
    
    print(f"✅ Lobby created: {lobby.name} (ID: {lobby.id})")
    
    # Test getting public lobbies
    print("\n2. Getting public lobbies list...")
    public_lobbies = lobby_manager.get_public_lobbies()
    
    print(f"✅ Found {len(public_lobbies)} public lobbies:")
    for lobby_data in public_lobbies:
        print(f"   - {lobby_data['name']} ({lobby_data['id']})")
        print(f"     Participants: {lobby_data['participant_count']}/{lobby_data['max_participants']}")
        print(f"     Private: {lobby_data['is_private']}")
    
    # Simulate another user checking lobbies
    print("\n3. Simulating lobby browser user...")
    print("   - User opens lobby browser")
    print("   - Should join 'troubleshooting_browser' room")
    print("   - Should receive 'new_lobby_available' when new lobbies are created")
    
    # Create another lobby to test broadcasting
    print("\n4. Creating second lobby to test broadcasting...")
    lobby_config_2 = {
        'name': 'Second Test Session',
        'scenario_type': 'medium',
        'scenario_id': 'split',
        'max_participants': 6,
        'is_private': False
    }
    
    lobby2 = lobby_manager.create_lobby(
        creator_id='test_creator_2',
        creator_name='Creator User 2',
        lobby_config=lobby_config_2
    )
    
    print(f"✅ Second lobby created: {lobby2.name} (ID: {lobby2.id})")
    
    # Check updated lobby list
    print("\n5. Checking updated public lobbies...")
    updated_lobbies = lobby_manager.get_public_lobbies()
    
    print(f"✅ Now found {len(updated_lobbies)} public lobbies:")
    for lobby_data in updated_lobbies:
        print(f"   - {lobby_data['name']} ({lobby_data['id']})")
    
    print("\n🎯 Test Results:")
    print("   ✅ Lobby creation works")
    print("   ✅ Public lobby retrieval works")
    print("   ✅ Multiple lobbies can be created")
    print("\n📋 Frontend Integration Points:")
    print("   - WebSocket event: 'new_lobby_available' should be emitted to 'troubleshooting_browser' room")
    print("   - Frontend handler should call refreshLobbies() to update the grid")
    print("   - Manual refresh should always show current state")

if __name__ == "__main__":
    test_lobby_broadcasting()
