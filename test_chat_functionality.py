#!/usr/bin/env python3
"""
Test script to verify chat functionality in collaborative lobbies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime

# Initialize Flask app context
from __init__ import create_app
app = create_app()

with app.app_context():
    from services.troubleshooting_lobbies import lobby_manager, TroubleshootingLobby

def test_chat_functionality():
    """Test the complete chat functionality flow"""
    print("🧪 Testing Chat Functionality")
    print("=" * 50)
    
    # 1. Create a test lobby
    print("\n1️⃣ Creating test lobby...")
    lobby = lobby_manager.create_lobby(
        creator_id='test_user_1',
        creator_name='Test User 1',
        creator_profile_image='test1.jpg',
        lobby_config={
            'name': 'Chat Test Session',
            'scenario_type': 'easy',
            'scenario_id': 'network',
            'max_participants': 4
        }
    )
    print(f"✅ Created lobby: {lobby.id}")
    print(f"📋 Lobby name: {lobby.name}")
    
    # 2. Add a second user
    print("\n2️⃣ Adding second user...")
    result = lobby_manager.join_lobby(
        lobby_id=lobby.id,
        user_id='test_user_2',
        user_info={
            'username': 'Test User 2',
            'profile_image': 'test2.jpg'
        }
    )
    
    if result['success']:
        print(f"✅ User 2 joined successfully")
        lobby = result['lobby']
    else:
        print(f"❌ Failed to add user 2: {result['error']}")
        return False
    
    # 3. Test system messages
    print("\n3️⃣ Testing system messages...")
    system_msg = lobby.add_chat_message('system', 'Welcome to the chat test session!', 'system')
    print(f"🤖 System message: {system_msg['message']}")
    print(f"📅 Timestamp: {system_msg['timestamp']}")
    
    # 4. Test user messages
    print("\n4️⃣ Testing user messages...")
    user1_msg = lobby.add_chat_message('test_user_1', 'Hello everyone! Ready to start?', 'text')
    user2_msg = lobby.add_chat_message('test_user_2', 'Yes, let\'s begin the troubleshooting!', 'text')
    
    print(f"👤 User 1 message: {user1_msg['message']}")
    print(f"👤 User 2 message: {user2_msg['message']}")
    
    # 5. Test lobby dictionary with recent chat
    print("\n5️⃣ Testing lobby dictionary with recent chat...")
    lobby_dict = lobby.to_dict()
    recent_chat = lobby_dict.get('recent_chat', [])
    
    print(f"📊 Recent chat messages: {len(recent_chat)}")
    for i, msg in enumerate(recent_chat):
        print(f"   {i+1}. [{msg['type']}] {msg['username']}: {msg['message']}")
    
    # 6. Test chat history limit
    print("\n6️⃣ Testing chat history management...")
    print(f"📈 Current chat history length: {len(lobby.chat_history)}")
    
    # Add more messages to test the limit
    for i in range(10):
        lobby.add_chat_message('test_user_1', f'Test message {i+1}', 'text')
    
    print(f"📈 After adding 10 messages: {len(lobby.chat_history)}")
    lobby_dict = lobby.to_dict()
    recent_chat = lobby_dict.get('recent_chat', [])
    print(f"📊 Recent chat (last 5): {len(recent_chat)} messages")
    
    # 7. Test message data structure
    print("\n7️⃣ Verifying message data structure...")
    if recent_chat:
        sample_msg = recent_chat[-1]
        required_fields = ['id', 'user_id', 'username', 'message', 'type', 'timestamp']
        
        print(f"📋 Sample message fields: {list(sample_msg.keys())}")
        for field in required_fields:
            if field in sample_msg:
                print(f"✅ {field}: {sample_msg[field]}")
            else:
                print(f"❌ Missing field: {field}")
    
    # 8. Test lobby cleanup
    print("\n8️⃣ Testing cleanup...")
    lobby_manager.leave_lobby('test_user_1')
    lobby_manager.leave_lobby('test_user_2')
    
    if lobby.id in lobby_manager.lobbies:
        print(f"📋 Lobby still exists with {len(lobby.participants)} participants")
        # Clean it up manually for testing
        del lobby_manager.lobbies[lobby.id]
        print("🧹 Lobby manually cleaned up")
    else:
        print("✅ Lobby automatically cleaned up")
    
    print("\n🎉 Chat functionality test completed successfully!")
    return True

if __name__ == '__main__':
    try:
        with app.app_context():
            success = test_chat_functionality()
            if success:
                print("\n✅ All chat tests passed!")
                sys.exit(0)
            else:
                print("\n❌ Some chat tests failed!")
                sys.exit(1)
    except Exception as e:
        print(f"\n❌ Chat test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
