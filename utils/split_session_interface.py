"""Split session interface to isolate admin and user sessions.

This prevents *session poisoning* where logging in as a user overwrites
the admin login (and vice‑versa) because both share the same Flask
session cookie. We maintain two independent signed cookies:

  - admin_session  -> used for all /admin* HTTP requests
  - user_session   -> used for all other routes

WebSocket ( /socket.io ) requests don't provide the original path.
During the WebSocket handshake we try to intelligently pick the right
session by inspecting both cookies and preferring the one whose stored
``auth_namespace`` matches ``admin`` if present.

SECURITY NOTES:
 - Cookies are still signed with the single app SECRET_KEY.
 - Session contents are isolated per namespace; code must not assume a
   key written in one namespace exists in the other.
 - When switching contexts (visiting an /admin URL after a student URL)
   each namespace preserves its own authentication state.

If you ever need to *explicitly* log out in both spaces, call the
logout endpoint in each namespace (or clear both cookies manually).
"""

import os
import logging
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer, BadSignature
from flask import request


ADMIN_COOKIE = "admin_session"
USER_COOKIE = "user_session"


class SplitSessionInterface(SecureCookieSessionInterface):
    """Session interface that multiplexes two secure cookies.

    Open / Save logic decides which cookie to use based on the request
    path or, for WebSocket handshakes, on stored namespace.
    """

    def get_signing_serializer(self, app):
        """Override to add better error handling and fallback"""
        secret_key = app.secret_key
        
        if not secret_key:
            # Generate a temporary key for this session
            temp_key = os.urandom(32)
            app.logger.error("🔑 No SECRET_KEY configured! Using temporary key - sessions will not persist!")
            secret_key = temp_key
        
        if isinstance(secret_key, str) and len(secret_key) < 16:
            app.logger.warning(f"🔑 SECRET_KEY is too short ({len(secret_key)} chars). Minimum 16 chars recommended.")
        
        try:
            serializer = URLSafeTimedSerializer(secret_key)
            app.logger.debug("🔑 Session serializer created successfully")
            return serializer
        except Exception as e:
            app.logger.error(f"🔑 Failed to create session serializer: {str(e)}")
            return None

    def _select_cookie_for_request(self):
        path = (request.path or "").lower()
        print(f"🍪 SplitSession: _select_cookie_for_request called for path: {path}")
        if path.startswith("/admin"):
            print(f"🍪 SplitSession: Admin path detected, returning ADMIN_COOKIE ({ADMIN_COOKIE})")
            return ADMIN_COOKIE
        if path.startswith("/socket.io"):
            print(f"🍪 SplitSession: Socket.io path detected, returning None for later decision")
            # WebSocket handshake: we don't know original page path; we will
            # decide later in open_session by inspecting both cookies.
            return None
        print(f"🍪 SplitSession: Non-admin path, returning USER_COOKIE ({USER_COOKIE})")
        return USER_COOKIE

    # ---------- OPEN SESSION ----------
    def open_session(self, app, request):  # type: ignore[override]
        serializer = self.get_signing_serializer(app)
        if not serializer:
            print(f"🍪 SplitSession: No serializer available for path: {request.path}")
            return self.session_class()

        chosen = self._select_cookie_for_request()
        print(f"🍪 SplitSession: Chosen cookie: {chosen}")

        # Normal HTTP request that maps cleanly to a cookie name
        if chosen:
            raw = request.cookies.get(chosen)
            print(f"🍪 SplitSession: Raw cookie value for {chosen}: {raw[:50] if raw else 'None'}...")
            if not raw:
                print(f"🍪 SplitSession: No cookie found for {chosen}, returning empty session")
                return self.session_class()
            try:
                max_age = int(app.permanent_session_lifetime.total_seconds())
                data = serializer.loads(raw, max_age=max_age)
                print(f"🍪 SplitSession: Successfully loaded session data, keys: {list(data.keys())}")
                return self.session_class(data)
            except BadSignature:
                print(f"🍪 SplitSession: Bad signature for {chosen}")
                return self.session_class()
            except Exception as e:
                print(f"🍪 SplitSession: Error loading session: {str(e)}")
                return self.session_class()

        # WebSocket (or ambiguous) – inspect both cookies and pick the most appropriate
        # First, try to determine context from Referer header (for Socket.IO handshakes)
        referer = request.headers.get('Referer', '').lower()
        print(f"🍪 SplitSession: WebSocket/ambiguous path, Referer: {referer}")
        
        # If Referer indicates admin context, prefer admin cookie
        prefer_admin = '/admin' in referer
        print(f"🍪 SplitSession: Prefer admin based on Referer: {prefer_admin}")
        
        sessions = []
        max_age = int(app.permanent_session_lifetime.total_seconds())
        for name in (ADMIN_COOKIE, USER_COOKIE):
            raw = request.cookies.get(name)
            if not raw:
                continue
            try:
                data = serializer.loads(raw, max_age=max_age)
                sessions.append((name, data))
                print(f"🍪 SplitSession: Loaded {name} with namespace: {data.get('auth_namespace')}")
            except BadSignature:
                print(f"🍪 SplitSession: Bad signature for {name}")
                continue
            except Exception as e:
                app.logger.warning(f"🍪 Error loading {name}: {str(e)}")
                continue

        # If referer indicates admin context, prefer admin session
        if prefer_admin:
            for name, data in sessions:
                if name == ADMIN_COOKIE or data.get("auth_namespace") == "admin":
                    print(f"🍪 SplitSession: Returning admin session based on Referer")
                    return self.session_class(data)
        
        # Otherwise prefer user session (for non-admin contexts)
        for name, data in sessions:
            if name == USER_COOKIE or data.get("auth_namespace") != "admin":
                print(f"🍪 SplitSession: Returning user session (default)")
                return self.session_class(data)
        
        # Fallback: return first available session
        if sessions:
            print(f"🍪 SplitSession: Fallback - returning first available session")
            return self.session_class(sessions[0][1])
        
        print(f"🍪 SplitSession: No valid sessions found, returning empty")
        return self.session_class()

    # ---------- SAVE SESSION ----------
    def save_session(self, app, session, response):  # type: ignore[override]
        cookie_name = self._select_cookie_for_request()
        # For WebSocket handshake or ambiguous path, derive from namespace
        if cookie_name is None:
            ns = session.get("auth_namespace")
            cookie_name = ADMIN_COOKIE if ns == "admin" else USER_COOKIE

        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        secure = self.get_cookie_secure(app)
        httponly = app.config.get("SESSION_COOKIE_HTTPONLY", True)
        samesite = self.get_cookie_samesite(app)

        # If session is empty, delete ONLY the relevant cookie
        if not session:
            response.delete_cookie(
                cookie_name,
                domain=domain,
                path=path,
                secure=secure,
                httponly=httponly,
                samesite=samesite,
            )
            return

        serializer = self.get_signing_serializer(app)
        if not serializer:
            return
        signed = serializer.dumps(dict(session))

        response.set_cookie(
            cookie_name,
            signed,
            max_age=self.get_expiration_time(app, session),
            expires=self.get_expiration_time(app, session),
            domain=domain,
            path=path,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )

__all__ = ["SplitSessionInterface", "ADMIN_COOKIE", "USER_COOKIE"]
