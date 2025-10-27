"""
MVP Team Chat Service
Handles database operations for team chat functionality
"""

from __init__ import db
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy import text
import html
import re

# Team Chat Message Model
class TeamChatMessage(db.Model):
    __tablename__ = 'team_chat_messages'
    
    id = db.Column(db.BigInteger, primary_key=True)
    simulation_session_id = db.Column(db.BigInteger, nullable=False)
    team_id = db.Column(db.BigInteger, nullable=True)
    lobby_id = db.Column(db.BigInteger, nullable=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    username_cache = db.Column(db.String(150), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'simulation_session_id': self.simulation_session_id,
            'team_id': self.team_id,
            'lobby_id': self.lobby_id,
            'user_id': self.user_id,
            'username': self.username_cache,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }


class TeamChatService:
    """Service class for team chat operations"""
    
    # Rate limiting configuration
    RATE_LIMIT_MESSAGES = 5
    RATE_LIMIT_WINDOW = 5  # seconds
    _user_message_history = {}  # In-memory rate limiting
    
    def __init__(self):
        pass
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize message content"""
        if not content:
            return ""
        
        # Strip leading/trailing whitespace
        content = content.strip()
        
        # Basic HTML escape for security
        content = html.escape(content)
        
        # Collapse multiple spaces to single space
        content = re.sub(r'\s+', ' ', content)
        
        # Remove control characters (except newlines and tabs)
        content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        
        return content
    
    def validate_content(self, content: str) -> Dict[str, any]:
        """Validate message content"""
        if not content or not content.strip():
            return {'valid': False, 'error': 'Message content cannot be empty'}
        
        content = content.strip()
        if len(content) > 2000:
            return {'valid': False, 'error': 'Message content too long (max 2000 characters)'}
        
        if len(content) < 1:
            return {'valid': False, 'error': 'Message content too short'}
        
        return {'valid': True, 'content': content}
    
    def check_rate_limit(self, user_id: int) -> Dict[str, any]:
        """Check if user is within rate limits"""
        now = datetime.now(timezone.utc)
        user_key = str(user_id)
        
        # Initialize user history if not exists
        if user_key not in self._user_message_history:
            self._user_message_history[user_key] = []
        
        # Clean old messages outside the window
        cutoff_time = now.timestamp() - self.RATE_LIMIT_WINDOW
        self._user_message_history[user_key] = [
            msg_time for msg_time in self._user_message_history[user_key]
            if msg_time > cutoff_time
        ]
        
        # Check if under limit
        if len(self._user_message_history[user_key]) >= self.RATE_LIMIT_MESSAGES:
            return {
                'allowed': False,
                'error': f'Rate limit exceeded: max {self.RATE_LIMIT_MESSAGES} messages per {self.RATE_LIMIT_WINDOW} seconds'
            }
        
        # Add current message time
        self._user_message_history[user_key].append(now.timestamp())
        
        return {'allowed': True}
    
    def save_message(self, simulation_session_id: int, user_id: int, username: str, 
                    content: str, team_id: Optional[int] = None, 
                    lobby_id: Optional[int] = None) -> Dict[str, any]:
        """
        Save a team chat message to the database
        
        Args:
            simulation_session_id: ID of the simulation session
            user_id: ID of the user sending the message
            username: Username for caching
            content: Message content
            team_id: Team ID (optional, for team-based chat)
            lobby_id: Lobby ID (optional, for lobby-based chat)
        
        Returns:
            Dict with success status and message data or error
        """
        try:
            # Validate content
            validation = self.validate_content(content)
            if not validation['valid']:
                return {'success': False, 'error': validation['error']}
            
            # Check rate limit
            rate_check = self.check_rate_limit(user_id)
            if not rate_check['allowed']:
                return {'success': False, 'error': rate_check['error']}
            
            # Sanitize content
            sanitized_content = self.sanitize_content(validation['content'])
            
            # Create message record
            message = TeamChatMessage(
                simulation_session_id=simulation_session_id,
                team_id=team_id,
                lobby_id=lobby_id,
                user_id=user_id,
                username_cache=username,
                content=sanitized_content,
                created_at=datetime.now(timezone.utc)
            )
            
            db.session.add(message)
            db.session.commit()
            
            # Return message data
            message_data = message.to_dict()
            
            print(f"[NOTE] Team chat message saved: ID={message.id}, user={username}, session={simulation_session_id}")
            
            return {
                'success': True,
                'message': message_data
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Error saving team chat message: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to save message: {str(e)}'
            }
    
    def fetch_recent(self, simulation_session_id: int, team_id: Optional[int] = None, 
                    lobby_id: Optional[int] = None, limit: int = 50) -> Dict[str, any]:
        """
        Fetch recent team chat messages
        
        Args:
            simulation_session_id: ID of the simulation session
            team_id: Team ID (optional, for team-based chat)
            lobby_id: Lobby ID (optional, for lobby-based chat)
            limit: Maximum number of messages to return (max 100)
        
        Returns:
            Dict with success status and messages list or error
        """
        try:
            # Enforce reasonable limits
            limit = min(max(1, limit), 100)
            
            # Build query
            query = TeamChatMessage.query.filter(
                TeamChatMessage.simulation_session_id == simulation_session_id,
                TeamChatMessage.deleted_at.is_(None)  # Exclude soft-deleted messages
            )
            
            # Add team or lobby filter
            if team_id is not None:
                query = query.filter(TeamChatMessage.team_id == team_id)
            elif lobby_id is not None:
                query = query.filter(TeamChatMessage.lobby_id == lobby_id)
            
            # Order by creation time (newest first for limit, then reverse)
            messages = query.order_by(TeamChatMessage.created_at.desc()).limit(limit).all()
            
            # Reverse to chronological order (oldest first)
            messages.reverse()
            
            # Convert to dictionaries
            message_list = [msg.to_dict() for msg in messages]
            
            print(f"📚 Fetched {len(message_list)} team chat messages for session {simulation_session_id}")
            
            return {
                'success': True,
                'messages': message_list,
                'count': len(message_list)
            }
            
        except Exception as e:
            print(f"[ERROR] Error fetching team chat messages: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to fetch messages: {str(e)}',
                'messages': []
            }
    
    def get_message_count(self, simulation_session_id: int, team_id: Optional[int] = None, 
                         lobby_id: Optional[int] = None) -> int:
        """Get total message count for a session/team/lobby"""
        try:
            query = TeamChatMessage.query.filter(
                TeamChatMessage.simulation_session_id == simulation_session_id,
                TeamChatMessage.deleted_at.is_(None)
            )
            
            if team_id is not None:
                query = query.filter(TeamChatMessage.team_id == team_id)
            elif lobby_id is not None:
                query = query.filter(TeamChatMessage.lobby_id == lobby_id)
            
            return query.count()
            
        except Exception as e:
            print(f"[ERROR] Error counting team chat messages: {str(e)}")
            return 0
    
    def soft_delete_message(self, message_id: int, user_id: int) -> Dict[str, any]:
        """Soft delete a message (future enhancement)"""
        try:
            message = TeamChatMessage.query.get(message_id)
            if not message:
                return {'success': False, 'error': 'Message not found'}
            
            # Only allow deletion by message author (basic authorization)
            if message.user_id != user_id:
                return {'success': False, 'error': 'Unauthorized to delete this message'}
            
            message.deleted_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return {'success': True, 'message': 'Message deleted'}
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Error soft deleting message: {str(e)}")
            return {'success': False, 'error': str(e)}


# Global service instance
_team_chat_service = TeamChatService()

def get_team_chat_service() -> TeamChatService:
    """Get the global team chat service instance"""
    return _team_chat_service

# Configuration constants
TEAM_CHAT_RECENT_LIMIT = 50  # Default number of recent messages to fetch
TEAM_CHAT_MAX_CONTENT_LENGTH = 2000  # Maximum message content length
TEAM_CHAT_RATE_LIMIT_MESSAGES = 5  # Max messages per time window
TEAM_CHAT_RATE_LIMIT_WINDOW = 5  # Time window in seconds