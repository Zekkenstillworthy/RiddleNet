# 🔧 SQLAlchemy Reserved Word Fix

## Issue

**Error:**
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

## Root Cause

The `ChallengeScore` model used `metadata` as a column name, which is a reserved attribute in SQLAlchemy's declarative base. SQLAlchemy uses `metadata` internally for table metadata management.

## Solution

Renamed the column from `metadata` to `challenge_metadata` throughout the codebase.

---

## Files Modified

### 1. `user/models/challenge_score.py`

**Before:**
```python
metadata = db.Column(db.JSON, nullable=True)
```

**After:**
```python
challenge_metadata = db.Column(db.JSON, nullable=True)  # Renamed to avoid reserved word
```

**Changes:**
- Column definition renamed
- All references in `record_attempt()` method updated
- `to_dict()` method now returns `challenge_metadata` key

### 2. `DASHBOARD_CHALLENGE_INTEGRATION_COMPLETE.md`

Updated documentation to reflect the column name change.

---

## Database Schema Update

The database column is now:

```sql
challenge_metadata JSON
```

Instead of:

```sql
metadata JSON
```

---

## Migration Impact

✅ **No manual SQL required** - The migration script uses the model's `__table__` attribute, which automatically reflects the corrected column name.

When you run:
```bash
python migrate_challenge_badges.py
```

The table will be created with `challenge_metadata` column automatically.

---

## Code Usage

The API remains the same - the `metadata` parameter in function calls is still used, only the database column name changed:

```python
# Still works the same way
ChallengeScore.save_score(
    user_id=1,
    challenge_type='crimping',
    score=100,
    metadata={'mode': 'rollover', 'time': 45}  # Parameter name unchanged
)

# Internally, it stores to challenge_metadata column
challenge_score.challenge_metadata  # Accesses the renamed column
```

---

## Verification

After restart, the dashboard should load without errors:

1. ✅ Application starts successfully
2. ✅ Dashboard route loads (`/dashboard`)
3. ✅ No SQLAlchemy errors in logs
4. ✅ Challenge scores can be saved
5. ✅ Badges can be awarded

---

## Testing

```bash
# 1. Restart the application
python run.py

# 2. Navigate to dashboard
# http://127.0.0.1:5001/dashboard

# 3. Complete a challenge to test
# http://127.0.0.1:5001/user/crimping-simulation

# 4. Verify no errors in terminal logs
```

---

## Why This Happened

SQLAlchemy reserves several attribute names for internal use:

- `metadata` - Table metadata registry
- `query` - Query property (when using Flask-SQLAlchemy)
- `__tablename__` - Table name specification
- `__table__` - Table object reference

Always avoid these names when defining model columns.

---

## Best Practices

When naming database columns in SQLAlchemy models:

✅ **Good naming:**
- `challenge_metadata`
- `user_metadata`
- `config_data`
- `extra_info`

❌ **Avoid:**
- `metadata` (reserved)
- `query` (reserved in Flask-SQLAlchemy)
- `type` (Python builtin)
- `id` (can conflict, but acceptable for primary keys)

---

**Status:** ✅ **FIXED**  
**Date:** October 9, 2025  
**Impact:** Critical - Application startup failure  
**Resolution Time:** Immediate
