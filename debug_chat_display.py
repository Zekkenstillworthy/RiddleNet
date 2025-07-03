#!/usr/bin/env python3
"""
Debug Chat Display Issue
Test script to identify why chat messages are not displaying in the lobby UI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock Flask app for testing
class MockLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")
    
    def error(self, msg):
        print(f"[ERROR] {msg}")

class MockApp:
    def __init__(self):
        self.logger = MockLogger()

# Set up mock app
import flask
flask.current_app = MockApp()

from services.troubleshooting_lobbies import LobbyManager
from datetime import datetime
import json

# Create a standalone lobby manager for testing
test_lobby_manager = LobbyManager()

def test_chat_display():
    """Test chat message creation and display"""
    print("🔍 Testing Chat Display Issue")
    print("=" * 50)
    
    # Create a test lobby
    lobby = test_lobby_manager.create_lobby(
        creator_id='test_user_1',
        creator_name='Test User',
        lobby_config={
            'name': 'Debug Chat Test',
            'scenario_type': 'easy',
            'scenario_id': 'network'
        },
        creator_profile_image='test_avatar.jpg'
    )
    
    print(f"✅ Created lobby: {lobby.id}")
    print(f"   Name: {lobby.name}")
    print(f"   Participants: {len(lobby.participants)}")
    
    # Add some test chat messages
    print("\n💬 Adding test chat messages...")
    
    # System message
    system_msg = lobby.add_chat_message('system', 'Welcome to the debug session!', 'system')
    print(f"   System message: {system_msg['message']}")
    
    # User message
    user_msg = lobby.add_chat_message('test_user_1', 'Hello everyone!', 'text')
    print(f"   User message: {user_msg['message']}")
    
    # Add a second user
    join_result = test_lobby_manager.join_lobby(lobby.id, 'test_user_2', {
        'username': 'Second User',
        'profile_image': 'user2.jpg'
    })
    
    if join_result['success']:
        print(f"✅ Second user joined successfully")
        
        # Second user message
        user2_msg = lobby.add_chat_message('test_user_2', 'Hi there!', 'text')
        print(f"   Second user message: {user2_msg['message']}")
    
    # Check lobby state
    print(f"\n📊 Lobby State:")
    print(f"   Total chat messages: {len(lobby.chat_history)}")
    print(f"   Participants: {len(lobby.participants)}")
    
    # Check lobby.to_dict() output
    lobby_dict = lobby.to_dict()
    print(f"\n📋 Lobby dict structure:")
    print(f"   Has recent_chat: {'recent_chat' in lobby_dict}")
    print(f"   Recent chat count: {len(lobby_dict.get('recent_chat', []))}")
    
    # Print actual chat messages
    print(f"\n💬 Chat History:")
    for i, msg in enumerate(lobby.chat_history):
        print(f"   {i+1}. [{msg['type']}] {msg['username']}: {msg['message']}")
        print(f"      Profile image: {msg.get('profile_image', 'None')}")
        print(f"      Timestamp: {msg['timestamp']}")
    
    # Print recent_chat from to_dict()
    print(f"\n📬 Recent Chat (from to_dict()):")
    for i, msg in enumerate(lobby_dict.get('recent_chat', [])):
        print(f"   {i+1}. [{msg['type']}] {msg['username']}: {msg['message']}")
        print(f"      Profile image: {msg.get('profile_image', 'None')}")
        print(f"      Timestamp: {msg['timestamp']}")
    
    # Test JSON serialization
    print(f"\n🔄 Testing JSON serialization...")
    try:
        json_str = json.dumps(lobby_dict, indent=2)
        print(f"✅ JSON serialization successful")
        print(f"   JSON length: {len(json_str)} characters")
        
        # Parse back to check
        parsed = json.loads(json_str)
        print(f"   Parsed recent_chat count: {len(parsed.get('recent_chat', []))}")
        
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
    
    print(f"\n🎯 Key Issues to Check:")
    print(f"   1. Are chat messages being added to lobby.chat_history? {'✅' if lobby.chat_history else '❌'}")
    print(f"   2. Are messages in recent_chat? {'✅' if lobby_dict.get('recent_chat') else '❌'}")
    print(f"   3. Do messages have required fields? {'✅' if all('username' in msg and 'message' in msg for msg in lobby.chat_history) else '❌'}")
    print(f"   4. Are profile images included? {'✅' if any('profile_image' in msg for msg in lobby.chat_history) else '❌'}")
    
    return lobby

if __name__ == '__main__':
    test_chat_display()
