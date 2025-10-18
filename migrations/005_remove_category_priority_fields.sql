-- =====================================================
-- Migration: Remove Category and Priority Fields
-- Description: Remove category and priority columns from class_announcements and class_assignments tables
-- Date: October 18, 2025
-- =====================================================

-- Remove priority column from class_announcements
ALTER TABLE class_announcements DROP COLUMN IF EXISTS priority;

-- Remove category and priority columns from class_assignments  
ALTER TABLE class_assignments DROP COLUMN IF EXISTS category;
ALTER TABLE class_assignments DROP COLUMN IF EXISTS priority;

-- Note: simulations.category is intentionally kept as it's used for simulation categorization
-- Note: quiz.category, score.category, question.category are kept for their respective features
-- Note: notification_history.priority is kept for notification system
