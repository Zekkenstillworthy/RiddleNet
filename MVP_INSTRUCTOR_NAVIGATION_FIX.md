# MVP Fix: Instructor Simulation View & Profile Navigation

## Issue Summary

From `/instructor/class-content-selector?class_id=7`:

1. **View Simulation Button** → Redirects to `/instructor/classes` instead of loading simulation
2. **Instructor Profile Link** → Redirects to `/instructor/` instead of profile page

## Root Cause Analysis

### ✅ Fixed Issues

1. **Permission Decorator Role Check** - RESOLVED
   - `@teacher_required` and `@instructor_required` decorators were rejecting `admin` role
   - **Fix Applied:** Updated `utils/permission_decorators.py` to accept `admin` role
   - Also checks `session['auth_namespace'] == 'instructor'` as fallback

2. **Socket Event Import** - RESOLVED  
   - `simulation_routes.py` imported non-existent `emit_admin_simulation_updated`
   - **Fix Applied:** Changed to `emit_instructor_simulation_updated`
   - Blueprint now registers successfully

3. **Profile Route Instance Check** - RESOLVED
   - Profile route only accepted `InstructorUser`, rejected `Instructor` accounts
   - **Fix Applied:** Now accepts both `isinstance(current_user, (Instructor, InstructorUser))`

### 🔍 Current Investigation

**Likely Cause of Redirect to `/instructor/classes`:**

The `view_simulation` route has fallback redirects:

```python
@admin_simulation_bp.route('/<int:simulation_id>')
@login_required
@teacher_required
def view_simulation(simulation_id):
    """Preview simulation"""
    try:
        simulation_data = simulation_controller.get_simulation_by_id(simulation_id, include_steps=True)
        if 'error' in simulation_data:
            flash(simulation_data['error'], 'error')
            return redirect(url_for('class_controller.index'))  # ← HERE
        
        return render_template(
            'instructor/simulation_preview.html',
            simulation=simulation_data['simulation']
        )
    except Exception as e:
        flash(f'Error loading simulation: {str(e)}', 'error')
        return redirect(url_for('class_controller.index'))  # ← AND HERE
```

**Possible reasons for error:**
1. Simulation ID doesn't exist or isn't published
2. Database query failing
3. Permission check still failing (unlikely after our fixes)
4. Template rendering issue

## Verification Steps

### 1. Check if Decorators Work Now

After restarting Flask, log in as instructor and check browser console when clicking "View Simulation":

- If you see `{"error":"Instructor access required"}` → Decorator still failing
- If you see flash message "Simulation not found" → Database issue
- If you see actual error message → Look at Flask logs

### 2. Check Database for Simulation

```python
# In Flask shell or Python
from instructor.models.simulation import Simulation
sim = Simulation.query.get(1)  # Use actual ID from URL
print(f"Found: {sim}")
print(f"Published: {sim.is_published if sim else 'N/A'}")
print(f"Active: {sim.is_active if sim else 'N/A'}")
```

### 3. Check Flask Logs

Look for these log messages when clicking "View Simulation":
```
[GET_SIMULATION_BY_ID] Looking for simulation_id=X
[GET_SIMULATION_BY_ID] Found simulation X: [title]
```

Or error:
```
[GET_SIMULATION_BY_ID] Simulation X not found in database
```

## Testing Commands

### Test 1: Verify Routes Registered
```bash
python test_instructor_routes.py
```
Expected: ✅ All routes including `/instructor/simulation/<int:simulation_id>` registered

### Test 2: Check Simulation Exists
```python
# Open Flask shell
python
>>> from run import app
>>> from instructor.models.simulation import Simulation
>>> with app.app_context():
...     sims = Simulation.query.all()
...     print(f"Total simulations: {len(sims)}")
...     for s in sims[:5]:
...         print(f"ID: {s.id}, Title: {s.title}, Published: {s.is_published}")
```

### Test 3: Test Permission Decorator
```python
# Check if admin role passes decorator
from utils.permission_decorators import teacher_required
from flask import Flask, jsonify
from flask_login import current_user

# Should not return {"error":"Instructor access required"} for admin role
```

## Next Debugging Steps

If issue persists after Flask restart:

1. **Check Browser Developer Console:**
   - Network tab: What URL is actually being requested?
   - Console tab: Any JavaScript errors?
   - Check HTTP status code (403 = permission, 404 = not found, 302 = redirect)

2. **Add Debug Logging:**
   ```python
   # In simulation_routes.py view_simulation function
   print(f"🔍 view_simulation called for ID: {simulation_id}")
   print(f"🔍 current_user: {current_user}")
   print(f"🔍 current_user.role: {getattr(current_user, 'role', 'NO ROLE')}")
   print(f"🔍 auth_namespace: {session.get('auth_namespace')}")
   ```

3. **Test Direct URL Access:**
   - Manually navigate to `http://127.0.0.1:5001/instructor/simulation/1`
   - Check what response you get (error message, redirect, or actual page)

## Profile Page Investigation

The profile link in `templates/instructor/base.html` uses:
```html
<a href="{{ url_for('admin_user.admin_profile') }}">
```

This should route to `/instructor/profile` based on the `@user_bp.route('/profile')` decorator.

**Potential Issues:**
1. If redirecting to `/instructor/` - Check if `dashboard_bp` has a root route catching it
2. Flash message appears - Check session namespace validation in profile route
3. 404 error - Blueprint not registered properly

## Files Modified

1. ✅ `utils/permission_decorators.py` - Added `admin` to accepted roles, added namespace check
2. ✅ `instructor/routes/simulation_routes.py` - Fixed socket event import
3. ✅ `instructor/controllers/user_controller.py` - Relaxed profile instance check

## Status

🟡 **Partial Fix Applied** - Permission decorators updated, but need to verify:
- Flask app restarted with new decorator code
- Actual simulation ID exists in database
- Template renders without errors

## Recommended Next Action

**Please provide:**
1. Flask console output when clicking "View Simulation"
2. Browser console errors (if any)
3. Result of simulation database query (see Test 2 above)
4. Confirm you restarted Flask after the permission decorator fix

This will help determine if:
- The decorator is still blocking (role check)
- The simulation doesn't exist (database issue)
- The template has errors (rendering issue)
- Something else is causing the redirect

---
**Date:** October 20, 2025  
**Status:** Investigating - Fixes applied, awaiting verification  
**Impact:** Medium - Core instructor navigation functionality
