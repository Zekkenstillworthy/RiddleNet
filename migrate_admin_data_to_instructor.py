"""One-time migration script to port historical admin data into the new instructor tables."""

from __future__ import annotations

import os
from typing import Dict, Any

import psycopg2
from psycopg2.extras import DictCursor


DB_PARAMS: Dict[str, Any] = {
	"dbname": os.getenv("RNET_DB_NAME", "riddlenet"),
	"user": os.getenv("RNET_DB_USER", "postgres"),
	"password": os.getenv("RNET_DB_PASSWORD", "admin"),
	"host": os.getenv("RNET_DB_HOST", "localhost"),
	"port": int(os.getenv("RNET_DB_PORT", 5432)),
}


def migrate_admins_to_instructors(cursor: DictCursor) -> None:
	"""Copy rows from the legacy ``admin`` table into ``instructor``."""

	print("\n[1/4] Migrating admin accounts into instructor table…")

	cursor.execute("SELECT to_regclass('public.instructor')")
	if cursor.fetchone()[0] is None:
		raise RuntimeError("instructor table does not exist; run database migrations first.")

	cursor.execute("SELECT to_regclass('public.admin')")
	if cursor.fetchone()[0] is None:
		print("   → admin table not found; skipping account migration.")
		return

	# Ensure the password hash column can store modern hashes.
	cursor.execute(
		"""
		ALTER TABLE instructor
		ALTER COLUMN password_hash TYPE VARCHAR(255)
		"""
	)

	# Remove placeholder instructor rows that clash on username so we can reuse
	# the original admin IDs without violating unique constraints.
	cursor.execute(
		"""
		DELETE FROM instructor i
		 WHERE EXISTS (
			   SELECT 1
				 FROM admin a
				WHERE a.username = i.username
				  AND a.id <> i.id
		 )
		"""
	)

	cursor.execute(
		"""
		INSERT INTO instructor (id, username, password_hash, email, role, created_at, last_login, profile_img)
		SELECT id,
			   username,
			   password_hash,
			   email,
			   COALESCE(NULLIF(role, ''), 'instructor'),
			   created_at,
			   last_login,
			   profile_img
		  FROM admin
		ON CONFLICT (id) DO UPDATE
			  SET username      = EXCLUDED.username,
				  password_hash = EXCLUDED.password_hash,
				  email         = EXCLUDED.email,
				  role          = EXCLUDED.role,
				  created_at    = COALESCE(instructor.created_at, EXCLUDED.created_at),
				  last_login    = EXCLUDED.last_login,
				  profile_img   = EXCLUDED.profile_img
		"""
	)

	cursor.execute(
		"""
		SELECT setval(
			pg_get_serial_sequence('instructor', 'id'),
			(SELECT COALESCE(MAX(id), 1) FROM instructor)
		)
		"""
	)


def migrate_admin_users_to_instructor_users(cursor: DictCursor) -> None:
	"""Copy legacy ``admin_users`` into ``instructor_users`` for continuity."""

	print("[2/4] Migrating admin user accounts into instructor_users…")

	cursor.execute("SELECT to_regclass('public.instructor_users')")
	if cursor.fetchone()[0] is None:
		print("   → instructor_users table is not present; skipping this step.")
		return

	cursor.execute("SELECT to_regclass('public.admin_users')")
	if cursor.fetchone()[0] is None:
		print("   → admin_users table not found; nothing to migrate.")
		return

	# Match password hash storage length.
	cursor.execute(
		"""
		ALTER TABLE instructor_users
		ALTER COLUMN password_hash TYPE VARCHAR(255)
		"""
	)

	cursor.execute(
		"""
		INSERT INTO instructor_users (
			id,
			username,
			password_hash,
			email,
			first_name,
			last_name,
			totp_key,
			profile_img,
			is_instructor,
			user_type,
			status,
			created_at,
			last_active,
			force_password_change,
			notes
		)
		SELECT id,
			   username,
			   password_hash,
			   email,
			   first_name,
			   last_name,
			   totp_key,
			   profile_img,
			   COALESCE(is_instructor, false) OR COALESCE(is_admin, false) AS is_instructor,
			   COALESCE(NULLIF(user_type, ''), 'instructor') AS user_type,
			   COALESCE(NULLIF(status, ''), 'active') AS status,
			   created_at,
			   last_active,
			   COALESCE(force_password_change, false) AS force_password_change,
			   notes
		  FROM admin_users
		ON CONFLICT (id) DO UPDATE
			  SET username              = EXCLUDED.username,
				  password_hash         = EXCLUDED.password_hash,
				  email                 = EXCLUDED.email,
				  first_name            = EXCLUDED.first_name,
				  last_name             = EXCLUDED.last_name,
				  totp_key              = EXCLUDED.totp_key,
				  profile_img           = EXCLUDED.profile_img,
				  is_instructor         = EXCLUDED.is_instructor,
				  user_type             = EXCLUDED.user_type,
				  status                = EXCLUDED.status,
				  created_at            = COALESCE(instructor_users.created_at, EXCLUDED.created_at),
				  last_active           = EXCLUDED.last_active,
				  force_password_change = EXCLUDED.force_password_change,
				  notes                 = EXCLUDED.notes
		"""
	)

	cursor.execute(
		"""
		SELECT setval(
			pg_get_serial_sequence('instructor_users', 'id'),
			(SELECT COALESCE(MAX(id), 1) FROM instructor_users)
		)
		"""
	)


def relink_foreign_keys(cursor: DictCursor) -> None:
	"""Point collaboration tables at the instructor table instead of admin."""

	print("[3/4] Updating foreign-key constraints to reference instructor…")

	cursor.execute("SELECT to_regclass('public.instructor')")
	if cursor.fetchone()[0] is None:
		print("   → instructor table missing; cannot relink foreign keys.")
		return

	cursor.execute("SELECT to_regclass('public.collaboration_settings')")
	if cursor.fetchone()[0] is not None:
		cursor.execute(
			"""
			ALTER TABLE collaboration_settings
			DROP CONSTRAINT IF EXISTS collaboration_settings_created_by_fkey
			"""
		)

		cursor.execute(
			"""
			ALTER TABLE collaboration_settings
			ADD CONSTRAINT collaboration_settings_created_by_fkey
			FOREIGN KEY (created_by) REFERENCES instructor(id)
			"""
		)
	else:
		print("   → collaboration_settings table not found; skipping FK update for it.")

	cursor.execute("SELECT to_regclass('public.team_assignments')")
	if cursor.fetchone()[0] is not None:
		cursor.execute(
			"""
			ALTER TABLE team_assignments
			DROP CONSTRAINT IF EXISTS team_assignments_created_by_fkey
			"""
		)

		cursor.execute(
			"""
			ALTER TABLE team_assignments
			ADD CONSTRAINT team_assignments_created_by_fkey
			FOREIGN KEY (created_by) REFERENCES instructor(id)
			"""
		)
	else:
		print("   → team_assignments table not found; skipping FK update for it.")


def summarize_counts(cursor: DictCursor) -> None:
	"""Print a small summary so the operator can verify row counts."""

	print("[4/4] Summary after migration:")

	cursor.execute("SELECT COUNT(*) FROM admin")
	admin_count = cursor.fetchone()[0]
	cursor.execute("SELECT COUNT(*) FROM instructor")
	instructor_count = cursor.fetchone()[0]

	cursor.execute("SELECT COUNT(*) FROM admin_users")
	admin_users = cursor.fetchone()[0]
	cursor.execute("SELECT COUNT(*) FROM instructor_users")
	instructor_users = cursor.fetchone()[0]

	print(f"  • admin rows migrated:         {admin_count}")
	print(f"  • instructor table row count:  {instructor_count}")
	print(f"  • admin_users migrated:        {admin_users}")
	print(f"  • instructor_users row count:  {instructor_users}")


def run_migration() -> None:
	print("=" * 60)
	print(" MIGRATING LEGACY ADMIN DATA TO INSTRUCTOR TABLES")
	print("=" * 60)

	conn = None
	cursor = None

	try:
		conn = psycopg2.connect(**DB_PARAMS)
		cursor = conn.cursor(cursor_factory=DictCursor)
		print("✅ Connected to database")

		migrate_admins_to_instructors(cursor)
		migrate_admin_users_to_instructor_users(cursor)
		relink_foreign_keys(cursor)
		summarize_counts(cursor)

		conn.commit()
		print("\n🎉 Migration completed successfully!")

	except psycopg2.Error as db_err:
		if conn:
			conn.rollback()
		print(f"❌ Database error: {db_err}")
		raise
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()
		print("🔌 Database connection closed")


if __name__ == "__main__":
	run_migration()
