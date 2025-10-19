-- SQL Migration Script: Fix Foreign Keys from admin_users to instructor_users
-- This updates all foreign key constraints in the PostgreSQL database

-- Note: This script assumes you're using PostgreSQL
-- Run this script directly in your PostgreSQL database

-- 1. Fix class_content table
ALTER TABLE class_content DROP CONSTRAINT IF EXISTS class_content_created_by_fkey;
ALTER TABLE class_content ADD CONSTRAINT class_content_created_by_fkey 
    FOREIGN KEY (created_by) REFERENCES instructor_users(id);

-- 2. Fix class_assignments table
ALTER TABLE class_assignments DROP CONSTRAINT IF EXISTS class_assignments_created_by_fkey;
ALTER TABLE class_assignments ADD CONSTRAINT class_assignments_created_by_fkey 
    FOREIGN KEY (created_by) REFERENCES instructor_users(id);

-- 3. Fix class_materials table
ALTER TABLE class_materials DROP CONSTRAINT IF EXISTS class_materials_created_by_fkey;
ALTER TABLE class_materials ADD CONSTRAINT class_materials_created_by_fkey 
    FOREIGN KEY (created_by) REFERENCES instructor_users(id);

-- 4. Fix class_simulations table
ALTER TABLE class_simulations DROP CONSTRAINT IF EXISTS class_simulations_created_by_fkey;
ALTER TABLE class_simulations ADD CONSTRAINT class_simulations_created_by_fkey 
    FOREIGN KEY (created_by) REFERENCES instructor_users(id);

-- 5. Fix modules table
ALTER TABLE modules DROP CONSTRAINT IF EXISTS modules_created_by_fkey;
ALTER TABLE modules ADD CONSTRAINT modules_created_by_fkey 
    FOREIGN KEY (created_by) REFERENCES instructor_users(id);

-- 6. Fix instructor_scores table
ALTER TABLE instructor_scores DROP CONSTRAINT IF EXISTS instructor_scores_user_id_fkey;
ALTER TABLE instructor_scores ADD CONSTRAINT instructor_scores_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES instructor_users(id);

-- 7. Fix simulations table  
ALTER TABLE simulations DROP CONSTRAINT IF EXISTS simulations_created_by_fkey;
ALTER TABLE simulations ADD CONSTRAINT simulations_created_by_fkey 
    FOREIGN KEY (created_by) REFERENCES instructor_users(id);

-- Verification query - should return no results if all fixed
SELECT 
    tc.table_name, 
    kcu.column_name,
    ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND ccu.table_name = 'admin_users';
