# Concurrent Login Prevention System

## Overview

This document describes the implementation of the concurrent login prevention system in RiddleNet. This system ensures that a user or instructor account can only be logged in from one device at a time.

## Features

- **Single Device Login**: Only one active session per user/instructor account
- **Automatic Session Termination**: Previous sessions are automatically terminated when a new login occurs
- **Session Validation**: Every request validates the session to ensure it's still active
- **Session Expiry**: Sessions expire after 24 hours of inactivity
- **Session Tracking**: Tracks IP address, user agent, and last activity for each session

## Architecture

### Database Tables

Two new tables have been added to track active sessions:

#### 1. `user_sessions`
Tracks active sessions for regular users.

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to `user.id`
- `session_token` - Unique session identifier (64 chars)
- `ip_address` - IP address of the session
- `user_agent` - Browser/device user agent
- `created_at` - When the session was created
- `last_activity` - Last request timestamp
- `expires_at` - When the session expires
- `is_active` - Boolean flag for active status

#### 2. `instructor_sessions`
Tracks active sessions for instructors.

**Columns:** (Same as user_sessions but with `instructor_id`)
- `id` - Primary key
- `instructor_id` - Foreign key to `instructor.id`
- `session_token` - Unique session identifier (64 chars)
- `ip_address` - IP address of the session
- `user_agent` - Browser/device user agent
- `created_at` - When the session was created
- `last_activity` - Last request timestamp
- `expires_at` - When the session expires
- `is_active` - Boolean flag for active status

### Code Components

#### 1. Session Models
- `user/models/user_session.py` - User session model with helper methods
- `instructor/models/instructor_session.py` - Instructor session model with helper methods

**Key Methods:**
- `create_session(user_id, expiry_hours, request_obj)` - Creates a new session
- `get_active_session(user_id)` - Gets the current active session for a user
- `get_session_by_token(session_token)` - Retrieves a session by token
- `terminate_user_sessions(user_id, except_token)` - Terminates all sessions for a user
- `update_activity()` - Updates last activity timestamp
- `terminate()` - Marks session as inactive
- `cleanup_expired_sessions()` - Removes expired sessions

#### 2. Session Guard Middleware
`utils/session_guard.py` - Contains validation logic and decorators

**Key Functions:**
- `validate_user_session()` - Validates the current session
- `session_guard` - Decorator for route protection
- `check_existing_session(user_id, namespace)` - Checks for active sessions
- `terminate_existing_sessions(user_id, namespace, except_token)` - Terminates sessions

#### 3. Database Migration
`migrations/007_add_session_tracking.py` - Creates the session tables

## Implementation Details

### Login Flow

1. **User/Instructor attempts to login**
   - Credentials are validated
   - System checks for existing active sessions

2. **If active session exists:**
   - Previous session is terminated
   - Database record is marked as `is_active = False`
   - WebSocket notification sent to the old device (if connected)

3. **New session created:**
   - New session record created in database
   - Unique session token generated (64-char URL-safe string)
   - Session token stored in Flask session
   - Session expires in 24 hours

4. **User is logged in:**
   - Flask-Login authenticates the user
   - Session namespace set to 'user' or 'instructor'
   - User redirected to dashboard

### Request Validation

On every request (via `before_request` handler):

1. **Skip conditions:**
   - Static files
   - Login/logout routes
   - Unauthenticated users

2. **Validation process:**
   - Retrieve session token from Flask session
   - Look up session in database
   - Check if session is active and not expired
   - Verify user_id matches current_user
   - Update last_activity timestamp

3. **If validation fails:**
   - Clear Flask session
   - Log out user
   - Redirect to login page

### Logout Flow

1. **User/Instructor logs out:**
   - Retrieve session token from Flask session
   - Mark database session as inactive
   - Clear Flask session
   - Redirect to login page

## Security Features

### 1. Session Token Security
- 64-character URL-safe random tokens
- Cryptographically secure generation using `secrets.token_urlsafe(48)`
- Tokens are unique and indexed for fast lookup

### 2. Session Validation
- Every request validates session authenticity
- Prevents session hijacking
- Prevents concurrent logins

### 3. Namespace Isolation
- Separate session tables for users and instructors
- Prevents cross-contamination
- Enforces role-based access control

### 4. Automatic Cleanup
- Sessions expire after 24 hours
- `cleanup_expired_sessions()` method removes old records
- Can be scheduled via cron job or periodic task

## Usage Examples

### Checking for Active Sessions

```python
from utils.session_guard import check_existing_session

has_session, info = check_existing_session(user_id=123, namespace='user')
if has_session:
    print(f"Active session from IP: {info['ip_address']}")
    print(f"Last activity: {info['last_activity']}")
```

### Terminating Sessions

```python
from utils.session_guard import terminate_existing_sessions

# Terminate all sessions for a user
count = terminate_existing_sessions(user_id=123, namespace='user')
print(f"Terminated {count} sessions")

# Terminate all except current session
count = terminate_existing_sessions(
    user_id=123, 
    namespace='user',
    except_token=current_session_token
)
```

### Using Session Guard Decorator

```python
from utils.session_guard import session_guard
from flask_login import login_required

@app.route('/protected')
@login_required
@session_guard
def protected_route():
    # This route will automatically validate the session
    # and redirect to login if session is invalid
    return "Protected content"
```

## Database Migration

### Running the Migration

```bash
# Upgrade (create tables)
python migrations/007_add_session_tracking.py upgrade

# Downgrade (drop tables)
python migrations/007_add_session_tracking.py downgrade
```

### Verification

After migration, verify tables exist:

```sql
SELECT * FROM user_sessions;
SELECT * FROM instructor_sessions;
```

## Configuration

### Session Expiry Time

To change the default 24-hour expiry, modify the `create_session` calls in login routes:

```python
# In user/views.py and instructor/controllers/auth_controller.py
new_session = UserSession.create_session(
    user_id=user.id,
    expiry_hours=48,  # Change to 48 hours
    request_obj=request
)
```

### Skip Session Validation

To skip session validation for specific routes, add them to the exclusion list in `application.py`:

```python
@application.before_request
def validate_session_before_request():
    # Add routes to skip validation
    if request.path.startswith('/static/') or \
       request.path in ['/user/login', '/instructor/login', 
                        '/your/custom/route']:  # Add here
        return None
    # ...
```

## Maintenance

### Cleaning Up Expired Sessions

Run periodically (e.g., daily via cron):

```python
from user.models.user_session import UserSession
from instructor.models.instructor_session import InstructorSession

# Clean up expired sessions
user_count = UserSession.cleanup_expired_sessions()
instructor_count = InstructorSession.cleanup_expired_sessions()

print(f"Cleaned up {user_count} user sessions")
print(f"Cleaned up {instructor_count} instructor sessions")
```

## User Experience

### What Users See

1. **First Login:**
   - User logs in normally
   - Session is created

2. **Second Login from Different Device:**
   - User logs in from another device
   - Previous device session is terminated
   - If the previous device is still connected, they see a notification:
     > "Your session has been terminated because you logged in from another device."

3. **Attempting to Use Previous Device:**
   - Any request will validate the session
   - Session is no longer valid
   - User is redirected to login page with message:
     > "Your session has been terminated. Another device may have logged in."

## Troubleshooting

### Issue: User keeps getting logged out

**Cause:** Session token not being stored properly in Flask session

**Solution:** 
1. Check that `session['session_token']` is set during login
2. Verify session cookies are being sent with requests
3. Check `SESSION_COOKIE_SECURE` and `SESSION_COOKIE_SAMESITE` settings

### Issue: Multiple sessions not being terminated

**Cause:** Database sessions not being created or terminated properly

**Solution:**
1. Check database migration ran successfully
2. Verify `db.session.commit()` is called after creating/terminating sessions
3. Check database constraints and indexes

### Issue: Session expires too quickly

**Cause:** Default expiry time or session cleanup

**Solution:**
1. Increase `expiry_hours` parameter in `create_session`
2. Ensure `last_activity` is being updated on requests
3. Check that `cleanup_expired_sessions` is not running too frequently

## Testing

### Manual Testing

1. **Login from Device 1:**
   - Login as "Gilbert" on Chrome
   - Verify you can access the dashboard

2. **Login from Device 2:**
   - Login as "Gilbert" on Firefox (or incognito)
   - Verify you can access the dashboard

3. **Return to Device 1:**
   - Try to navigate or refresh the page
   - Verify you are redirected to login
   - Should see message about session termination

### Automated Testing

```python
def test_concurrent_login_prevention():
    # Login from client 1
    response1 = client1.post('/user/login', data={
        'email': 'gilbert@test.com',
        'password': 'password123'
    })
    assert response1.status_code == 302
    
    # Login from client 2 (same user)
    response2 = client2.post('/user/login', data={
        'email': 'gilbert@test.com',
        'password': 'password123'
    })
    assert response2.status_code == 302
    
    # Client 1 should be logged out
    response3 = client1.get('/user/dashboard')
    assert response3.status_code == 302  # Redirect to login
```

## Future Enhancements

1. **Session Limit Configuration:**
   - Allow admins to configure max concurrent sessions per user
   - Support multiple sessions for specific roles

2. **Session Management Dashboard:**
   - UI for users to view active sessions
   - Ability to terminate specific sessions remotely

3. **Session Notifications:**
   - Email notifications when login from new device
   - Push notifications for session events

4. **Geographic Tracking:**
   - Store geolocation data with sessions
   - Alert on suspicious location changes

5. **Device Fingerprinting:**
   - Enhanced device tracking
   - Trusted device management

## Related Documentation

- `SESSION_SECURITY_QUICK_REFERENCE.md` - General session security guidelines
- `SESSION_DELETE_FIX.md` - Session authentication fixes
- Database schema documentation

## Support

For issues or questions about the concurrent login prevention system:
1. Check this documentation
2. Review the code comments in session models and middleware
3. Check application logs for session-related errors
4. Contact the development team
