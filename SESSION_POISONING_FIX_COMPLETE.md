# Session and Route Poisoning Fix - Complete Resolution

**Date:** October 19, 2025  
**Status:** ✅ RESOLVED  
**Affected Routes:** `/instructor/class-content-selector`  
**Issues Fixed:** Route poisoning + Database schema mismatch

---

## Problem Summary

### Issue 1: Route Poisoning (404 Errors)
JavaScript files were hardcoded to call legacy `/admin/api/*` routes after the admin → instructor refactoring, causing:
- 404 errors for `/admin/api/deadlines`
- 404 errors for `/admin/api/collaboration/classes`
- 404 errors for `/admin/api/collaboration/settings`
- Session contamination (wrong namespace used)

### Issue 2: Database Schema Mismatch
Missing `simulations.task_config` column causing:
```
ERROR: column simulations.task_config does not exist
UndefinedColumn exception
InFailedSqlTransaction: current transaction is aborted
```

---

## Root Cause Analysis

### Route Poisoning
During the admin → instructor refactoring (commit 78ca80c), Python backend routes were updated:
- ✅ Blueprint changed: `/admin/api` → `/instructor/api` 
- ✅ Controllers updated
- ✅ Templates updated
- ❌ **JavaScript files NOT updated** ← Root cause

**Files affected:**
1. `static/js/deadline-manager.js` - 2 hardcoded `/admin/api/deadlines` calls
2. `static/js/collaboration-manager.js` - 17 hardcoded `/admin/api/collaboration/*` calls

### Session Contamination
When JavaScript called `/admin/api/*` paths:
1. SplitSession detected **non-instructor path** → returned `user_session` cookie
2. User loader received `user_id=3` but **no namespace** (unknown)
3. Tried to load from `users` table (student table) → not found
4. Error: "No user found in any table for ID 3"

### Database Schema Drift
Model `instructor/models/simulation.py` defined:
```python
task_config = db.Column(JSON, default=dict)  # Line 33
```

But database schema missing this column → migration never run.

---

## Solution Implementation

### Fix 1: JavaScript Route Updates (Commit 34e17d2)

**File: `static/js/deadline-manager.js`**
```javascript
// Line 21 - BEFORE:
fetch('/admin/api/deadlines')

// Line 21 - AFTER:
fetch('/instructor/api/deadlines')

// Line 383 - BEFORE:
fetch('/admin/api/deadlines', {method: 'POST'})

// Line 383 - AFTER:
fetch('/instructor/api/deadlines', {method: 'POST'})
```

**File: `static/js/collaboration-manager.js`**
Global replacement (17 occurrences):
```powershell
(Get-Content 'static\js\collaboration-manager.js') -replace '/admin/api/collaboration', '/instructor/api/collaboration' | Set-Content 'static\js\collaboration-manager.js'
```

**Changed routes:**
- Line 228: `/admin/api/collaboration/classes` → `/instructor/api/collaboration/classes`
- Line 256: `/admin/api/collaboration/simulation-session` → `/instructor/api/collaboration/simulation-session`
- Line 280: `/admin/api/collaboration/session/${sessionId}/assign` → `/instructor/api/collaboration/session/${sessionId}/assign`
- Lines 295, 319, 635, 680, 745, 772, 801, 894, 924, 957, 992, 1042, 1109, 1118: Various collaboration endpoints

**Verification:**
```bash
findstr /C:"/admin/api/" static\js\*.js
# Result: 0 matches (all fixed)

findstr /C:"/instructor/api/" static\js\*.js
# Result: 19 matches (all updated)
```

### Fix 2: Database Schema Migration

**SQL executed:**
```sql
ALTER TABLE simulations ADD COLUMN task_config JSON DEFAULT '{}';
```

**Verification:**
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'simulations' AND column_name = 'task_config';

-- Result: task_config (1 row)
```

### Fix 3: Deployment

**Steps:**
1. Git commit: `34e17d2` - "Fix: Update JavaScript API routes from /admin/api to /instructor/api to resolve route poisoning"
2. Git push to GitHub
3. SSH deploy: `cd ~/RiddleNet && git pull origin main && sudo systemctl restart riddlenet`
4. Database migration: `ALTER TABLE simulations ADD COLUMN task_config JSON`
5. Service restart: `sudo systemctl restart riddlenet`

---

## Verification Results

### Before Fix
**Server logs (22:39:41):**
```
GET /admin/api/deadlines HTTP/1.0" 404
GET /admin/api/collaboration/classes HTTP/1.0" 404
GET /admin/api/collaboration/settings HTTP/1.0" 404
ERROR: column simulations.task_config does not exist
InFailedSqlTransaction: current transaction is aborted
```

**Session contamination:**
```
🍪 SplitSession: Non-instructor path, returning USER_COOKIE (user_session)
❌ No user found in any table for ID 3
```

### After Fix
**Server logs (22:51:40):**
```
✅ /instructor/api/collaboration/active - 200 OK
✅ instructor_session cookie used
✅ Admin session: Loaded admin Jemar A. Banawa (ID: 3)
✅ No 404 errors
✅ No database errors
✅ No session contamination
```

**Service status:**
```
Active: active (running) since Sun 2025-10-19 22:51:09 UTC
Main PID: 220710 (gunicorn)
Status: "Gunicorn arbiter booted"
```

**Error check:**
```bash
sudo journalctl -u riddlenet -n 50 | grep -E '(ERROR|404|InFailedSqlTransaction)'
# Result: No output (no errors)
```

---

## Browser Cache Issue

⚠️ **IMPORTANT:** After deployment, old JavaScript files may be cached in browsers.

**Symptoms:**
- Server logs show NO new 404 errors after 22:51:09
- But users may still see errors if they haven't cleared cache

**User action required:**
1. **Hard refresh:** Press `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
2. **Or clear browser cache** for riddlenet.me domain
3. **Verify in DevTools:** Network tab should show requests to `/instructor/api/*` (not `/admin/api/*`)

---

## Technical Details

### SplitSession Path Detection
```python
def _select_cookie_for_request(self):
    path = request.path
    
    # Instructor paths → instructor_session
    if path.startswith('/instructor'):
        return 'instructor_session'
    
    # All other paths → user_session
    else:
        return 'user_session'
```

**Before fix:** `/admin/api/deadlines` → `user_session` (wrong namespace)  
**After fix:** `/instructor/api/deadlines` → `instructor_session` (correct)

### Blueprint Registration
```python
# instructor/routes/api_routes.py, line 13
api_bp = Blueprint('instructor_api', __name__, url_prefix='/instructor/api')

# Routes registered:
@api_bp.route('/deadlines', methods=['GET'])
@api_bp.route('/collaboration/classes', methods=['GET'])
@api_bp.route('/collaboration/settings', methods=['GET'])
# etc.
```

**Full URLs:**
- `https://riddlenet.me/instructor/api/deadlines`
- `https://riddlenet.me/instructor/api/collaboration/classes`
- `https://riddlenet.me/instructor/api/collaboration/settings`

### Database Schema Fix
**Column added:**
```sql
-- Column name: task_config
-- Data type: JSON
-- Default value: {}
-- Nullable: YES (implicit)
```

**Model definition (Python):**
```python
class Simulation(db.Model):
    task_config = db.Column(JSON, default=dict)  # Task builder configuration
```

---

## Files Changed

### Commit 34e17d2
```
static/js/deadline-manager.js      |  4 ++--
static/js/collaboration-manager.js | 34 +++++++++++++++++-----------------
2 files changed, 19 insertions(+), 19 deletions(-)
```

### Database Migration
```sql
ALTER TABLE simulations ADD COLUMN task_config JSON DEFAULT '{}';
```

---

## Related Documentation

- **Previous fix:** `ROUTE_POISONING_FIX.md` (initial investigation and partial fix)
- **Refactoring:** `ADMIN_TO_INSTRUCTOR_REFACTORING_COMPLETE.md`
- **Blueprint changes:** `instructor/routes/api_routes.py` line 13

---

## Lessons Learned

1. **Frontend-backend sync:** When refactoring route prefixes, search ALL files including JavaScript
2. **Global search patterns:**
   ```bash
   # Search for route references
   grep -r "/admin/api" --include="*.js" static/
   findstr /s /c:"/admin/api" static\*.js
   ```

3. **Database migrations:** Always run schema migrations after model changes
   - Check: `information_schema.columns` vs model definitions
   - Fix: Create migration or manual `ALTER TABLE`

4. **Browser cache:** After JavaScript changes, users MUST clear cache or hard refresh
   - Consider: Cache-busting query strings (`?v=20251019`)
   - Or: Disable static file caching during development

5. **Session namespace:** Path-based session selection requires consistent URL patterns
   - `/instructor/*` → instructor_session
   - All other paths → user_session

---

## Verification Commands

**Check for route poisoning:**
```bash
# Local
findstr /C:"/admin/api" static\js\*.js

# Server
ssh ubuntu@54.66.229.118 "cd ~/RiddleNet && grep -r '/admin/api' static/js/"
```

**Check database schema:**
```bash
ssh ubuntu@54.66.229.118 "psql postgresql://postgres:admin@localhost:5432/riddlenet -c \"SELECT column_name FROM information_schema.columns WHERE table_name = 'simulations' AND column_name = 'task_config';\""
```

**Check for errors:**
```bash
ssh ubuntu@54.66.229.118 "sudo journalctl -u riddlenet -n 100 --no-pager | grep -E '(ERROR|404|InFailedSqlTransaction)'"
```

**Check service status:**
```bash
ssh ubuntu@54.66.229.118 "sudo systemctl status riddlenet"
```

---

## Resolution Confirmation

✅ **Route poisoning:** Fixed - all JavaScript files now call `/instructor/api/*`  
✅ **Database schema:** Fixed - `task_config` column added  
✅ **Session contamination:** Fixed - correct namespace used  
✅ **Service running:** Active and healthy  
✅ **No errors:** Clean logs after 22:51:09 UTC  

⚠️ **User action required:** Clear browser cache to load new JavaScript files

---

## Next Steps (If Users Report Issues)

1. **Verify browser cache cleared:**
   - Open DevTools → Network tab
   - Check requests go to `/instructor/api/*` (not `/admin/api/*`)
   - Check response codes are 200 (not 404)

2. **Check for new errors:**
   ```bash
   ssh ubuntu@54.66.229.118 "sudo journalctl -u riddlenet -f"
   ```

3. **Verify column exists:**
   ```bash
   ssh ubuntu@54.66.229.118 "psql postgresql://postgres:admin@localhost:5432/riddlenet -c 'SELECT * FROM simulations LIMIT 1;'"
   ```

4. **Force cache clear (nuclear option):**
   - Rename JavaScript files: `deadline-manager.js?v=2`
   - Update template references
   - Or add cache-busting middleware

---

**Resolution completed:** October 19, 2025, 22:51:09 UTC  
**Commits:** fb56919, 42f8e1f, 34e17d2  
**Database migration:** task_config column added  
**Status:** Production deployed and verified ✅
