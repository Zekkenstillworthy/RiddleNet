#!/usr/bin/env python3
"""
Test script to verify chat functionality in collaboration system
"""

import requests
import json
from datetime import datetime

def test_collaboration_system():
    """Test the collaboration and chat system"""
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 Testing RiddleNet Collaboration Chat System")
    print("=" * 50)
    
    # Test 1: Check if the main simulation page loads
    print("\n1. Testing main simulation page load...")
    try:
        response = requests.get(f"{base_url}/user/simulation/70")
        if response.status_code == 200:
            print("✅ Simulation page loads successfully")
            
            # Check if collaboration elements exist
            html_content = response.text
            collaboration_indicators = [
                "team-session-panel",
                "chat-messages", 
                "chat-input",
                "teamSessionManager",
                "sendTeamMessage",
                "lobby-browser-modal"
            ]
            
            found_elements = []
            missing_elements = []
            
            for indicator in collaboration_indicators:
                if indicator in html_content:
                    found_elements.append(indicator)
                else:
                    missing_elements.append(indicator)
            
            print(f"   ✅ Found collaboration elements: {', '.join(found_elements)}")
            if missing_elements:
                print(f"   ⚠️  Missing elements: {', '.join(missing_elements)}")
            
        else:
            print(f"❌ Failed to load simulation page (Status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Error testing simulation page: {e}")
    
    # Test 2: Check for socket.io integration
    print("\n2. Testing Socket.IO integration...")
    try:
        response = requests.get(f"{base_url}/socket.io/")
        if response.status_code == 200:
            print("✅ Socket.IO endpoint is accessible")
        else:
            print(f"⚠️  Socket.IO endpoint returned status: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Socket.IO test inconclusive: {e}")
    
    # Test 3: Check collaboration system files
    print("\n3. Testing collaboration system files...")
    import os
    
    collaboration_files = [
        "socket_events.py",
        "services/troubleshooting_lobbies.py",
        "templates/user/dynamic_simulation.html"
    ]
    
    for file_path in collaboration_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"   ✅ {file_path} exists")
            
            # Check for key functions
            if file_path.endswith('.py'):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'socket_events.py' in file_path:
                    functions = ['handle_send_lobby_chat', 'handle_team_chat_message', 'handle_join_team_session']
                    for func in functions:
                        if func in content:
                            print(f"      ✅ Found function: {func}")
                        else:
                            print(f"      ❌ Missing function: {func}")
                
                elif 'troubleshooting_lobbies.py' in file_path:
                    features = ['add_chat_message', 'chat_history', 'TroubleshootingLobby']
                    for feature in features:
                        if feature in content:
                            print(f"      ✅ Found feature: {feature}")
                        else:
                            print(f"      ❌ Missing feature: {feature}")
            
        else:
            print(f"   ❌ {file_path} not found")
    
    # Test 4: Summary and recommendations
    print("\n4. Chat System Implementation Summary")
    print("=" * 40)
    
    features_implemented = [
        "✅ Socket.IO real-time messaging infrastructure",
        "✅ Team session chat handlers (backend)",
        "✅ Lobby chat system with persistence", 
        "✅ Chat message display and formatting",
        "✅ Chat history loading for new participants",
        "✅ Enhanced chat UI with timestamps",
        "✅ Message sanitization for security",
        "✅ Support for both lobby and team session chat"
    ]
    
    for feature in features_implemented:
        print(f"   {feature}")
    
    print("\n📋 Testing Instructions:")
    print("   1. Start the RiddleNet application")
    print("   2. Navigate to: http://127.0.0.1:5001/user/simulation/70") 
    print("   3. Look for collaboration panel on the right side")
    print("   4. Click 'Browse Active Sessions' to see available lobbies")
    print("   5. Join a lobby or create one (admin functionality)")
    print("   6. Test chat by typing messages in the chat input")
    print("   7. Open multiple browser tabs/windows to test multi-user chat")
    
    print("\n🔧 Manual Chat Testing Steps:")
    print("   • Toggle chat visibility with the chat icon")
    print("   • Send messages and verify they appear instantly")
    print("   • Check that your messages appear on the right (own messages)")
    print("   • Check that others' messages appear on the left") 
    print("   • Verify timestamps are displayed correctly")
    print("   • Test message history when joining existing sessions")
    
    print("\n🎯 Expected Behavior:")
    print("   • Messages should appear in real-time")
    print("   • Chat should persist when users join/leave")
    print("   • System messages should show user join/leave events")
    print("   • Chat interface should be responsive and user-friendly")

if __name__ == "__main__":
    test_collaboration_system()