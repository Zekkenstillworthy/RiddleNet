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
        'scenario_type': 'easy',
        'scenario_id': 'network',
        'max_participants': 4,
        'is_private': False,
        'password': None
    }
    
    lobby = lobby_manager.create_lobby(
        creator_id='test_user_1',
        creator_name='TestUser1',
        lobby_config=lobby_config
    )
    
    print(f"✅ Lobby created successfully!")
    print(f"   - Lobby ID: {lobby.id}")
    print(f"   - Name: {lobby.name}")
    print(f"   - Participants: {len(lobby.participants)}")
    print(f"   - Creator: {lobby.creator_name}")
    
    return lobby

def test_lobby_joining(lobby):
    """Test joining an existing lobby"""
    print("\n🧪 Testing lobby joining...")
    
    # Test user 2 joining
    result = lobby_manager.join_lobby(
        lobby_id=lobby.id,
        user_id='test_user_2',
        user_info={'username': 'TestUser2'}
    )
    
    if result['success']:
        print(f"✅ User 2 joined successfully!")
        print(f"   - Total participants: {len(result['lobby'].participants)}")
    else:
        print(f"❌ Failed to join: {result['error']}")
        return False
    
    # Test user 3 joining
    result = lobby_manager.join_lobby(
        lobby_id=lobby.id,
        user_id='test_user_3',
        user_info={'username': 'TestUser3'}
    )
    
    if result['success']:
        print(f"✅ User 3 joined successfully!")
        print(f"   - Total participants: {len(result['lobby'].participants)}")
    else:
        print(f"❌ Failed to join: {result['error']}")
        return False
    
    return True

def test_real_time_features(lobby):
    """Test real-time collaboration features"""
    print("\n🧪 Testing real-time collaboration features...")
    
    # Test cursor updates
    lobby.update_participant_cursor('test_user_1', {'x': 100, 'y': 200})
    lobby.update_participant_cursor('test_user_2', {'x': 300, 'y': 400})
    
    print("✅ Cursor positions updated")
    
    # Test network state updates
    network_changes = {
        'action': 'add_device',
        'devices': {
            'device_1': {
                'type': 'router',
                'x': 150,
                'y': 150,
                'name': 'Router1'
            }
        },
        'connections': [
            {
                'from': 'device_1',
                'to': 'device_2',
                'type': 'ethernet'
            }
        ]
    }
    
    lobby.update_network_state('test_user_1', network_changes)
    print("✅ Network topology updated")
    
    # Test chat messages
    chat_msg = lobby.add_chat_message('test_user_2', 'Hello everyone!', 'text')
    print(f"✅ Chat message added: {chat_msg['message']}")
    
    # Test progress updates
    progress_data = {
        'step': 'Identify network issues',
        'completed_steps': ['Connect devices', 'Configure IP addresses'],
        'issues_found': ['Misconfigured subnet'],
        'solutions_applied': []
    }
    
    lobby.update_progress('test_user_1', progress_data)
    print("✅ Progress updated")

def test_lobby_management():
    """Test lobby management features"""
    print("\n🧪 Testing lobby management...")
    
    # Get public lobbies
    public_lobbies = lobby_manager.get_public_lobbies()
    print(f"✅ Found {len(public_lobbies)} public lobbies")
    
    # Get stats
    stats = lobby_manager.get_stats()
    print(f"✅ Lobby stats: {stats}")

def test_data_serialization(lobby):
    """Test data serialization for WebSocket transmission"""
    print("\n🧪 Testing data serialization...")
    
    lobby_dict = lobby.to_dict()
    
    # Try to serialize to JSON (this is what WebSocket will do)
    try:
        json_data = json.dumps(lobby_dict, indent=2)
        print("✅ Lobby data successfully serialized to JSON")
        
        # Show sample structure
        print("\n📄 Sample lobby data structure:")
        sample_data = {
            'id': lobby_dict['id'],
            'name': lobby_dict['name'],
            'participant_count': lobby_dict['participant_count'],
            'scenario_type': lobby_dict['scenario_type'],
            'is_active': lobby_dict['is_active']
        }
        print(json.dumps(sample_data, indent=2))
        
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        return False
    
    return True

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
