# Admin → Instructor Comprehensive Refactoring Plan

**Created:** 2025-10-19  
**Status:** Planning Complete  
**Scope:** Complete codebase renaming from "Admin" terminology to "Instructor"

## Executive Summary
This document outlines a comprehensive plan to rename all "Admin" references to "Instructor" throughout the RiddleNet codebase. This includes:
- 200+ code references
- 6+ folder renames (static/js/admin, static/css/admin, etc.)
- Database table renames (admin_users → instructor_users)
- Model classes, routes, session logic, WebSocket rooms
- Template files, static assets, documentation

---

## Phase 1: Database Migration

### Files to Execute
- `migrations/rename_admin_to_instructor.sql` ✅ Already exists

### Database Changes
```sql
-- Tables to rename:
admin → instructor (already done?)
admin_users → instructor_users ⚠️ CRITICAL - Foreign keys reference this
admin_password_reset_tokens → instructor_password_reset_tokens

-- Sequences:
admin_id_seq → instructor_id_seq
admin_users_id_seq → instructor_users_id_seq

-- Columns to update:
Role values: 'admin' → 'instructor'
user_type values: 'admin' → 'instructor'

-- Foreign Key Constraints:
All constraints containing 'admin' → 'instructor'
```

### Risk Assessment
⚠️ **HIGH RISK** - Foreign keys in these tables reference `admin_users`:
- `student_deadline_extensions.approved_by` → FK to `admin_users.id`
- `assignment_submissions.graded_by` → FK to `admin_users.id`
- `class_assignments.created_by` → FK to `admin_users.id` (likely)
- `deadline_policies.created_by` → FK to `admin_users.id`

**Mitigation:** 
- Stop application before migration
- Backup database first
- Test on staging/dev environment

---

## Phase 2: Python Model Changes

### Model Files to Update

#### `instructor/models/user.py`
**Current State:**
```python
class AdminUser(db.Model):
    __tablename__ = 'admin_users'  # ← CHANGE TO 'instructor_users'
    # ...fields
    is_admin = Column(Boolean, default=False)  # ← RENAME to is_instructor
```

**Target State:**
```python
class InstructorUser(db.Model):  # Rename class
    __tablename__ = 'instructor_users'  # Match database
    # ...fields
    is_instructor = Column(Boolean, default=False)  # Rename field
```

**Note:** The `InstructorUser` class already exists! May need to:
1. Merge `AdminUser` into `InstructorUser` class
2. Or deprecate `AdminUser` entirely
3. Update `__init__.py` exports

#### `instructor/models/__init__.py`
```python
# Current:
from instructor.models.user import InstructorUser, AdminUser

# Target:
from instructor.models.user import InstructorUser  # Remove AdminUser
```

#### `instructor/models/deadline_policy.py`
Line 47, 220, 237:
```python
# Current:
created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
approved_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
approver = db.relationship('AdminUser', ...)

# Target:
created_by = db.Column(db.Integer, db.ForeignKey('instructor_users.id'))
approved_by = db.Column(db.Integer, db.ForeignKey('instructor_users.id'))
approver = db.relationship('InstructorUser', ...)
```

#### `instructor/models/assignment_submission.py`
Line 31, 45, 127-128:
```python
# Current:
graded_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
grader = db.relationship('AdminUser', ...)
changed_by_type = db.Column(db.String(10))  # 'student' or 'admin'

# Target:
graded_by = db.Column(db.Integer, db.ForeignKey('instructor_users.id'))
grader = db.relationship('InstructorUser', ...)
changed_by_type = db.Column(db.String(10))  # 'student' or 'instructor'
```

### Other Model References
Search for:
- `'AdminUser'` string in relationships
- `'admin_users'` in ForeignKey definitions
- Comments mentioning "admin"

---

## Phase 3: Routes and URLs

### URL Path Changes
**Current:** `/instructor/*` (already correct ✅)  
**URLs to verify/update:**
- Check `run.py` for any `/admin` routes
- Check CORS configuration: `r"/admin/topology/*"` → `r"/instructor/topology/*"`

### Session and Authentication

#### `utils/split_session_interface.py`
Line 33, 69-70, 114-115, 137-138, 161:
```python
# Current:
ADMIN_COOKIE = "admin_session"
# Check if auth_namespace == "admin"

# Target:
INSTRUCTOR_COOKIE = "instructor_session"
# Check if auth_namespace == "instructor"
```

#### `utils/session_cleanup_middleware.py`
Multiple references to "admin" in:
- Function names: `clean_admin_session_contamination()`
- Route lists: `admin_accessible_routes`
- Session checks: `session['auth_namespace'] == 'admin'`

#### `utils/namespace_validator.py`
Line 40, 47, 50, 94, 96, etc.:
```python
# Current:
if namespace == 'admin':
    flash('Admin credentials required.')
    
# Target:
if namespace == 'instructor':
    flash('Instructor credentials required.')
```

#### `run.py`
Line ~170+:
```python
# Current in load_user():
if auth_namespace == 'instructor':
    admin = db.session.get(Admin, user_id_int)  # ← Should be Instructor
    
# Also check before_request_handler() for admin auth checks
```

---

## Phase 4: WebSocket Room Names

### Files with Socket Emit References

#### `user/views.py`
Lines: 855, 909, 929, 953, 974, 997, 1023, 1043, 1070, 1125, 1252, 1280, 1305, 1335, 1755, 1780, 1837, 1876, 1906, 1927
```python
# Current:
socketio.emit('event', data, room='admin_room')

# Target:
socketio.emit('event', data, room='instructor_room')
```

#### `user/routes/simulation_runner.py`
Lines: 721, 780
```python
# Current:
room=f'admin_simulation_{simulation_id}'

# Target:
room=f'instructor_simulation_{simulation_id}'
```

#### `user/dynamic_simulation_routes.py`
Lines: Various
```python
# Check for admin_room references
```

### Socket Event Handlers
Check `socket_events.py` and `socket_manager.py` for room joins/leaves

---

## Phase 5: Static File Folders

### Folders to Rename

#### JavaScript Files
```
static/js/admin/ → static/js/instructor/
├── questions.js
├── notification-center.js
├── lesson-editor.js
├── simulation-builder.js
├── essay.js
├── user_creation.js
└── simulation-creator.js

Root level JS files to rename:
- admin-socket-debug.js → instructor-socket-debug.js
- admin-sync-monitor.js → instructor-sync-monitor.js
- admin-websocket-enabler.js → instructor-websocket-enabler.js
- admin-websocket-manager.js → instructor-websocket-manager.js
```

#### CSS Files
```
static/css/admin/ → static/css/instructor/
├── dashboard.css
├── classroom-style.css
├── enhanced-assignment-modal.css
└── class.css

Root level CSS files:
- admin-actions-banner.css → instructor-actions-banner.css
```

#### Other Static Assets
```
static/img/profiles/admin_3_*.jpg → instructor_3_*.jpg (?)
scripts/admin_assign_smoke_test.py → scripts/instructor_assign_smoke_test.py
```

### Import Path Updates
After renaming folders, update all imports:
```html
<!-- In templates: -->
<script src="/static/js/instructor/lesson-editor.js"></script>
<link rel="stylesheet" href="/static/css/instructor/dashboard.css">
```

---

## Phase 6: Template Files

### Templates to Update
```
templates/instructor/admin_settings.html → instructor_settings.html (?)
```

### Template References
Search for:
- `admin_room` in WebSocket client code
- `admin_session` cookie references
- Hardcoded "Admin" text in UI
- `{% if current_user.is_admin %}`
- Comments mentioning "admin"

---

## Phase 7: Additional Code References

### Permission Decorators
`utils/permission_decorators.py` line 12:
```python
# Current:
if role not in ('admin', 'super_admin', 'instructor'):

# Target:
if role not in ('instructor', 'super_admin'):
```

### Notification Types
`user/models/notification_preferences.py`:
```python
# Current:
admin_notice_email = db.Column(db.Boolean)
admin_notice_websocket = db.Column(db.Boolean)

# Target:
instructor_notice_email = db.Column(db.Boolean)
instructor_notice_websocket = db.Column(db.Boolean)
```

### Comments and Strings
- `user/views.py`: "Notify admin of..." → "Notify instructor of..."
- `user/dynamic_simulation_routes.py`: "admin-created simulations" → "instructor-created simulations"
- `user/routes/notification_routes.py`: "Admin notices" → "Instructor notices"

---

## Phase 8: Configuration Files

### `__init__.py`
Lines: 72, 132, 136, 206-207, 236, 320-340
- Session cookie comments
- SplitSessionInterface references
- Admin blueprints registration
- Context processor `inject_admin_sidebar_context()`
- Path checks: `if path.startswith('/admin')`

### CORS Configuration in `run.py`
```python
# Current:
cors = CORS(app, resources={
    r"/admin/topology/*": {"origins": "*"},
    r"/admin/troubleshooting/*": {"origins": "*"}
})

# Target:
cors = CORS(app, resources={
    r"/instructor/topology/*": {"origins": "*"},
    r"/instructor/troubleshooting/*": {"origins": "*"}
})
```

---

## Execution Order

### Pre-Migration Checklist
- [ ] Create full database backup
- [ ] Test migration script on dev/staging environment
- [ ] Stop all application servers
- [ ] Document current state (git commit)
- [ ] Notify users of maintenance window

### Migration Steps (Must be done in this order)

1. **Stop Application** ⚠️
   ```bash
   # Kill all running Python processes
   taskkill /F /IM python.exe
   ```

2. **Backup Database** ⚠️ CRITICAL
   ```bash
   # Export current database
   pg_dump riddlenetv1 > backup_before_admin_rename_$(date +%Y%m%d_%H%M%S).sql
   ```

3. **Apply Database Migration**
   ```bash
   psql riddlenetv1 < migrations/rename_admin_to_instructor.sql
   ```

4. **Update Python Models** (in order)
   - Merge `AdminUser` into `InstructorUser` or rename
   - Update `__tablename__` to `'instructor_users'`
   - Update all `ForeignKey('admin_users.id')` → `ForeignKey('instructor_users.id')`
   - Update all `relationship('AdminUser')` → `relationship('InstructorUser')`
   - Update `instructor/models/__init__.py` exports

5. **Update Session Logic**
   - `utils/split_session_interface.py`
   - `utils/session_cleanup_middleware.py`
   - `utils/namespace_validator.py`
   - `run.py` load_user function

6. **Update WebSocket Rooms**
   - All files with `room='admin_room'` → `room='instructor_room'`
   - Update socket join/leave events
   - Update client-side WebSocket code

7. **Rename Static Folders**
   ```bash
   # JavaScript
   ren "static\js\admin" "instructor"
   ren "static\js\admin-*.js" "instructor-*.js"
   
   # CSS
   ren "static\css\admin" "instructor"
   ren "static\css\admin-*.css" "instructor-*.css"
   ```

8. **Update All Import Paths**
   - Search for `/static/js/admin/` → `/static/js/instructor/`
   - Search for `/static/css/admin/` → `/static/css/instructor/`
   - Update template `<script>` and `<link>` tags

9. **Update Route Configuration**
   - CORS rules in `run.py`
   - Any hardcoded `/admin` paths

10. **Update Comments and Documentation**
    - Code comments
    - README files
    - Configuration examples

11. **Test Application**
    ```bash
    python run.py
    ```

12. **Verify Functionality**
    - [ ] Instructor login works
    - [ ] Session isolation works
    - [ ] WebSocket rooms connect properly
    - [ ] Database queries succeed
    - [ ] Static assets load
    - [ ] All routes accessible

---

## Rollback Plan

If migration fails:

1. **Stop Application**
2. **Restore Database Backup**
   ```bash
   psql riddlenetv1 < backup_before_admin_rename_*.sql
   ```
3. **Revert Code Changes**
   ```bash
   git reset --hard HEAD
   ```
4. **Restart Application**

---

## Post-Migration Tasks

- [ ] Update production deployment scripts
- [ ] Update environment variables/configs
- [ ] Clear browser caches (cookies may be stale)
- [ ] Update documentation
- [ ] Notify users to re-login
- [ ] Monitor logs for errors
- [ ] Update any external API integrations

---

## Risk Mitigation

### High-Risk Areas
1. **Database Foreign Keys** - Ensure no orphaned records
2. **Active Sessions** - Users will need to re-login
3. **WebSocket Connections** - May need reconnection
4. **Static Asset Caching** - Clear CDN/browser caches

### Testing Checklist
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing of key workflows:
  - [ ] Instructor login/logout
  - [ ] Student assignment submission
  - [ ] WebSocket notifications
  - [ ] Simulation creation/editing
  - [ ] Class management

---

## Estimated Time
- **Planning:** 1 hour ✅
- **Backup & Prep:** 15 minutes
- **Database Migration:** 5 minutes
- **Code Changes:** 2-3 hours
- **Testing:** 1-2 hours
- **Total:** ~4-6 hours

---

## Notes
- This is a breaking change - cannot be done incrementally
- All servers must be stopped during migration
- Users will be logged out and must re-authenticate
- Consider scheduling during off-peak hours
- Have rollback plan ready

---

## Status Log
- **2025-10-19 21:54:** Planning document created
- **Next:** Await user approval to proceed
