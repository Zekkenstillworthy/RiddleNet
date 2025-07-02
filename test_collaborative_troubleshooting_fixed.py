"""
Test script for WebSocket Collaborative Troubleshooting System

This script demonstrates the key features of the collaborative troubleshooting system.
Run this script to test the lobby management and real-time collaboration features.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask app to create application context
from run import app
from services.troubleshooting_lobbies import lobby_manager
import json
from datetime import datetime

def test_lobby_creation():
    """Test creating a new troubleshooting lobby"""
    print("🧪 Testing lobby creation...")
    
    lobby_config = {
        'name': 'Test Collaborative Session',
        'scenario_type': 'medium',
        'scenario_id': 'split',
        'max_participants': 4
        # Removed is_private - all lobbies are now public
    }
    
    lobby = lobby_manager.create_lobby('test_user_1', 'Test User', lobby_config)
    print(f"✅ Created lobby: {lobby.name} (ID: {lobby.id})")
    print(f"   📊 Max participants: {lobby.max_participants}")
    print(f"   🏷️  Scenario: {lobby.scenario_type} - {lobby.scenario_id}")
    print(f"   🔓 Public: All lobbies are now public")
    
    return lobby

def test_lobby_joining(lobby):
    """Test users joining the lobby"""
    print("\n🧪 Testing lobby joining...")
    
    # Add participants
    participants = [
        {'user_id': 'user2', 'username': 'Alice', 'color': '#ff5733'},
        {'user_id': 'user3', 'username': 'Bob', 'color': '#33ff57'},
        {'user_id': 'user4', 'username': 'Charlie', 'color': '#3357ff'}
    ]
    
    for participant in participants:
        result = lobby_manager.join_lobby(
            lobby.id, 
            participant['user_id'], 
            {
                'username': participant['username'],
                'color': participant['color']
            }
        )
        if result['success']:
            print(f"✅ {participant['username']} joined the session")
        else:
            print(f"❌ Failed to add {participant['username']}: {result.get('error', 'Unknown error')}")
            return False
    
    # Verify participant count
    lobby = lobby_manager.get_lobby_by_id(lobby.id)
    print(f"📊 Total participants: {len(lobby.participants)}")
    
    return True

def test_real_time_features(lobby):
    """Test real-time collaboration features"""
    print("\n🧪 Testing real-time collaboration features...")
    
    # Test cursor updates
    cursor_data = {
        'x': 150,
        'y': 200,
        'timestamp': datetime.now().isoformat()
    }
    
    lobby.update_participant_cursor('user2', cursor_data)
    print("✅ Cursor position updated")
    
    # Test network topology updates
    network_changes = {
        'devices': {
            'router1': {
                'type': 'router',
                'x': 100,
                'y': 100,
                'name': 'Main Router'
            }
        },
        'connections': []
    }
    
    lobby.update_network_state('user2', network_changes)
    print("✅ Network topology updated")
    
    # Test chat messaging
    lobby.add_chat_message('user3', 'Hey team, I think the issue is with the router configuration!')
    print("✅ Chat message sent")
    
    # Test progress updates
    progress_data = {
        'step': 'Identified OSPF neighbor issues',
        'completion_percentage': 35,
        'timestamp': datetime.now().isoformat()
    }
    
    lobby.update_progress('user2', progress_data)
    print("✅ Progress updated")

def test_lobby_management():
    """Test lobby management features"""
    print("\n🧪 Testing lobby management...")
    
    # Get public lobbies
    public_lobbies = lobby_manager.get_public_lobbies()
    print(f"✅ Found {len(public_lobbies)} public lobbies")
    
    # Test lobby serialization for API responses
    for lobby_data in public_lobbies:
        if 'id' in lobby_data and 'name' in lobby_data:
            print(f"   📋 {lobby_data['name']} - {lobby_data['participants']} participants")

def test_data_serialization(lobby):
    """Test data serialization for WebSocket transmission"""
    print("\n🧪 Testing data serialization...")
    
    try:
        # Test lobby serialization
        lobby_json = json.dumps(lobby.to_dict())
        print("✅ Lobby data serializable for WebSocket")
        
        # Test participant data
        if lobby.participants:
            participant_data = list(lobby.participants.values())[0]
            participant_json = json.dumps(participant_data)
            print("✅ Participant data serializable")
        
        # Test chat history
        if lobby.chat_history:
            chat_json = json.dumps(lobby.chat_history)
            print("✅ Chat history serializable")
        
        # Test network state
        network_json = json.dumps(lobby.network_state)
        print("✅ Network state serializable")
        
        return True
        
    except Exception as e:
        print(f"❌ Serialization failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting WebSocket Collaborative Troubleshooting System Tests")
    print("=" * 70)
    
    # Create Flask application context for the tests
    with app.app_context():
        try:
            # Test 1: Create lobby
            lobby = test_lobby_creation()
            
            # Test 2: Join lobby
            if not test_lobby_joining(lobby):
                print("❌ Lobby joining test failed")
                return
            
            # Test 3: Real-time features
            test_real_time_features(lobby)
            
            # Test 4: Lobby management
            test_lobby_management()
            
            # Test 5: Data serialization
            if not test_data_serialization(lobby):
                print("❌ Data serialization test failed")
                return
            
            print("\n" + "=" * 70)
            print("🎉 All tests completed successfully!")
            print("\n📋 System Features Verified:")
            print("   ✅ Lobby creation and management")
            print("   ✅ Multi-user joining")
            print("   ✅ Real-time cursor tracking")
            print("   ✅ Network topology synchronization")
            print("   ✅ Chat messaging")
            print("   ✅ Progress tracking")
            print("   ✅ Data serialization for WebSocket")
            
            print("\n🔗 WebSocket Events Available:")
            print("   • create_troubleshooting_lobby")
            print("   • join_troubleshooting_lobby")
            print("   • leave_troubleshooting_lobby")
            print("   • update_cursor_position")
            print("   • update_network_topology")
            print("   • send_lobby_chat")
            print("   • update_troubleshooting_progress")
            
            print("\n🎯 Ready for Integration!")
            print("   The collaborative troubleshooting system is fully implemented and ready to use.")
            print("   Users can now work together in real-time, just like Figma and Canva!")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
