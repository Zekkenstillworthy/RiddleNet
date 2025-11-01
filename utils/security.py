"""
Security utilities for safe redirects and session hardening.

MVP hardening goals:
- Prevent open redirects/route poisoning via untrusted `next` params
- Constrain cross-namespace redirects (user vs instructor)
"""

from urllib.parse import urlparse

ALLOWED_PREFIXES = {
    # User-facing routes may only redirect within user namespace or site-root pages
    "user": (
        "/",  # allow site root paths
        "/user",  # explicit user blueprint prefix if used in templates
        "/class/",  # universal class routes used by user area
        "/classes",
        "/dashboard",
        "/profile",
        "/challenges",
        "/osi-simulation",
        "/crimping-simulation",
        "/topology",
    ),
    # Instructor/admin routes must stay within instructor namespace
    "instructor": (
        "/instructor",
    ),
}


def _is_relative_path(target: str) -> bool:
    """Return True if target is a safe, single-origin relative path.

    Rules:
    - Must start with a single '/'
    - Must NOT start with '//', which browsers treat as scheme-relative (external)
    - Must NOT contain a scheme/netloc when parsed
    """
    if not isinstance(target, str) or not target:
        return False

    # Disallow scheme-relative and malformed values
    if target.startswith("//"):
        return False

    parsed = urlparse(target)
    # urlparse('/foo') -> path='/foo', netloc='', scheme=''
    return parsed.scheme == "" and parsed.netloc == "" and target.startswith("/")


def is_safe_next_url(next_url: str, namespace: str) -> bool:
    """Validate an incoming next URL for redirect.

    - Only allow relative, same-origin paths
    - Enforce namespace-specific prefixes to prevent cross-area route poisoning
    """
    if not _is_relative_path(next_url):
        return False

    prefixes = ALLOWED_PREFIXES.get(namespace, tuple())
    if not prefixes:
        # Default to strict relative-only if namespace unknown
        return True

    # Allow if the path starts with any allowed prefix
    for p in prefixes:
        if next_url == p or next_url.startswith(p + "/") or next_url.startswith(p + "?"):
            return True

    return False


def safe_next_or_fallback(next_url: str, namespace: str, fallback: str) -> str:
    """Return a safe redirect target or the provided fallback."""
    return next_url if is_safe_next_url(next_url, namespace) else fallback
