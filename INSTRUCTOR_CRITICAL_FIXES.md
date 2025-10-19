# Critical Instructor Refactoring Fixes

## Date: October 19, 2025

## Issues Fixed

### 1. ❌ Missing `instructor_required` Decorator
**Error:** `cannot import name 'instructor_required' from 'utils.permission_decorators'`

**Location:** `instructor/routes/collaboration_api.py`

**Fix Applied:**
- Added `instructor_required` function to `utils/permission_decorators.py`
- Mirrors `teacher_required` but uses the decorator naming convention expected by collaboration_api

**Status:** ✅ FIXED

---

### 2. ❌ Foreign Key References to Deleted Table
**Error:** `Foreign key associated with column 'instructor_scores.user_id' could not find table 'admin_users'`

**Affected Files:**
- `instructor/models/class_content.py` (4 references)
- `instructor/models/module.py` (1 reference)
- `instructor/models/score.py` (1 reference + docstring)
- `instructor/models/simulation.py` (1 reference)

**Fix Applied:**
```python
# Changed all instances of:
db.ForeignKey('admin_users.id')
# To:
db.ForeignKey('instructor_users.id')
```

**Bulk Fix Command:**
```powershell
# Applied to all model files
(Get-Content 'file.py') -replace "'admin_users\.id'", "'instructor_users.id'" | Set-Content 'file.py'
```

**Status:** ✅ FIXED in code

---

### 3. ⚠️ Database Foreign Key Constraints Need Update
**Issue:** Database still has old foreign key constraints pointing to `admin_users` table

**Migration Script Created:** `fix_instructor_foreign_keys.py`

**Tables Requiring Migration:**
1. `class_content` - `created_by` column
2. `class_assignments` - `created_by` column
3. `class_materials` - `created_by` column  
4. `class_simulations` - `created_by` column
5. `modules` - `created_by` column
6. `instructor_scores` - `user_id` column
7. `simulations` - `created_by` column

**To Apply Database Fix:**
```bash
python fix_instructor_foreign_keys.py
```

**Status:** ⚠️ READY TO RUN (requires database update)

---

### 4. ⚠️ Template Folder Warning
**Warning:** `Template folder does not exist: templates\admin`

**Root Cause:** Some blueprints still configured to look in `templates\admin` folder

**Files to Check:**
- Blueprint template folder configurations in route files
- Any manual template path overrides

**Status:** ⚠️ NEEDS INVESTIGATION

---

### 5. ❌ Authentication Issues
**Issue:** `❌ Admin path fallback: No admin found for ID 1`

**Root Cause:** User loader trying to authenticate as instructor but user exists in `user` table, not `instructor_users` table

**Possible Solutions:**
1. Create corresponding instructor record in `instructor_users` table
2. Update user loader logic to handle dual user/instructor accounts
3. Ensure proper session isolation between user and instructor contexts

**Status:** ⚠️ NEEDS INVESTIGATION

---

## Summary of Changes

### Code Files Modified: 5
1. `utils/permission_decorators.py` - Added `instructor_required` decorator
2. `instructor/models/class_content.py` - Fixed 4 foreign key references
3. `instructor/models/module.py` - Fixed 1 foreign key reference
4. `instructor/models/score.py` - Fixed 1 foreign key reference + docstring
5. `instructor/models/simulation.py` - Fixed 1 foreign key reference

### Total Foreign Key References Fixed: 8

### Verification Commands:
```powershell
# Verify no more admin_users references in models
Get-ChildItem -Path 'instructor\models' -Recurse -Filter *.py | Select-String -Pattern 'admin_users'
# Result: No matches found ✅

# Check for import errors
python -c "from utils.permission_decorators import instructor_required; print('✅ Import successful')"
```

---

## Next Steps

### Immediate Actions Required:

1. **Run Database Migration**
   ```bash
   python fix_instructor_foreign_keys.py
   ```

2. **Restart Application**
   ```bash
   python run.py
   ```

3. **Test Instructor Login**
   - Navigate to `/instructor/login`
   - Verify authentication works
   - Check that no foreign key errors appear in logs

4. **Fix Template Folder Warnings**
   - Search for blueprint template folder configurations
   - Update any `templates/admin` references to `templates/instructor`

5. **Resolve Authentication Issues**
   - Investigate user loader logic
   - Ensure ID 1 has proper instructor permissions
   - Consider creating test instructor account

### Testing Checklist:

- [ ] Application starts without foreign key errors
- [ ] Instructor login page loads
- [ ] Authentication system works
- [ ] No template folder warnings
- [ ] Collaboration API imports successfully
- [ ] All blueprints register correctly
- [ ] WebSocket connections work
- [ ] No `admin_users` references in logs

---

## Rollback Instructions

If issues occur, you can rollback the changes:

```powershell
# Revert model files (if needed)
git checkout instructor/models/class_content.py
git checkout instructor/models/module.py
git checkout instructor/models/score.py
git checkout instructor/models/simulation.py
git checkout utils/permission_decorators.py
```

For database rollback, you would need to manually recreate the `admin_users` table and restore foreign keys (not recommended).

---

## Related Documentation

- Main refactoring summary: `ADMIN_TO_INSTRUCTOR_REFACTORING_COMPLETE.md`
- Database schema: `riddlenetv1.sql`
- Application entry point: `run.py`

---

**Created:** October 19, 2025  
**Last Updated:** October 19, 2025  
**Status:** Code fixes applied, database migration ready
