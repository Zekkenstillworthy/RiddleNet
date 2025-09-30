-- Migration to add profile_img column to admin table
-- Run this migration to enable admin profile pictures

ALTER TABLE admin ADD COLUMN profile_img VARCHAR(150);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_admin_profile_img ON admin(profile_img);