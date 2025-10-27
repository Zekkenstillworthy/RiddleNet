"""
Lobby Persistence Service
Integrates database persistence with the in-memory lobby manager
Provides automatic saving, loading, and recovery of lobby data
"""

from __init__ import db
from user.models.collaboration_lobby import (
    CollaborationLobby, LobbyParticipant, LobbyChatMessage, 
    LobbyDeviceLock, LobbyCLIHistory
)
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import json


class LobbyPersistenceService:
    """Service for persisting and loading lobby data"""
    
    @staticmethod
    def save_lobby(lobby_obj):
        """
        Save or update a lobby to the database
        
        Args:
            lobby_obj: TroubleshootingLobby instance from lobby manager
            
        Returns:
            CollaborationLobby: Database model instance
        """
        try:
            # Check if lobby already exists
            db_lobby = CollaborationLobby.query.get(lobby_obj.id)
            
            if db_lobby:
                # Update existing lobby
                db_lobby.name = lobby_obj.name
                db_lobby.scenario_type = lobby_obj.scenario_type
                db_lobby.scenario_id = lobby_obj.scenario_id
                db_lobby.max_participants = lobby_obj.max_participants
                db_lobby.is_active = lobby_obj.is_active
                db_lobby.is_locked = lobby_obj.is_locked
                db_lobby.network_state = lobby_obj.network_state
                db_lobby.progress = lobby_obj.progress
                db_lobby.last_activity_at = datetime.utcnow()
            else:
                # Create new lobby
                db_lobby = CollaborationLobby(
                    id=lobby_obj.id,
                    name=lobby_obj.name,
                    scenario_type=lobby_obj.scenario_type,
                    scenario_id=lobby_obj.scenario_id,
                    max_participants=lobby_obj.max_participants,
                    class_id=lobby_obj.class_id,
                    creator_id=int(lobby_obj.creator_id) if lobby_obj.creator_id else None,
                    creator_name=lobby_obj.creator_name,
                    is_active=lobby_obj.is_active,
                    is_locked=lobby_obj.is_locked,
                    network_state=lobby_obj.network_state,
                    progress=lobby_obj.progress,
                    created_at=lobby_obj.created_at,
                    last_activity_at=datetime.utcnow()
                )
                db.session.add(db_lobby)
            
            db.session.commit()
            current_app.logger.info(f"[OK] Saved lobby {lobby_obj.id} to database")
            return db_lobby
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[ERROR] Error saving lobby {lobby_obj.id}: {e}")
            raise
    
    @staticmethod
    def save_participant(lobby_id, user_id, participant_info):
        """
        Save or update a participant in the database
        
        Args:
            lobby_id: Lobby ID
            user_id: User ID
            participant_info: Participant data dictionary
            
        Returns:
            LobbyParticipant: Database model instance
        """
        try:
            # Check if participant already exists
            db_participant = LobbyParticipant.query.filter_by(
                lobby_id=lobby_id,
                user_id=int(user_id)
            ).first()
            
            if db_participant:
                # Update existing participant
                db_participant.username = participant_info.get('username', db_participant.username)
                db_participant.profile_image = participant_info.get('profile_image')
                db_participant.role = participant_info.get('role', 'participant')
                cursor_pos = participant_info.get('cursor_position', {})
                db_participant.cursor_x = cursor_pos.get('x', 0)
                db_participant.cursor_y = cursor_pos.get('y', 0)
                db_participant.selected_device = participant_info.get('selected_device')
                db_participant.is_active = participant_info.get('is_active', True)
                db_participant.last_activity = datetime.utcnow()
                
                # Update scores
                score = participant_info.get('score', {})
                db_participant.individual_score = score.get('individual', 0)
                db_participant.team_contribution = score.get('team_contribution', 0)
            else:
                # Create new participant
                cursor_pos = participant_info.get('cursor_position', {})
                score = participant_info.get('score', {})
                
                db_participant = LobbyParticipant(
                    lobby_id=lobby_id,
                    user_id=int(user_id),
                    username=participant_info.get('username', 'Unknown'),
                    profile_image=participant_info.get('profile_image'),
                    role=participant_info.get('role', 'participant'),
                    cursor_x=cursor_pos.get('x', 0),
                    cursor_y=cursor_pos.get('y', 0),
                    selected_device=participant_info.get('selected_device'),
                    user_color=participant_info.get('color', '#00D9FF'),
                    is_active=participant_info.get('is_active', True),
                    individual_score=score.get('individual', 0),
                    team_contribution=score.get('team_contribution', 0),
                    joined_at=datetime.fromisoformat(participant_info['joined_at']) 
                             if 'joined_at' in participant_info else datetime.utcnow()
                )
                db.session.add(db_participant)
            
            db.session.commit()
            return db_participant
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[ERROR] Error saving participant {user_id} in lobby {lobby_id}: {e}")
            raise
    
    @staticmethod
    def save_chat_message(lobby_id, message_data):
        """
        Save a chat message to the database
        
        Args:
            lobby_id: Lobby ID
            message_data: Message data dictionary
            
        Returns:
            LobbyChatMessage: Database model instance
        """
        try:
            db_message = LobbyChatMessage(
                lobby_id=lobby_id,
                user_id=str(message_data.get('user_id', 'system')),
                username=message_data.get('username', 'System'),
                profile_image=message_data.get('profile_image'),
                message=message_data.get('message', ''),
                message_type=message_data.get('type', 'text'),
                timestamp=datetime.fromisoformat(message_data['timestamp']) 
                         if 'timestamp' in message_data else datetime.utcnow()
            )
            db.session.add(db_message)
            db.session.commit()
            return db_message
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[ERROR] Error saving chat message in lobby {lobby_id}: {e}")
            raise
    
    @staticmethod
    def save_device_lock(lobby_id, device_id, lock_info):
        """
        Save a device lock to the database
        
        Args:
            lobby_id: Lobby ID
            device_id: Device ID
            lock_info: Lock information dictionary
            
        Returns:
            LobbyDeviceLock: Database model instance
        """
        try:
            # Remove existing lock for this device
            LobbyDeviceLock.query.filter_by(
                lobby_id=lobby_id,
                device_id=device_id
            ).delete()
            
            db_lock = LobbyDeviceLock(
                lobby_id=lobby_id,
                device_id=device_id,
                locked_by=int(lock_info['locked_by']),
                username=lock_info['username'],
                locked_at=datetime.fromisoformat(lock_info['locked_at']) 
                         if 'locked_at' in lock_info else datetime.utcnow(),
                auto_unlock_at=datetime.fromisoformat(lock_info['auto_unlock_at']) 
                              if 'auto_unlock_at' in lock_info else datetime.utcnow() + timedelta(minutes=5)
            )
            db.session.add(db_lock)
            db.session.commit()
            return db_lock
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[ERROR] Error saving device lock for {device_id} in lobby {lobby_id}: {e}")
            raise
    
    @staticmethod
    def remove_device_lock(lobby_id, device_id):
        """Remove a device lock from the database"""
        try:
            LobbyDeviceLock.query.filter_by(
                lobby_id=lobby_id,
                device_id=device_id
            ).delete()
            db.session.commit()
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[ERROR] Error removing device lock for {device_id} in lobby {lobby_id}: {e}")
    
    @staticmethod
    def save_cli_command(lobby_id, device_id, command_data):
        """
        Save a CLI command to the database
        
        Args:
            lobby_id: Lobby ID
            device_id: Device ID
            command_data: Command data dictionary
            
        Returns:
            LobbyCLIHistory: Database model instance
        """
        try:
            db_command = LobbyCLIHistory(
                lobby_id=lobby_id,
                device_id=device_id,
                command=command_data.get('command', ''),
                output=command_data.get('output', ''),
                executed_by=int(command_data['executed_by']),
                username=command_data.get('username', 'Unknown'),
                timestamp=datetime.fromisoformat(command_data['timestamp']) 
                         if 'timestamp' in command_data else datetime.utcnow()
            )
            db.session.add(db_command)
            db.session.commit()
            return db_command
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[ERROR] Error saving CLI command for {device_id} in lobby {lobby_id}: {e}")
            raise
    
    @staticmethod
    def load_lobby(lobby_id):
        """
        Load a lobby from the database
        
        Args:
            lobby_id: Lobby ID to load
            
        Returns:
            dict: Lobby data ready to recreate TroubleshootingLobby instance
        """
        try:
            db_lobby = CollaborationLobby.query.get(lobby_id)
            if not db_lobby:
                return None
            
            # Load participants
            participants = {}
            for db_participant in db_lobby.participants.filter_by(is_active=True).all():
                participants[str(db_participant.user_id)] = {
                    'user_id': str(db_participant.user_id),
                    'username': db_participant.username,
                    'profile_image': db_participant.profile_image,
                    'role': db_participant.role,
                    'cursor_position': {'x': db_participant.cursor_x, 'y': db_participant.cursor_y},
                    'selected_device': db_participant.selected_device,
                    'color': db_participant.user_color,
                    'is_active': db_participant.is_active,
                    'score': {
                        'individual': db_participant.individual_score,
                        'team_contribution': db_participant.team_contribution
                    },
                    'joined_at': db_participant.joined_at.isoformat(),
                    'last_activity': db_participant.last_activity.isoformat()
                }
            
            # Load device locks
            device_locks = {}
            for db_lock in db_lobby.device_locks.all():
                # Check if lock is expired
                if db_lock.auto_unlock_at > datetime.utcnow():
                    device_locks[db_lock.device_id] = {
                        'locked_by': str(db_lock.locked_by),
                        'username': db_lock.username,
                        'locked_at': db_lock.locked_at.isoformat(),
                        'auto_unlock_at': db_lock.auto_unlock_at.isoformat()
                    }
            
            # Load chat history (last 100 messages)
            chat_history = []
            for db_message in db_lobby.chat_messages.order_by(
                LobbyChatMessage.timestamp.desc()
            ).limit(100).all():
                chat_history.append({
                    'id': str(db_message.id),
                    'user_id': db_message.user_id,
                    'username': db_message.username,
                    'profile_image': db_message.profile_image,
                    'message': db_message.message,
                    'type': db_message.message_type,
                    'timestamp': db_message.timestamp.isoformat()
                })
            chat_history.reverse()  # Oldest first
            
            # Load CLI history (last 50 commands per device)
            cli_history = {}
            for db_command in db_lobby.cli_history.order_by(
                LobbyCLIHistory.timestamp.desc()
            ).limit(200).all():
                if db_command.device_id not in cli_history:
                    cli_history[db_command.device_id] = []
                
                if len(cli_history[db_command.device_id]) < 50:
                    cli_history[db_command.device_id].append({
                        'id': str(db_command.id),
                        'command': db_command.command,
                        'output': db_command.output,
                        'executed_by': str(db_command.executed_by),
                        'username': db_command.username,
                        'timestamp': db_command.timestamp.isoformat()
                    })
            
            # Reverse to have oldest first
            for device_id in cli_history:
                cli_history[device_id].reverse()
            
            return {
                'id': db_lobby.id,
                'name': db_lobby.name,
                'scenario_type': db_lobby.scenario_type,
                'scenario_id': db_lobby.scenario_id,
                'max_participants': db_lobby.max_participants,
                'class_id': db_lobby.class_id,
                'creator_id': str(db_lobby.creator_id) if db_lobby.creator_id else None,
                'creator_name': db_lobby.creator_name,
                'participants': participants,
                'network_state': db_lobby.network_state or {},
                'device_locks': device_locks,
                'cli_history': cli_history,
                'created_at': db_lobby.created_at,
                'is_active': db_lobby.is_active,
                'is_locked': db_lobby.is_locked,
                'progress': db_lobby.progress or {},
                'chat_history': chat_history
            }
            
        except SQLAlchemyError as e:
            current_app.logger.error(f"[ERROR] Error loading lobby {lobby_id}: {e}")
            return None
    
    @staticmethod
    def get_all_active_lobbies():
        """
        Get all active lobbies from database
        
        Returns:
            list: List of active lobby dictionaries
        """
        try:
            active_lobbies = CollaborationLobby.query.filter_by(is_active=True).all()
            return [LobbyPersistenceService.load_lobby(lobby.id) for lobby in active_lobbies]
            
        except SQLAlchemyError as e:
            current_app.logger.error(f"[ERROR] Error loading active lobbies: {e}")
            return []
    
    @staticmethod
    def mark_participant_inactive(lobby_id, user_id):
        """Mark a participant as inactive (left the lobby)"""
        try:
            db_participant = LobbyParticipant.query.filter_by(
                lobby_id=lobby_id,
                user_id=int(user_id)
            ).first()
            
            if db_participant:
                db_participant.is_active = False
                db_participant.left_at = datetime.utcnow()
                db.session.commit()
                
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[ERROR] Error marking participant {user_id} inactive: {e}")
    
    @staticmethod
    def close_lobby(lobby_id):
        """Mark a lobby as closed"""
        try:
            db_lobby = CollaborationLobby.query.get(lobby_id)
            if db_lobby:
                db_lobby.is_active = False
                db_lobby.closed_at = datetime.utcnow()
                db.session.commit()
                
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[ERROR] Error closing lobby {lobby_id}: {e}")
    
    @staticmethod
    def cleanup_old_lobbies(hours=24):
        """
        Clean up old inactive lobbies from the database
        
        Args:
            hours: Delete lobbies older than this many hours
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            old_lobbies = CollaborationLobby.query.filter(
                CollaborationLobby.is_active == False,
                CollaborationLobby.last_activity_at < cutoff_time
            ).all()
            
            for lobby in old_lobbies:
                db.session.delete(lobby)
            
            db.session.commit()
            current_app.logger.info(f"🧹 Cleaned up {len(old_lobbies)} old lobbies")
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"[ERROR] Error cleaning up old lobbies: {e}")
    
    @staticmethod
    def get_user_lobby_history(user_id, limit=10):
        """Get lobby participation history for a user"""
        try:
            participations = LobbyParticipant.query.filter_by(
                user_id=int(user_id)
            ).order_by(
                LobbyParticipant.joined_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    'lobby_id': p.lobby_id,
                    'lobby_name': p.lobby.name,
                    'role': p.role,
                    'joined_at': p.joined_at.isoformat(),
                    'left_at': p.left_at.isoformat() if p.left_at else None,
                    'is_active': p.is_active,
                    'individual_score': p.individual_score,
                    'team_contribution': p.team_contribution
                }
                for p in participations
            ]
            
        except SQLAlchemyError as e:
            current_app.logger.error(f"[ERROR] Error loading user lobby history: {e}")
            return []


# Global persistence service instance
lobby_persistence = LobbyPersistenceService()
