"""
Real-time Collaborative Troubleshooting Lobby System
Figma/Canva-style collaborative sessions for network troubleshooting
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import uuid
import json
import threading
from flask import current_app


@dataclass 
class TroubleshootingLobby:
    """Represents a collaborative troubleshooting lobby"""
    id: str
    name: str
    scenario_type: str  # 'easy', 'medium', 'hard'
    scenario_id: str    # specific scenario like 'network', 'passive', etc.
    max_participants: int = 6
    creator_id: str = None
    creator_name: str = None
    participants: Dict[str, dict] = field(default_factory=dict)  # user_id -> user_info
    network_state: Dict = field(default_factory=dict)  # shared network topology
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    progress: Dict[str, any] = field(default_factory=dict)  # shared progress tracking
    chat_history: List[dict] = field(default_factory=list)
    
    def add_participant(self, user_id: str, user_info: dict) -> bool:
        """Add a participant to the lobby"""
        if len(self.participants) >= self.max_participants:
            return False
        
        self.participants[user_id] = {
            'user_id': user_id,
            'username': user_info.get('username', 'Unknown'),
            'joined_at': datetime.utcnow().isoformat(),
            'cursor_position': {'x': 0, 'y': 0},
            'selected_device': None,
            'is_active': True,
            'color': self._generate_user_color(user_id),
            'role': 'creator' if user_id == self.creator_id else 'participant'
        }
        return True
    
    def remove_participant(self, user_id: str):
        """Remove a participant from the lobby"""
        if user_id in self.participants:
            del self.participants[user_id]
    
    def update_participant_cursor(self, user_id: str, position: dict):
        """Update participant's cursor position for real-time collaboration"""
        if user_id in self.participants:
            self.participants[user_id]['cursor_position'] = position
            self.participants[user_id]['last_activity'] = datetime.utcnow().isoformat()
    
    def update_network_state(self, user_id: str, changes: dict):
        """Update shared network topology state"""
        timestamp = datetime.utcnow().isoformat()
        
        # Apply changes to network state
        if 'devices' in changes:
            if 'devices' not in self.network_state:
                self.network_state['devices'] = {}
            self.network_state['devices'].update(changes['devices'])
        
        if 'connections' in changes:
            if 'connections' not in self.network_state:
                self.network_state['connections'] = []
            
            # Merge new connections with existing ones
            existing_connections = {f"{c['from']}-{c['to']}": c for c in self.network_state['connections']}
            for new_conn in changes['connections']:
                key = f"{new_conn['from']}-{new_conn['to']}"
                existing_connections[key] = new_conn
            self.network_state['connections'] = list(existing_connections.values())
        
        if 'removed_devices' in changes:
            for device_id in changes['removed_devices']:
                if str(device_id) in self.network_state.get('devices', {}):
                    del self.network_state['devices'][str(device_id)]
        
        if 'removed_connections' in changes:
            if 'connections' in self.network_state:
                for conn_to_remove in changes['removed_connections']:
                    self.network_state['connections'] = [
                        c for c in self.network_state['connections'] 
                        if not (c['from'] == conn_to_remove['from'] and c['to'] == conn_to_remove['to'])
                    ]
        
        # Track who made the change
        if 'history' not in self.network_state:
            self.network_state['history'] = []
        
        self.network_state['history'].append({
            'user_id': user_id,
            'username': self.participants[user_id]['username'],
            'timestamp': timestamp,
            'action': changes.get('action', 'update'),
            'changes': changes
        })
        
        # Keep only last 50 history entries to prevent memory bloat
        if len(self.network_state['history']) > 50:
            self.network_state['history'] = self.network_state['history'][-50:]
    
    def add_chat_message(self, user_id: str, message: str, message_type: str = 'text'):
        """Add a chat message to lobby history"""
        if user_id == 'system':
            username = 'System'
        else:
            username = self.participants.get(user_id, {}).get('username', 'Unknown')
        
        chat_message = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'username': username,
            'message': message,
            'type': message_type,  # 'text', 'system', 'action', 'progress'
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.chat_history.append(chat_message)
        
        # Keep only last 100 messages
        if len(self.chat_history) > 100:
            self.chat_history = self.chat_history[-100:]
        
        return chat_message
    
    def _generate_user_color(self, user_id: str) -> str:
        """Generate a unique color for each user"""
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
            '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD',
            '#FD79A8', '#E17055', '#00B894', '#0984E3'
        ]
        return colors[hash(user_id) % len(colors)]
    
    def update_progress(self, user_id: str, progress_data: dict):
        """Update troubleshooting progress for a user"""
        if 'team_progress' not in self.progress:
            self.progress['team_progress'] = {}
        
        self.progress['team_progress'][user_id] = {
            **progress_data,
            'user_id': user_id,
            'username': self.participants[user_id]['username'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Calculate overall team progress
        all_completed_steps = set()
        total_issues_found = set()
        total_solutions_applied = set()
        
        for user_progress in self.progress['team_progress'].values():
            all_completed_steps.update(user_progress.get('completed_steps', []))
            total_issues_found.update(user_progress.get('issues_found', []))
            total_solutions_applied.update(user_progress.get('solutions_applied', []))
        
        self.progress['overall'] = {
            'completed_steps': list(all_completed_steps),
            'total_issues_found': list(total_issues_found),
            'total_solutions_applied': list(total_solutions_applied),
            'completion_percentage': min(len(all_completed_steps) * 10, 100),  # Assuming 10 steps total
            'last_updated': datetime.utcnow().isoformat(),
            'active_participants': len([p for p in self.participants.values() if p['is_active']])
        }
    
    def to_dict(self) -> dict:
        """Convert lobby to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'scenario_type': self.scenario_type,
            'scenario_id': self.scenario_id,
            'max_participants': self.max_participants,
            'creator_id': self.creator_id,
            'creator_name': self.creator_name,
            'participants': self.participants,
            'participant_count': len(self.participants),
            'network_state': self.network_state,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'progress': self.progress,
            'recent_chat': self.chat_history[-5:] if self.chat_history else [],
            'last_activity': max(
                [p.get('last_activity', self.created_at.isoformat()) for p in self.participants.values()],
                default=self.created_at.isoformat()
            )
        }


class LobbyManager:
    """Manages all troubleshooting lobbies"""
    
    def __init__(self):
        self.lobbies: Dict[str, TroubleshootingLobby] = {}
        self.user_lobby_map: Dict[str, str] = {}  # user_id -> lobby_id
        self._lock = threading.RLock()
        self._cleanup_timer = None
        self.start_cleanup_timer()
    
    def start_cleanup_timer(self):
        """Start periodic cleanup of inactive lobbies"""
        def cleanup_task():
            try:
                self.cleanup_inactive_lobbies()
            except Exception as e:
                current_app.logger.error(f"Error in lobby cleanup: {e}")
            finally:
                # Schedule next cleanup
                self._cleanup_timer = threading.Timer(300, cleanup_task)  # Every 5 minutes
                self._cleanup_timer.daemon = True
                self._cleanup_timer.start()
        
        self._cleanup_timer = threading.Timer(300, cleanup_task)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def create_lobby(self, creator_id: str, creator_name: str, lobby_config: dict) -> TroubleshootingLobby:
        """Create a new troubleshooting lobby"""
        with self._lock:
            lobby_id = str(uuid.uuid4())[:8].upper()
            
            lobby = TroubleshootingLobby(
                id=lobby_id,
                name=lobby_config.get('name', f"{creator_name}'s Troubleshooting Session"),
                scenario_type=lobby_config['scenario_type'],
                scenario_id=lobby_config['scenario_id'],
                max_participants=lobby_config.get('max_participants', 6),
                creator_id=creator_id,
                creator_name=creator_name
            )
            
            # Add creator as first participant
            lobby.add_participant(creator_id, {
                'username': creator_name,
                'is_creator': True
            })
            
            self.lobbies[lobby_id] = lobby
            self.user_lobby_map[creator_id] = lobby_id
            
            # Add system welcome message
            lobby.add_chat_message('system', f"Welcome to {lobby.name}! Session created successfully.", 'system')
            
            current_app.logger.info(f"Created lobby {lobby_id} by user {creator_name}")
            return lobby
    
    def join_lobby(self, lobby_id: str, user_id: str, user_info: dict) -> dict:
        """Join an existing lobby"""
        with self._lock:
            if lobby_id not in self.lobbies:
                return {'success': False, 'error': 'Session not found'}
            
            lobby = self.lobbies[lobby_id]
            
            # Check if lobby is active
            if not lobby.is_active:
                return {'success': False, 'error': 'Session is no longer active'}
            
            # Check if lobby is full
            if len(lobby.participants) >= lobby.max_participants:
                return {'success': False, 'error': 'Session is full'}
            
            # Check if user is already in this lobby
            if user_id in lobby.participants:
                return {'success': True, 'lobby': lobby, 'message': 'Already in session'}
            
            # Remove user from previous lobby if they were in one
            if user_id in self.user_lobby_map:
                self.leave_lobby(user_id)
            
            # Add to lobby
            if lobby.add_participant(user_id, user_info):
                self.user_lobby_map[user_id] = lobby_id
                
                # Add system message
                lobby.add_chat_message('system', f"{user_info['username']} joined the session", 'system')
                
                current_app.logger.info(f"User {user_info['username']} joined lobby {lobby_id}")
                return {'success': True, 'lobby': lobby}
            
            return {'success': False, 'error': 'Failed to join session'}
    
    def leave_lobby(self, user_id: str) -> bool:
        """Leave current lobby"""
        with self._lock:
            if user_id not in self.user_lobby_map:
                return False
            
            lobby_id = self.user_lobby_map[user_id]
            lobby = self.lobbies.get(lobby_id)
            
            if lobby:
                username = lobby.participants.get(user_id, {}).get('username', 'Unknown')
                lobby.remove_participant(user_id)
                lobby.add_chat_message('system', f"{username} left the session", 'system')
                
                # If lobby is empty or creator left, mark as inactive
                if not lobby.participants or user_id == lobby.creator_id:
                    lobby.is_active = False
                    current_app.logger.info(f"Lobby {lobby_id} marked as inactive")
            
            del self.user_lobby_map[user_id]
            current_app.logger.info(f"User {user_id} left lobby {lobby_id}")
            return True
    
    def get_public_lobbies(self) -> List[dict]:
        """Get list of all active lobbies (all lobbies are now public)"""
        with self._lock:
            public_lobbies = []
            for lobby in self.lobbies.values():
                if lobby.is_active:
                    lobby_dict = lobby.to_dict()
                    lobby_dict['is_joinable'] = len(lobby.participants) < lobby.max_participants
                    public_lobbies.append(lobby_dict)
            
            # Sort by creation time (newest first)
            public_lobbies.sort(key=lambda x: x['created_at'], reverse=True)
            
            # Debug logging
            if hasattr(current_app, 'logger'):
                current_app.logger.info(f"🔍 get_public_lobbies: Found {len(public_lobbies)} public lobbies")
                for lobby in public_lobbies:
                    current_app.logger.info(f"   📋 {lobby['name']} - {lobby['participant_count']}/{lobby['max_participants']} participants")
            
            return public_lobbies
    
    def get_user_lobby(self, user_id: str) -> Optional[TroubleshootingLobby]:
        """Get user's current lobby"""
        with self._lock:
            lobby_id = self.user_lobby_map.get(user_id)
            return self.lobbies.get(lobby_id) if lobby_id else None
    
    def get_lobby_by_id(self, lobby_id: str) -> Optional[TroubleshootingLobby]:
        """Get lobby by ID"""
        with self._lock:
            return self.lobbies.get(lobby_id)
    
    def update_participant_activity(self, user_id: str):
        """Update participant's last activity timestamp"""
        with self._lock:
            lobby = self.get_user_lobby(user_id)
            if lobby and user_id in lobby.participants:
                lobby.participants[user_id]['last_activity'] = datetime.utcnow().isoformat()
                lobby.participants[user_id]['is_active'] = True
    
    def cleanup_inactive_lobbies(self):
        """Remove inactive lobbies and disconnected users"""
        with self._lock:
            current_time = datetime.utcnow()
            lobbies_to_remove = []
            
            for lobby_id, lobby in self.lobbies.items():
                # Check if lobby is old (4+ hours) or inactive
                if (not lobby.is_active or 
                    (current_time - lobby.created_at > timedelta(hours=4))):
                    lobbies_to_remove.append(lobby_id)
                    continue
                
                # Check for inactive participants (30+ minutes without activity)
                inactive_participants = []
                for user_id, participant in lobby.participants.items():
                    last_activity = datetime.fromisoformat(
                        participant.get('last_activity', lobby.created_at.isoformat())
                    )
                    if current_time - last_activity > timedelta(minutes=30):
                        inactive_participants.append(user_id)
                
                # Remove inactive participants
                for user_id in inactive_participants:
                    username = lobby.participants[user_id]['username']
                    lobby.remove_participant(user_id)
                    lobby.add_chat_message('system', f"{username} was disconnected due to inactivity", 'system')
                    
                    if user_id in self.user_lobby_map:
                        del self.user_lobby_map[user_id]
                
                # If lobby is now empty, mark as inactive
                if not lobby.participants:
                    lobby.is_active = False
                    lobbies_to_remove.append(lobby_id)
            
            # Remove inactive lobbies
            for lobby_id in lobbies_to_remove:
                lobby = self.lobbies[lobby_id]
                
                # Remove all users from mapping
                for user_id in list(lobby.participants.keys()):
                    if user_id in self.user_lobby_map:
                        del self.user_lobby_map[user_id]
                
                del self.lobbies[lobby_id]
                current_app.logger.info(f"Cleaned up inactive lobby {lobby_id}")
    
    def get_stats(self) -> dict:
        """Get lobby manager statistics"""
        with self._lock:
            active_lobbies = sum(1 for lobby in self.lobbies.values() if lobby.is_active)
            total_participants = sum(len(lobby.participants) for lobby in self.lobbies.values() if lobby.is_active)
            
            return {
                'total_lobbies': len(self.lobbies),
                'active_lobbies': active_lobbies,
                'total_participants': total_participants,
                'avg_participants_per_lobby': total_participants / max(active_lobbies, 1)
            }


# Global lobby manager instance
lobby_manager = LobbyManager()
