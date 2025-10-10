# Priority Field Removal - Database Migration Guide

## Overview
This document provides instructions for removing the `priority` column from the `class_assignments` table as part of the assignment simplification initiative.

**Date**: October 9, 2025  
**Affected Table**: `class_assignments`  
**Affected Column**: `priority`  
**Status**: Ready for execution

---

## Changes Summary

The `priority` field has been removed from:
- ✅ **Model**: `admin/models/class_content.py` - `ClassAssignment.priority` column definition
- ✅ **Model**: `admin/models/class_content.py` - `ClassAssignment.to_dict()` method
- ✅ **UI Templates**: `class_content_manager.html` - Create/Edit/View forms and modals
- ✅ **UI Templates**: `module_builder.html` - Assignment creation form
- ✅ **JavaScript**: All assignment-related functions in both templates
- ✅ **JavaScript**: `enhanced-tooltip-system.js` - Tooltip configuration
- ✅ **Backend API**: `class_content_controller.py` - Create and update endpoints

---

## Database Migration

### Prerequisites
1. **Backup your database** before running any migration commands
2. Verify you have database administrator privileges
3. Ensure the application is stopped or in maintenance mode during migration

### Migration SQL Command

```sql
-- Drop the priority column from class_assignments table
ALTER TABLE class_assignments DROP COLUMN priority;
```

### Alternative: Safe Migration with Backup

```sql
-- Step 1: Create a backup of the table (optional but recommended)
CREATE TABLE class_assignments_backup AS SELECT * FROM class_assignments;

-- Step 2: Verify the backup
SELECT COUNT(*) FROM class_assignments;
SELECT COUNT(*) FROM class_assignments_backup;
-- These counts should match

-- Step 3: Drop the priority column
ALTER TABLE class_assignments DROP COLUMN priority;

-- Step 4: Verify the column is removed
DESCRIBE class_assignments;
-- or
PRAGMA table_info(class_assignments);  -- for SQLite
-- or
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'class_assignments';  -- for MySQL/PostgreSQL
```

---

## Verification Steps

### 1. Verify Database Schema
After running the migration, confirm the `priority` column no longer exists:

**SQLite**:
```sql
PRAGMA table_info(class_assignments);
```

**MySQL**:
```sql
DESCRIBE class_assignments;
```

**PostgreSQL**:
```sql
\d class_assignments
```

### 2. Verify Application Functionality
1. Start the application
2. Navigate to the Class Content Manager
3. Test creating a new assignment (should work without priority field)
4. Test editing an existing assignment (should work without priority field)
5. Test viewing assignment details (should not show priority)
6. Verify no errors in the application logs

### 3. Test Data Integrity
```sql
-- Check that existing assignments are still accessible
SELECT id, title, assignment_type, category, due_date 
FROM class_assignments 
LIMIT 10;

-- Verify count hasn't changed
SELECT COUNT(*) FROM class_assignments;
```

---

## Rollback Procedure

If you need to rollback this change:

### 1. Restore Database Column
```sql
-- Add the priority column back
ALTER TABLE class_assignments 
ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';

-- Update existing records to have a default value
UPDATE class_assignments 
SET priority = 'medium' 
WHERE priority IS NULL;
```

### 2. Restore Code Changes
```bash
# Use git to revert the changes
git log --oneline  # Find the commit before priority removal
git revert <commit-hash>
```

---

## Database-Specific Commands

### SQLite
```sql
-- SQLite doesn't support DROP COLUMN directly in older versions
-- You may need to recreate the table

-- Step 1: Create new table without priority column
CREATE TABLE class_assignments_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    due_date DATETIME,
    points INTEGER DEFAULT 100,
    assignment_type VARCHAR(50) DEFAULT 'assignment',
    category VARCHAR(50) DEFAULT 'general',
    is_published BOOLEAN DEFAULT 0,
    allow_file_uploads BOOLEAN DEFAULT 1,
    allowed_file_types VARCHAR(500) DEFAULT 'pdf,doc,docx,txt,jpg,png,zip',
    max_file_size_mb INTEGER DEFAULT 10,
    max_files INTEGER DEFAULT 5,
    allow_text_submission BOOLEAN DEFAULT 1,
    allow_late_submissions BOOLEAN DEFAULT 1,
    late_penalty_per_day REAL DEFAULT 10.0,
    allow_resubmission BOOLEAN DEFAULT 1,
    module_id INTEGER,
    sort_order INTEGER DEFAULT 0,
    question_group_id INTEGER,
    simulation_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (question_group_id) REFERENCES question_groups(id),
    FOREIGN KEY (simulation_id) REFERENCES simulations(id),
    FOREIGN KEY (created_by) REFERENCES admin_users(id)
);

-- Step 2: Copy data (excluding priority column)
INSERT INTO class_assignments_new 
SELECT id, class_id, title, description, instructions, due_date, points, 
       assignment_type, category, is_published, allow_file_uploads, 
       allowed_file_types, max_file_size_mb, max_files, allow_text_submission, 
       allow_late_submissions, late_penalty_per_day, allow_resubmission, 
       module_id, sort_order, question_group_id, simulation_id, 
       created_at, updated_at, created_by
FROM class_assignments;

-- Step 3: Drop old table
DROP TABLE class_assignments;

-- Step 4: Rename new table
ALTER TABLE class_assignments_new RENAME TO class_assignments;

-- Step 5: Recreate indexes (if any)
-- Add any index creation statements here
```

### MySQL
```sql
-- MySQL supports DROP COLUMN directly
ALTER TABLE class_assignments DROP COLUMN priority;
```

### PostgreSQL
```sql
-- PostgreSQL supports DROP COLUMN directly
ALTER TABLE class_assignments DROP COLUMN priority;
```

---

## Impact Assessment

### Low Risk Areas
- ✅ **Assignment Creation**: Forms no longer include priority field
- ✅ **Assignment Editing**: Priority field removed from edit modals
- ✅ **Assignment Display**: Priority not shown in UI
- ✅ **API Endpoints**: Priority parameter removed from create/update

### Areas to Monitor
- ⚠️ **Existing Assignments**: All existing assignments will retain their other data
- ⚠️ **Reports/Analytics**: Any reports that referenced priority will need updates
- ⚠️ **Third-party Integrations**: Check if any external systems used the priority field

---

## Post-Migration Checklist

- [ ] Database backup created before migration
- [ ] Migration SQL executed successfully
- [ ] Database schema verified (priority column removed)
- [ ] Application restarted
- [ ] Create assignment form tested
- [ ] Edit assignment form tested
- [ ] View assignment details tested
- [ ] No console errors in browser
- [ ] No errors in application logs
- [ ] Assignment data integrity verified
- [ ] User acceptance testing completed
- [ ] Backup table (if created) can be dropped after verification period

---

## Cleanup (Optional)

After confirming the migration was successful and the system has been stable for a reasonable period (e.g., 1 week):

```sql
-- Drop the backup table if you created one
DROP TABLE IF EXISTS class_assignments_backup;
```

---

## Support

If you encounter any issues during migration:

1. **Check application logs** for error messages
2. **Review database logs** for SQL errors
3. **Verify database schema** matches expected structure
4. **Test with a single assignment** before rolling out to all users
5. **Keep backup available** for at least 1 week after migration

---

## Notes

- The `priority` field was a VARCHAR(20) column with default value 'medium'
- Possible values were: 'low', 'medium', 'high'
- This field was used for visual organization but not for any critical business logic
- Removing it simplifies the assignment model and reduces UI complexity

---

**Migration Status**: Ready for Execution  
**Estimated Downtime**: < 5 minutes  
**Risk Level**: Low (non-critical field removal)  
**Reversible**: Yes (see Rollback Procedure)
