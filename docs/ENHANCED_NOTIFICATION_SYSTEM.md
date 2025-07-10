# RiddleNet Enhanced Notification System Documentation

## Overview

The Enhanced Notification System provides comprehensive notification capabilities for RiddleNet, supporting both email and WebSocket notifications with a cyber-themed design. The system includes automated communication about account activity, system updates, admin notices, and more.

## Features

### ✅ **Current Implementation**
- **Dual Delivery System**: Email + WebSocket notifications
- **Cyber-Themed Email Templates**: HTML emails with RiddleNet branding
- **Admin Notification Dashboard**: Centralized management interface
- **Database Audit Trail**: Complete notification history tracking
- **Multiple Notification Types**: Account activity, system updates, admin notices, security alerts, course updates, quiz results, maintenance, emergency alerts
- **Priority System**: Low, Normal, High, Urgent priority levels
- **Template System**: Pre-defined and customizable notification templates
- **Gmail SMTP Integration**: Optimized for 5-second delivery target
- **Real-time WebSocket Notifications**: Instant delivery to active users

### 🔧 **Technical Architecture**

#### Core Components

1. **NotificationService** (`services/notification_service.py`)
   - Main service class handling all notification operations
   - Supports multiple delivery channels (email, WebSocket, both)
   - Cyber-themed HTML email template generation
   - Database logging and audit trail

2. **NotificationHistory Model** (`admin/models/notification_history.py`)
   - Persistent storage for all sent notifications
   - Statistics and analytics capabilities
   - Cleanup and maintenance functions

3. **Admin Controller** (`admin/controllers/notification_controller.py`)
   - REST API endpoints for notification management
   - Template management
   - Statistics and reporting

4. **Frontend Dashboard** (`templates/admin/notification_center.html`)
   - User-friendly interface for sending notifications
   - Real-time statistics display
   - Template management
   - Notification history with filtering

## Notification Types

### 📧 **Email Notifications**
- **SMTP Configuration**: Gmail with optimized delivery
- **Template System**: Cyber-themed HTML emails
- **Color-coded Priority**: Different colors for different notification types
- **Responsive Design**: Mobile-friendly email templates
- **Personalization**: User-specific content and branding

### ⚡ **WebSocket Notifications**
- **Real-time Delivery**: Instant notifications to active users
- **Room-based Delivery**: User-specific and admin rooms
- **Priority Escalation**: High-priority notifications sent to admin room
- **User Presence**: Notifications only sent to active users

## Configuration

### Gmail SMTP Setup
```python
# Environment variables required
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-app-password
```

### Notification Service Configuration
```python
# In services/notification_service.py
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_server_ip = '142.250.153.109'  # Direct IP for optimized delivery
```

## Usage Examples

### 1. Send Account Activity Notification
```python
from services.notification_service import get_notification_service, NotificationPriority

notification_service = get_notification_service(socketio)
result = notification_service.send_account_activity_notification(
    user_id=user.id,
    activity_type="Login",
    details="Successful login from new device",
    priority=NotificationPriority.NORMAL
)
```

### 2. Send System Announcement
```python
sender_info = {
    'sender_id': admin.id,
    'sender_type': 'admin',
    'sender_username': admin.username,
    'recipient_type': 'all_users',
    'channel': 'both'
}

result = notification_service.send_system_announcement(
    title="System Maintenance Notice",
    message="Scheduled maintenance tonight from 11 PM to 1 AM EST",
    priority=NotificationPriority.HIGH,
    sender_info=sender_info
)
```

### 3. Send Security Alert
```python
all_users = User.query.all()
result = notification_service.send_security_alert(
    users=all_users,
    alert_type="Suspicious Activity",
    details="Multiple failed login attempts detected",
    priority=NotificationPriority.HIGH
)
```

### 4. Send Course Update
```python
enrolled_users = User.query.filter_by(course_id=course.id).all()
result = notification_service.send_course_update_notification(
    users=enrolled_users,
    course_name="Networking 1",
    update_details="New simulation added: TCP/IP Protocol Stack",
    priority=NotificationPriority.NORMAL
)
```

## API Endpoints

### Admin API Routes
- `GET /admin/notifications` - Notification center dashboard
- `POST /admin/api/notifications/send` - Send notification
- `GET /admin/api/notifications/history` - Get notification history
- `GET /admin/api/notifications/stats` - Get notification statistics
- `GET /admin/api/notifications/templates` - Get notification templates
- `POST /admin/api/notifications/cleanup` - Cleanup old notifications
- `POST /admin/api/notifications/send-maintenance` - Send maintenance notification
- `POST /admin/api/notifications/send-security-alert` - Send security alert
- `POST /admin/api/notifications/send-course-update` - Send course update

### Example API Request
```javascript
// Send notification via API
const response = await fetch('/admin/api/notifications/send', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        recipient_type: 'all_users',
        notification_type: 'system_update',
        priority: 'high',
        title: 'System Update',
        message: 'New features available!',
        channel: 'both'
    })
});
```

## Database Schema

### notification_history Table
```sql
CREATE TABLE notification_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    sender_type VARCHAR(20) NOT NULL,
    sender_username VARCHAR(100) NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL,
    recipient_type VARCHAR(20) NOT NULL,
    recipient_count INTEGER DEFAULT 0,
    specific_user_id INTEGER,
    delivery_channel VARCHAR(20) NOT NULL,
    email_sent INTEGER DEFAULT 0,
    websocket_sent INTEGER DEFAULT 0,
    failed_deliveries INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'sent',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_time REAL,
    template_data TEXT,
    error_details TEXT
);
```

## Email Templates

### Cyber-Themed Design Features
- **Dark Theme**: Professional dark color scheme
- **Neon Accents**: Cyber-inspired color highlights
- **Responsive Layout**: Mobile-optimized design
- **Brand Consistency**: RiddleNet branding throughout
- **Priority Colors**: Different colors for different notification types

### Template Structure
```html
<!-- Cyber-themed notification email -->
<div class="container">
    <div class="header">
        <div class="logo">⚡ RiddleNet</div>
        <div class="subtitle">Cyber Security Learning Platform</div>
    </div>
    <div class="content">
        <div class="notification-title">{title}</div>
        <div class="priority-badge">{priority}</div>
        <div class="notification-message">{message}</div>
        <div class="details-box">
            <!-- User and notification details -->
        </div>
        <div class="action-button">
            <a href="http://localhost:5000">Access RiddleNet Platform</a>
        </div>
    </div>
</div>
```

## Admin Dashboard Features

### 📊 **Statistics Dashboard**
- Total notifications sent today
- Email vs WebSocket delivery counts
- Active user count
- Success/failure rates

### 🎯 **Targeted Notifications**
- Send to all users
- Send to all admins
- Send to specific user
- Priority-based delivery

### 📝 **Template Management**
- Pre-defined templates for common notifications
- Custom template creation
- Template preview functionality
- Quick template loading

### 🔍 **Notification History**
- Complete audit trail of all sent notifications
- Advanced filtering options
- Delivery statistics per notification
- Error tracking and debugging

### 🛠️ **Management Tools**
- Bulk notification sending
- Scheduled notifications (future enhancement)
- Notification cleanup tools
- Performance monitoring

## Security Features

### 🔐 **Access Control**
- Admin-only access to notification center
- User authentication required for all operations
- Role-based permissions

### 🛡️ **Data Protection**
- Encrypted email transmission
- Secure database storage
- Audit trail for compliance
- Error handling and logging

## Performance Optimization

### ⚡ **Email Delivery**
- Direct IP connection to Gmail SMTP
- Optimized for 5-second delivery target
- Connection pooling and reuse
- Minimal message formatting

### 📡 **WebSocket Efficiency**
- Room-based message delivery
- Selective user targeting
- Minimal payload size
- Connection state management

## Maintenance and Monitoring

### 🔧 **Database Maintenance**
- Automated cleanup of old notifications
- Configurable retention periods
- Performance monitoring
- Storage optimization

### 📈 **Analytics**
- Delivery success rates
- Response time monitoring
- User engagement tracking
- System performance metrics

## Future Enhancements

### 🚀 **Planned Features**
- Scheduled notification system
- User notification preferences
- Mobile push notifications
- Advanced template editor
- Notification analytics dashboard
- Integration with external services

### 🔄 **Continuous Improvements**
- Performance optimizations
- Additional notification types
- Enhanced security features
- Better error handling
- Improved user experience

## Troubleshooting

### Common Issues
1. **Email delivery failures**: Check Gmail app password and SMTP settings
2. **WebSocket connection issues**: Verify SocketIO configuration
3. **Database errors**: Check notification_history table exists
4. **Template loading failures**: Verify template file permissions

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing

### Run Test Suite
```bash
cd /path/to/RiddleNet
python test_notification_system.py
```

### Create Test Database
```bash
python admin/utils/create_notification_table.py
```

## Support

For issues or questions regarding the notification system:
1. Check the troubleshooting section
2. Review the error logs in the admin dashboard
3. Test with the provided test scripts
4. Check database integrity

---

**Last Updated**: July 2025
**Version**: 2.0 Enhanced
**Author**: RiddleNet Development Team
