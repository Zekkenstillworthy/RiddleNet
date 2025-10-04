# Session Security Quick Reference Guide
## RiddleNet Application - Developer Guidelines

---

## Overview

This guide provides quick reference for developers working on RiddleNet to maintain session security and prevent session poisoning attacks.

---

## Key Concepts

### Auth Namespace
Every authenticated session MUST have an `auth_namespace` that is either:
- `'admin'` - For admin/instructor users
- `'user'` - For student users

**NEVER** allow a session without a valid namespace.

### Session Poisoning
Attack where an attacker manipulates session data to gain unauthorized access to resources meant for a different user type.

Example:
```
1. Login as user → session['auth_namespace'] = 'user'
2. Manipulate cookie to set auth_namespace = 'admin'
3. Access admin routes → SHOULD BE BLOCKED
```

---

## Security Checklist for New Routes

When creating a new authenticated route, ensure:

- [ ] Route uses `@login_required` decorator
- [ ] Route validates `auth_namespace` matches expected type
- [ ] Route verifies `current_user` instance type
- [ ] Route clears session on validation failure
- [ ] Route redirects to appropriate login page
- [ ] Route logs security events (optional but recommended)

---

## Code Templates

### Admin Route Template
```python
from flask import session, redirect, url_for, flash
from flask_login import login_required, current_user
from admin.models.user import Admin

@admin_bp.route('/admin/some-route')
@login_required
def admin_route():
    # 1. Check namespace
    auth_namespace = session.get('auth_namespace', 'unknown')
    if auth_namespace != 'admin':
        flash('Access denied. Admin credentials required.', 'error')
        session.clear()
        return redirect(url_for('auth.login'))
    
    # 2. Verify user type
    if not isinstance(current_user, Admin):
        flash('Access denied. Admin credentials required.', 'error')
        session.clear()
        return redirect(url_for('auth.login'))
    
    # 3. Your route logic here
    return render_template('admin/template.html')
```

### User Route Template
```python
from flask import session, redirect, url_for, flash
from flask_login import login_required, current_user
from user.models.user import User

@user_bp.route('/user/some-route')
@login_required
def user_route():
    # 1. Check namespace
    auth_namespace = session.get('auth_namespace', 'unknown')
    if auth_namespace != 'user':
        flash('Access denied. User credentials required.', 'error')
        session.clear()
        return redirect(url_for('user.login'))
    
    # 2. Verify user type
    if not isinstance(current_user, User):
        flash('Access denied. User credentials required.', 'error')
        session.clear()
        return redirect(url_for('user.login'))
    
    # 3. Your route logic here
    return render_template('user/template.html')
```

### Using the Decorator (Recommended)
```python
from flask_login import login_required
from utils.namespace_validator import require_namespace

@admin_bp.route('/admin/some-route')
@login_required
@require_namespace('admin')  # Handles all validation automatically
def admin_route():
    # Your route logic here - validation already done
    return render_template('admin/template.html')

@user_bp.route('/user/some-route')
@login_required
@require_namespace('user')  # Handles all validation automatically
def user_route():
    # Your route logic here - validation already done
    return render_template('user/template.html')
```

---

## Login Route Requirements

### Setting Namespace on Login
**CRITICAL:** Always set `auth_namespace` when logging in a user.

```python
# Admin Login
session['auth_namespace'] = 'admin'
login_user(admin, remember=True)

# User Login
session['auth_namespace'] = 'user'
login_user(user, remember=True)
```

### Clearing Namespace on Logout
**CRITICAL:** Always clear namespace when logging out.

```python
# Logout
session.clear()  # Clears everything including auth_namespace
logout_user()
```

---

## Common Pitfalls

### ❌ DON'T: Use Fallback Logic
```python
# BAD - allows namespace poisoning
if auth_namespace == 'admin':
    return db.session.get(Admin, user_id)
else:
    return db.session.get(User, user_id)  # Fallback is dangerous
```

### ✅ DO: Require Explicit Namespace
```python
# GOOD - strict validation
if auth_namespace == 'admin':
    return db.session.get(Admin, user_id)
elif auth_namespace == 'user':
    return db.session.get(User, user_id)
else:
    session.clear()  # Invalid namespace
    return None
```

### ❌ DON'T: Only Check Authentication
```python
# BAD - doesn't check namespace or type
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')
```

### ✅ DO: Check Namespace AND Type
```python
# GOOD - checks both namespace and type
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    auth_namespace = session.get('auth_namespace', 'unknown')
    if auth_namespace != 'admin' or not isinstance(current_user, Admin):
        session.clear()
        return redirect(url_for('auth.login'))
    return render_template('admin/dashboard.html')
```

### ❌ DON'T: Assume current_user Type
```python
# BAD - assumes type without checking
@app.route('/profile')
@login_required
def profile():
    user = current_user  # Could be Admin or User!
    return render_template('profile.html', user=user)
```

### ✅ DO: Validate Type Explicitly
```python
# GOOD - validates type before use
@app.route('/profile')
@login_required
def profile():
    auth_namespace = session.get('auth_namespace', 'unknown')
    if auth_namespace != 'user' or not isinstance(current_user, User):
        session.clear()
        return redirect(url_for('user.login'))
    user = current_user
    return render_template('profile.html', user=user)
```

---

## Security Best Practices

### 1. Always Clear Session on Failure
```python
if validation_fails:
    session.clear()  # Don't leave partial session data
    return redirect(...)
```

### 2. Log Security Events
```python
from utils.namespace_validator import log_security_event

if auth_namespace != 'admin':
    log_security_event('NAMESPACE_VIOLATION', {
        'expected': 'admin',
        'actual': auth_namespace,
        'route': request.path
    })
    session.clear()
    return redirect(...)
```

### 3. Use Type Checking
```python
from admin.models.user import Admin
from user.models.user import User

# Check if user is correct type
if isinstance(current_user, Admin):
    # Admin-specific logic
elif isinstance(current_user, User):
    # User-specific logic
else:
    # Unknown type - security issue
    session.clear()
```

### 4. No Mixed Routes
Don't create routes that work for both admin and user:
```python
# BAD - mixed route
@app.route('/profile')
def profile():
    if isinstance(current_user, Admin):
        return admin_profile()
    else:
        return user_profile()
```

Instead, create separate routes:
```python
# GOOD - separate routes
@admin_bp.route('/profile')
@require_namespace('admin')
def admin_profile():
    return render_template('admin/profile.html')

@user_bp.route('/profile')
@require_namespace('user')
def user_profile():
    return render_template('user/profile.html')
```

---

## Testing Your Routes

### Manual Testing
1. Login as user
2. Try to access admin route
3. Should be rejected with "Access denied. Admin credentials required."
4. Verify session was cleared
5. Verify redirected to admin login

Repeat in reverse (admin → user routes).

### Unit Test Template
```python
def test_admin_route_requires_admin_namespace(client):
    # Login as user
    client.post('/login', data={'username': 'testuser', 'password': 'pass'})
    
    # Try to access admin route
    response = client.get('/admin/dashboard', follow_redirects=True)
    
    # Should be rejected
    assert response.status_code == 200
    assert b'Access denied' in response.data
    assert b'Admin credentials required' in response.data
```

---

## Utility Functions Available

### From `utils/namespace_validator.py`:

1. **`@require_namespace(namespace)`**
   - Decorator for route protection
   - Automatically validates namespace and type
   - Handles session clearing and redirects

2. **`validate_namespace_on_request()`**
   - Use in `@app.before_request`
   - Validates every incoming request

3. **`get_safe_namespace()`**
   - Returns validated namespace or None
   - Clears session if poisoning detected

4. **`clear_session_on_namespace_mismatch()`**
   - Utility to check and clear if needed
   - Returns True if valid, False if cleared

5. **`log_security_event(event_type, details)`**
   - Log security events for monitoring
   - Sends real-time alerts to admin room

---

## Quick Fixes for Common Issues

### Issue: "User can access admin routes"
**Solution:** Add namespace validation to the route:
```python
auth_namespace = session.get('auth_namespace', 'unknown')
if auth_namespace != 'admin':
    session.clear()
    return redirect(url_for('auth.login'))
```

### Issue: "Admin can access user routes"
**Solution:** Add namespace validation to the route:
```python
auth_namespace = session.get('auth_namespace', 'unknown')
if auth_namespace != 'user':
    session.clear()
    return redirect(url_for('user.login'))
```

### Issue: "Session persists after logout"
**Solution:** Use `session.clear()` in logout route:
```python
@app.route('/logout')
def logout():
    session.clear()  # Clear ALL session data
    logout_user()
    return redirect(url_for('user.index'))
```

### Issue: "Type mismatch not caught"
**Solution:** Add type verification:
```python
from admin.models.user import Admin

if not isinstance(current_user, Admin):
    session.clear()
    return redirect(url_for('auth.login'))
```

---

## Resources

- **Full Security Report:** `SESSION_POISONING_FIX_REPORT.md`
- **Namespace Validator:** `utils/namespace_validator.py`
- **Example Admin Route:** `admin/controllers/user_controller.py:admin_profile()`
- **Example User Route:** `user/views.py:profile()`

---

## Support

For security questions or concerns, contact:
- Security Team: security@riddlenet.me
- Development Team: dev@riddlenet.me

**Remember:** When in doubt about session security, always:
1. Validate namespace
2. Verify type
3. Clear session on failure
4. Log security events

---

**Last Updated:** October 4, 2025  
**Version:** 1.0  
**Status:** Active
