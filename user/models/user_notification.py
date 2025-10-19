"""
User Notification Model for RiddleNet
Stores individual notifications for each user with read/unread status
"""

from datetime import datetime
from __init__ import db
from instructor.models.notification_history import NotificationHistory

class UserNotification(db.Model):
    """
    Model for storing individual user notifications
    Links to the admin notification_history table
    """
    __tablename__ = 'user_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Notification Reference
    notification_history_id = db.Column(db.Integer, db.ForeignKey('notification_history.id'), nullable=True)
    
    # Notification Content (can be independent or reference history)
    notification_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='normal')
    
    # Status and Timing
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete
    
    # Delivery Information
    delivery_channel = db.Column(db.String(20), nullable=False, default='both')
    email_delivered = db.Column(db.Boolean, default=False)
    websocket_delivered = db.Column(db.Boolean, default=False)
    
    # Additional Metadata
    action_url = db.Column(db.String(500), nullable=True)  # URL for notification action
    extra_data = db.Column(db.Text, nullable=True)  # JSON string for additional data
    
    # Relationships
    user = db.relationship('User', backref='notifications', lazy=True)
    notification_history = db.relationship('NotificationHistory', backref='user_notifications', lazy=True)
    
    def __repr__(self):
        return f"<UserNotification {self.id}: {self.title} for User {self.user_id}>"
    
    def to_dict(self):
        """Convert user notification to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'delivery_channel': self.delivery_channel,
            'email_delivered': self.email_delivered,
            'websocket_delivered': self.websocket_delivered,
            'action_url': self.action_url,
            'metadata': self.metadata
        }
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            db.session.commit()
    
    def soft_delete(self):
        """Soft delete the notification"""
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def create_notification(cls, user_id, notification_type, title, message, priority='normal', 
                          delivery_channel='both', action_url=None, metadata=None, 
                          notification_history_id=None):
        """Create a new user notification"""
        try:
            notification = cls(
                user_id=user_id,
                notification_history_id=notification_history_id,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                delivery_channel=delivery_channel,
                action_url=action_url,
                metadata=metadata
            )
            
            db.session.add(notification)
            db.session.commit()
            return notification
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user notification: {e}")
            return None
    
    @classmethod
    def get_user_notifications(cls, user_id, limit=50, unread_only=False, include_deleted=False):
        """Get notifications for a specific user"""
        query = cls.query.filter_by(user_id=user_id)
        
        if not include_deleted:
            query = query.filter(cls.deleted_at.is_(None))
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_unread_count(cls, user_id):
        """Get count of unread notifications for user"""
        return cls.query.filter_by(
            user_id=user_id,
            is_read=False
        ).filter(cls.deleted_at.is_(None)).count()
    
    @classmethod
    def mark_all_read(cls, user_id):
        """Mark all notifications as read for a user"""
        try:
            notifications = cls.query.filter_by(
                user_id=user_id,
                is_read=False
            ).filter(cls.deleted_at.is_(None)).all()
            
            for notification in notifications:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
            
            db.session.commit()
            return len(notifications)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error marking all notifications as read: {e}")
            return 0
    
    @classmethod
    def get_notifications_by_type(cls, user_id, notification_type, limit=20):
        """Get notifications by type for a user"""
        return cls.query.filter_by(
            user_id=user_id,
            notification_type=notification_type
        ).filter(cls.deleted_at.is_(None)).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def cleanup_old_notifications(cls, user_id, days=30):
        """Clean up old notifications for a user"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_notifications = cls.query.filter(
            cls.user_id == user_id,
            cls.created_at < cutoff_date
        ).all()
        
        count = len(old_notifications)
        for notification in old_notifications:
            db.session.delete(notification)
        
        db.session.commit()
        return count
    
    @classmethod
    def get_user_stats(cls, user_id):
        """Get notification statistics for a user"""
        total = cls.query.filter_by(user_id=user_id).filter(cls.deleted_at.is_(None)).count()
        unread = cls.query.filter_by(user_id=user_id, is_read=False).filter(cls.deleted_at.is_(None)).count()
        read = total - unread
        
        # Get counts by type
        type_counts = {}
        notifications = cls.query.filter_by(user_id=user_id).filter(cls.deleted_at.is_(None)).all()
        for notification in notifications:
            if notification.notification_type not in type_counts:
                type_counts[notification.notification_type] = {'total': 0, 'unread': 0}
            type_counts[notification.notification_type]['total'] += 1
            if not notification.is_read:
                type_counts[notification.notification_type]['unread'] += 1
        
        return {
            'total_notifications': total,
            'unread_count': unread,
            'read_count': read,
            'types': type_counts
        }
