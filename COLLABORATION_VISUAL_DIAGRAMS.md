# 📐 RiddleNet Collaboration System - Visual Architecture Diagrams

**Quick Visual Reference for Understanding the Collaboration System**

---

## 🎨 High-Level Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RIDDLENET PLATFORM                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────┐                    ┌─────────────────────┐    │
│  │   ADMIN PORTAL      │                    │    USER PORTAL      │    │
│  │ ┌─────────────────┐ │                    │ ┌─────────────────┐ │    │
│  │ │ Simulation Edit │ │                    │ │ Dynamic Sim View│ │    │
│  │ │   /edit/70      │ │                    │ │ /dynamic/70     │ │    │
│  │ └────────┬────────┘ │                    │ └────────┬────────┘ │    │
│  │          │          │                    │          │          │    │
│  │  ┌───────▼────────┐ │                    │  ┌───────▼────────┐ │    │
│  │  │ Enable Collab  │ │                    │  │ Join Session   │ │    │
│  │  │ Set Team Size  │ │                    │  │ View Lobby     │ │    │
│  │  │ Manage Teams   │ │                    │  │ Collaborate    │ │    │
│  │  └───────┬────────┘ │                    │  └───────┬────────┘ │    │
│  └──────────┼──────────┘                    └──────────┼──────────┘    │
│             │                                           │                │
│             │                                           │                │
│             └───────────────────┬───────────────────────┘                │
│                                 │                                        │
│                        ┌────────▼─────────┐                             │
│                        │  Flask Backend   │                             │
│                        │                  │                             │
│                        │  ┌────────────┐  │                             │
│                        │  │ Socket.IO  │  │                             │
│                        │  │ WebSocket  │  │                             │
│                        │  └─────┬──────┘  │                             │
│                        │        │         │                             │
│                        │  ┌─────▼──────┐  │                             │
│                        │  │Collaboration│ │                             │
│                        │  │  Service    │ │                             │
│                        │  └─────┬──────┘  │                             │
│                        │        │         │                             │
│                        │  ┌─────▼──────┐  │                             │
│                        │  │  Database  │  │                             │
│                        │  │  (SQLite)  │  │                             │
│                        │  └────────────┘  │                             │
│                        └──────────────────┘                             │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 👥 Session Lifecycle Flow

```
START
  │
  ├─────────────────────────────────────────┐
  │                                         │
  ▼                                         ▼
┌─────────────────┐              ┌─────────────────┐
│  ADMIN CREATES  │              │  USER BROWSES   │
│    SESSION      │              │    LOBBIES      │
└────────┬────────┘              └────────┬────────┘
         │                                │
         │ 1. Enable collaboration        │
         │ 2. Set max team size: 4        │
         │ 3. Choose public/private       │
         │                                │
         ▼                                │
┌─────────────────┐                       │
│  LOBBY CREATED  │◄──────────────────────┘
│                 │    2. User finds lobby
│  ID: abc-123    │    3. Clicks "Join"
│  Size: 0/4      │
└────────┬────────┘
         │
         │ ┌──────────────────────────┐
         │ │ Multiple users can join  │
         ▼ └──────────────────────────┘
┌─────────────────┐
│  ACTIVE SESSION │
│                 │
│  👤 User A      │ ← Session Leader
│  👤 User B      │
│  👤 User C      │
│  👥 3/4 slots   │
└────────┬────────┘
         │
         │ WebSocket connection established
         │ Real-time sync begins
         ▼
┌─────────────────────────────────────────┐
│      COLLABORATION FEATURES ACTIVE       │
├─────────────────────────────────────────┤
│  ✓ Cursor tracking                      │
│  ✓ Device locking                       │
│  ✓ Network state sync                   │
│  ✓ Team chat                            │
│  ✓ Presence indicators                  │
└────────┬────────────────────────────────┘
         │
         │ Users collaborate on network simulation
         │ Changes synced in real-time
         ▼
┌─────────────────┐
│  USER LEAVES    │
└────────┬────────┘
         │
         ├─────────► If last user → Session ends
         │
         └─────────► If others remain → Session continues
                     └─► Leader transferred if needed
```

---

## 🖱️ Cursor Tracking Flow (Detailed)

```
USER A's BROWSER                  SERVER                    USER B's BROWSER
┌─────────────────┐         ┌──────────────┐          ┌─────────────────┐
│                 │         │              │          │                 │
│  Move mouse     │         │              │          │  Waiting for    │
│  at (450, 320)  │         │              │          │  updates...     │
│        │        │         │              │          │                 │
│        ▼        │         │              │          │                 │
│  Throttle check │         │              │          │                 │
│  Last: 0ms      │         │              │          │                 │
│  Now: 50ms ✓    │         │              │          │                 │
│        │        │         │              │          │                 │
│        ▼        │         │              │          │                 │
│  Emit WS Event  │─────────>              │          │                 │
│  'team_cursor_  │         │              │          │                 │
│   update'       │         │              │          │                 │
│                 │         │              │          │                 │
│  Data: {        │         │              │          │                 │
│   position: {   │         │   Receive    │          │                 │
│     x: 450,     │         │   & Validate │          │                 │
│     y: 320      │         │      │       │          │                 │
│   },            │         │      ▼       │          │                 │
│   session_id,   │         │  Get session │          │                 │
│   timestamp     │         │  participants│          │                 │
│  }              │         │      │       │          │                 │
│                 │         │      ▼       │          │                 │
│                 │         │  Broadcast   │          │                 │
│                 │         │  to session  │          │                 │
│                 │         │  room        │          │                 │
│                 │         │      │       │──────────>                 │
│                 │         │      ▼       │          │  Receive WS     │
│                 │         │  Emit 'team_ │          │  'team_cursor_  │
│                 │         │  cursor_     │          │   moved'        │
│                 │         │  moved'      │          │        │        │
│                 │         │              │          │        ▼        │
│                 │         │              │          │  Check user_id  │
│                 │         │              │          │  (not self)     │
│                 │         │              │          │        │        │
│                 │         │              │          │        ▼        │
│                 │         │              │          │ Update cursor   │
│                 │         │              │          │ element         │
│                 │         │              │          │        │        │
│                 │         │              │          │        ▼        │
│                 │         │              │          │ ┌─────────────┐ │
│                 │         │              │          │ │   👆 User A │ │
│                 │         │              │          │ │  (450, 320) │ │
│                 │         │              │          │ └─────────────┘ │
│                 │         │              │          │                 │
└─────────────────┘         └──────────────┘          └─────────────────┘

Time: ~50-100ms total latency
```

---

## 🔒 Device Locking Mechanism

```
UNLOCKED STATE
┌────────────────────────────────────────────────────────────┐
│                         Router-1                            │
│                    ┌──────────────┐                         │
│                    │    [===]     │                         │
│                    │    Router    │                         │
│                    │   10.0.0.1   │                         │
│                    └──────────────┘                         │
│                   No lock indicator                         │
│                   Anyone can click                          │
└────────────────────────────────────────────────────────────┘

          │
          │ User A clicks device
          │
          ▼

LOCK REQUESTED
┌────────────────────────────────────────────────────────────┐
│  User A's Browser                                           │
│  ├─ emit('lock_device', { device_id: 'router-1' })         │
│  └─ Show loading indicator                                 │
└────────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────────┐
│  Server: socket_events.py                                   │
│  ├─ Check if device already locked                         │
│  ├─ If free: Acquire lock                                  │
│  │   └─ device_locks['router-1'] = {                       │
│  │       user_id: 'user-a',                                │
│  │       username: 'Alice',                                │
│  │       locked_at: timestamp                              │
│  │     }                                                    │
│  └─ Broadcast to room                                      │
└────────────────────────────────────────────────────────────┘
          │
          ▼

LOCKED STATE (All Users See This)
┌────────────────────────────────────────────────────────────┐
│                         Router-1                            │
│                    ┌──────────────┐                         │
│  ╔═══════════════╗ │    [===]     │                         │
│  ║ 🔒 Alice      ║ │    Router    │                         │
│  ╚═══════════════╝ │   10.0.0.1   │                         │
│  Lock indicator    └──────────────┘                         │
│  (glowing border)                                           │
└────────────────────────────────────────────────────────────┘

USER A (Lock Owner)                    USER B (Other User)
┌─────────────────────┐             ┌─────────────────────┐
│ Can edit device     │             │ Cannot edit device  │
│ Can configure       │             │ Sees lock warning   │
│ Can unlock          │             │ "Locked by Alice"   │
│                     │             │ Must wait           │
└─────────────────────┘             └─────────────────────┘

          │
          │ User A releases lock OR timeout (30s)
          ▼

UNLOCKED AGAIN
┌────────────────────────────────────────────────────────────┐
│  emit('unlock_device', { device_id: 'router-1' })          │
│  └─ Remove lock indicator                                  │
│  └─ Notify all users: "Router-1 available"                 │
└────────────────────────────────────────────────────────────┘
```

---

## 💬 Team Chat Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     TEAM CHAT SYSTEM                         │
└─────────────────────────────────────────────────────────────┘

USER INTERFACE
┌──────────────────────────────────────────────────────────────┐
│  Team Chat                                           [ - ] [X]│
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ [Alice] 10:30 AM                                    │    │
│  │ Hey team, I'm working on the router config         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ [Bob] 10:31 AM                                      │    │
│  │ Great! I'll handle the switch connections          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ [You] 10:32 AM                                      │    │
│  │ Let me configure the firewall rules                │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  Charlie is typing...                                        │
├──────────────────────────────────────────────────────────────┤
│  [Type message...                                    ] [Send]│
└──────────────────────────────────────────────────────────────┘

DATA FLOW
┌─────────────────┐
│ User types msg  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Click Send or   │
│ Press Enter     │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────┐
│ emit('team_chat_send', {         │
│   message: "Hello team!",        │
│   session_id: "abc-123",         │
│   timestamp: Date.now()          │
│ })                               │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ SERVER                           │
│ ├─ Validate message              │
│ ├─ Rate limit check (10/sec)    │
│ ├─ Save to database              │
│ └─ Broadcast to session room    │
└────────┬─────────────────────────┘
         │
         ├─────────────────────────────┐
         │                             │
         ▼                             ▼
┌─────────────────┐         ┌─────────────────┐
│ YOUR BROWSER    │         │ OTHER BROWSERS  │
│ Show sent ✓     │         │ Receive & show  │
└─────────────────┘         └─────────────────┘

DATABASE PERSISTENCE
┌──────────────────────────────────────┐
│ TeamChatMessage Table                │
├──────────────────────────────────────┤
│ id          | 1                      │
│ session_id  | abc-123                │
│ user_id     | user-a                 │
│ username    | Alice                  │
│ message     | Hello team!            │
│ timestamp   | 2025-10-13 10:30:00    │
│ is_system   | false                  │
└──────────────────────────────────────┘

SPECIAL FEATURES
┌────────────────────────────────────────┐
│ 🔔 Typing Indicators                   │
│ ├─ emit('user_typing_start')          │
│ ├─ Shows "[User] is typing..."        │
│ └─ Auto-hide after 3s                 │
├────────────────────────────────────────┤
│ 📜 Message History                     │
│ ├─ Last 100 messages cached           │
│ ├─ Load on join session               │
│ └─ Scroll to load older               │
├────────────────────────────────────────┤
│ 🚨 System Messages                     │
│ ├─ "Alice joined the session"         │
│ ├─ "Bob left the session"             │
│ └─ "Session will end in 5 minutes"    │
└────────────────────────────────────────┘
```

---

## 🌐 Network State Synchronization

```
INITIAL STATE (User A joins first)
┌──────────────────────────────────────────────────────────┐
│  User A's Topology                                        │
│                                                           │
│   [Router1]────────[Switch1]                             │
│                         │                                │
│                    [Switch2]                             │
│                                                           │
│  Network State: { devices: 3, connections: 2 }           │
└──────────────────────────────────────────────────────────┘

User B joins → Receives full network state
┌──────────────────────────────────────────────────────────┐
│  User B's Topology (synced)                              │
│                                                           │
│   [Router1]────────[Switch1]                             │
│                         │                                │
│                    [Switch2]                             │
│                                                           │
│  Network State: { devices: 3, connections: 2 }           │
└──────────────────────────────────────────────────────────┘

User A adds new device
┌──────────────────────────────────────────────────────────┐
│  User A adds Firewall                                    │
│                                                           │
│   [Router1]────────[Switch1]────[Firewall] ← NEW!       │
│                         │                                │
│                    [Switch2]                             │
│                                                           │
└──────────────────────────────────────────────────────────┘
         │
         │ emit('team_network_update', {
         │   action: 'add_device',
         │   device: { id: 'fw-1', type: 'firewall', ... }
         │ })
         ▼
┌──────────────────────────────────────────────────────────┐
│  SERVER                                                   │
│  ├─ Validate change                                      │
│  ├─ Update shared state                                  │
│  ├─ Version++  (v2 → v3)                                 │
│  └─ Broadcast to all                                     │
└─────────────┬────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│  User B receives update                                  │
│                                                           │
│   [Router1]────────[Switch1]────[Firewall] ✨ Appears!  │
│                         │                                │
│                    [Switch2]                             │
│                                                           │
│  Network State: { devices: 4, connections: 3, v: 3 }    │
└──────────────────────────────────────────────────────────┘

CONFLICT SCENARIO (Simultaneous Edits)
┌─────────────────────────────┐    ┌─────────────────────────────┐
│ User A                      │    │ User B                      │
│ Moves Router1 to (100, 200) │    │ Moves Router1 to (300, 400) │
│ Version: 3 → 4              │    │ Version: 3 → 4              │
└──────────┬──────────────────┘    └──────────┬──────────────────┘
           │                                   │
           └───────────────┬───────────────────┘
                           ▼
                    ┌──────────────┐
                    │   SERVER     │
                    │              │
                    │ Conflict!    │
                    │ Version 3→4  │
                    │ (twice)      │
                    └──────┬───────┘
                           │
                    Resolution Strategy:
                    ├─ LAST WRITE WINS (current)
                    │  └─ User B's update accepted
                    │      Router1 at (300, 400)
                    │
                    OR (future enhancement):
                    └─ MERGE STRATEGY
                       └─ Show conflict UI
                          Allow users to choose
```

---

## 🎭 Participant Presence System

```
PARTICIPANT STATUS STATES
┌───────────────────────────────────────────────────────────┐
│                                                            │
│  🟢 ONLINE    - Active in session, responsive             │
│  🟡 IDLE      - No activity for 2 minutes                 │
│  🔴 OFFLINE   - Disconnected                              │
│  🔵 EDITING   - Currently editing a device                │
│                                                            │
└───────────────────────────────────────────────────────────┘

PARTICIPANTS SIDEBAR
┌────────────────────────────────────────────────────────────┐
│  Team Members                                       [ X ]  │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 🅰️  Alice                              🟢 Online  │   │
│  │     Team Leader                                    │   │
│  │     🔵 Editing: Router-1                           │   │
│  │     Cursor: (450, 320)                             │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 🅱️  Bob                                 🟢 Online  │   │
│  │     💬 Typing...                                   │   │
│  │     Cursor: (120, 580)                             │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 🆄  You (Charlie)                      🟢 Online  │   │
│  │     🔵 Editing: Switch-2                           │   │
│  │     Cursor: (600, 200)                             │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 🅳  Diana                              🟡 Idle     │   │
│  │     Last activity: 3 minutes ago                   │   │
│  │     Cursor: (200, 400)                             │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
├────────────────────────────────────────────────────────────┤
│  💬 Team Chat    📊 Progress    ⚙️ Settings              │
└────────────────────────────────────────────────────────────┘

CURSOR VISUAL INDICATORS
┌────────────────────────────────────────────────────────────┐
│  Network Topology Canvas                                   │
│                                                             │
│                        👆 Alice                            │
│                        (editing)                           │
│    [Router-1]──────────╔══════════╗                       │
│                        ║ LOCKED   ║                       │
│                        ╚══════════╝                       │
│                                                             │
│                👆 Bob                                      │
│               (cursor)                                     │
│                                                             │
│         [Switch-1]                                         │
│                                                             │
│    👆 You                                                  │
│   (editing)                                                │
│   [Switch-2]                                               │
│   ╔═════════════╗                                          │
│   ║ YOU LOCKED  ║                                          │
│   ╚═════════════╝                                          │
│                                                             │
│                                  👆 Diana                  │
│                                 (idle - faded)             │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 Session Recovery Flow

```
NORMAL SESSION
┌────────────────────────────────┐
│  User connected to session     │
│  Collaborating normally        │
└──────────────┬─────────────────┘
               │
               │ Network issue / Browser refresh
               ▼
┌────────────────────────────────┐
│  CONNECTION LOST               │
│  🔌 Disconnected               │
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│  AUTO-RECONNECT                │
│  Attempt 1 of 5...             │
│  ⏳ Waiting 1s                 │
└──────────────┬─────────────────┘
               │
               ├─ Success → Go to REJOIN
               │
               ├─ Fail → Attempt 2 (wait 2s)
               │
               ├─ Fail → Attempt 3 (wait 3s)
               │
               └─ After 5 fails → GIVE UP
                  └─> Show: "Unable to reconnect.
                             Please refresh page."

REJOIN SESSION
┌────────────────────────────────┐
│  Connection restored           │
│  emit('rejoin_team_session')   │
│                                │
│  Send last known state:        │
│  - network_state               │
│  - locked_devices              │
│  - last_message_id             │
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│  SERVER RECONCILIATION         │
│  Compare client vs server      │
│                                │
│  If conflict:                  │
│  └─> Server state wins         │
│       (send full sync)         │
│                                │
│  If devices locked by user:    │
│  └─> Auto-release locks        │
│       (user was disconnected)  │
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│  FULL STATE SYNC               │
│  Client receives:              │
│  - Current network topology    │
│  - Active participants         │
│  - Device locks                │
│  - Last 100 chat messages      │
│  - Session settings            │
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│  SESSION RESTORED ✅           │
│  User rejoined successfully    │
│  Collaborating normally        │
└────────────────────────────────┘
```

---

## 📊 Admin Monitoring View

```
┌───────────────────────────────────────────────────────────────┐
│  Admin Dashboard - Simulation #70 Collaboration Monitor       │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  📊 LIVE STATISTICS                                           │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │ Active Sessions│  │   Total Users  │  │  Messages/min  │ │
│  │       3        │  │       12       │  │      45        │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
│                                                                │
│  🔴 LIVE SESSIONS                                             │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Session #1: "Team Alpha"                        [View]   ││
│  │ ├─ Simulation: Network Security Lab                      ││
│  │ ├─ Participants: Alice, Bob, Charlie, Diana (4/4)        ││
│  │ ├─ Duration: 25:34                                       ││
│  │ ├─ Activity: 🟢 High (15 changes/min)                   ││
│  │ └─ Status: 🟢 Healthy                                    ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Session #2: "Study Group Beta"                  [View]   ││
│  │ ├─ Simulation: Router Configuration                      ││
│  │ ├─ Participants: Eve, Frank (2/4)                        ││
│  │ ├─ Duration: 12:08                                       ││
│  │ ├─ Activity: 🟡 Medium (5 changes/min)                  ││
│  │ └─ Status: 🟢 Healthy                                    ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Session #3: "Solo Practice"                     [View]   ││
│  │ ├─ Simulation: Firewall Rules                            ││
│  │ ├─ Participants: Grace (1/4)                             ││
│  │ ├─ Duration: 45:22                                       ││
│  │ ├─ Activity: 🟢 Active (8 changes/min)                  ││
│  │ └─ Status: ⚠️ Idle warning (no activity 10 min)         ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  [Refresh]  [Export Report]  [End All Sessions]              │
└───────────────────────────────────────────────────────────────┘

DETAILED SESSION VIEW (Click "View" on Session #1)
┌───────────────────────────────────────────────────────────────┐
│  Session Details: Team Alpha                          [ X ]   │
├───────────────────────────────────────────────────────────────┤
│  📍 Session ID: abc-123-def-456                               │
│  🎯 Simulation: Network Security Lab (#70)                    │
│  ⏱️ Started: 10:30 AM  │  Duration: 25:34  │  Status: Active │
│                                                                │
│  👥 PARTICIPANTS (4)                                          │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Alice (Leader)      🟢 Online    Editing: Router-1       ││
│  │ Bob                 🟢 Online    Idle                     ││
│  │ Charlie             🟢 Online    Editing: Switch-2        ││
│  │ Diana               🟡 Idle      Last seen: 3 min ago     ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  🔒 DEVICE LOCKS (2)                                          │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ Router-1     Locked by Alice     Duration: 5:23          ││
│  │ Switch-2     Locked by Charlie   Duration: 2:10          ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  📊 ACTIVITY METRICS                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │ Network Changes│  │  Chat Messages │  │ Cursor Updates │ │
│  │      127       │  │      45        │  │    15,230      │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
│                                                                │
│  💬 RECENT CHAT (Last 10 messages)                            │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ [10:52] Alice: Let's add a firewall here                 ││
│  │ [10:53] Bob: Good idea! I'll configure the rules         ││
│  │ [10:54] Charlie: Working on switch redundancy            ││
│  │ ...                                                       ││
│  └──────────────────────────────────────────────────────────┘│
│                                                                │
│  🎬 ACTIONS                                                    │
│  [Send Message to Team]  [Force Unlock All]  [End Session]   │
└───────────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Reference: Event Names

### Client → Server (Emit)
```
create_team_session       - Create new collaboration session
join_team_session         - Join existing session
leave_team_session        - Leave current session
team_cursor_update        - Update cursor position
team_network_update       - Sync network topology change
lock_device               - Request device lock
unlock_device             - Release device lock
team_chat_send            - Send chat message
user_typing_start         - Start typing indicator
user_typing_stop          - Stop typing indicator
```

### Server → Client (Receive)
```
team_session_created      - Session created successfully
team_session_joined       - Joined session successfully
team_session_left         - Left session
team_member_joined        - New member joined
team_member_left          - Member left session
team_cursor_moved         - Remote cursor position update
team_network_updated      - Network state changed
device_locked             - Device locked by user
device_unlocked           - Device unlocked
device_lock_failed        - Lock request denied
team_chat_message         - New chat message
user_is_typing            - Someone is typing
session_ended_by_admin    - Admin ended session
```

---

**Last Updated:** October 13, 2025  
**For:** RiddleNet Development Team  
**Purpose:** Visual understanding of collaboration architecture
