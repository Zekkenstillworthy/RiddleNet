"""
User Notification Preferences Model for RiddleNet
Stores user preferences for different notification types and delivery methods
"""

from datetime import datetime, time
from __init__ import db
import json

class NotificationPreferences(db.Model):
    """
    Model for storing user notification preferences
    """
    __tablename__ = 'notification_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # General Preferences
    enabled = db.Column(db.Boolean, default=True)  # Master switch for all notifications
    sound_enabled = db.Column(db.Boolean, default=True)
    browser_notifications = db.Column(db.Boolean, default=False)
    
    # Do Not Disturb Settings
    dnd_enabled = db.Column(db.Boolean, default=False)
    dnd_start_time = db.Column(db.Time, nullable=True)  # e.g., 22:00
    dnd_end_time = db.Column(db.Time, nullable=True)    # e.g., 08:00
    dnd_days = db.Column(db.String(20), default='[]')   # JSON array of day numbers (0=Monday)
    
    # Notification Type Preferences (JSON strings)
    account_activity_email = db.Column(db.Boolean, default=True)
    account_activity_websocket = db.Column(db.Boolean, default=True)
    
    system_update_email = db.Column(db.Boolean, default=True)
    system_update_websocket = db.Column(db.Boolean, default=True)
    
    instructor_notice_email = db.Column(db.Boolean, default=True)
    instructor_notice_websocket = db.Column(db.Boolean, default=True)
    
    security_alert_email = db.Column(db.Boolean, default=True)
    security_alert_websocket = db.Column(db.Boolean, default=True)
    
    course_update_email = db.Column(db.Boolean, default=True)
    course_update_websocket = db.Column(db.Boolean, default=True)
    
    quiz_result_email = db.Column(db.Boolean, default=True)
    quiz_result_websocket = db.Column(db.Boolean, default=True)
    
    maintenance_email = db.Column(db.Boolean, default=True)
    maintenance_websocket = db.Column(db.Boolean, default=True)
    
    emergency_email = db.Column(db.Boolean, default=True)
    emergency_websocket = db.Column(db.Boolean, default=True)
    
    login_activity_email = db.Column(db.Boolean, default=True)
    login_activity_websocket = db.Column(db.Boolean, default=False)
    
    otp_request_email = db.Column(db.Boolean, default=True)
    otp_request_websocket = db.Column(db.Boolean, default=True)
    
    # Frequency Settings
    digest_frequency = db.Column(db.String(20), default='instant')  # instant, daily, weekly
    digest_time = db.Column(db.Time, nullable=True)  # Time for daily/weekly digest
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('notification_preferences', uselist=False), lazy=True)
    
    def __repr__(self):
        return f"<NotificationPreferences for User {self.user_id}>"
    
    def to_dict(self):
        """Convert preferences to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'enabled': self.enabled,
            'sound_enabled': self.sound_enabled,
            'browser_notifications': self.browser_notifications,
            'dnd_enabled': self.dnd_enabled,
            'dnd_start_time': self.dnd_start_time.strftime('%H:%M') if self.dnd_start_time else None,
            'dnd_end_time': self.dnd_end_time.strftime('%H:%M') if self.dnd_end_time else None,
            'dnd_days': json.loads(self.dnd_days) if self.dnd_days else [],
            'preferences': {
                'account_activity': {
                    'email': self.account_activity_email,
                    'websocket': self.account_activity_websocket
                },
                'system_update': {
                    'email': self.system_update_email,
                    'websocket': self.system_update_websocket
                },
                'instructor_notice': {
                    'email': self.instructor_notice_email,
                    'websocket': self.instructor_notice_websocket
                },
                'security_alert': {
                    'email': self.security_alert_email,
                    'websocket': self.security_alert_websocket
                },
                'course_update': {
                    'email': self.course_update_email,
                    'websocket': self.course_update_websocket
                },
                'quiz_result': {
                    'email': self.quiz_result_email,
                    'websocket': self.quiz_result_websocket
                },
                'maintenance': {
                    'email': self.maintenance_email,
                    'websocket': self.maintenance_websocket
                },
                'emergency': {
                    'email': self.emergency_email,
                    'websocket': self.emergency_websocket
                },
                'login_activity': {
                    'email': self.login_activity_email,
                    'websocket': self.login_activity_websocket
                },
                'otp_request': {
                    'email': self.otp_request_email,
                    'websocket': self.otp_request_websocket
                }
            },
            'digest_frequency': self.digest_frequency,
            'digest_time': self.digest_time.strftime('%H:%M') if self.digest_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_dnd_active(self):
        """Check if Do Not Disturb is currently active"""
        if not self.dnd_enabled:
            return False
        
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()  # 0=Monday, 6=Sunday
        
        # Check if current day is in DND days
        dnd_days = json.loads(self.dnd_days) if self.dnd_days else []
        if dnd_days and current_day not in dnd_days:
            return False
        
        # Check time range
        if self.dnd_start_time and self.dnd_end_time:
            if self.dnd_start_time <= self.dnd_end_time:
                # Same day range (e.g., 22:00 to 23:59)
                return self.dnd_start_time <= current_time <= self.dnd_end_time
            else:
                # Overnight range (e.g., 22:00 to 08:00)
                return current_time >= self.dnd_start_time or current_time <= self.dnd_end_time
        
        return False
    
    def should_receive_notification(self, notification_type, channel):
        """Check if user should receive a notification based on preferences"""
        if not self.enabled:
            return False
        
        if self.is_dnd_active():
            # Only allow emergency notifications during DND
            if notification_type != 'emergency':
                return False
        
        # Get preference for specific type and channel
        email_attr = f"{notification_type}_email"
        websocket_attr = f"{notification_type}_websocket"
        
        if channel == 'email' and hasattr(self, email_attr):
            return getattr(self, email_attr)
        elif channel == 'websocket' and hasattr(self, websocket_attr):
            return getattr(self, websocket_attr)
        elif channel == 'both':
            email_pref = getattr(self, email_attr, True) if hasattr(self, email_attr) else True
            websocket_pref = getattr(self, websocket_attr, True) if hasattr(self, websocket_attr) else True
            return email_pref or websocket_pref
        
        # Default to allowing if preference not found
        return True
    
    def update_preferences(self, preferences_data):
        """Update user preferences from dictionary"""
        try:
            # Update general preferences
            if 'enabled' in preferences_data:
                self.enabled = preferences_data['enabled']
            if 'sound_enabled' in preferences_data:
                self.sound_enabled = preferences_data['sound_enabled']
            if 'browser_notifications' in preferences_data:
                self.browser_notifications = preferences_data['browser_notifications']
            
            # Update DND settings
            if 'dnd_enabled' in preferences_data:
                self.dnd_enabled = preferences_data['dnd_enabled']
            if 'dnd_start_time' in preferences_data and preferences_data['dnd_start_time']:
                self.dnd_start_time = datetime.strptime(preferences_data['dnd_start_time'], '%H:%M').time()
            if 'dnd_end_time' in preferences_data and preferences_data['dnd_end_time']:
                self.dnd_end_time = datetime.strptime(preferences_data['dnd_end_time'], '%H:%M').time()
            if 'dnd_days' in preferences_data:
                self.dnd_days = json.dumps(preferences_data['dnd_days'])
            
            # Update notification type preferences
            if 'preferences' in preferences_data:
                prefs = preferences_data['preferences']
                for notification_type, channels in prefs.items():
                    if isinstance(channels, dict):
                        for channel, enabled in channels.items():
                            attr_name = f"{notification_type}_{channel}"
                            if hasattr(self, attr_name):
                                setattr(self, attr_name, enabled)
            
            # Update digest settings
            if 'digest_frequency' in preferences_data:
                self.digest_frequency = preferences_data['digest_frequency']
            if 'digest_time' in preferences_data and preferences_data['digest_time']:
                self.digest_time = datetime.strptime(preferences_data['digest_time'], '%H:%M').time()
            
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating notification preferences: {e}")
            return False
    
    @classmethod
    def get_or_create_preferences(cls, user_id):
        """Get existing preferences or create default ones"""
        preferences = cls.query.filter_by(user_id=user_id).first()
        
        if not preferences:
            preferences = cls(user_id=user_id)
            db.session.add(preferences)
            db.session.commit()
        
        return preferences
    
    @classmethod
    def create_default_preferences(cls, user_id):
        """Create default preferences for a new user"""
        try:
            preferences = cls(user_id=user_id)
            db.session.add(preferences)
            db.session.commit()
            return preferences
        except Exception as e:
            db.session.rollback()
            print(f"Error creating default preferences: {e}")
            return None
