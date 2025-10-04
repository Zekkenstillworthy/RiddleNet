# Namespace Route Separation Guide

## Overview
RiddleNet uses a **dual namespace authentication system** to completely separate admin and user sessions. This prevents session poisoning attacks and ensures proper access control.

## Critical Security Rule

**NEVER mix admin and user routes in the same user flow.**

### Authentication Namespaces

- **Admin Namespace** (`auth_namespace = 'admin'`)
  - Routes: `/admin/*`
  - Login: `/admin/login`
  - Profile: `/users/profile`
  - Model: `admin.models.user.Admin`

- **User Namespace** (`auth_namespace = 'user'`)
  - Routes: `/dynamic/*`, `/simulation/*`, `/profile`, `/dashboard`, etc.
  - Login: `/login`
  - Profile: `/profile`
  - Model: `user.models.user.User`

## Common Session Poisoning Patterns (AVOID THESE!)

### ❌ WRONG: Admin redirecting to user route
```javascript
// In admin template - WRONG!
function editSimulation(simulationId) {
    window.location.href = `/dynamic/simulation/${simulationId}`; // User route!
}
```

### ✅ CORRECT: Admin redirecting to admin route
```javascript
// In admin template - CORRECT!
function editSimulation(simulationId) {
    window.location.href = `/admin/simulation/edit/${simulationId}`; // Admin route!
}
```

### ❌ WRONG: User redirecting to admin route
```javascript
// In user template - WRONG!
function viewClass(classId) {
    window.location.href = `/admin/classes/${classId}`; // Admin route!
}
```

### ✅ CORRECT: User redirecting to user route
```javascript
// In user template - CORRECT!
function viewClass(classId) {
    window.location.href = `/class/${classId}`; // User route!
}
```

## Route Mapping Reference

### Simulation Routes

| Feature | Admin Route | User Route | Notes |
|---------|-------------|------------|-------|
| Edit Simulation | `/admin/simulation/edit/<id>` | N/A | Admin only |
| Run Simulation | N/A | `/dynamic/simulation/<id>` | User only |
| View Simulation | `/admin/simulation/<id>` | N/A | Admin preview |
| Create Simulation | `/admin/simulation/edit/new` | N/A | Admin only |

### Profile Routes

| Feature | Admin Route | User Route | Notes |
|---------|-------------|------------|-------|
| View Profile | `/users/profile` | `/profile` | Different routes! |
| Update Profile | `/users/update_profile` | `/update_profile` | Different routes! |

### Class/Content Routes

| Feature | Admin Route | User Route | Notes |
|---------|-------------|------------|-------|
| Class Management | `/admin/classes` | N/A | Admin only |
| View Class | `/admin/class/<id>/overview` | `/class/<id>` | Different routes! |
| Content Manager | `/admin/class-content-selector` | N/A | Admin only |
| Student Dashboard | N/A | `/dashboard` | User only |

## Security Enforcement Points

### 1. User Loader (`application.py`)
```python
@login_manager.user_loader
def load_user(user_id):
    auth_namespace = session.get('auth_namespace', 'unknown')
    
    if auth_namespace == 'admin':
        # Load from Admin table
        return db.session.get(Admin, user_id)
    elif auth_namespace == 'user':
        # Load from User table
        return db.session.get(User, user_id)
    else:
        # NO FALLBACK - reject invalid namespace
        session.clear()
        return None
```

### 2. Before Request Handler (`application.py`)
```python
@application.before_request
def enforce_namespace_security():
    # Admin routes require admin namespace
    if path.startswith('/admin'):
        if auth_namespace != 'admin':
            session.clear()
            return redirect(url_for('auth.login'))
    
    # User routes require user namespace
    elif path.startswith('/dynamic') or path.startswith('/simulation'):
        if auth_namespace != 'user':
            session.clear()
            return redirect(url_for('user.login'))
```

### 3. Route Decorators
```python
# Admin routes
@login_required
@teacher_required  # Validates admin namespace
def edit_simulation(simulation_id):
    pass

# User routes
@user_login_required  # Validates user namespace
def run_simulation(simulation_id):
    pass
```

## Testing Checklist

When adding new features, verify:

- [ ] Admin templates only link to `/admin/*` routes
- [ ] User templates only link to user routes (not `/admin/*`)
- [ ] No `window.location.href` mixing namespaces
- [ ] No `redirect()` mixing namespaces
- [ ] Profile routes use correct namespace (`/users/profile` vs `/profile`)
- [ ] Proper decorators on all routes (`@teacher_required` vs `@user_login_required`)

## Quick Reference: Is this route poisoning?

Ask yourself:
1. **Who is logged in?** (Admin or User)
2. **Where are they trying to go?** (Admin route or User route)
3. **Does the route match their namespace?**

If the answer to #3 is NO → **Session Poisoning! Fix it!**

## Recent Fixes

### October 4, 2025 - Class Content Selector Edit Simulation Fix

**Issue:** Admin clicking "Edit Simulation" redirected to `/dynamic/simulation/<id>` (user route), causing session poisoning and redirect to `/login`.

**Fix:** Changed `editSimulation()` function in `class_content_manager.html` to use `/admin/simulation/edit/<id>` (admin route).

**Files Changed:**
- `templates/admin/class_content_manager.html` - Line 9399

## Support

For questions about namespace separation, contact the security team or review:
- `SESSION_POISONING_FIX_REPORT.md` - Comprehensive security analysis
- `SESSION_SECURITY_QUICK_REFERENCE.md` - Developer quick reference
- `utils/namespace_validator.py` - Security validation utilities
