# Security hardening notes

Date: 2025-10-30

This update addresses two issues observed during login flows:

- Route poisoning / open redirect via `next` parameter
- Session poisoning / session fixation around cross-namespace logins

Key changes

- Introduced `utils/security.py` with `is_safe_next_url` and `safe_next_or_fallback` to validate `next` redirects.
  - Disallows scheme-relative targets like `//evil.com`.
  - Enforces namespace-specific prefixes (user vs instructor) to block cross-area redirects.
- Hardened login handlers:
  - `instructor/controllers/auth_controller.py@login`: clears session at POST start; uses `safe_next_or_fallback(namespace='instructor')`.
  - `user/views.py@login`: clears session at POST start; sanitizes `next` for both GET (display) and POST (redirect) with `namespace='user'`.

Manual verification

- Visiting `/login?next=/instructor/class-content-selector?class_id=7` and logging in as a user now ignores `next` and lands on the user dashboard.
- Instructor login only honors `next` paths under `/instructor`.
- Attempts like `?next=//attacker.com` are ignored for both roles.

Recommended config (if not already set)

- `SESSION_COOKIE_SAMESITE = 'Lax'`
- `SESSION_COOKIE_SECURE = True` (when using HTTPS)
- `REMEMBER_COOKIE_SAMESITE = 'Lax'`
- `REMEMBER_COOKIE_SECURE = True`
