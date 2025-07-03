#!/usr/bin/env python3
"""
Test script to verify chat message functionality in the collaborative troubleshooting system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.troubleshooting_lobbies import TroubleshootingLobby
from datetime import datetime

def test_chat_messages():
    """Test chat message creation and retrieval"""
    print("🧪 Testing Chat Message Functionality")
    print("=" * 50)
    
    # Create a test lobby directly
    lobby = TroubleshootingLobby(
        id='TEST123',
        name='Chat Test Lobby',
        scenario_type='easy',
        scenario_id='network',
        creator_id='test_user_1',
        creator_name='Test User 1'
    )
    
    # Add creator as participant
    lobby.add_participant('test_user_1', {
        'username': 'Test User 1',
        'profile_image': 'test_user_1.jpg'
    })
    
    print(f"✅ Created lobby: {lobby.id}")
    print(f"📋 Lobby name: {lobby.name}")
    
    # Add a welcome system message
    welcome_msg = lobby.add_chat_message('system', 'Welcome to Chat Test Lobby! Session created successfully.', 'system')
    print(f"\n🤖 Added welcome message: {welcome_msg['message']}")
    
    # Add another participant
    user2_info = {
        'username': 'Test User 2',
        'profile_image': 'test_user_2.jpg'
    }
    lobby.add_participant('test_user_2', user2_info)
    
    # Add a regular chat message
    chat_msg = lobby.add_chat_message('test_user_1', 'Hello everyone! Ready to start troubleshooting?', 'text')
    print(f"\n💬 Added user message: {chat_msg['message']}")
    print(f"📷 Profile image: {chat_msg.get('profile_image', 'None')}")
    
    # Add another message from user 2
    chat_msg2 = lobby.add_chat_message('test_user_2', 'Yes, let\'s get started!', 'text')
    print(f"\n💬 Added user 2 message: {chat_msg2['message']}")
    print(f"📷 Profile image: {chat_msg2.get('profile_image', 'None')}")
    
    # Add a system message
    system_msg = lobby.add_chat_message('system', 'Scenario has been loaded successfully.', 'system')
    print(f"\n🤖 Added system message: {system_msg['message']}")
    
    # Test recent chat (last 5 messages)
    lobby_dict = lobby.to_dict()
    recent_chat = lobby_dict.get('recent_chat', [])
    
    print(f"\n📊 Recent chat ({len(recent_chat)} messages):")
    for i, msg in enumerate(recent_chat):
        profile_info = f" (📷 {msg['profile_image']})" if msg.get('profile_image') else ""
        print(f"  {i+1}. [{msg['type']}] {msg['username']}{profile_info}: {msg['message']}")
        print(f"     🕒 {msg['timestamp']}")
    
    print(f"\n🧪 Testing message data structure:")
    if recent_chat:
        sample_msg = recent_chat[0]
        print(f"Sample message keys: {list(sample_msg.keys())}")
        print(f"Sample message data: {sample_msg}")
    
    print(f"\n✅ Chat functionality test completed!")
    print(f"📈 Total messages in lobby: {len(lobby.chat_history)}")
    print(f"👥 Participants: {len(lobby.participants)}")
    
    return lobby

if __name__ == '__main__':
    lobby = test_chat_messages()
    
    print(f"\n🔍 Additional Debug Info:")
    print(f"Lobby participants: {list(lobby.participants.keys())}")
    for user_id, participant in lobby.participants.items():
        print(f"  - {participant['username']} (profile: {participant.get('profile_image', 'None')})")
