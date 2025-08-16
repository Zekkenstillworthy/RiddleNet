"""
Admin Notification Controller
Handles admin notification center functionality
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from services.notification_service import get_notification_service, NotificationType, NotificationPriority, NotificationChannel
from user.models.user import User
from admin.models.user import Admin
from admin.models.notification_history import NotificationHistory
from utils.auth_decorators import admin_required, api_admin_required
from __init__ import db
import json
import os

# SocketIO injection to avoid circular imports
_socketio_instance = None

def set_socketio_instance(socketio_instance):
    """Set the socketio instance to avoid circular imports"""
    global _socketio_instance
    _socketio_instance = socketio_instance
    print(f"✅ SocketIO instance set in notification controller: {socketio_instance is not None}")

def get_socketio_instance():
    """Get the socketio instance"""
    return _socketio_instance


# Create blueprint
notification_controller = Blueprint('notification_controller', __name__, url_prefix='/admin')

@notification_controller.route('/notifications')
@login_required
def notification_center():
    """Display the notification center dashboard"""
    return render_template('admin/notification_center.html')

@notification_controller.route('/api/notifications/send', methods=['POST'])
@login_required
def send_notification():
    """Send notification via API"""
    try:
        print(f"🔔 Notification API called by user {current_user.username} at {datetime.now()}")
        
        data = request.get_json()
        print(f"📋 Notification data: {data}")
        
        # Validate required fields
        if not data.get('title') or not data.get('message'):
            return jsonify({'error': 'Title and message are required'}), 400
        
        # Get notification service
        notification_service = get_notification_service(get_socketio_instance())
        
        # Parse notification type and priority
        notification_type = NotificationType(data.get('notification_type', 'admin_notice'))
        priority = NotificationPriority(data.get('priority', 'normal'))
        channel = NotificationChannel(data.get('channel', 'both'))
        
        # Prepare sender info
        sender_info = {
            'sender_id': current_user.id,
            'sender_type': 'admin' if hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins' else 'user',
            'sender_username': current_user.username,
            'recipient_type': data.get('recipient_type', 'all_admins'),
            'specific_user': data.get('specific_user'),
            'channel': data.get('channel', 'both')
        }
        
        # Determine recipients
        recipient_type = data.get('recipient_type', 'all_admins')
        
        if recipient_type == 'all_admins':
            # Send to all admins
            result = notification_service.send_admin_notification(
                notification_type=notification_type,
                title=data['title'],
                message=data['message'],
                priority=priority,
                sender_info=sender_info
            )
        elif recipient_type == 'specific_user':
            # Send to specific user
            user_id = data.get('specific_user')
            if not user_id:
                return jsonify({'error': 'User ID required for specific user notifications'}), 400
                
            result = notification_service.send_user_notification(
                user_id=int(user_id),
                notification_type=notification_type,
                title=data['title'],
                message=data['message'],
                priority=priority,
                channel=channel,
                sender_info=sender_info
            )
        else:
            return jsonify({'error': 'Invalid recipient type'}), 400
        
        print(f"✅ Notification sent successfully: {result}")
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error sending notification: {e}")
        return jsonify({'error': str(e)}), 500

@notification_controller.route('/api/notifications/history')
@login_required
def notification_history():
    """Get notification history"""
    try:
        # Get limit from query parameters
        limit = request.args.get('limit', 50, type=int)
        
        # Get notifications from database
        notifications = NotificationHistory.get_recent_notifications(limit=limit)
        
        # notifications already contains dictionaries from get_recent_notifications
        return jsonify(notifications)
        
    except Exception as e:
        current_app.logger.error(f"Error getting notification history: {e}")
        return jsonify({'error': str(e)}), 500

@notification_controller.route('/api/notifications/stats')
@login_required
def notification_stats():
    """Get notification statistics"""
    try:
        # Get stats from database
        stats = NotificationHistory.get_statistics(days=1)
        
        # Add additional stats
        stats.update({
            'active_users': User.query.count(),
            'total_admins': Admin.query.count() + User.query.filter_by(is_admin=True).count(),
            'last_24h': NotificationHistory.get_statistics(days=1)['total_sent']
        })
        
        return jsonify(stats)
        
    except Exception as e:
        current_app.logger.error(f"Error getting notification stats: {e}")
        return jsonify({'error': str(e)}), 500

@notification_controller.route('/api/users')
@login_required
def get_users():
    """Get list of users for notification targeting"""
    try:
        users = User.query.all()
        user_list = []
        
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': getattr(user, 'email', None),
                'is_admin': getattr(user, 'is_admin', False)
            })
        
        return jsonify(user_list)
        
    except Exception as e:
        current_app.logger.error(f"Error getting users: {e}")
        return jsonify({'error': str(e)}), 500

# Additional API endpoints for enhanced notification management

@notification_controller.route('/api/notifications/cleanup', methods=['POST'])
@login_required
def cleanup_notifications():
    """Cleanup old notification records"""
    try:
        data = request.get_json()
        days = data.get('days', 30)
        
        # Check if user is admin
        if not (hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins') and not getattr(current_user, 'is_admin', False):
            return jsonify({'error': 'Unauthorized'}), 403
        
        count = NotificationHistory.cleanup_old_records(days=days)
        
        return jsonify({
            'success': True,
            'deleted_count': count,
            'message': f'Cleaned up {count} old notification records'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up notifications: {e}")
        return jsonify({'error': str(e)}), 500

@notification_controller.route('/api/notifications/send-maintenance', methods=['POST'])
@login_required
def send_maintenance_notification():
    """Send maintenance notification with specific timing"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('message'):
            return jsonify({'error': 'Title and message are required'}), 400
        
        # Parse dates
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        
        # Get notification service
        notification_service = get_notification_service(get_socketio_instance())
        
        # Send maintenance notification
        result = notification_service.send_maintenance_notification(
            title=data['title'],
            message=data['message'],
            start_time=start_time,
            end_time=end_time,
            priority=NotificationPriority(data.get('priority', 'high'))
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error sending maintenance notification: {e}")
        return jsonify({'error': str(e)}), 500

@notification_controller.route('/api/notifications/send-security-alert', methods=['POST'])
@login_required
def send_security_alert():
    """Send security alert notification"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('alert_type') or not data.get('details'):
            return jsonify({'error': 'Alert type and details are required'}), 400
        
        # Get notification service
        notification_service = get_notification_service(get_socketio_instance())
        
        # Get all users for security alert
        all_users = User.query.all()
        
        # Send security alert
        result = notification_service.send_security_alert(
            users=all_users,
            alert_type=data['alert_type'],
            details=data['details'],
            priority=NotificationPriority(data.get('priority', 'high'))
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error sending security alert: {e}")
        return jsonify({'error': str(e)}), 500

@notification_controller.route('/api/notifications/send-course-update', methods=['POST'])
@login_required
def send_course_update():
    """Send course update notification"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('course_name') or not data.get('update_details'):
            return jsonify({'error': 'Course name and update details are required'}), 400
        
        # Get notification service
        notification_service = get_notification_service(get_socketio_instance())
        
        # Get target users (all users for now, could be filtered by course enrollment)
        all_users = User.query.all()
        
        # Send course update notification
        result = notification_service.send_course_update_notification(
            users=all_users,
            course_name=data['course_name'],
            update_details=data['update_details'],
            priority=NotificationPriority(data.get('priority', 'normal'))
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error sending course update: {e}")
        return jsonify({'error': str(e)}), 500

@notification_controller.route('/api/notifications/templates')
@login_required
def get_notification_templates():
    """Get predefined notification templates"""
    try:
        templates = {
            'maintenance': {
                'title': 'Scheduled Maintenance Notice',
                'message': 'RiddleNet will undergo scheduled maintenance on [DATE] from [START_TIME] to [END_TIME]. Some features may be temporarily unavailable during this period.',
                'priority': 'high',
                'type': 'maintenance'
            },
            'security': {
                'title': 'Security Alert',
                'message': 'A security update has been applied to your account. Please review your recent activity and contact support if you notice any suspicious activity.',
                'priority': 'urgent',
                'type': 'security_alert'
            },
            'update': {
                'title': 'System Update Available',
                'message': 'A new system update is available with improved features and security enhancements. The update will be applied automatically during your next login.',
                'priority': 'normal',
                'type': 'system_update'
            },
            'welcome': {
                'title': 'Welcome to RiddleNet!',
                'message': 'Welcome to the RiddleNet learning platform! Get started by exploring our interactive simulations and courses.',
                'priority': 'normal',
                'type': 'account_activity'
            },
            'course_update': {
                'title': 'New Course Available',
                'message': 'A new course has been added to your learning path. Check out the latest content and continue your cyber security journey.',
                'priority': 'normal',
                'type': 'course_update'
            },
            'quiz_result': {
                'title': 'Quiz Results Available',
                'message': 'Your quiz results are now available. Review your performance and identify areas for improvement.',
                'priority': 'normal',
                'type': 'quiz_result'
            }
        }
        
        return jsonify(templates)
        
    except Exception as e:
        current_app.logger.error(f"Error getting templates: {e}")
        return jsonify({'error': str(e)}), 500

@notification_controller.route('/api/notifications/test-email', methods=['POST'])
@api_admin_required
def test_email_configuration():
    """Test email configuration by sending a test email"""
    try:
        data = request.get_json()
        recipient_email = data.get('email', getattr(current_user, 'email', 'admin@example.com'))
        
        notification_service = get_notification_service(get_socketio_instance())
        
        # Send test notification
        from user.models.user import User
        test_user = User.query.first()  # Get any user for testing
        if not test_user:
            # Create a temporary user object for testing
            class TestUser:
                def __init__(self):
                    self.username = current_user.username
                    self.email = recipient_email
                    self.id = current_user.id
            test_user = TestUser()
        
        result = notification_service.send_user_notification(
            user_id=test_user.id,
            notification_type=NotificationType.SYSTEM_UPDATE,
            title="Email Configuration Test",
            message="This is a test email to verify your notification system is working correctly.",
            priority=NotificationPriority.LOW,
            channel=NotificationChannel.EMAIL
        )
        
        return jsonify({
            'success': result.get('email_sent', 0) > 0,
            'result': result,
            'message': 'Test email sent successfully' if result.get('email_sent', 0) > 0 else 'Test email failed'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error testing email configuration: {e}")
        return jsonify({'error': str(e)}), 500

@notification_controller.route('/api/notifications/config-status')
@api_admin_required
def get_configuration_status():
    """Get notification system configuration status"""
    try:
        status = {
            'email_configured': bool(os.getenv('MAIL_USERNAME') and os.getenv('MAIL_PASSWORD')),
            'websocket_available': get_socketio_instance() is not None,
            'database_connected': True,  # If we reach here, DB is connected
            'templates_loaded': True,
            'mail_server': os.getenv('MAIL_USERNAME', 'Not configured'),
            'socketio_status': 'Connected' if get_socketio_instance() is not None else 'Disconnected'
        }
        
        return jsonify(status)
        
    except Exception as e:
        current_app.logger.error(f"Error getting configuration status: {e}")
        return jsonify({'error': str(e)}), 500

# WebSocket events for real-time notification management
def setup_notification_websocket_events(socketio):
    """Set up WebSocket events for notification management"""
    
    @socketio.on('admin_send_notification')
    def handle_admin_notification(data):
        """Handle real-time notification sending from admin"""
        try:
            if not current_user.is_authenticated:
                return
                
            # Check if user is admin
            is_admin = False
            if hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins':
                is_admin = True
            elif hasattr(current_user, 'is_admin') and current_user.is_admin:
                is_admin = True
                
            if not is_admin:
                socketio.emit('error', {'message': 'Unauthorized'})
                return
            
            # Send notification
            notification_service = get_notification_service(get_socketio_instance())
            
            # Process the notification based on data
            notification_type = NotificationType(data.get('type', 'admin_notice'))
            priority = NotificationPriority(data.get('priority', 'normal'))
            
            # Create sender info for WebSocket notifications
            sender_info = {
                'sender_id': current_user.id,
                'sender_type': 'admin',
                'sender_username': current_user.username,
                'timestamp': datetime.now().isoformat()
            }
            
            if data.get('target') == 'all_admins':
                result = notification_service.send_admin_notification(
                    notification_type=notification_type,
                    title=data['title'],
                    message=data['message'],
                    priority=priority
                )
            else:
                # Send to specific user
                user_id = data.get('user_id')
                if user_id:
                    result = notification_service.send_user_notification(
                        user_id=user_id,
                        notification_type=notification_type,
                        title=data['title'],
                        message=data['message'],
                        priority=priority
                    )
                else:
                    result = {'error': 'Invalid target'}
            
            # Send result back to admin
            socketio.emit('notification_sent', result, room=request.sid)
            
        except Exception as e:
            socketio.emit('notification_error', {'error': str(e)}, room=request.sid)
    
    @socketio.on('admin_get_notification_stats')
    def handle_get_notification_stats():
        """Get real-time notification statistics"""
        try:
            if not current_user.is_authenticated:
                return
                
            # Check if user is admin
            is_admin = False
            if hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins':
                is_admin = True
            elif hasattr(current_user, 'is_admin') and current_user.is_admin:
                is_admin = True
                
            if not is_admin:
                return
            
            # Get stats
            stats = {
                'active_users': len(User.query.all()),
                'total_admins': len(Admin.query.all()),
                'online_users': 0,  # Would need WebSocket connection tracking
                'recent_notifications': 0  # Would come from database
            }
            
            socketio.emit('notification_stats_update', stats, room=request.sid)
            
        except Exception as e:
            socketio.emit('notification_error', {'error': str(e)}, room=request.sid)
