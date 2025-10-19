"""
Complete Collaboration Service for RiddleNet
Handles team sessions, real-time synchronization, chat functionality, and collaboration management
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import uuid
from collections import defaultdict
from threading import Lock

from __init__ import db
from instructor.models.collaboration import CollaborationSetting, CollaborationLobby, TeamAssignment
from instructor.models.simulation import Simulation
from instructor.models.class_model import Class
from instructor.models.user import User


class TeamSession:
    """Represents an active team collaboration session"""
    
    def __init__(self, session_id: str, simulation_id: int, team_members: List[str], 
                 settings: Dict[str, Any], created_by: str):
        self.session_id = session_id
        self.simulation_id = simulation_id
        self.team_members = team_members  # List of user IDs
        self.settings = settings
        self.created_by = created_by
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        
        # Session state
        self.is_active = True
        self.is_locked = False
        self.current_leader = None
        
        # Collaboration data
        self.participants = {}  # user_id: {username, role, status, cursor_position, etc}
        self.network_state = {}  # Shared network topology state
        self.device_locks = {}  # device_id: user_id
        self.shared_progress = {}  # Shared progress tracking
        self.chat_messages = []  # Chat history
        self.cli_history = {}  # device_id: [commands]
        
        # Synchronization
        self.state_lock = Lock()
        
        # Initialize participants
        self._initialize_participants()
    
    def _initialize_participants(self):
        """Initialize participant data structure"""
        for user_id in self.team_members:
            self.participants[user_id] = {
                'user_id': user_id,
                'username': '',  # Will be updated when they join
                'role': 'member',
                'status': 'offline',
                'joined_at': None,
                'last_seen': None,
                'cursor_position': {'x': 0, 'y': 0},
                'current_device': None,
                'permissions': self._get_default_permissions(),
                'progress': {}
            }
        
        # Set team leader if specified
        if self.created_by in self.participants:
            self.participants[self.created_by]['role'] = 'leader'
            self.current_leader = self.created_by
    
    def _get_default_permissions(self) -> Dict[str, bool]:
        """Get default permissions for a team member"""
        return {
            'can_edit_devices': True,
            'can_move_devices': True,
            'can_configure_devices': True,
            'can_execute_commands': True,
            'can_chat': True,
            'can_view_progress': True
        }
    
    def join_session(self, user_id: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """User joins the team session"""
        with self.state_lock:
            if user_id not in self.team_members:
                return {'success': False, 'error': 'User not assigned to this team'}
            
            if user_id in self.participants:
                self.participants[user_id].update({
                    'username': user_info.get('username', 'Unknown'),
                    'status': 'online',
                    'joined_at': datetime.utcnow(),
                    'last_seen': datetime.utcnow()
                })
                
                self.last_activity = datetime.utcnow()
                
                return {
                    'success': True,
                    'session': self.to_dict(),
                    'participant_info': self.participants[user_id]
                }
            
            return {'success': False, 'error': 'User not found in session'}
    
    def leave_session(self, user_id: str) -> Dict[str, Any]:
        """User leaves the team session"""
        with self.state_lock:
            if user_id in self.participants:
                self.participants[user_id]['status'] = 'offline'
                self.participants[user_id]['last_seen'] = datetime.utcnow()
                
                # Release any device locks held by this user
                devices_to_unlock = [device_id for device_id, locked_by in self.device_locks.items() 
                                   if locked_by == user_id]
                for device_id in devices_to_unlock:
                    del self.device_locks[device_id]
                
                # Transfer leadership if this user was the leader
                if self.current_leader == user_id:
                    self._transfer_leadership()
                
                self.last_activity = datetime.utcnow()
                
                return {'success': True, 'devices_unlocked': devices_to_unlock}
            
            return {'success': False, 'error': 'User not in session'}
    
    def _transfer_leadership(self):
        """Transfer leadership to another online participant"""
        online_members = [uid for uid, data in self.participants.items() 
                         if data['status'] == 'online' and uid != self.current_leader]
        
        if online_members:
            new_leader = online_members[0]
            self.participants[new_leader]['role'] = 'leader'
            self.current_leader = new_leader
        else:
            self.current_leader = None
    
    def update_network_state(self, user_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Update shared network state"""
        with self.state_lock:
            if user_id not in self.participants:
                return {'success': False, 'error': 'User not in session'}
            
            if not self.participants[user_id]['permissions']['can_edit_devices']:
                return {'success': False, 'error': 'Insufficient permissions'}
            
            # Apply changes to network state
            if 'devices' in changes:
                if 'devices' not in self.network_state:
                    self.network_state['devices'] = {}
                self.network_state['devices'].update(changes['devices'])
            
            if 'connections' in changes:
                if 'connections' not in self.network_state:
                    self.network_state['connections'] = []
                self.network_state['connections'].extend(changes['connections'])
            
            if 'removed_devices' in changes:
                for device_id in changes['removed_devices']:
                    if 'devices' in self.network_state and device_id in self.network_state['devices']:
                        del self.network_state['devices'][device_id]
                    # Also remove device locks
                    if device_id in self.device_locks:
                        del self.device_locks[device_id]
            
            if 'removed_connections' in changes:
                if 'connections' in self.network_state:
                    self.network_state['connections'] = [
                        conn for conn in self.network_state['connections']
                        if conn['id'] not in changes['removed_connections']
                    ]
            
            self.last_activity = datetime.utcnow()
            
            return {'success': True, 'network_state': self.network_state}
    
    def lock_device(self, device_id: str, user_id: str) -> Dict[str, Any]:
        """Lock a device for exclusive editing"""
        with self.state_lock:
            if user_id not in self.participants:
                return {'success': False, 'error': 'User not in session'}
            
            if device_id in self.device_locks:
                if self.device_locks[device_id] == user_id:
                    return {'success': True, 'message': 'Device already locked by you'}
                else:
                    locked_by_username = self.participants.get(self.device_locks[device_id], {}).get('username', 'Unknown')
                    return {
                        'success': False, 
                        'error': f'Device is locked by {locked_by_username}',
                        'locked_by': self.device_locks[device_id]
                    }
            
            self.device_locks[device_id] = user_id
            self.last_activity = datetime.utcnow()
            
            return {'success': True}
    
    def unlock_device(self, device_id: str, user_id: str) -> Dict[str, Any]:
        """Unlock a device"""
        with self.state_lock:
            if device_id not in self.device_locks:
                return {'success': True, 'message': 'Device was not locked'}
            
            # Check if user owns the lock or is a leader
            is_leader = self.participants.get(user_id, {}).get('role') == 'leader'
            if self.device_locks[device_id] != user_id and not is_leader:
                return {'success': False, 'error': 'You do not own this device lock'}
            
            del self.device_locks[device_id]
            self.last_activity = datetime.utcnow()
            
            return {'success': True}
    
    def send_chat_message(self, user_id: str, message: str, message_type: str = 'text') -> Dict[str, Any]:
        """Send a chat message"""
        with self.state_lock:
            print(f"💬 [DEBUG] TeamSession.send_chat_message called")
            print(f"💬 [DEBUG]   - user_id: {user_id} (type: {type(user_id)})")
            print(f"💬 [DEBUG]   - message: {message}")
            print(f"💬 [DEBUG]   - session_id: {self.session_id}")
            print(f"💬 [DEBUG]   - team_members: {self.team_members}")
            print(f"💬 [DEBUG]   - participants: {list(self.participants.keys())}")
            
            if user_id not in self.team_members:
                print(f"❌ [DEBUG] User {user_id} not in team_members")
                return {'success': False, 'error': 'User not assigned to this team'}
            
            if user_id not in self.participants:
                print(f"❌ [DEBUG] User {user_id} not in participants")
                return {'success': False, 'error': 'User not in session'}
            
            if not self.participants[user_id]['permissions']['can_chat']:
                print(f"❌ [DEBUG] User {user_id} doesn't have chat permission")
                return {'success': False, 'error': 'Chat permission denied'}
            
            # CRITICAL FIX: Get fresh username from database instead of cached value
            # The cached participant username can be stale/poisoned from previous sessions
            try:
                from models import User
                user = User.query.get(int(user_id))
                actual_username = user.username if user else self.participants[user_id]['username']
                print(f"💬 [DEBUG] Username lookup:")
                print(f"💬 [DEBUG]   - Cached username: {self.participants[user_id]['username']}")
                print(f"💬 [DEBUG]   - Fresh username from DB: {actual_username}")
            except Exception as e:
                print(f"⚠️ [DEBUG] Failed to get fresh username from DB: {e}")
                actual_username = self.participants[user_id]['username']
            
            chat_message = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'username': actual_username,  # ← Use fresh username from DB
                'message': message,
                'message_type': message_type,
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': self.session_id
            }
            
            print(f"💬 [DEBUG] Created chat_message:")
            print(f"💬 [DEBUG]   - id: {chat_message['id']}")
            print(f"💬 [DEBUG]   - user_id: {chat_message['user_id']}")
            print(f"💬 [DEBUG]   - username: {chat_message['username']}")
            
            self.chat_messages.append(chat_message)
            
            # Keep only last 100 messages to prevent memory issues
            if len(self.chat_messages) > 100:
                self.chat_messages = self.chat_messages[-100:]
            
            self.last_activity = datetime.utcnow()
            
            print(f"✅ [DEBUG] Chat message created successfully")
            return {'success': True, 'message': chat_message}
    
    def get_chat_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent chat messages"""
        return self.chat_messages[-limit:] if self.chat_messages else []
    
    def clear_chat_history(self) -> bool:
        """Clear chat history (admin only)"""
        with self.state_lock:
            self.chat_messages = []
            return True
    
    def update_progress(self, user_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user's progress in the session"""
        with self.state_lock:
            if user_id not in self.participants:
                return {'success': False, 'error': 'User not in session'}
            
            self.participants[user_id]['progress'].update(progress_data)
            
            # Update shared progress
            self.shared_progress.update({
                'last_updated_by': user_id,
                'last_updated_at': datetime.utcnow().isoformat(),
                'individual_progress': {
                    uid: data['progress'] for uid, data in self.participants.items()
                }
            })
            
            self.last_activity = datetime.utcnow()
            
            return {'success': True, 'shared_progress': self.shared_progress}
    
    def execute_cli_command(self, user_id: str, device_id: str, command: str) -> Dict[str, Any]:
        """Execute a CLI command on a device"""
        with self.state_lock:
            if user_id not in self.participants:
                return {'success': False, 'error': 'User not in session'}
            
            if not self.participants[user_id]['permissions']['can_execute_commands']:
                return {'success': False, 'error': 'Command execution permission denied'}
            
            # Check if user can access this device (not locked by someone else)
            if device_id in self.device_locks and self.device_locks[device_id] != user_id:
                return {'success': False, 'error': 'Device is locked by another user'}
            
            # Add command to CLI history
            if device_id not in self.cli_history:
                self.cli_history[device_id] = []
            
            command_entry = {
                'user_id': user_id,
                'username': self.participants[user_id]['username'],
                'command': command,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.cli_history[device_id].append(command_entry)
            
            # Keep only last 50 commands per device
            if len(self.cli_history[device_id]) > 50:
                self.cli_history[device_id] = self.cli_history[device_id][-50:]
            
            self.last_activity = datetime.utcnow()
            
            return {'success': True, 'command_entry': command_entry}
    
    def update_cursor_position(self, user_id: str, position: Dict[str, float]) -> Dict[str, Any]:
        """Update user's cursor position"""
        with self.state_lock:
            if user_id in self.participants:
                self.participants[user_id]['cursor_position'] = position
                self.participants[user_id]['last_seen'] = datetime.utcnow()
                return {'success': True}
            
            return {'success': False, 'error': 'User not in session'}
    
    def get_active_participants(self) -> List[Dict[str, Any]]:
        """Get list of currently active participants"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)  # 5 minutes timeout
        
        active = []
        for user_id, data in self.participants.items():
            if (data['status'] == 'online' and 
                data['last_seen'] and 
                datetime.fromisoformat(data['last_seen'].replace('Z', '+00:00')) > cutoff_time):
                active.append(data)
        
        return active
    
    def is_expired(self) -> bool:
        """Check if session has expired (no activity for 1 hour)"""
        return datetime.utcnow() - self.last_activity > timedelta(hours=1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'session_id': self.session_id,
            'simulation_id': self.simulation_id,
            'team_members': self.team_members,
            'settings': self.settings,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'current_leader': self.current_leader,
            'participants': self.participants,
            'network_state': self.network_state,
            'device_locks': self.device_locks,
            'shared_progress': self.shared_progress,
            'recent_chat': self.chat_messages[-10:] if self.chat_messages else [],
            'active_participant_count': len(self.get_active_participants())
        }


class CollaborationService:
    """Main collaboration service managing team sessions and real-time collaboration"""
    
    def __init__(self):
        self.active_sessions: Dict[str, TeamSession] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id: session_id
        self.service_lock = Lock()
        
        # Statistics
        self.stats = {
            'total_sessions_created': 0,
            'active_sessions': 0,
            'total_messages_sent': 0,
            'total_commands_executed': 0
        }
    
    def create_team_session(self, simulation_id: int, team_members: List[str], 
                          created_by: str, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new team collaboration session"""
        with self.service_lock:
            # Generate unique session ID
            session_id = str(uuid.uuid4())[:8]
            
            # Ensure session ID is unique
            while session_id in self.active_sessions:
                session_id = str(uuid.uuid4())[:8]
            
            # Validate simulation exists
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'success': False, 'error': 'Simulation not found'}
            
            # Get collaboration settings for the simulation
            collaboration_setting = CollaborationSetting.query.filter_by(
                simulation_id=simulation_id
            ).first()
            
            if not collaboration_setting or not collaboration_setting.collaboration_enabled:
                return {'success': False, 'error': 'Collaboration not enabled for this simulation'}
            
            # Use provided settings or get from database
            if settings is None:
                settings = collaboration_setting.to_dict()
            
            # Create team session
            session = TeamSession(
                session_id=session_id,
                simulation_id=simulation_id,
                team_members=team_members,
                settings=settings,
                created_by=created_by
            )
            
            self.active_sessions[session_id] = session
            
            # Update user session mappings
            for user_id in team_members:
                self.user_sessions[user_id] = session_id
            
            # Update statistics
            self.stats['total_sessions_created'] += 1
            self.stats['active_sessions'] = len(self.active_sessions)
            
            return {
                'success': True,
                'session_id': session_id,
                'session': session.to_dict()
            }
    
    def join_session(self, session_id: str, user_id: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """User joins a team session"""
        with self.service_lock:
            if session_id not in self.active_sessions:
                return {'success': False, 'error': 'Session not found'}
            
            session = self.active_sessions[session_id]
            result = session.join_session(user_id, user_info)
            
            if result['success']:
                self.user_sessions[user_id] = session_id
            
            return result
    
    def leave_session(self, user_id: str) -> Dict[str, Any]:
        """User leaves their current session"""
        with self.service_lock:
            if user_id not in self.user_sessions:
                return {'success': False, 'error': 'User not in any session'}
            
            session_id = self.user_sessions[user_id]
            session = self.active_sessions.get(session_id)
            
            if not session:
                # Clean up orphaned user session mapping
                del self.user_sessions[user_id]
                return {'success': False, 'error': 'Session not found'}
            
            result = session.leave_session(user_id)
            
            if result['success']:
                del self.user_sessions[user_id]
                
                # Check if session should be cleaned up
                active_participants = session.get_active_participants()
                if not active_participants or session.is_expired():
                    self._cleanup_session(session_id)
            
            return result
    
    def get_session(self, session_id: str) -> Optional[TeamSession]:
        """Get a session by ID"""
        return self.active_sessions.get(session_id)
    
    def get_user_session(self, user_id: str) -> Optional[TeamSession]:
        """Get the session a user is currently in"""
        if user_id in self.user_sessions:
            session_id = self.user_sessions[user_id]
            return self.active_sessions.get(session_id)
        return None
    
    def update_network_state(self, user_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Update network state in user's session"""
        session = self.get_user_session(user_id)
        if not session:
            return {'success': False, 'error': 'User not in any session'}
        
        return session.update_network_state(user_id, changes)
    
    def lock_device(self, user_id: str, device_id: str) -> Dict[str, Any]:
        """Lock a device in user's session"""
        session = self.get_user_session(user_id)
        if not session:
            return {'success': False, 'error': 'User not in any session'}
        
        return session.lock_device(device_id, user_id)
    
    def unlock_device(self, user_id: str, device_id: str) -> Dict[str, Any]:
        """Unlock a device in user's session"""
        session = self.get_user_session(user_id)
        if not session:
            return {'success': False, 'error': 'User not in any session'}
        
        return session.unlock_device(device_id, user_id)
    
    def send_chat_message(self, session_id: str, user_id: str, message: str, message_type: str = 'text') -> Dict[str, Any]:
        """Send a chat message to a team session"""
        with self.service_lock:
            if session_id not in self.active_sessions:
                return {'success': False, 'error': 'Session not found'}
            
            session = self.active_sessions[session_id]
            result = session.send_chat_message(user_id, message, message_type)
            
            if result['success']:
                # Update statistics
                self.stats['total_messages_sent'] += 1
                
                # Broadcast to all session participants
                self._broadcast_chat_message(session_id, result['message'])
            
            return result
    
    def get_chat_history(self, session_id: str, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get chat history for a session"""
        with self.service_lock:
            if session_id not in self.active_sessions:
                return {'success': False, 'error': 'Session not found'}
            
            session = self.active_sessions[session_id]
            
            # Check if user is in session
            if user_id not in session.team_members:
                return {'success': False, 'error': 'User not in session'}
            
            chat_history = session.get_chat_history(limit)
            
            return {
                'success': True,
                'chat_history': chat_history,
                'session_id': session_id
            }
    
    def _broadcast_chat_message(self, session_id: str, message: Dict[str, Any]):
        """Broadcast chat message to all session participants"""
        # This would integrate with your WebSocket system
        # For now, we'll emit a generic event that can be caught by socket handlers
        if hasattr(self, 'socketio') and self.socketio:
            self.socketio.emit('collaboration_chat_message', {
                'session_id': session_id,
                'message': message,
                'success': True
            }, room=f'session_{session_id}')
            
            # Also emit as team_chat_message for compatibility
            self.socketio.emit('team_chat_message', message, room=f'session_{session_id}')
    
    def clear_chat_history(self, session_id: str, admin_user_id: str) -> Dict[str, Any]:
        """Clear chat history for a session (admin only)"""
        with self.service_lock:
            if session_id not in self.active_sessions:
                return {'success': False, 'error': 'Session not found'}
            
            session = self.active_sessions[session_id]
            session.clear_chat_history()
            
            # Add system message about chat clear
            system_message = {
                'id': str(uuid.uuid4()),
                'user_id': 'system',
                'username': 'System',
                'message': 'Chat history cleared by administrator',
                'message_type': 'system',
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': session_id
            }
            
            session.chat_messages.append(system_message)
            
            # Broadcast clear event
            if hasattr(self, 'socketio') and self.socketio:
                self.socketio.emit('chat_history_cleared', {
                    'session_id': session_id,
                    'cleared_by': admin_user_id
                }, room=f'session_{session_id}')
            
            return {'success': True, 'message': 'Chat history cleared'}

    def execute_cli_command(self, user_id: str, device_id: str, command: str) -> Dict[str, Any]:
        """Execute CLI command in user's session"""
        session = self.get_user_session(user_id)
        if not session:
            return {'success': False, 'error': 'User not in any session'}
        
        result = session.execute_cli_command(user_id, device_id, command)
        if result['success']:
            self.stats['total_commands_executed'] += 1
        
        return result
    
    def update_progress(self, user_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user progress in their session"""
        session = self.get_user_session(user_id)
        if not session:
            return {'success': False, 'error': 'User not in any session'}
        
        return session.update_progress(user_id, progress_data)
    
    def update_cursor_position(self, user_id: str, position: Dict[str, float]) -> Dict[str, Any]:
        """Update user cursor position in their session"""
        session = self.get_user_session(user_id)
        if not session:
            return {'success': False, 'error': 'User not in any session'}
        
        return session.update_cursor_position(user_id, position)
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        with self.service_lock:
            return [session.to_dict() for session in self.active_sessions.values()]
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        with self.service_lock:
            self.stats['active_sessions'] = len(self.active_sessions)
            
            # Add real-time stats
            total_participants = sum(
                len(session.get_active_participants()) 
                for session in self.active_sessions.values()
            )
            
            return {
                **self.stats,
                'total_active_participants': total_participants
            }
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (should be called periodically)"""
        with self.service_lock:
            expired_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if session.is_expired()
            ]
            
            for session_id in expired_sessions:
                self._cleanup_session(session_id)
            
            return len(expired_sessions)
    
    def _cleanup_session(self, session_id: str):
        """Clean up a session and its related data"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Remove user session mappings
            users_to_remove = [
                user_id for user_id, mapped_session_id in self.user_sessions.items()
                if mapped_session_id == session_id
            ]
            
            for user_id in users_to_remove:
                if user_id in self.user_sessions:
                    del self.user_sessions[user_id]
            
            # Remove session
            del self.active_sessions[session_id]
            
            print(f"🧹 Cleaned up expired session {session_id}")
    
    def force_end_session(self, session_id: str, admin_user_id: str = None) -> Dict[str, Any]:
        """Force end a session (admin function)"""
        with self.service_lock:
            if session_id not in self.active_sessions:
                return {'success': False, 'error': 'Session not found'}
            
            session = self.active_sessions[session_id]
            
            # Mark session as inactive
            session.is_active = False
            
            # Add system message
            if admin_user_id:
                session.chat_messages.append({
                    'id': str(uuid.uuid4()),
                    'user_id': 'system',
                    'username': 'System',
                    'message': f'Session ended by administrator',
                    'message_type': 'system',
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Clean up
            self._cleanup_session(session_id)
            
            return {'success': True, 'message': 'Session ended successfully'}


# Global collaboration service instance
_collaboration_service = None

def get_collaboration_service():
    global _collaboration_service
    if _collaboration_service is None:
        _collaboration_service = CollaborationService()
    return _collaboration_service

# Utility functions for integration with other parts of the system

def create_team_assignments(class_id: int, simulation_id: int, teams: List[Dict[str, Any]], 
                          instructor_id: int) -> Dict[str, Any]:
    """Create team assignments for a class and simulation"""
    try:
        assignments = []
        
        for team_data in teams:
            team_assignment = TeamAssignment(
                class_id=class_id,
                simulation_id=simulation_id,
                team_name=team_data['name'],
                team_members=team_data['members'],  # List of user IDs
                team_leader=team_data.get('leader'),
                created_by=instructor_id
            )
            
            db.session.add(team_assignment)
            assignments.append(team_assignment)
        
        db.session.commit()
        
        return {
            'success': True,
            'assignments': [assignment.to_dict() for assignment in assignments]
        }
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}

def get_team_assignments(class_id: int, simulation_id: int = None) -> List[Dict[str, Any]]:
    """Get team assignments for a class"""
    query = TeamAssignment.query.filter_by(class_id=class_id, is_active=True)
    
    if simulation_id:
        query = query.filter_by(simulation_id=simulation_id)
    
    assignments = query.all()
    return [assignment.to_dict() for assignment in assignments]

def get_collaboration_settings(simulation_id: int) -> Dict[str, Any]:
    """Get collaboration settings for a simulation"""
    setting = CollaborationSetting.query.filter_by(simulation_id=simulation_id).first()
    
    if setting:
        return setting.to_dict()
    else:
        # Return default settings
        return {
            'collaboration_enabled': False,
            'team_size': 2,
            'shared_terminal': False,
            'individual_terminals': True,
            'follow_leader': False,
            'chat_enabled': False,
            'transcript_logging': False,
            'allow_late_join': True,
            'require_instructor': False,
            'time_window': None,
            'roles': ['Leader', 'Observer', 'Operator']
        }

def save_collaboration_settings(simulation_id: int, settings: Dict[str, Any], instructor_id: int) -> Dict[str, Any]:
    """Save collaboration settings for a simulation"""
    try:
        setting = CollaborationSetting.query.filter_by(simulation_id=simulation_id).first()
        
        if not setting:
            setting = CollaborationSetting(
                simulation_id=simulation_id,
                created_by=instructor_id
            )
            db.session.add(setting)
        
        # Update settings
        setting.collaboration_enabled = settings.get('collaboration_enabled', False)
        setting.team_size = settings.get('team_size', 2)
        setting.shared_terminal = settings.get('shared_terminal', False)
        setting.individual_terminals = settings.get('individual_terminals', True)
        setting.follow_leader = settings.get('follow_leader', False)
        setting.chat_enabled = settings.get('chat_enabled', False)
        setting.transcript_logging = settings.get('transcript_logging', False)
        setting.allow_late_join = settings.get('allow_late_join', True)
        setting.require_instructor = settings.get('require_instructor', False)
        setting.time_window = settings.get('time_window')
        setting.roles = settings.get('roles', ['Leader', 'Observer', 'Operator'])
        setting.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return {'success': True, 'settings': setting.to_dict()}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}

# Background cleanup task (should be scheduled to run periodically)
def cleanup_expired_sessions():
    """Cleanup task to remove expired sessions"""
    return collaboration_service.cleanup_expired_sessions()
