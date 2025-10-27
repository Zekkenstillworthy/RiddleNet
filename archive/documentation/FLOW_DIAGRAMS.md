# Concurrent Login Prevention - Flow Diagrams

## 1. Login Flow with Session Management

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER/INSTRUCTOR LOGIN                        │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ User enters  │
    │ credentials  │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Validate    │
    │  password    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────────────────┐
    │ Check for active session │
    │ check_existing_session() │
    └──────┬───────────────────┘
           │
           ├──── YES ───┐
           │            ▼
           │     ┌──────────────────────┐
           │     │ Terminate old        │
           │     │ session in database  │
           │     └──────┬───────────────┘
           │            │
           │            ▼
           │     ┌──────────────────────┐
           │     │ Send WebSocket       │
           │     │ notification to      │
           │     │ old device           │
           │     └──────┬───────────────┘
           │            │
           ▼            ▼
    ┌──────────────────────────────┐
    │ Create new session           │
    │ - Generate session token     │
    │ - Store in database          │
    │ - Set expiry (24 hours)      │
    └──────┬───────────────────────┘
           │
           ▼
    ┌──────────────────────────┐
    │ Store in Flask session:  │
    │ - user_id                │
    │ - auth_namespace         │
    │ - session_token          │
    └──────┬───────────────────┘
           │
           ▼
    ┌──────────────┐
    │ Flask-Login  │
    │ login_user() │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  Redirect to │
    │  Dashboard   │
    └──────────────┘
```

## 2. Request Validation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EVERY REQUEST VALIDATION                          │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ User makes   │
    │ request      │
    └──────┬───────┘
           │
           ▼
    ┌──────────────────────┐
    │ before_request()     │
    │ handler triggered    │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ Is static file or    │
    │ login/logout route?  │
    └──────┬───────────────┘
           │
           ├──── YES ──────► SKIP VALIDATION
           │
           NO
           │
           ▼
    ┌──────────────────────┐
    │ Is user              │
    │ authenticated?       │
    └──────┬───────────────┘
           │
           ├──── NO ───────► ALLOW REQUEST
           │
           YES
           │
           ▼
    ┌──────────────────────────┐
    │ Get session_token from   │
    │ Flask session            │
    └──────┬───────────────────┘
           │
           ▼
    ┌──────────────────────────┐
    │ Look up session in DB    │
    │ by token                 │
    └──────┬───────────────────┘
           │
           ├──── NOT FOUND ──┐
           │                 │
           ▼                 │
    ┌──────────────┐         │
    │ Session      │         │
    │ exists?      │         │
    └──────┬───────┘         │
           │                 │
           YES               │
           │                 │
           ▼                 │
    ┌──────────────────────┐ │
    │ Is session active    │ │
    │ and not expired?     │ │
    └──────┬───────────────┘ │
           │                 │
           ├──── NO ────────►│
           │                 │
           YES               │
           │                 │
           ▼                 │
    ┌──────────────────────┐ │
    │ User ID matches?     │ │
    └──────┬───────────────┘ │
           │                 │
           ├──── NO ────────►│
           │                 │
           YES               │
           │                 │
           ▼                 │
    ┌──────────────────────┐ │
    │ Update last_activity │ │
    └──────┬───────────────┘ │
           │                 │
           ▼                 │
    ┌──────────────┐         │
    │ ALLOW        │         │
    │ REQUEST      │         │
    └──────────────┘         │
                             │
                             ▼
                    ┌─────────────────┐
                    │ Clear session   │
                    │ logout_user()   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Redirect to     │
                    │ login page      │
                    └─────────────────┘
```

## 3. Concurrent Login Scenario

```
┌─────────────────────────────────────────────────────────────────────┐
│              CONCURRENT LOGIN - WHAT HAPPENS                         │
└─────────────────────────────────────────────────────────────────────┘

TIME   DEVICE A (Chrome)              DEVICE B (Firefox)
─────  ─────────────────────          ──────────────────────

09:00  Gilbert logs in
       └─► Session A created
       └─► session_token: abc123...
       └─► Dashboard loads
       └─► Browsing content...
                                       
09:15                                  Gilbert logs in
                                       ├─► Check: Session A active!
                                       ├─► Terminate Session A
                                       │   └─► is_active = False
                                       │   └─► WebSocket notification
                                       └─► Session B created
                                           └─► session_token: xyz789...
                                           └─► Dashboard loads

09:16  Clicks on "Settings"
       ├─► before_request validates
       ├─► Look up Session A
       ├─► Session A: is_active = False
       └─► VALIDATION FAILS
           ├─► Clear Flask session
           ├─► logout_user()
           └─► Redirect to /user/login
               └─► Flash: "Your session has been terminated.
                           Another device may have logged in."

09:17  Sees login page
       └─► Must login again to continue

                                       Still logged in
                                       └─► Browsing normally...
```

## 4. Database Schema

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE TABLES                              │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌───────────────────────────┐
│   user_sessions      │         │  instructor_sessions      │
├──────────────────────┤         ├───────────────────────────┤
│ id (PK)              │         │ id (PK)                   │
│ user_id (FK)     ────┼────┐    │ instructor_id (FK)    ────┼────┐
│ session_token        │    │    │ session_token             │    │
│ ip_address           │    │    │ ip_address                │    │
│ user_agent           │    │    │ user_agent                │    │
│ created_at           │    │    │ created_at                │    │
│ last_activity        │    │    │ last_activity             │    │
│ expires_at           │    │    │ expires_at                │    │
│ is_active            │    │    │ is_active                 │    │
└──────────────────────┘    │    └───────────────────────────┘    │
                            │                                     │
                            ▼                                     ▼
                    ┌───────────────┐                   ┌──────────────┐
                    │   user        │                   │ instructor   │
                    ├───────────────┤                   ├──────────────┤
                    │ id (PK)       │                   │ id (PK)      │
                    │ username      │                   │ username     │
                    │ email         │                   │ email        │
                    │ ...           │                   │ ...          │
                    └───────────────┘                   └──────────────┘
```

## 5. Session Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SESSION LIFECYCLE                               │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   CREATED    │  ← Login successful
    │              │    - session_token generated
    │ is_active=1  │    - expires_at = now + 24h
    └──────┬───────┘
           │
           │  ┌───────────────────┐
           ├──┤ User makes request│
           │  └───────────────────┘
           │           │
           │           ▼
           │  ┌───────────────────┐
           │  │ Update            │
           │  │ last_activity     │
           │  └───────────────────┘
           │           │
           │           └─────────────┐
           │                         │
           ▼                         │
    ┌──────────────┐                 │
    │   ACTIVE     │◄────────────────┘
    │              │  Request validation loop
    │ is_active=1  │  - Validates on each request
    │ expires_at   │  - Updates last_activity
    └──────┬───────┘
           │
           │  Triggers:
           │  ├─► New login (same user)
           │  ├─► User logout
           │  ├─► Session expires (24h)
           │  └─► Manual termination
           │
           ▼
    ┌──────────────┐
    │  TERMINATED  │
    │              │
    │ is_active=0  │  ← Can't be reused
    └──────┬───────┘    Validation fails
           │
           │  Optional: cleanup job
           │
           ▼
    ┌──────────────┐
    │   DELETED    │  ← cleanup_expired_sessions()
    │              │    Removes old records
    └──────────────┘
```

## 6. User Experience Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER EXPERIENCE                               │
└─────────────────────────────────────────────────────────────────────┘

SCENARIO: Gilbert logs in from home, then from office

┌─────────────────────────────────────────────────────────────────────┐
│ HOME COMPUTER                                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  09:00 AM - Login                                                   │
│  ┌────────────────────────────────────────┐                        │
│  │ ✓ Login successful                     │                        │
│  │ ✓ Welcome to RiddleNet!                │                        │
│  └────────────────────────────────────────┘                        │
│                                                                      │
│  09:00-09:30 - Working on assignments                              │
│  [Dashboard] [Assignments] [Progress] [Logout]                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ OFFICE COMPUTER                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  09:30 AM - Login                                                   │
│  ┌────────────────────────────────────────┐                        │
│  │ ℹ️ You had an active session           │                        │
│  │   from another device.                 │                        │
│  │ ✓ Login successful                     │                        │
│  │ ✓ Welcome to RiddleNet!                │                        │
│  └────────────────────────────────────────┘                        │
│                                                                      │
│  09:30+ - Working normally                                         │
│  [Dashboard] [Assignments] [Progress] [Logout]                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ HOME COMPUTER (Continued)                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  09:31 AM - Clicks on "Assignments"                                │
│  ┌────────────────────────────────────────┐                        │
│  │ ⚠️ Session Terminated                   │                        │
│  │                                         │                        │
│  │ Your session has been terminated        │                        │
│  │ because you logged in from another      │                        │
│  │ device.                                 │                        │
│  │                                         │                        │
│  │ Please log in again to continue.        │                        │
│  └────────────────────────────────────────┘                        │
│                                                                      │
│  [Login Page]                                                       │
│  Email: ________________                                            │
│  Password: _____________                                            │
│  [Login]                                                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 7. Security Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                                 │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │   USER REQUEST      │
                    └──────────┬──────────┘
                               │
                ┌──────────────▼──────────────┐
                │  LAYER 1: Flask-Login       │
                │  ✓ User authenticated?      │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │  LAYER 2: Auth Namespace    │
                │  ✓ Correct namespace?       │
                │    (user/instructor)        │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │  LAYER 3: Session Token     │
                │  ✓ Token exists?            │
                │  ✓ Token valid?             │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │  LAYER 4: Session Status    │
                │  ✓ Session active?          │
                │  ✓ Not expired?             │
                └──────────────┬──────────────┘
                               │
                ┌──────────────▼──────────────┐
                │  LAYER 5: User Match        │
                │  ✓ User ID matches?         │
                │  ✓ Instance type correct?   │
                └──────────────┬──────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   ALLOW REQUEST     │
                    └─────────────────────┘
                    
    If ANY layer fails ──► Log out ──► Redirect to login
```

## 8. Code Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CODE STRUCTURE                                  │
└─────────────────────────────────────────────────────────────────────┘

application.py
└─► before_request handler
    └─► validate_session_before_request()
        ├─► Checks every request
        └─► Calls utils/session_guard.py

utils/session_guard.py
├─► validate_user_session()
│   ├─► Retrieves session_token
│   ├─► Looks up in database
│   └─► Validates session
│
├─► check_existing_session()
│   └─► Called before login
│
└─► terminate_existing_sessions()
    └─► Terminates old sessions

user/models/user_session.py
instructor/models/instructor_session.py
├─► create_session()
├─► get_active_session()
├─► get_session_by_token()
├─► terminate_user_sessions()
├─► update_activity()
└─► cleanup_expired_sessions()

user/views.py (login)
instructor/controllers/auth_controller.py (login)
├─► 1. Validate credentials
├─► 2. Check existing sessions
├─► 3. Terminate old sessions
├─► 4. Create new session
├─► 5. Store session_token
└─► 6. login_user()

user/views.py (logout)
instructor/controllers/auth_controller.py (logout)
├─► 1. Get session_token
├─► 2. Terminate session in DB
├─► 3. Clear Flask session
└─► 4. logout_user()
```

---

**Legend:**
- ┌─┐ │ ├ └ ─ = Box/tree characters
- ► = Flow direction
- ✓ = Success check
- ⚠️ = Warning
- ℹ️ = Information
- ❌ = Error/failure
