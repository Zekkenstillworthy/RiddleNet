# RiddleNet Notification Center - Immediate Code Fixes

## 🚨 **Critical Fix #1: Blueprint Registration**

The notification center is not accessible because the blueprint name doesn't match the registration.

### **Problem:**
- Blueprint is named `notification_controller` but registered as `notification`
- This causes 404 errors when accessing `/admin/notifications`

### **Solution:**

**File:** `admin/controllers/notification_controller.py` (Line 12)
```python
# CHANGE FROM:
notification_controller = Blueprint('notification', __name__, url_prefix='/admin')

# CHANGE TO:
notification_controller = Blueprint('notification_controller', __name__, url_prefix='/admin')
```

**File:** `run.py` (Add to blueprints_to_register list, around line 110)
```python
# ADD THIS LINE:
('admin.controllers.notification_controller', 'notification_controller', None, None),
```

## 🚨 **Critical Fix #2: Circular Import Resolution**

The notification controller tries to import socketio from run.py, causing circular imports.

### **Problem:**
- `from run import socketio` creates circular dependency
- Causes import errors and prevents proper initialization

### **Solution:**

**File:** `admin/controllers/notification_controller.py` (Add at top, around line 15)
```python
# ADD THESE LINES AFTER IMPORTS:
_socketio_instance = None

def set_socketio_instance(socketio_instance):
    """Set the socketio instance to avoid circular imports"""
    global _socketio_instance
    _socketio_instance = socketio_instance

def get_socketio_instance():
    """Get the socketio instance"""
    return _socketio_instance
```

**File:** `admin/controllers/notification_controller.py` (Replace all occurrences)
```python
# CHANGE FROM:
from run import socketio
notification_service = get_notification_service(socketio)

# CHANGE TO:
notification_service = get_notification_service(get_socketio_instance())
```

**File:** `run.py` (Add after socketio initialization, around line 25)
```python
# ADD AFTER: init_socketio(app)
try:
    from admin.controllers.notification_controller import set_socketio_instance
    set_socketio_instance(socketio)
    print("✅ SocketIO instance injected into notification controller")
except ImportError as e:
    print(f"⚠️ Could not inject socketio into notification controller: {e}")
```

## 🚨 **Critical Fix #3: Database Threading Fix**

SQLite threading issues cause "cannot notify on un-acquired lock" errors.

### **Problem:**
- Multiple threads accessing SQLite database simultaneously
- Database session conflicts

### **Solution:**

**File:** `admin/models/notification_history.py` (Replace create_record method, around line 65)
```python
@classmethod
def create_record(cls, sender_id, sender_type, sender_username, notification_data, result, delivery_time=None):
    """Create a new notification history record with thread-safe session handling"""
    import threading
    import time
    
    # Create a new session for this thread
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Use the main app's database URI
    engine = db.get_engine()
    Session = sessionmaker(bind=engine)
    local_session = Session()
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
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
            
            local_session.add(record)
            local_session.commit()
            return record
            
        except Exception as e:
            local_session.rollback()
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Error creating notification history record after {max_retries} retries: {e}")
                return None
            else:
                print(f"Database write retry {retry_count}/{max_retries}: {e}")
                time.sleep(0.1 * retry_count)  # Progressive delay
        finally:
            try:
                local_session.close()
            except:
                pass
    
    return None
```

## 🚨 **Critical Fix #4: Frontend JavaScript Error Handling**

The frontend doesn't properly handle API errors and loading states.

### **Problem:**
- No error handling for network failures
- No loading states for user feedback
- API endpoint mismatches

### **Solution:**

**File:** `templates/admin/notification_center.html` (Replace sendNotification function, around line 647)
```javascript
async function sendNotification(event) {
    event.preventDefault();
    
    const submitBtn = document.querySelector('#notificationForm button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    try {
        // Show loading state
        submitBtn.textContent = 'Sending...';
        submitBtn.disabled = true;
        
        const formData = new FormData(event.target);
        const data = {
            title: formData.get('title'),
            message: formData.get('message'),
            notification_type: formData.get('notification_type') || 'admin_notice',
            priority: formData.get('priority') || 'normal',
            recipient_type: formData.get('recipient_type') || 'all_users',
            specific_user: formData.get('specific_user'),
            channel: formData.get('channel') || 'both'
        };
        
        console.log('Sending notification:', data);
        
        const response = await fetch('/admin/api/notifications/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        console.log('Notification result:', result);
        
        if (response.ok) {
            showNotification('Notification sent successfully!', 'success');
            event.target.reset();
            loadNotificationHistory();
            updateStats();
        } else {
            showNotification(result.error || 'Failed to send notification', 'error');
        }
        
    } catch (error) {
        console.error('Network error:', error);
        showNotification('Network error: ' + error.message, 'error');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Add this new function for better error notifications
function showNotification(message, type = 'info') {
    // Create notification container if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            pointer-events: none;
        `;
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        background: var(--card-bg);
        border: 1px solid var(--glass-border);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        color: ${type === 'error' ? '#ff6b6b' : type === 'success' ? '#51cf66' : '#74c0fc'};
        border-left: 4px solid ${type === 'error' ? '#ff6b6b' : type === 'success' ? '#51cf66' : '#74c0fc'};
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        transform: translateX(100%);
        transition: transform 0.3s ease;
        pointer-events: auto;
        cursor: pointer;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    notification.textContent = message;
    notification.title = 'Click to dismiss';
    
    // Add click to dismiss
    notification.addEventListener('click', () => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    });
    
    container.appendChild(notification);
    
    // Slide in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}
```

## ⚡ **Quick Implementation Script**

Save this as `fix_notification_center.py` and run it:

```python
#!/usr/bin/env python3
"""
Quick fix script for RiddleNet notification center critical issues
"""

import os
import re

def fix_blueprint_registration():
    """Fix the blueprint registration issue"""
    controller_file = "admin/controllers/notification_controller.py"
    
    if os.path.exists(controller_file):
        with open(controller_file, 'r') as f:
            content = f.read()
        
        # Fix blueprint name
        content = re.sub(
            r"notification_controller = Blueprint\('notification'",
            "notification_controller = Blueprint('notification_controller'",
            content
        )
        
        with open(controller_file, 'w') as f:
            f.write(content)
        
        print("✅ Fixed blueprint registration in notification_controller.py")
    else:
        print("❌ Could not find notification_controller.py")

def add_socketio_injection():
    """Add socketio injection code"""
    controller_file = "admin/controllers/notification_controller.py"
    
    if os.path.exists(controller_file):
        with open(controller_file, 'r') as f:
            content = f.read()
        
        # Add socketio injection code after imports
        injection_code = """
# SocketIO injection to avoid circular imports
_socketio_instance = None

def set_socketio_instance(socketio_instance):
    global _socketio_instance
    _socketio_instance = socketio_instance

def get_socketio_instance():
    return _socketio_instance

"""
        
        # Insert after the last import
        import_pattern = r"(from __init__ import db\n)"
        content = re.sub(import_pattern, r"\1" + injection_code, content)
        
        # Replace socketio imports
        content = re.sub(
            r"from run import socketio.*\n",
            "",
            content
        )
        
        content = re.sub(
            r"notification_service = get_notification_service\(socketio\)",
            "notification_service = get_notification_service(get_socketio_instance())",
            content
        )
        
        with open(controller_file, 'w') as f:
            f.write(content)
        
        print("✅ Added socketio injection to notification_controller.py")

def main():
    print("🔧 Fixing RiddleNet Notification Center Critical Issues...")
    print("=" * 60)
    
    # Change to project directory
    project_dir = "c:\\Users\\gilbe\\OneDrive\\Desktop\\RiddleNet - Copy (2)"
    if os.path.exists(project_dir):
        os.chdir(project_dir)
        print(f"📁 Changed to project directory: {os.getcwd()}")
    
    # Apply fixes
    fix_blueprint_registration()
    add_socketio_injection()
    
    print("\n✅ Critical fixes applied!")
    print("\n📋 Next steps:")
    print("1. Restart the Flask server")
    print("2. Navigate to /admin/notifications")
    print("3. Test sending a notification")
    print("4. Check for any remaining errors in the console")

if __name__ == "__main__":
    main()
```

## 🎯 **Test Verification Steps**

After applying the fixes:

1. **Restart Server:**
   ```bash
   cd "c:\Users\gilbe\OneDrive\Desktop\RiddleNet - Copy (2)"
   python run.py
   ```

2. **Test Access:**
   - Navigate to `http://localhost:5001/admin/notifications`
   - Should see the notification center interface

3. **Test Functionality:**
   - Try sending a test notification
   - Check browser console for errors
   - Verify database updates

4. **Verify Integration:**
   - Check that emails are sent (if configured)
   - Test WebSocket notifications
   - Review notification history

---

**Priority:** 🔥 **IMMEDIATE IMPLEMENTATION REQUIRED**  
**Impact:** 🎯 **FIXES CORE FUNCTIONALITY**  
**Time Estimate:** ⏱️ **15-30 minutes**
