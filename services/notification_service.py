"""
Enhanced Notification Service for RiddleNet
Handles both email and WebSocket notifications with cyber-themed templates
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import time
from flask import current_app
from user.models.user import User
from instructor.models.user import Instructor
from __init__ import db

class NotificationType(Enum):
    """Notification types for different categories"""
    ACCOUNT_ACTIVITY = "account_activity"
    SYSTEM_UPDATE = "system_update"
    ADMIN_NOTICE = "admin_notice"
    OTP_REQUEST = "otp_request"
    LOGIN_ACTIVITY = "login_activity"
    SECURITY_ALERT = "security_alert"
    COURSE_UPDATE = "course_update"
    QUIZ_RESULT = "quiz_result"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"

class NotificationPriority(Enum):
    """Priority levels for notifications"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(Enum):
    """Delivery channels for notifications"""
    EMAIL = "email"
    WEBSOCKET = "websocket"
    BOTH = "both"

class NotificationService:
    """Enhanced notification service with email and WebSocket delivery"""
    
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.sender_email = os.getenv('MAIL_USERNAME')
        self.sender_password = os.getenv('MAIL_PASSWORD')
        
    def send_notification(self, 
                         users: List[Any], 
                         notification_type: NotificationType,
                         title: str,
                         message: str,
                         priority: NotificationPriority = NotificationPriority.NORMAL,
                         channel: NotificationChannel = NotificationChannel.BOTH,
                         template_data: Optional[Dict] = None,
                         sender_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send notification to multiple users via specified channels
        
        Args:
            users: List of User/Admin objects
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Priority level
            channel: Delivery channel (email, websocket, or both)
            template_data: Additional data for email templates
            sender_info: Information about who sent the notification
            
        Returns:
            Dict with delivery results
        """
        start_time = time.time()
        
        results = {
            'email_sent': 0,
            'websocket_sent': 0,
            'failed': 0,
            'errors': []
        }
        
        if not users:
            results['errors'].append("No users specified")
            return results
            
        # Create notification record
        notification_data = {
            'type': notification_type.value,
            'title': title,
            'message': message,
            'priority': priority.value,
            'timestamp': datetime.utcnow().isoformat(),
            'template_data': template_data or {}
        }
        # Include sender username if available for UI display
        if sender_info and sender_info.get('sender_username'):
            notification_data['sender_username'] = sender_info.get('sender_username')
        
        for user in users:
            try:
                # Create UserNotification record for persistent display on dashboard
                from user.models.user_notification import UserNotification
                
                # Create UserNotification for this user 
                user_notification = UserNotification.create_notification(
                    user_id=user.id,
                    notification_type=notification_type.value,
                    title=title,
                    message=message,
                    priority=priority.value.lower(),
                    delivery_channel=channel.value if hasattr(channel, 'value') else 'both'
                )
                
                if user_notification:
                    print(f"✅ Created UserNotification for {user.username}")
                else:
                    print(f"❌ Failed to create UserNotification for {user.username}")
                
                # Send via WebSocket if requested
                if channel in [NotificationChannel.WEBSOCKET, NotificationChannel.BOTH]:
                    if self._send_websocket_notification(user, notification_data, user_notification=user_notification):
                        results['websocket_sent'] += 1
                        
                # Send via Email if requested
                if channel in [NotificationChannel.EMAIL, NotificationChannel.BOTH]:
                    if self._send_email_notification(user, notification_type, notification_data):
                        results['email_sent'] += 1
                        
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Failed to send to {user.username}: {str(e)}")
                print(f"❌ Error processing notification for {user.username}: {e}")
        
        # Record in database for audit trail
        delivery_time = time.time() - start_time
        if sender_info:
            self._record_notification_history(sender_info, notification_data, results, delivery_time)
        
        # Add success flag
        results['success'] = results['failed'] == 0
        results['total_processed'] = len(users)
                
        return results
    
    def _send_websocket_notification(self, user: Any, notification_data: Dict, user_notification: Optional[Any] = None) -> bool:
        """Send WebSocket notification to user"""
        if not self.socketio:
            print(f"⚠️ SocketIO not available for WebSocket notification to {user.username}")
            return False
            
        try:
            # Determine user room
            room = f"user_{user.id}"
            
            print(f"🔍 DEBUG: Preparing WebSocket notification for user {user.id} ({user.username})")
            print(f"🔍 DEBUG: Room: {room}")
            print(f"🔍 DEBUG: Notification data: {notification_data}")
            print(f"🔍 DEBUG: SocketIO available: {self.socketio is not None}")
            
            # Send to user's personal room
            self.socketio.emit('notification', notification_data, room=room)
            print(f"📤 Notification sent to user {user.id} ({user.username}) room: {room}")
            
            # For ALL admin notifications, also emit as announcement for better visibility
            notification_type = notification_data.get('type', '')
            print(f"🔍 DEBUG: Notification type: {notification_type}")
            
            # Expanded list to include all relevant notification types
            announcement_types = [
                'system_update', 'admin_notice', 'maintenance', 'security_alert', 
                'course_update', 'system_announcement', 'account_activity', 
                'login_activity', 'otp_request', 'emergency'
            ]
            
            if notification_type in announcement_types:
                # Create properly formatted announcement data for dashboard
                announcement_data = {
                    'id': getattr(user_notification, 'id', None) if user_notification else None,  # Include ID for dismiss functionality
                    'title': notification_data.get('title', 'Announcement'),
                    'message': notification_data.get('message', ''),
                    'type': notification_data.get('type', 'admin_notice'),
                    'priority': notification_data.get('priority', 'normal'),
                    'timestamp': notification_data.get('timestamp'),
                    'from_instructor': True,
                    'instructor_name': notification_data.get('sender_username', 'Admin'),
                    'content': notification_data.get('message', ''),  # Alternative field for message
                    'source': 'admin_notification'
                }
                
                print(f"🔍 DEBUG: Sending announcement data: {announcement_data}")
                
                # Emit to specific user for dashboard announcements
                self.socketio.emit('new_announcement', announcement_data, room=room)
                print(f"✅ Announcement sent to user {user.id} ({user.username}): {announcement_data['title']} (ID: {announcement_data['id']})")
                
                # ALSO emit to all_users room for broader reach
                self.socketio.emit('new_announcement', announcement_data, room='all_users')
                print(f"✅ Announcement also sent to all_users room")
                
                # ALSO emit to announcements room for general announcement handling
                self.socketio.emit('new_announcement', announcement_data, room='announcements')
                print(f"✅ Announcement also sent to announcements room")
                
            else:
                print(f"🔍 DEBUG: Notification type '{notification_type}' not in announcement types, only sending as notification")
            
            # Also send to admin room if it's a high priority notification
            if notification_data.get('priority') in ['high', 'urgent']:
                admin_data = notification_data.copy()
                admin_data['user_info'] = {
                    'username': user.username,
                    'email': getattr(user, 'email', 'N/A'),
                    'user_id': user.id
                }
                self.socketio.emit('admin_notification', admin_data, room='admin_room')
                print(f"📤 High priority notification also sent to admin_room")
                
            return True
            
        except Exception as e:
            print(f"❌ WebSocket notification failed for user {user.username}: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return False
    
    def _send_email_notification(self, user: Any, notification_type: NotificationType, notification_data: Dict) -> bool:
        """Send email notification with cyber-themed template"""
        if not hasattr(user, 'email') or not user.email:
            return False
            
        try:
            # Generate email content
            email_content = self._generate_email_content(
                user, notification_type, notification_data
            )
            
            # Create email message
            message = MIMEMultipart('alternative')
            message['Subject'] = f"[RiddleNet] {notification_data['title']}"
            message['From'] = self.sender_email
            message['To'] = user.email
            
            # Create HTML part
            html_part = MIMEText(email_content, 'html')
            message.attach(html_part)
            
            # Send email using optimized SMTP
            return self._send_smtp_email(user.email, message)
            
        except Exception as e:
            print(f"Email notification failed for {user.username}: {e}")
            return False
    
    def _generate_email_content(self, user: Any, notification_type: NotificationType, notification_data: Dict) -> str:
        """Generate cyber-themed HTML email content"""
        
        # Color scheme based on notification type
        type_colors = {
            NotificationType.ACCOUNT_ACTIVITY: '#00D4FF',
            NotificationType.SYSTEM_UPDATE: '#39FF14',
            NotificationType.ADMIN_NOTICE: '#FF6B35',
            NotificationType.SECURITY_ALERT: '#FF4757',
            NotificationType.LOGIN_ACTIVITY: '#00D4FF',
            NotificationType.COURSE_UPDATE: '#8B5CF6',
            NotificationType.QUIZ_RESULT: '#10B981',
            NotificationType.MAINTENANCE: '#F59E0B',
            NotificationType.EMERGENCY: '#EF4444'
        }
        
        primary_color = type_colors.get(notification_type, '#00D4FF')
        
        # Generate email HTML with cyber theme
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{notification_data['title']}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', Arial, sans-serif;
                    background: linear-gradient(135deg, #0a0c14, #1a1b2e);
                    color: #ffffff;
                    line-height: 1.6;
                }}
                
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: rgba(15, 23, 42, 0.95);
                    border-radius: 20px;
                    overflow: hidden;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                }}
                
                .header {{
                    background: linear-gradient(135deg, {primary_color}20, {primary_color}10);
                    padding: 30px;
                    text-align: center;
                    border-bottom: 2px solid {primary_color}40;
                }}
                
                .logo {{
                    font-size: 28px;
                    font-weight: 700;
                    color: {primary_color};
                    margin-bottom: 10px;
                    text-shadow: 0 0 20px {primary_color}60;
                }}
                
                .subtitle {{
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 14px;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                
                .content {{
                    padding: 40px;
                }}
                
                .notification-title {{
                    font-size: 24px;
                    font-weight: 600;
                    color: {primary_color};
                    margin-bottom: 20px;
                    text-align: center;
                }}
                
                .notification-message {{
                    font-size: 16px;
                    color: rgba(255, 255, 255, 0.9);
                    margin-bottom: 30px;
                    text-align: center;
                }}
                
                .details-box {{
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                
                .detail-item {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
                
                .detail-item:last-child {{
                    border-bottom: none;
                }}
                
                .detail-label {{
                    color: rgba(255, 255, 255, 0.7);
                    font-weight: 500;
                }}
                
                .detail-value {{
                    color: {primary_color};
                    font-weight: 600;
                }}
                
                .action-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, {primary_color}, {primary_color}CC);
                    color: white;
                    padding: 12px 30px;
                    border-radius: 25px;
                    text-decoration: none;
                    font-weight: 600;
                    margin: 20px auto;
                    text-align: center;
                    box-shadow: 0 4px 15px {primary_color}40;
                    transition: all 0.3s ease;
                }}
                
                .footer {{
                    background: rgba(0, 0, 0, 0.3);
                    padding: 20px;
                    text-align: center;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }}
                
                .footer-text {{
                    color: rgba(255, 255, 255, 0.6);
                    font-size: 12px;
                    margin-bottom: 10px;
                }}
                
                .social-links {{
                    margin-top: 15px;
                }}
                
                .priority-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .priority-high {{
                    background: linear-gradient(135deg, #FF4757, #FF6B35);
                    color: white;
                }}
                
                .priority-normal {{
                    background: linear-gradient(135deg, #00D4FF, #39FF14);
                    color: white;
                }}
                
                .priority-low {{
                    background: rgba(255, 255, 255, 0.2);
                    color: rgba(255, 255, 255, 0.8);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">RiddleNet</div>
                    <div class="subtitle">Learning Platform</div>
                </div>
                
                <div class="content">
                    <div class="notification-title">
                        {notification_data['title']}
                    </div>
                    
                    <div style="text-align: center; margin-bottom: 20px;">
                        <span class="priority-badge priority-{notification_data['priority']}">
                            {notification_data['priority'].upper()} Priority
                        </span>
                    </div>
                    
                    <div class="notification-message">
                        {notification_data['message']}
                    </div>
                    
                    <div class="details-box">
                        <div class="detail-item">
                            <span class="detail-label">User:</span>
                            <span class="detail-value">{user.username}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Type:</span>
                            <span class="detail-value">{notification_type.value.replace('_', ' ').title()}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Date:</span>
                            <span class="detail-value">{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
                        </div>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="http://localhost:5000" class="action-button">
                            Access RiddleNet Platform
                        </a>
                    </div>
                </div>
                
                <div class="footer">
                    <div class="footer-text">
                        This is an automated notification from RiddleNet Platform
                    </div>
                    <div class="footer-text">
                        © 2025 RiddleNet - Learning Platform
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _send_smtp_email(self, recipient_email: str, message: MIMEMultipart) -> bool:
        """Send email using optimized SMTP connection"""
        try:
            # Use the same optimized SMTP approach from the existing OTP system
            smtp_server_ip = '142.250.153.109'  # Gmail SMTP server IP
            
            # Create connection
            with smtplib.SMTP(smtp_server_ip, self.smtp_port, timeout=5) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                
                # Send email with proper encoding
                server.send_message(message)
                
            return True
            
        except Exception as e:
            print(f"SMTP email failed: {e}")
            return False
    
    def send_admin_notification(self, 
                              notification_type: NotificationType,
                              title: str,
                              message: str,
                              priority: NotificationPriority = NotificationPriority.NORMAL,
                              additional_data: Optional[Dict] = None,
                              sender_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Send notification to all instructor users"""
        
        # Get all instructor users
        admins = Instructor.query.all()
        
        # Also get users with is_instructor=True
        admin_users = User.query.filter_by(is_instructor=True).all()
        
        all_admins = admins + admin_users
        
        return self.send_notification(
            users=all_admins,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            channel=NotificationChannel.BOTH,
            template_data=additional_data,
            sender_info=sender_info
        )
    
    def send_user_notification(self, 
                             user_id: int,
                             notification_type: NotificationType,
                             title: str,
                             message: str,
                             priority: NotificationPriority = NotificationPriority.NORMAL,
                             channel: NotificationChannel = NotificationChannel.BOTH,
                             sender_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Send notification to specific user with session management"""
        
        try:
            # Try to find user in regular users table with fresh query
            db.session.commit()  # Ensure session is clean
            user = User.query.get(user_id)
            
            if not user:
                return {'error': 'User not found', 'success': False}
            
            # Extract user data to avoid session detachment issues
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': getattr(user, 'email', None)
            }
            
            # Create temporary user object for processing
            class TempUser:
                def __init__(self, data):
                    self.id = data['id']
                    self.username = data['username']
                    self.email = data['email']
            
            temp_user = TempUser(user_data)
            
            return self.send_notification(
                users=[temp_user],
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                channel=channel,
                sender_info=sender_info
            )
            
        except Exception as e:
            print(f"❌ Error in send_user_notification for user {user_id}: {e}")
            return {'error': str(e), 'success': False}
    
    def send_system_announcement(self, 
                               title: str,
                               message: str,
                               priority: NotificationPriority = NotificationPriority.NORMAL,
                               sender_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Send system-wide announcement to all users with proper session management"""
        
        start_time = time.time()
        
        # Get all users with fresh session to avoid detached instance issues
        try:
            db.session.commit()  # Ensure current session is clean
            all_users = User.query.all()
            
            # Create list of user data to avoid session issues
            user_data_list = []
            for user in all_users:
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': getattr(user, 'email', None)
                }
                user_data_list.append(user_data)
                
            print(f"👥 Processing system announcement for {len(user_data_list)} users")
            
        except Exception as e:
            print(f"❌ Error querying users: {e}")
            return {'error': f'Failed to query users: {str(e)}', 'success': False}
        
        results = {
            'email_sent': 0,
            'websocket_sent': 0,
            'failed': 0,
            'errors': [],
            'total_processed': len(user_data_list),
            'success': True
        }
        
        # Step 1: Create individual UserNotification records first
        from user.models.user_notification import UserNotification
        user_notification_map = {}
        user_notifications_created = 0
        
        for user_data in user_data_list:
            try:
                user_notification = UserNotification.create_notification(
                    user_id=user_data['id'],
                    notification_type='system_announcement',
                    title=title,
                    message=message,
                    priority=priority.value.lower(),
                    delivery_channel=sender_info.get('channel', 'both') if sender_info else 'both'
                )
                if user_notification:
                    user_notification_map[user_data['id']] = user_notification
                    user_notifications_created += 1
                    print(f"✅ Created UserNotification for {user_data['username']} (ID: {user_notification.id})")
                else:
                    print(f"❌ Failed to create UserNotification for {user_data['username']}")
                    results['failed'] += 1
            except Exception as e:
                print(f"❌ Failed to create UserNotification for {user_data['username']}: {e}")
                results['errors'].append(f"UserNotification for {user_data['username']} failed: {e}")
                results['failed'] += 1

        print(f"✅ Created {user_notifications_created} individual user notifications")
        results['user_notifications_created'] = user_notifications_created

        # Step 2: Emit announcements with IDs to each user's room
        if self.socketio:
            try:
                sender_name = sender_info.get('sender_username', 'Admin') if sender_info else 'System'
                print(f"✅ Sending system announcement via WebSocket to all users: {title}")
                websocket_count = 0
                
                for user_data in user_data_list:
                    try:
                        room = f"user_{user_data['id']}"
                        user_notification = user_notification_map.get(user_data['id'])
                        announcement_data = {
                            'id': getattr(user_notification, 'id', None),
                            'title': title,
                            'message': message,
                            'content': message,
                            'type': 'system_announcement',
                            'priority': priority.value,
                            'timestamp': datetime.utcnow().isoformat(),
                            'from_instructor': True,
                            'instructor_name': sender_name,
                            'source': 'system_announcement'
                        }
                        self.socketio.emit('new_announcement', announcement_data, room=room)
                        websocket_count += 1
                        
                    except Exception as e:
                        print(f"❌ Failed to send WebSocket to {user_data['username']}: {e}")
                        results['errors'].append(f"WebSocket to {user_data['username']} failed: {e}")
                        
                results['websocket_sent'] = websocket_count
                print(f"✅ Sent {websocket_count} WebSocket announcements")
                
            except Exception as e:
                print(f"❌ Failed to send announcements: {e}")
                results['errors'].append(f"WebSocket announcement failed: {e}")

        # Step 3: Send emails to all users (if email channel is enabled)
        channel = NotificationChannel(sender_info.get('channel', 'both')) if sender_info else NotificationChannel.BOTH
        if channel in [NotificationChannel.EMAIL, NotificationChannel.BOTH]:
            email_count = 0
            
            for user_data in user_data_list:
                if user_data.get('email'):
                    try:
                        email_data = {
                            'title': title,
                            'message': message,
                            'type': NotificationType.SYSTEM_UPDATE.value,
                            'priority': priority.value,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        
                        # Create temporary user object for email sending
                        class TempUser:
                            def __init__(self, data):
                                self.id = data['id']
                                self.username = data['username']
                                self.email = data['email']
                        
                        temp_user = TempUser(user_data)
                        email_sent = self._send_email_notification(temp_user, NotificationType.SYSTEM_UPDATE, email_data)
                        if email_sent:
                            email_count += 1
                            
                    except Exception as e:
                        print(f"❌ Failed to send email to {user_data['username']}: {e}")
                        results['errors'].append(f"Email to {user_data['username']} failed: {e}")
                        results['failed'] += 1
                        
            results['email_sent'] = email_count
            print(f"✅ Sent {email_count} emails")

        # Record single notification history entry for "all users" for admin audit trail
        delivery_time = time.time() - start_time
        if sender_info:
            try:
                from instructor.models.notification_history import NotificationHistory
                
                # Create single record for system announcement
                db_notification_data = {
                    'notification_type': NotificationType.SYSTEM_UPDATE.value,
                    'title': title,
                    'message': message,
                    'priority': priority.value,
                    'recipient_type': 'all_users',
                    'specific_user': None,
                    'channel': sender_info.get('channel', 'both'),
                    'template_data': json.dumps({
                        'user_count': len(user_data_list),
                        'user_notifications_created': user_notifications_created
                    })
                }
                
                NotificationHistory.create_record(
                    sender_id=sender_info.get('sender_id'),
                    sender_type=sender_info.get('sender_type', 'admin'),
                    sender_username=sender_info.get('sender_username', 'System'),
                    notification_data=db_notification_data,
                    result=results,
                    delivery_time=delivery_time
                )
                
            except Exception as e:
                print(f"❌ Error recording notification history: {e}")
        
        return results
    
    def _record_notification_history(self, sender_info: Dict, notification_data: Dict, result: Dict, delivery_time: float):
        """Record notification in database for audit trail"""
        try:
            # Import here to avoid circular imports
            from instructor.models.notification_history import NotificationHistory
            
            # Prepare notification data for database
            db_notification_data = {
                'notification_type': notification_data['type'],
                'title': notification_data['title'],
                'message': notification_data['message'],
                'priority': notification_data['priority'],
                'recipient_type': sender_info.get('recipient_type', 'all_users'),
                'specific_user': sender_info.get('specific_user'),
                'channel': sender_info.get('channel', 'both'),
                'template_data': json.dumps(notification_data.get('template_data', {}))
            }
            
            NotificationHistory.create_record(
                sender_id=sender_info.get('sender_id'),
                sender_type=sender_info.get('sender_type', 'admin'),
                sender_username=sender_info.get('sender_username', 'System'),
                notification_data=db_notification_data,
                result=result,
                delivery_time=delivery_time
            )
            
        except Exception as e:
            print(f"Error recording notification history: {e}")
    
    def send_account_activity_notification(self, 
                                         user_id: int,
                                         activity_type: str,
                                         details: str,
                                         priority: NotificationPriority = NotificationPriority.NORMAL) -> Dict[str, Any]:
        """Send account activity notification"""
        
        title = f"Account Activity: {activity_type}"
        message = f"Activity detected on your account: {details}"
        
        return self.send_user_notification(
            user_id=user_id,
            notification_type=NotificationType.ACCOUNT_ACTIVITY,
            title=title,
            message=message,
            priority=priority,
            channel=NotificationChannel.BOTH
        )
    
    def send_security_alert(self, 
                           users: List[Any],
                           alert_type: str,
                           details: str,
                           priority: NotificationPriority = NotificationPriority.HIGH) -> Dict[str, Any]:
        """Send security alert notification"""
        
        title = f"Security Alert: {alert_type}"
        message = f"Security alert: {details}"
        
        return self.send_notification(
            users=users,
            notification_type=NotificationType.SECURITY_ALERT,
            title=title,
            message=message,
            priority=priority,
            channel=NotificationChannel.BOTH
        )
    
    def send_course_update_notification(self, 
                                      users: List[Any],
                                      course_name: str,
                                      update_details: str,
                                      priority: NotificationPriority = NotificationPriority.NORMAL,
                                      sender_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Send course update notification"""
        
        title = f"Course Update: {course_name}"
        message = f"Update to {course_name}: {update_details}"
        
        # Enhanced template data for course notifications
        template_data = {
            'course_name': course_name,
            'update_details': update_details,
            'notification_category': 'course_update'
        }
        
        # Send notification with course_update type for proper announcement handling
        return self.send_notification(
            users=users,
            notification_type=NotificationType.COURSE_UPDATE,
            title=title,
            message=message,
            priority=priority,
            channel=NotificationChannel.BOTH,
            template_data=template_data,
            sender_info=sender_info
        )
    
    def send_quiz_result_notification(self, 
                                    user_id: int,
                                    quiz_name: str,
                                    score: int,
                                    total: int,
                                    priority: NotificationPriority = NotificationPriority.NORMAL) -> Dict[str, Any]:
        """Send quiz result notification"""
        
        title = f"Quiz Results: {quiz_name}"
        message = f"You scored {score}/{total} on {quiz_name}"
        
        return self.send_user_notification(
            user_id=user_id,
            notification_type=NotificationType.QUIZ_RESULT,
            title=title,
            message=message,
            priority=priority,
            channel=NotificationChannel.BOTH
        )
    
    def send_maintenance_notification(self, 
                                    title: str,
                                    message: str,
                                    start_time: datetime,
                                    end_time: datetime,
                                    priority: NotificationPriority = NotificationPriority.HIGH) -> Dict[str, Any]:
        """Send maintenance notification to all users"""
        
        # Get all users
        all_users = User.query.all()
        
        # Add maintenance times to template data
        template_data = {
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'duration': str(end_time - start_time)
        }
        
        return self.send_notification(
            users=all_users,
            notification_type=NotificationType.MAINTENANCE,
            title=title,
            message=message,
            priority=priority,
            channel=NotificationChannel.BOTH,
            template_data=template_data
        )
    
    def send_emergency_notification(self, 
                                  title: str,
                                  message: str,
                                  priority: NotificationPriority = NotificationPriority.URGENT) -> Dict[str, Any]:
        """Send emergency notification to all users and admins"""
        
        # Get all users and admins
        all_users = User.query.all()
        all_admins = Instructor.query.all()
        admin_users = User.query.filter_by(is_instructor=True).all()
        
        all_recipients = all_users + all_admins + admin_users
        
        return self.send_notification(
            users=all_recipients,
            notification_type=NotificationType.EMERGENCY,
            title=f"🚨 EMERGENCY: {title}",
            message=message,
            priority=priority,
            channel=NotificationChannel.BOTH
        )

# Global notification service instance
notification_service = None

def get_notification_service(socketio=None):
    """Get or create notification service instance"""
    global notification_service
    if notification_service is None:
        notification_service = NotificationService(socketio)
    elif socketio and notification_service.socketio is None:
        notification_service.socketio = socketio
    return notification_service
