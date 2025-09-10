"""Instance-specific configuration (PostgreSQL ONLY).

This deployment has been locked to PostgreSQL; SQLite is no longer supported
as a fallback to avoid data divergence between environments.

Required environment variables (defaults in parentheses):
	POSTGRES_HOST        (localhost)
	POSTGRES_PORT        (5432)
	POSTGRES_DB          (riddlenet)
	POSTGRES_USER        (postgres)
	POSTGRES_PASSWORD    (blank) – supply in production
	POSTGRES_SSL_MODE    (optional: e.g. require, disable)

If the URI cannot be built, an exception is raised at import time to fail
fast rather than silently creating a local SQLite file.
"""

import os

pg_host = os.getenv("POSTGRES_HOST", "localhost")
pg_port = os.getenv("POSTGRES_PORT", "5432")
pg_db = os.getenv("POSTGRES_DB", "riddlenet")
pg_user = os.getenv("POSTGRES_USER", "postgres")
pg_password = os.getenv("POSTGRES_PASSWORD", "")
pg_sslmode = os.getenv("POSTGRES_SSL_MODE")  # optional

if not pg_host or not pg_db or not pg_user:
	raise RuntimeError("PostgreSQL configuration incomplete: host/db/user required")

if pg_password:
	auth_segment = f"{pg_user}:{pg_password}"
else:
	auth_segment = pg_user

SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{auth_segment}@{pg_host}:{pg_port}/{pg_db}"
if pg_sslmode:
	SQLALCHEMY_DATABASE_URI += f"?sslmode={pg_sslmode}"

SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_for_development_only_change_in_production')

print(f"[config] Using PostgreSQL database URI: {SQLALCHEMY_DATABASE_URI}")
