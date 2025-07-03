import unittest
import sys
import os
import json
from flask import Flask
from flask_socketio import SocketIO
from unittest.mock import MagicMock, patch
import services.troubleshooting_lobbies as lobby_service

class TestLobbyParticipantsUpdate(unittest.TestCase):
    """
    Test the real-time updates of participants in a troubleshooting lobby
    """
    
    def setUp(self):
        # Create a mock Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test_key'
        self.app.config['TESTING'] = True
        
        # Create mock SocketIO instance
        self.socketio = SocketIO(self.app)
        
        # Create a test lobby
        self.test_lobby = lobby_service.TroubleshootingLobby(
            id="test-lobby-1",
            name="Test Lobby",
            scenario_type="easy",
            scenario_id="network",
            max_participants=6,
            creator_id="user-1",
            creator_name="User 1"
        )
        
        # Add a first participant
        self.test_lobby.add_participant("user-1", {"username": "User 1"})
        
        # Mock the lobby service
        self.original_get_lobby = lobby_service.get_lobby
        lobby_service.get_lobby = MagicMock(return_value={"success": True, "lobby": self.test_lobby})
        
        # Set up socket event handlers
        with patch('flask_socketio.emit') as self.mock_emit:
            from socket_events import join_lobby_handler, leave_lobby_handler
            self.join_lobby_handler = join_lobby_handler
            self.leave_lobby_handler = leave_lobby_handler
    
    def tearDown(self):
        # Restore original functions
        lobby_service.get_lobby = self.original_get_lobby
    
    def test_participant_joined_event_data(self):
        """Test that participant_joined event sends correctly formatted data"""
        # Mock current user
        current_user = MagicMock()
        current_user.id = "user-2"
        current_user.username = "User 2"
        
        # Mock session
        session = {}
        
        # Mock join room
        join_room = MagicMock()
        
        # Test with patched dependencies
        with patch('socket_events.current_user', current_user), \
             patch('socket_events.session', session), \
             patch('socket_events.join_room', join_room):
            
            # Call the join lobby handler
            self.join_lobby_handler({"lobby_id": "test-lobby-1"})
            
            # Check that participant_joined was emitted with correct data structure
            participant_joined_calls = [
                call for call in self.mock_emit.call_args_list 
                if call[0][0] == 'participant_joined'
            ]
            
            self.assertTrue(len(participant_joined_calls) > 0, 
                           "participant_joined event was not emitted")
            
            # Get the data from the first participant_joined call
            event_name, event_data = participant_joined_calls[0][0]
            
            # Verify data structure matches what the client expects
            self.assertEqual(event_name, 'participant_joined')
            self.assertIn('user_id', event_data, "user_id missing in participant_joined data")
            self.assertIn('username', event_data, "username missing in participant_joined data")
            self.assertIn('participant_data', event_data, "participant_data missing in participant_joined data")
            
            # Print the data for verification
            print("✅ participant_joined event data format is correct:")
            print(json.dumps(event_data, indent=2))
            
            # Check that this matches what the client expects in the handler

    def test_participant_left_event_data(self):
        """Test that participant_left event sends correctly formatted data"""
        # Mock current user
        current_user = MagicMock()
        current_user.id = "user-2"
        current_user.username = "User 2"
        
        # Mock session with an active lobby
        session = {"current_lobby_id": "test-lobby-1"}
        
        # Mock leave room
        leave_room = MagicMock()
        
        # Test with patched dependencies
        with patch('socket_events.current_user', current_user), \
             patch('socket_events.session', session), \
             patch('socket_events.leave_room', leave_room):
            
            # Call the leave lobby handler
            self.leave_lobby_handler({})
            
            # Check that participant_left was emitted with correct data structure
            participant_left_calls = [
                call for call in self.mock_emit.call_args_list 
                if call[0][0] == 'participant_left'
            ]
            
            self.assertTrue(len(participant_left_calls) > 0, 
                           "participant_left event was not emitted")
            
            # Get the data from the first participant_left call
            event_name, event_data = participant_left_calls[0][0]
            
            # Verify data structure matches what the client expects
            self.assertEqual(event_name, 'participant_left')
            self.assertIn('user_id', event_data, "user_id missing in participant_left data")
            self.assertIn('username', event_data, "username missing in participant_left data")
            
            # Print the data for verification
            print("✅ participant_left event data format is correct:")
            print(json.dumps(event_data, indent=2))

if __name__ == '__main__':
    unittest.main()
