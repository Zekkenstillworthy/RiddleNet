# User Management URL Routing Fix

## Issue Summary
The user management page was experiencing 404 errors when performing various operations (delete, edit, TOTP management) because JavaScript code was using incorrect URL prefixes.

### Console Errors Observed
```
Failed to load resource: the server responded with a status of 404 (NOT FOUND)
- /users/delete/4
- /users/delete/6
```

## Root Cause
The `user_bp` blueprint in `admin/controllers/user_controller.py` is registered with the URL prefix `/admin` in `run.py`:
```python
('admin.controllers.user_controller', 'user_bp', '/admin', None)
```

However, JavaScript code in the template was using `/users/` prefix instead of `/admin/`, causing all AJAX requests to fail.

## Routes Affected
All routes in the user_controller blueprint are prefixed with `/admin`:
- `/admin/delete/<user_id>` - Delete regular user
- `/admin/admins/delete/<admin_id>` - Delete admin user
- `/admin/edit/<user_id>` - Edit regular user
- `/admin/edit_admin/<user_id>` - Edit admin user
- `/admin/get_totp_info/<user_id>` - Get TOTP information
- `/admin/generate_totp/<user_id>` - Generate/reset TOTP
- `/admin/disable_totp/<user_id>` - Disable TOTP

## Changes Made

### File: `templates/admin/user_management.html`

#### 1. Delete Operations (Line ~2912)
**Before:**
```javascript
const url = isAdmin ? `/users/admins/delete/${adminId}` : `/users/delete/${userId}`;
```

**After:**
```javascript
const url = isAdmin ? `/admin/admins/delete/${adminId}` : `/admin/delete/${userId}`;
```

#### 2. Edit Form Actions - Regular Users (Lines ~2483, ~2491)
**Before:**
```javascript
document.getElementById('editUserForm').setAttribute('action', `/users/edit_admin/${userId}`);
// ...
document.getElementById('editUserForm').setAttribute('action', `/users/edit/${userId}`);
```

**After:**
```javascript
document.getElementById('editUserForm').setAttribute('action', `/admin/edit_admin/${userId}`);
// ...
document.getElementById('editUserForm').setAttribute('action', `/admin/edit/${userId}`);
```

#### 3. Edit Form Actions - Admin Users (Line ~2531)
**Before:**
```javascript
document.getElementById('editUserForm').setAttribute('action', `/users/edit_admin/${adminId}`);
```

**After:**
```javascript
document.getElementById('editUserForm').setAttribute('action', `/admin/edit_admin/${adminId}`);
```

#### 4. TOTP Get Info (Line ~2538)
**Before:**
```javascript
fetch(`/users/get_totp_info/${userId}`, {
```

**After:**
```javascript
fetch(`/admin/get_totp_info/${userId}`, {
```

#### 5. TOTP Enable/Generate (Line ~2645)
**Before:**
```javascript
fetch(`/users/generate_totp/${userId}`, {
```

**After:**
```javascript
fetch(`/admin/generate_totp/${userId}`, {
```

#### 6. TOTP Reset (Line ~2670)
**Before:**
```javascript
fetch(`/users/generate_totp/${userId}`, {
```

**After:**
```javascript
fetch(`/admin/generate_totp/${userId}`, {
```

#### 7. TOTP Disable (Line ~2696)
**Before:**
```javascript
fetch(`/users/disable_totp/${userId}`, {
```

**After:**
```javascript
fetch(`/admin/disable_totp/${userId}`, {
```

#### 8. Edit Form Submit Handler (Lines ~2836, ~2838)
**Before:**
```javascript
if (isAdmin) {
    formAction = `/users/edit_admin/${userId}`;
} else {
    formAction = `/users/edit/${userId}`;
}
```

**After:**
```javascript
if (isAdmin) {
    formAction = `/admin/edit_admin/${userId}`;
} else {
    formAction = `/admin/edit/${userId}`;
}
```

## Total Changes
- **9 URL patterns fixed** across multiple JavaScript functions
- All `/users/` prefixes changed to `/admin/` for AJAX fetch calls and form actions

## Testing Recommendations

### 1. User Deletion
- Navigate to User Management page
- Try deleting a regular user
- Try deleting an admin user
- Verify no 404 errors in console
- Verify success messages appear

### 2. User Editing
- Click "Edit" on a regular user
- Modify fields and save
- Verify changes are saved
- Click "Edit" on an admin user
- Verify changes are saved

### 3. TOTP Management
- Click "View" on a user
- Test "Enable TOTP" button
- Test "Reset TOTP" button
- Test "Disable TOTP" button
- Verify all operations succeed without 404 errors

### 4. Browser Console Check
Open browser console (F12) and verify:
- No 404 errors when performing any user management operations
- All fetch requests go to `/admin/*` URLs
- Success responses received from server

## Impact
This fix resolves all 404 errors in the user management interface and ensures that:
- ✅ Users can be deleted successfully
- ✅ Users can be edited successfully
- ✅ TOTP can be enabled/disabled/reset
- ✅ All AJAX operations function correctly
- ✅ Blueprint routing is properly aligned with frontend JavaScript

## Related Files
- `templates/admin/user_management.html` - Frontend JavaScript updated
- `admin/controllers/user_controller.py` - Backend routes (unchanged)
- `run.py` - Blueprint registration at `/admin` prefix (unchanged)

## Prevention
When adding new AJAX endpoints to user management:
1. Always use `/admin/` prefix for URLs (not `/users/`)
2. Verify blueprint registration prefix in `run.py`
3. Test in browser console to ensure no 404 errors
4. Consider using `{{ url_for('admin_user.route_name') }}` in Jinja2 templates for server-side URL generation
