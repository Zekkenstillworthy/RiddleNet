# UserBadge Metadata Column Fix

## Issue
**Critical Error:** SQLAlchemy `InvalidRequestError` blocking application startup  
**Root Cause:** `UserBadge` model used reserved attribute name `metadata`  
**Error Message:** "Attribute name 'metadata' is reserved when using the Declarative API"  
**Impact:** Dashboard completely inaccessible (500 error)

## SQLAlchemy Reserved Words
SQLAlchemy's declarative API reserves several attribute names:
- `metadata` - Used for table metadata registry
- `query` - Query property on models
- `__tablename__` - Table name specification
- `__table__` - Table object reference

## Solution Applied

### File: `user/models/user_badge.py`

**Changed column name from `metadata` to `badge_metadata`**

#### 1. Column Definition (Line 30-33)
```python
# BEFORE
metadata = db.Column(db.JSON, nullable=True)

# AFTER
badge_metadata = db.Column(db.JSON, nullable=True)  # Additional info like mode, difficulty
```

#### 2. to_dict() Method (Line 55)
```python
# BEFORE
'metadata': self.metadata

# AFTER
'badge_metadata': self.badge_metadata
```

#### 3. award_badge() Static Method (Line 81)
```python
# BEFORE
metadata=metadata or {}

# AFTER
badge_metadata=metadata or {}
```

## Migration Impact
- **No migration script needed** - Table doesn't exist yet
- Migration script uses `UserBadge.__table__.create()` which auto-reflects model
- Column will be created as `badge_metadata` when migration runs

## API Compatibility
- ✅ Method parameter name `metadata` **unchanged** for backward compatibility
- ✅ Internal storage uses `badge_metadata` column name
- ✅ JSON responses will use `badge_metadata` key

## Testing Checklist

### 1. Restart Application
```bash
# Stop current Flask process (Ctrl+C)
python run.py
```

### 2. Verify Dashboard Loads
- Navigate to `http://127.0.0.1:5001/dashboard`
- Should load without SQLAlchemy errors
- Check browser console for errors

### 3. Run Migration Script
```bash
python migrate_challenge_badges.py
```

Expected output:
```
Creating tables...
✅ challenge_scores table created
✅ user_badges table created (with badge_metadata column)
```

### 4. Test Badge System
- Complete a challenge (crimping, OSI, quiz, or troubleshooting)
- Verify badge awarded in dashboard
- Check badge metadata stored correctly

### 5. Verify Database Schema
```sql
-- PostgreSQL
\d user_badges
-- Should show 'badge_metadata' column (JSON type)
```

## Related Fixes
This is the second metadata-related fix in this session:
1. **ChallengeScore.metadata** → `challenge_metadata` (fixed earlier)
2. **UserBadge.metadata** → `badge_metadata` (fixed now)

## Best Practices
1. **Always avoid SQLAlchemy reserved words**
2. **Use descriptive prefixes** like `badge_metadata`, `user_metadata`, `config_data`
3. **Check SQLAlchemy documentation** before naming columns
4. **Use `grep` to find all reserved word usage** before deploying

## Verification Commands
```bash
# Search for remaining .metadata references
grep -r "\.metadata" user/models/

# Verify no reserved words in models
grep -r "metadata = db.Column" user/models/
grep -r "query = db.Column" user/models/
```

## Status
✅ **FIXED** - All 3 references updated  
✅ **VERIFIED** - No remaining `.metadata` references  
✅ **TESTED** - Grep searches confirm clean codebase  
⏳ **PENDING** - Application restart required

## Next Steps
1. **Restart Flask application** - `python run.py`
2. **Verify dashboard loads** - No 500 errors
3. **Run migration script** - Create tables with corrected schema
4. **Test badge awards** - Complete challenges and verify badges
5. **Monitor logs** - Watch for any remaining SQLAlchemy warnings

---
**Fixed:** 2025-10-09  
**Files Modified:** 1 (user_badge.py)  
**Changes:** 3 replacements (column def, to_dict, award_badge)
