-- Migration: Rename Admin to Instructor
-- This script renames the admin table, sequences, and all related references to instructor
-- Created: 2025-10-19

BEGIN;

-- Step 1: Rename the main admin table to instructor
ALTER TABLE IF EXISTS admin RENAME TO instructor;

-- Step 2: Rename the sequence
ALTER SEQUENCE IF EXISTS admin_id_seq RENAME TO instructor_id_seq;

-- Step 3: Rename password reset tokens table
ALTER TABLE IF EXISTS admin_password_reset_tokens RENAME TO instructor_password_reset_tokens;

-- Step 4: Rename admin_users table to instructor_users (if it exists)
ALTER TABLE IF EXISTS admin_users RENAME TO instructor_users;

-- Step 5: Update the sequence for instructor_users
ALTER SEQUENCE IF EXISTS admin_users_id_seq RENAME TO instructor_users_id_seq;

-- Step 6: Update role column values (change 'admin' to 'instructor' in role field)
UPDATE instructor SET role = 'instructor' WHERE role = 'admin';

-- Step 7: Update foreign key references in instructor_password_reset_tokens
-- Rename the admin_id column to instructor_id
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'instructor_password_reset_tokens' 
        AND column_name = 'admin_id'
    ) THEN
        ALTER TABLE instructor_password_reset_tokens 
        RENAME COLUMN admin_id TO instructor_id;
    END IF;
END $$;

-- Step 8: Check for any other tables that reference admin and update them
-- Activity logs might reference admin users
DO $$
BEGIN
    -- Check if there's a user_type or similar column that needs updating
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'activity_logs' 
        AND column_name = 'related_entity_type'
    ) THEN
        UPDATE activity_logs 
        SET related_entity_type = 'instructor' 
        WHERE related_entity_type = 'admin';
    END IF;
END $$;

-- Step 9: Update any enum types or check constraints
-- If there are any enum types with 'admin', update them
DO $$
BEGIN
    -- Update user_type columns in various tables
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE column_name = 'user_type'
    ) THEN
        UPDATE instructor_users SET user_type = 'instructor' WHERE user_type = 'admin';
    END IF;
END $$;

-- Step 10: Update foreign key constraint names (if they exist)
DO $$
DECLARE
    constraint_name TEXT;
BEGIN
    -- Find and rename foreign key constraints
    FOR constraint_name IN 
        SELECT conname 
        FROM pg_constraint 
        WHERE conname LIKE '%admin%'
    LOOP
        EXECUTE format('ALTER TABLE %I RENAME CONSTRAINT %I TO %I',
            (SELECT conrelid::regclass FROM pg_constraint WHERE conname = constraint_name),
            constraint_name,
            replace(constraint_name, 'admin', 'instructor')
        );
    END LOOP;
END $$;

-- Verify the changes
SELECT 'Migration completed successfully. Tables renamed:' as status;
SELECT tablename FROM pg_tables WHERE tablename LIKE '%instructor%' ORDER BY tablename;

COMMIT;

-- Rollback instructions (run these if you need to revert):
/*
BEGIN;
ALTER TABLE IF EXISTS instructor RENAME TO admin;
ALTER SEQUENCE IF EXISTS instructor_id_seq RENAME TO admin_id_seq;
ALTER TABLE IF EXISTS instructor_password_reset_tokens RENAME TO admin_password_reset_tokens;
ALTER TABLE IF EXISTS instructor_users RENAME TO admin_users;
ALTER SEQUENCE IF EXISTS instructor_users_id_seq RENAME TO admin_users_id_seq;
ALTER TABLE instructor_password_reset_tokens RENAME COLUMN instructor_id TO admin_id;
UPDATE admin SET role = 'admin' WHERE role = 'instructor';
UPDATE activity_logs SET related_entity_type = 'admin' WHERE related_entity_type = 'instructor';
UPDATE admin_users SET user_type = 'admin' WHERE user_type = 'instructor';
COMMIT;
*/
