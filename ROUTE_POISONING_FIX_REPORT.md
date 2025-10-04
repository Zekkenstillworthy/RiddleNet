# Route Poisoning Fix Report - October 4, 2025

## Issue Summary

**Problem:** Admin users clicking "Edit Simulation" button on the Class Content Selector page (`/admin/class-content-selector?class_id=7`) were being redirected to `/login`, losing their admin session.

**Root Cause:** Session poisoning due to namespace crossing. The "Edit Simulation" button was redirecting admins to the **user route** `/dynamic/simulation/<id>` instead of the **admin route** `/admin/simulation/edit/<id>`.

**Severity:** HIGH - Complete authentication failure for admin simulation editing workflow

## Technical Analysis

### Authentication Architecture

RiddleNet uses a dual namespace system to separate admin and user sessions:

1. **Admin Namespace** (`auth_namespace = 'admin'`)
   - Routes: `/admin/*`
   - Model: `admin.models.user.Admin`
   - Login: `/admin/login`

2. **User Namespace** (`auth_namespace = 'user'`)
   - Routes: `/dynamic/*`, `/simulation/*`, `/profile`, etc.
   - Model: `user.models.user.User`
   - Login: `/login`

### Failure Sequence

1. Admin logs in → session gets `auth_namespace = 'admin'`
2. Admin navigates to `/admin/class-content-selector?class_id=7`
3. Admin clicks "Edit Simulation" button
4. JavaScript redirects to `/dynamic/simulation/<id>` (USER ROUTE)
5. Route handler checks namespace with `@user_login_required` decorator
6. Decorator finds `auth_namespace = 'admin'` (wrong namespace!)
7. `enforce_namespace_security()` middleware detects poisoning
8. Session cleared and redirected to `/login`

### Code Location

**File:** `templates/admin/class_content_manager.html`  
**Line:** 9399  
**Function:** `editSimulation(simulationId)`

**Before (VULNERABLE):**
```javascript
function editSimulation(simulationId) {
    window.location.href = `/dynamic/simulation/${simulationId}`;  // WRONG! User route
}
```

**After (FIXED):**
```javascript
function editSimulation(simulationId) {
    // SECURITY FIX: Use admin route, not user route to prevent session poisoning
    // Admin users must use /admin/simulation/edit/<id> (admin namespace)
    // NOT /dynamic/simulation/<id> (user namespace - causes session poisoning)
    window.location.href = `/admin/simulation/edit/${simulationId}`;
}
```

## Security Enforcement Mechanisms

### 1. User Loader (`application.py`)

Validates namespace on every authenticated request:

```python
@login_manager.user_loader
def load_user(user_id):
    auth_namespace = session.get('auth_namespace', 'unknown')
    
    if auth_namespace == 'admin':
        return db.session.get(Admin, user_id)
    elif auth_namespace == 'user':
        return db.session.get(User, user_id)
    else:
        # NO FALLBACK - reject invalid namespace
        session.clear()
        return None
```

### 2. Before Request Middleware (`application.py`)

Global route protection:

```python
@application.before_request
def enforce_namespace_security():
    if path.startswith('/admin'):
        if auth_namespace != 'admin':
            session.clear()
            return redirect(url_for('auth.login'))
```

### 3. Route Decorators

- **Admin routes:** `@login_required` + `@teacher_required`
- **User routes:** `@user_login_required`

## Fix Implementation

### Changes Made

1. **Fixed editSimulation() function** in `templates/admin/class_content_manager.html`
   - Changed redirect from `/dynamic/simulation/<id>` → `/admin/simulation/edit/<id>`
   - Added security comments explaining the namespace separation

2. **Created comprehensive documentation** in `NAMESPACE_ROUTE_SEPARATION_GUIDE.md`
   - Route mapping reference table
   - Common poisoning patterns (with examples of what NOT to do)
   - Testing checklist for developers
   - Security enforcement point explanations

### Files Modified

```
templates/admin/class_content_manager.html   (Line 9399)
NAMESPACE_ROUTE_SEPARATION_GUIDE.md         (New file)
```

## Verification

### Testing Steps

1. ✅ Admin login at `/admin/login`
2. ✅ Navigate to `/admin/class-content-selector?class_id=7`
3. ✅ Click "Edit Simulation" button
4. ✅ Verify redirect to `/admin/simulation/edit/<id>`
5. ✅ Verify simulation editor loads without session loss
6. ✅ Verify admin session remains valid throughout

### No Other Poisoning Found

Comprehensive search performed for similar issues:
- ✅ No admin templates redirecting to `/dynamic/*` routes
- ✅ No admin templates using `url_for('user.*')` inappropriately
- ✅ No admin Python code redirecting to user routes
- ✅ Profile routes properly separated (`/users/profile` vs `/profile`)

## Route Mapping Reference

### Simulation Routes

| Feature | Admin Route | User Route |
|---------|-------------|------------|
| **Edit Simulation** | `/admin/simulation/edit/<id>` | ❌ N/A |
| Run Simulation | ❌ N/A | `/dynamic/simulation/<id>` |
| View Simulation | `/admin/simulation/<id>` | ❌ N/A |
| Create Simulation | `/admin/simulation/edit/new` | ❌ N/A |

### Profile Routes

| Feature | Admin Route | User Route |
|---------|-------------|------------|
| View Profile | `/users/profile` | `/profile` |
| Update Profile | `/users/update_profile` | `/update_profile` |

### Class Routes

| Feature | Admin Route | User Route |
|---------|-------------|------------|
| Content Manager | `/admin/class-content-selector` | ❌ N/A |
| View Class | `/admin/class/<id>/overview` | `/class/<id>` |

## Prevention Measures

### Developer Guidelines

1. **Always check the namespace** before adding redirects or links
2. **Use the route mapping table** to find the correct route
3. **Never mix namespaces** in the same user flow
4. **Add comments** explaining why a particular route was chosen
5. **Test with both admin and user accounts** before deploying

### Code Review Checklist

- [ ] Admin templates only link to `/admin/*` routes
- [ ] User templates only link to user routes (not `/admin/*`)
- [ ] No `window.location.href` mixing namespaces
- [ ] No `redirect()` calls mixing namespaces
- [ ] Profile routes use correct namespace
- [ ] Proper decorators on all routes

## Related Documentation

- **SESSION_POISONING_FIX_REPORT.md** - Original session poisoning vulnerability analysis
- **SESSION_SECURITY_QUICK_REFERENCE.md** - Quick reference for developers
- **NAMESPACE_ROUTE_SEPARATION_GUIDE.md** - Comprehensive namespace guide (NEW)
- **utils/namespace_validator.py** - Namespace validation utilities

## Deployment Notes

### Changes Required

- ✅ Update `templates/admin/class_content_manager.html` (already done)
- ✅ Add `NAMESPACE_ROUTE_SEPARATION_GUIDE.md` to documentation (already done)
- ✅ No database migrations required
- ✅ No configuration changes required
- ✅ No dependency updates required

### Rollback Plan

If issues arise, revert the single line change:

```javascript
// Revert to (not recommended):
window.location.href = `/dynamic/simulation/${simulationId}`;
```

However, this will restore the original vulnerability.

## Conclusion

The route poisoning issue has been **completely resolved**. The "Edit Simulation" button now correctly redirects admin users to the admin simulation editor route while maintaining their admin session.

**Status:** ✅ FIXED AND VERIFIED

**Security Impact:** HIGH - Prevents complete authentication failure  
**User Impact:** Positive - Admin simulation editing workflow now functions correctly  
**Risk Level:** LOW - Single line change with comprehensive testing

---

**Fixed by:** GitHub Copilot  
**Date:** October 4, 2025  
**Review Status:** Ready for deployment
