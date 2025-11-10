"""Split session interface to isolate instructor and user sessions.

This prevents *session poisoning* where logging in as a user overwrites
the instructor login (and vice‑versa) because both share the same Flask
session cookie. We maintain two independent signed cookies:

  - instructor_session  -> used for all /instructor* HTTP requests
  - user_session   -> used for all other routes

WebSocket ( /socket.io ) requests don't provide the original path.
During the WebSocket handshake we try to intelligently pick the right
session by inspecting both cookies and preferring the one whose stored
``auth_namespace`` matches ``instructor`` if present.

SECURITY NOTES:
 - Cookies are still signed with the single app SECRET_KEY.
 - Session contents are isolated per namespace; code must not assume a
   key written in one namespace exists in the other.
 - When switching contexts (visiting an /instructor URL after a student URL)
   each namespace preserves its own authentication state.

If you ever need to *explicitly* log out in both spaces, call the
logout endpoint in each namespace (or clear both cookies manually).
"""

import os
from typing import Optional
from flask.sessions import SecureCookieSessionInterface
from itsdangerous import URLSafeTimedSerializer, BadSignature
from flask import request


INSTRUCTOR_COOKIE = "instructor_session"
USER_COOKIE = "user_session"


class SplitSessionInterface(SecureCookieSessionInterface):
    """Session interface that multiplexes two secure cookies.

    Open / Save logic decides which cookie to use based on the request
    path or, for WebSocket handshakes, on stored namespace.
    """

    @staticmethod
    def _expected_namespace(cookie_name: Optional[str]) -> str:
        """Return the namespace that should live inside a given cookie."""
        return "instructor" if cookie_name == INSTRUCTOR_COOKIE else "user"

    def get_signing_serializer(self, app):
        """Override to add better error handling and fallback"""
        secret_key = app.secret_key
        
        if not secret_key:
            # Generate a temporary key for this session
            temp_key = os.urandom(32)
            app.logger.error("[KEY] No SECRET_KEY configured! Using temporary key - sessions will not persist!")
            secret_key = temp_key
        
        if isinstance(secret_key, str) and len(secret_key) < 16:
            app.logger.warning(f"[KEY] SECRET_KEY is too short ({len(secret_key)} chars). Minimum 16 chars recommended.")
        
        try:
            serializer = URLSafeTimedSerializer(secret_key)
            app.logger.debug("[KEY] Session serializer created successfully")
            return serializer
        except Exception as e:
            app.logger.error(f"[KEY] Failed to create session serializer: {str(e)}")
            return None

    def _select_cookie_for_request(self):
        path = (request.path or "").lower()
        
        # INSTRUCTOR PATHS: /instructor* AND /admin* both use instructor_session
        if path.startswith("/instructor") or path.startswith("/admin"):
            return INSTRUCTOR_COOKIE
        
        if path.startswith("/socket.io"):
            # WebSocket handshake: we don't know original page path; we will
            # decide later in open_session by inspecting both cookies.
            return None
        
        return USER_COOKIE

    # ---------- OPEN SESSION ----------
    def open_session(self, app, request):  # type: ignore[override]
        serializer = self.get_signing_serializer(app)
        if not serializer:
            return self.session_class()

        chosen = self._select_cookie_for_request()

        # Normal HTTP request that maps cleanly to a cookie name
        if chosen:
            raw = request.cookies.get(chosen)
            if not raw:
                return self.session_class()
            try:
                max_age = int(app.permanent_session_lifetime.total_seconds())
                data = serializer.loads(raw, max_age=max_age)
                expected_ns = self._expected_namespace(chosen)
                actual_ns = data.get("auth_namespace")

                if actual_ns and actual_ns != expected_ns:
                    app.logger.warning(
                        "[COOKIE] SplitSession: Detected namespace mismatch (%s) in %s cookie; purging cross-namespace data",
                        actual_ns,
                        chosen,
                    )
                    # Drop identity related keys to prevent session poisoning
                    data = {"auth_namespace": expected_ns}
                else:
                    if not actual_ns:
                        data["auth_namespace"] = expected_ns
                return self.session_class(data)
            except BadSignature:
                return self.session_class()
            except Exception as e:
                print(f"[COOKIE] SplitSession: Error loading session: {str(e)}")
                return self.session_class()

        # WebSocket (or ambiguous) – inspect both cookies and pick the most appropriate
        # First, try to determine context from Referer header (for Socket.IO handshakes)
        referer = request.headers.get('Referer', '').lower()
        
        # If Referer indicates instructor context, prefer instructor cookie
        prefer_instructor = '/instructor' in referer
        
        sessions = []
        max_age = int(app.permanent_session_lifetime.total_seconds())
        for name in (INSTRUCTOR_COOKIE, USER_COOKIE):
            raw = request.cookies.get(name)
            if not raw:
                continue
            try:
                data = serializer.loads(raw, max_age=max_age)
                expected_ns = self._expected_namespace(name)
                actual_ns = data.get("auth_namespace")

                if actual_ns and actual_ns != expected_ns:
                    app.logger.warning(
                        "[COOKIE] SplitSession: Skipping %s cookie due to namespace mismatch (%s)",
                        name,
                        actual_ns,
                    )
                    continue

                if not actual_ns:
                    data["auth_namespace"] = expected_ns

                sessions.append((name, data))
            except BadSignature:
                continue
            except Exception as e:
                app.logger.warning(f"[COOKIE] Error loading {name}: {str(e)}")
                continue

        # If referer indicates instructor context, prefer instructor session
        if prefer_instructor:
            for name, data in sessions:
                if name == INSTRUCTOR_COOKIE or data.get("auth_namespace") == "instructor":
                    return self.session_class(data)
        
        # Otherwise prefer user session (for non-instructor contexts)
        for name, data in sessions:
            if name == USER_COOKIE or data.get("auth_namespace") != "instructor":
                return self.session_class(data)
        
        # Fallback: return first available session
        if sessions:
            return self.session_class(sessions[0][1])
        
        return self.session_class()

    # ---------- SAVE SESSION ----------
    def save_session(self, app, session, response):  # type: ignore[override]
        cookie_name = self._select_cookie_for_request()
        # For WebSocket handshake or ambiguous path, derive from namespace
        if cookie_name is None:
            ns = session.get("auth_namespace")
            cookie_name = INSTRUCTOR_COOKIE if ns == "instructor" else USER_COOKIE

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

        session_payload = dict(session)
        expected_ns = self._expected_namespace(cookie_name)
        actual_ns = session_payload.get("auth_namespace")

        if actual_ns and actual_ns != expected_ns:
            app.logger.warning(
                "[COOKIE] SplitSession: Preventing cross-namespace write (%s into %s); sanitising payload",
                actual_ns,
                cookie_name,
            )
            # Preserve only non-auth data and enforce expected namespace
            session_payload = {
                key: value
                for key, value in session_payload.items()
                if key in {"_flashes", "_permanent"}
            }
            session_payload["auth_namespace"] = expected_ns
        else:
            session_payload.setdefault("auth_namespace", expected_ns)

        signed = serializer.dumps(session_payload)

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

__all__ = ["SplitSessionInterface", "INSTRUCTOR_COOKIE", "USER_COOKIE"]
