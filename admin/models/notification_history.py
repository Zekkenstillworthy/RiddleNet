"""
Notification History Model for RiddleNet
Stores all sent notifications for audit and tracking purposes
"""

from datetime import datetime
from admin import db

class NotificationHistory(db.Model):
    """
    Model for storing notification history and audit trail
    """
    __tablename__ = 'notification_history'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Sender Information
    sender_id = db.Column(db.Integer, nullable=False)  # Admin/User who sent the notification
    sender_type = db.Column(db.String(20), nullable=False)  # 'admin' or 'user'
    sender_username = db.Column(db.String(100), nullable=False)
    
    # Notification Content
    notification_type = db.Column(db.String(50), nullable=False)  # account_activity, system_update, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False)  # low, normal, high, urgent
    
    # Recipient Information
    recipient_type = db.Column(db.String(20), nullable=False)  # all_users, all_admins, specific_user
    recipient_count = db.Column(db.Integer, default=0)  # Number of recipients
    specific_user_id = db.Column(db.Integer, nullable=True)  # If sent to specific user
    
    # Delivery Information
    delivery_channel = db.Column(db.String(20), nullable=False)  # email, websocket, both
    email_sent = db.Column(db.Integer, default=0)  # Number of emails sent
    websocket_sent = db.Column(db.Integer, default=0)  # Number of websocket notifications sent
    failed_deliveries = db.Column(db.Integer, default=0)  # Number of failed deliveries
    
    # Status and Timing
    status = db.Column(db.String(20), default='sent')  # sent, failed, partial
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_time = db.Column(db.Float, nullable=True)  # Time taken to send (in seconds)
    
    # Additional Data
    template_data = db.Column(db.Text, nullable=True)  # JSON string for template variables
    error_details = db.Column(db.Text, nullable=True)  # Error details if any
    
    def __repr__(self):
        return f"<NotificationHistory {self.id}: {self.title} to {self.recipient_type}>"
    
    def to_dict(self):
        """Convert notification history to dictionary"""
        return {
            'id': self.id,
            'sender_username': self.sender_username,
            'sender_type': self.sender_type,
            'type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'recipient_type': self.recipient_type,
            'recipient_count': self.recipient_count,
            'delivery_channel': self.delivery_channel,
            'email_sent': self.email_sent,
            'websocket_sent': self.websocket_sent,
            'failed_deliveries': self.failed_deliveries,
            'status': self.status,
            'timestamp': self.created_at.isoformat() if self.created_at else None,
            'delivery_time': self.delivery_time
        }
    
    @classmethod
    def create_record(cls, sender_id, sender_type, sender_username, notification_data, result, delivery_time=None):
        """Create a new notification history record"""
        try:
            record = cls(
                sender_id=sender_id,
                sender_type=sender_type,
                sender_username=sender_username,
                notification_type=notification_data.get('notification_type', 'admin_notice'),
                title=notification_data.get('title', ''),
                message=notification_data.get('message', ''),
                priority=notification_data.get('priority', 'normal'),
                recipient_type=notification_data.get('recipient_type', 'all_users'),
                recipient_count=result.get('email_sent', 0) + result.get('websocket_sent', 0),
                specific_user_id=notification_data.get('specific_user'),
                delivery_channel=notification_data.get('channel', 'both'),
                email_sent=result.get('email_sent', 0),
                websocket_sent=result.get('websocket_sent', 0),
                failed_deliveries=result.get('failed', 0),
                status='sent' if result.get('failed', 0) == 0 else 'partial' if result.get('email_sent', 0) > 0 or result.get('websocket_sent', 0) > 0 else 'failed',
                delivery_time=delivery_time,
                template_data=notification_data.get('template_data'),
                error_details=', '.join(result.get('errors', []))
            )
            
            db.session.add(record)
            db.session.commit()
            return record
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating notification history record: {e}")
            return None
    
    @classmethod
    def get_recent_notifications(cls, limit=50):
        """Get recent notifications"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_statistics(cls, days=1):
        """Get notification statistics for the past X days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        notifications = cls.query.filter(cls.created_at >= cutoff_date).all()
        
        total_sent = len(notifications)
        total_emails = sum(n.email_sent for n in notifications)
        total_websockets = sum(n.websocket_sent for n in notifications)
        total_failed = sum(n.failed_deliveries for n in notifications)
        
        return {
            'total_sent': total_sent,
            'emails_sent': total_emails,
            'websockets_sent': total_websockets,
            'failed_deliveries': total_failed,
            'success_rate': ((total_sent - total_failed) / total_sent * 100) if total_sent > 0 else 0
        }
    
    @classmethod
    def cleanup_old_records(cls, days=30):
        """Remove old notification records"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_records = cls.query.filter(cls.created_at < cutoff_date).all()
        count = len(old_records)
        
        for record in old_records:
            db.session.delete(record)
        
        db.session.commit()
        return count
