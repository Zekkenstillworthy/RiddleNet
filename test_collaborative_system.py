"""
Real-time Collaboration System Test
Tests the full collaborative troubleshooting functionality
"""

import pytest
import json
from unittest.mock import Mock, patch
from flask import Flask
from flask_socketio import SocketIOTestClient
from datetime import datetime

from services.troubleshooting_lobbies import TroubleshootingLobbyManager, TroubleshootingLobby
from socket_events import socketio
from user.models.user import User

class TestCollaborativeTroubleshooting:
    
    def setup_method(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret'
        
        socketio.init_app(self.app)
        
        # Mock users
        self.user1 = Mock(spec=User)
        self.user1.id = '1'
        self.user1.username = 'alice'
        
        self.user2 = Mock(spec=User)
        self.user2.id = '2'
        self.user2.username = 'bob'
        
        # Initialize lobby manager
        self.lobby_manager = TroubleshootingLobbyManager()
        
    def test_lobby_creation_and_joining(self):
        """Test basic lobby creation and joining"""
        with self.app.test_client() as client:
            with patch('socket_events.current_user', self.user1):
                with patch('socket_events.lobby_manager', self.lobby_manager):
                    socketio_test = SocketIOTestClient(self.app, socketio)
                    
                    # User 1 creates a lobby
                    lobby_config = {
                        'name': 'Test Collaboration',
                        'scenario_type': 'medium',
                        'scenario_id': 'split',
                        'max_participants': 4
                    }
                    
                    received = socketio_test.emit('create_troubleshooting_lobby', lobby_config)
                    assert received[0]['name'] == 'lobby_created'
                    assert received[0]['args'][0]['success'] == True
                    
                    lobby_id = received[0]['args'][0]['lobby']['id']
                    
                    # User 2 joins the lobby
                    with patch('socket_events.current_user', self.user2):
                        received = socketio_test.emit('join_troubleshooting_lobby', {'lobby_id': lobby_id})
                        assert received[0]['name'] == 'lobby_joined'
                        assert received[0]['args'][0]['success'] == True

    def test_device_synchronization(self):
        """Test real-time device addition and removal"""
        # Create lobby
        lobby = self.lobby_manager.create_lobby(
            creator_id=self.user1.id,
            creator_name=self.user1.username,
            lobby_config={'name': 'Device Test'}
        )
        
        # Add user 2 to lobby
        self.lobby_manager.join_lobby(lobby['lobby'].id, self.user2.id, {'username': self.user2.username})
        
        with self.app.test_client() as client:
            with patch('socket_events.lobby_manager', self.lobby_manager):
                socketio_test = SocketIOTestClient(self.app, socketio)
                
                # User 1 adds a device
                with patch('socket_events.current_user', self.user1):
                    device_data = {
                        'id': 'router_1',
                        'type': 'router',
                        'x': 100,
                        'y': 100,
                        'label': 'Router 1',
                        'ipv4': '192.168.1.1'
                    }
                    
                    received = socketio_test.emit('add_device', {'device': device_data})
                    
                    # Check that device was added to lobby network state
                    lobby_obj = self.lobby_manager.get_lobby(lobby['lobby'].id)
                    assert 'router_1' in lobby_obj.network_state['devices']
                    assert lobby_obj.network_state['devices']['router_1']['type'] == 'router'

    def test_connection_synchronization(self):
        """Test real-time connection management"""
        # Create lobby and add users
        lobby = self.lobby_manager.create_lobby(
            creator_id=self.user1.id,
            creator_name=self.user1.username,
            lobby_config={'name': 'Connection Test'}
        )
        
        self.lobby_manager.join_lobby(lobby['lobby'].id, self.user2.id, {'username': self.user2.username})
        
        with self.app.test_client() as client:
            with patch('socket_events.lobby_manager', self.lobby_manager):
                socketio_test = SocketIOTestClient(self.app, socketio)
                
                # Add devices first
                lobby_obj = self.lobby_manager.get_lobby(lobby['lobby'].id)
                lobby_obj.update_network_state(self.user1.id, {
                    'devices': {
                        'router_1': {'id': 'router_1', 'type': 'router'},
                        'router_2': {'id': 'router_2', 'type': 'router'}
                    }
                })
                
                # User 1 adds a connection
                with patch('socket_events.current_user', self.user1):
                    received = socketio_test.emit('add_connection', {
                        'device1_id': 'router_1',
                        'device2_id': 'router_2',
                        'type': 'ethernet'
                    })
                    
                    # Check that connection was added
                    lobby_obj = self.lobby_manager.get_lobby(lobby['lobby'].id)
                    assert len(lobby_obj.network_state['connections']) > 0
                    conn = lobby_obj.network_state['connections'][0]
                    assert conn['device1_id'] == 'router_1'
                    assert conn['device2_id'] == 'router_2'

    def test_cli_command_sharing(self):
        """Test CLI command execution sharing"""
        # Create lobby and add users
        lobby = self.lobby_manager.create_lobby(
            creator_id=self.user1.id,
            creator_name=self.user1.username,
            lobby_config={'name': 'CLI Test'}
        )
        
        self.lobby_manager.join_lobby(lobby['lobby'].id, self.user2.id, {'username': self.user2.username})
        
        with self.app.test_client() as client:
            with patch('socket_events.lobby_manager', self.lobby_manager):
                socketio_test = SocketIOTestClient(self.app, socketio)
                
                # User 1 executes CLI command
                with patch('socket_events.current_user', self.user1):
                    received = socketio_test.emit('execute_cli_command', {
                        'device_id': 'router_1',
                        'command': 'show ip route'
                    })
                    
                    # Check that command was added to CLI history
                    lobby_obj = self.lobby_manager.get_lobby(lobby['lobby'].id)
                    assert 'router_1' in lobby_obj.cli_history
                    assert len(lobby_obj.cli_history['router_1']) > 0
                    assert lobby_obj.cli_history['router_1'][0]['command'] == 'show ip route'

    def test_device_locking(self):
        """Test device locking mechanism"""
        # Create lobby and add users
        lobby = self.lobby_manager.create_lobby(
            creator_id=self.user1.id,
            creator_name=self.user1.username,
            lobby_config={'name': 'Lock Test'}
        )
        
        self.lobby_manager.join_lobby(lobby['lobby'].id, self.user2.id, {'username': self.user2.username})
        
        with self.app.test_client() as client:
            with patch('socket_events.lobby_manager', self.lobby_manager):
                socketio_test = SocketIOTestClient(self.app, socketio)
                
                # User 1 locks a device
                with patch('socket_events.current_user', self.user1):
                    received = socketio_test.emit('lock_device', {'device_id': 'router_1'})
                    
                    lobby_obj = self.lobby_manager.get_lobby(lobby['lobby'].id)
                    assert 'router_1' in lobby_obj.device_locks
                    assert lobby_obj.device_locks['router_1']['locked_by'] == self.user1.id
                
                # User 2 tries to move the locked device
                with patch('socket_events.current_user', self.user2):
                    received = socketio_test.emit('move_device', {
                        'device_id': 'router_1',
                        'position': {'x': 200, 'y': 200}
                    })
                    
                    # Should receive denial
                    assert received[0]['name'] == 'device_move_denied'

    def test_progress_tracking(self):
        """Test collaborative progress tracking"""
        # Create lobby and add users
        lobby = self.lobby_manager.create_lobby(
            creator_id=self.user1.id,
            creator_name=self.user1.username,
            lobby_config={'name': 'Progress Test'}
        )
        
        self.lobby_manager.join_lobby(lobby['lobby'].id, self.user2.id, {'username': self.user2.username})
        
        with self.app.test_client() as client:
            with patch('socket_events.lobby_manager', self.lobby_manager):
                socketio_test = SocketIOTestClient(self.app, socketio)
                
                # User 1 updates progress
                with patch('socket_events.current_user', self.user1):
                    progress_data = {
                        'scenario_completed': False,
                        'steps_completed': 3,
                        'total_steps': 10,
                        'percentage': 30
                    }
                    
                    received = socketio_test.emit('update_scenario_progress', {
                        'progress': progress_data
                    })
                    
                    # Check that progress was updated
                    lobby_obj = self.lobby_manager.get_lobby(lobby['lobby'].id)
                    assert hasattr(lobby_obj, 'progress')
                    assert lobby_obj.progress['percentage'] == 30

    def test_full_state_synchronization(self):
        """Test full state sync functionality"""
        # Create lobby with some initial state
        lobby = self.lobby_manager.create_lobby(
            creator_id=self.user1.id,
            creator_name=self.user1.username,
            lobby_config={'name': 'Sync Test'}
        )
        
        lobby_obj = self.lobby_manager.get_lobby(lobby['lobby'].id)
        lobby_obj.update_network_state(self.user1.id, {
            'devices': {
                'router_1': {'id': 'router_1', 'type': 'router', 'x': 100, 'y': 100}
            },
            'connections': [
                {'device1_id': 'router_1', 'device2_id': 'router_2', 'type': 'ethernet'}
            ]
        })
        
        # User 2 joins and requests full sync
        self.lobby_manager.join_lobby(lobby['lobby'].id, self.user2.id, {'username': self.user2.username})
        
        with self.app.test_client() as client:
            with patch('socket_events.lobby_manager', self.lobby_manager):
                socketio_test = SocketIOTestClient(self.app, socketio)
                
                with patch('socket_events.current_user', self.user2):
                    received = socketio_test.emit('request_full_sync')
                    
                    # Check that full state was returned
                    assert received[0]['name'] == 'full_state_sync'
                    sync_data = received[0]['args'][0]
                    assert 'network_state' in sync_data
                    assert 'router_1' in sync_data['network_state']['devices']

if __name__ == '__main__':
    pytest.main([__file__])
