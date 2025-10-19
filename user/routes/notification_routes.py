"""
User Notification Routes for RiddleNet
Provides user-facing notification dashboard and API endpoints
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from user.models.user_notification import UserNotification
from user.models.notification_preferences import NotificationPreferences
from instructor.models.notification_history import NotificationHistory
from utils.auth_decorators import user_required
from __init__ import db
import json

# Create blueprint
notification_bp = Blueprint('user_notifications', __name__, url_prefix='/user')

@notification_bp.route('/notifications')
@login_required
@user_required
def notification_dashboard():
    """Main user notification dashboard"""
    try:
        # Get user notification stats
        unread_count = UserNotification.get_unread_count(current_user.id)
        total_count = UserNotification.query.filter_by(user_id=current_user.id).count()
        
        # Get recent notifications (first 10)
        recent_notifications = UserNotification.get_user_notifications(
            current_user.id, 
            limit=10
        )
        
        # Get user preferences
        preferences = NotificationPreferences.get_or_create_preferences(current_user.id)
        
        return render_template(
            'user/notifications.html',
            unread_count=unread_count,
            total_count=total_count,
            recent_notifications=recent_notifications,
            preferences=preferences.to_dict(),
            page_title="Notification Center"
        )
        
    except Exception as e:
        print(f"Error loading notification dashboard: {e}")
        return render_template(
            'user/notifications.html',
            unread_count=0,
            total_count=0,
            recent_notifications=[],
            preferences={},
            error="Failed to load notifications",
            page_title="Notification Center"
        )

@notification_bp.route('/api/notifications')
@login_required
@user_required
def get_user_notifications():
    """API endpoint to get user notifications with pagination and filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        notification_type = request.args.get('type', None)
        read_status = request.args.get('read_status', None)  # 'read', 'unread', or None for all
        
        # Validate limit
        limit = min(limit, 100)  # Maximum 100 per request
        
        # Get notifications with filters
        notifications = UserNotification.get_user_notifications(
            current_user.id,
            page=page,
            limit=limit,
            notification_type=notification_type,
            read_status=read_status
        )
        
        # Get total count for pagination
        query = UserNotification.query.filter_by(user_id=current_user.id)
        if notification_type:
            query = query.filter_by(notification_type=notification_type)
        if read_status == 'read':
            query = query.filter_by(is_read=True)
        elif read_status == 'unread':
            query = query.filter_by(is_read=False)
            
        total_count = query.count()
        total_pages = (total_count + limit - 1) // limit
        
        return jsonify({
            'success': True,
            'notifications': [n.to_dict() for n in notifications],
            'pagination': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })
        
    except Exception as e:
        print(f"Error getting user notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch notifications'
        }), 500

@notification_bp.route('/api/notifications/mark-read', methods=['POST'])
@login_required
@user_required
def mark_notifications_read():
    """Mark one or more notifications as read"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        notification_ids = data.get('notification_ids', [])
        mark_all = data.get('mark_all', False)
        
        if mark_all:
            # Mark all user notifications as read
            count = UserNotification.mark_all_as_read(current_user.id)
            return jsonify({
                'success': True,
                'message': f'Marked {count} notifications as read'
            })
        
        elif notification_ids:
            # Mark specific notifications as read
            count = 0
            for notification_id in notification_ids:
                if UserNotification.mark_as_read(current_user.id, notification_id):
                    count += 1
            
            return jsonify({
                'success': True,
                'message': f'Marked {count} notifications as read'
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'No notifications specified'
            }), 400
            
    except Exception as e:
        print(f"Error marking notifications as read: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark notifications as read'
        }), 500

@notification_bp.route('/api/notifications/preferences', methods=['GET', 'POST'])
@login_required
@user_required
def notification_preferences():
    """Get or update user notification preferences"""
    try:
        preferences = NotificationPreferences.get_or_create_preferences(current_user.id)
        
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'preferences': preferences.to_dict()
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Update preferences
            if preferences.update_preferences(data):
                return jsonify({
                    'success': True,
                    'message': 'Preferences updated successfully',
                    'preferences': preferences.to_dict()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update preferences'
                }), 500
                
    except Exception as e:
        print(f"Error handling notification preferences: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to handle preferences request'
        }), 500

@notification_bp.route('/api/notifications/stats')
@login_required
@user_required
def notification_stats():
    """Get user notification statistics"""
    try:
        stats = UserNotification.get_notification_stats(current_user.id)
        
        # Get weekly activity (last 7 days)
        weekly_activity = []
        for i in range(7):
            date = datetime.now().date() - timedelta(days=i)
            day_count = UserNotification.query.filter(
                UserNotification.user_id == current_user.id,
                db.func.date(UserNotification.created_at) == date
            ).count()
            
            weekly_activity.append({
                'date': date.isoformat(),
                'count': day_count
            })
        
        # Get notification type breakdown
        type_breakdown = db.session.query(
            UserNotification.notification_type,
            db.func.count(UserNotification.id).label('count')
        ).filter_by(user_id=current_user.id).group_by(
            UserNotification.notification_type
        ).all()
        
        type_stats = {item[0]: item[1] for item in type_breakdown}
        
        return jsonify({
            'success': True,
            'stats': {
                'overall': stats,
                'weekly_activity': weekly_activity,
                'type_breakdown': type_stats
            }
        })
        
    except Exception as e:
        print(f"Error getting notification stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch notification statistics'
        }), 500

@notification_bp.route('/api/notifications/delete', methods=['POST'])
@login_required
@user_required
def delete_notifications():
    """Delete one or more notifications"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        notification_ids = data.get('notification_ids', [])
        delete_all_read = data.get('delete_all_read', False)
        
        if delete_all_read:
            # Delete all read notifications for user
            deleted_count = UserNotification.query.filter_by(
                user_id=current_user.id,
                is_read=True
            ).delete()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Deleted {deleted_count} read notifications'
            })
        
        elif notification_ids:
            # Delete specific notifications
            deleted_count = UserNotification.query.filter(
                UserNotification.user_id == current_user.id,
                UserNotification.id.in_(notification_ids)
            ).delete(synchronize_session=False)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Deleted {deleted_count} notifications'
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'No notifications specified'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete notifications'
        }), 500

@notification_bp.route('/api/notifications/test', methods=['POST'])
@login_required
@user_required
def test_notification():
    """Create a test notification for the user"""
    try:
        # Create a test notification
        test_notification = UserNotification.create_notification(
            user_id=current_user.id,
            title="Test Notification",
            message="This is a test notification to verify the system is working correctly.",
            notification_type="system_update",
            priority="medium",
            source_id="test"
        )
        
        if test_notification:
            return jsonify({
                'success': True,
                'message': 'Test notification created successfully',
                'notification': test_notification.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create test notification'
            }), 500
            
    except Exception as e:
        print(f"Error creating test notification: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create test notification'
        }), 500

@notification_bp.route('/api/notifications/recent-announcements')
@login_required
@user_required
def get_recent_announcements():
    """Get recent system announcements for display on page load"""
    try:
        # Get recent notifications and filter for system announcements AND Instructor notices
        all_notifications = UserNotification.get_user_notifications(
            user_id=current_user.id,
            limit=50,  # Get more to filter from
            unread_only=False,
            include_deleted=False
        )
        
        # Filter for announcement-like types used across the system
        # Note: Keep this list in sync with services/notification_service.py
        ANNOUNCEMENT_TYPES = [
            'system_announcement',   # Explicit system-wide announcements
            'instructor_notice',          # Instructor notices
            'maintenance_alert',     # Legacy/alternate maintenance type
            'system_update',         # General system updates
            'maintenance',           # Maintenance notifications
            'security_alert',        # Security-related alerts
            'course_update'          # Course-related updates
        ]

        announcements = [n for n in all_notifications if n.notification_type in ANNOUNCEMENT_TYPES][:10]
        
        # Convert to format expected by frontend
        announcement_data = []
        for announcement in announcements:
            # Try to get the actual admin name from the notification
            instructor_name = 'System'  # Default fallback
            
            # Check if there's sender info in the notification
            if hasattr(announcement, 'sender_id') and announcement.sender_id:
                try:
                    from instructor.models.user import Instructor
                    instructor = Instructor.query.get(announcement.sender_id)
                    if instructor:
                        instructor_name = instructor.username
                except:
                    pass  # Keep default if lookup fails
            
            # For certain types, use more specific names
            if announcement.notification_type in ['maintenance', 'maintenance_alert']:
                instructor_name = 'System Maintenance'
            elif announcement.notification_type == 'security_alert':
                instructor_name = 'Security Team'
            elif announcement.notification_type == 'course_update':
                instructor_name = 'Course Instructor'
            
            announcement_data.append({
                'id': announcement.id,
                'title': announcement.title,
                'message': announcement.message,
                'content': announcement.message,  # Alternative field for compatibility
                # Preserve original type so UI can style/handle appropriately
                'type': announcement.notification_type,
                'priority': announcement.priority,
                'timestamp': announcement.created_at.isoformat(),
                'from_instructor': True,
                'instructor_name': instructor_name,  # Now uses actual admin name when available
                'source': 'system_announcement',  # Keep source stable for now
                'is_read': announcement.is_read,
                'created_at': announcement.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'announcements': announcement_data,
            'count': len(announcement_data)
        })
        
    except Exception as e:
        print(f"Error getting recent announcements: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch recent announcements',
            'announcements': []
        }), 500

@notification_bp.route('/api/notifications/cleanup', methods=['POST'])
@login_required
@user_required
def cleanup_old_notifications():
    """Clean up old notifications for the user"""
    try:
        data = request.get_json() or {}
        days_old = data.get('days_old', 30)  # Default to 30 days
        
        # Validate days_old
        if not isinstance(days_old, int) or days_old < 1:
            return jsonify({
                'success': False,
                'error': 'Invalid days_old parameter'
            }), 400
        
        cleanup_count = UserNotification.cleanup_old_notifications(
            current_user.id, 
            days_old
        )
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {cleanup_count} old notifications',
            'cleaned_count': cleanup_count
        })
        
    except Exception as e:
        print(f"Error cleaning up notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to cleanup notifications'
        }), 500
