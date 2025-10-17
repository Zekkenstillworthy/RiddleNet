# 🎨 Lobby Database Architecture - Visual Guide

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│            (Dynamic Simulation / Admin Panel)            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│            troubleshooting_lobbies.py                    │
│              (LobbyManager - In-Memory)                  │
│  • Create/Join/Leave Lobby                              │
│  • Real-time Collaboration                              │
│  • Auto-save to Database ⚡                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│           lobby_persistence.py                           │
│           (Persistence Service Layer)                    │
│  • save_lobby()                                         │
│  • save_participant()                                   │
│  • save_chat_message()                                  │
│  • load_lobby()                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL Database                         │
│                                                          │
│  ┌────────────────────────────────────────────┐        │
│  │  collaboration_lobby                       │        │
│  │  • id, name, scenario_type                 │        │
│  │  • creator_id, is_active                   │        │
│  │  • network_state (JSON)                    │        │
│  └────────────┬───────────────────────────────┘        │
│               │                                          │
│               ├─► lobby_participant                     │
│               │   • user_id, cursor_x, cursor_y        │
│               │                                          │
│               ├─► lobby_chat_message                    │
│               │   • message, timestamp                  │
│               │                                          │
│               ├─► lobby_device_lock                     │
│               │   • device_id, locked_by               │
│               │                                          │
│               └─► lobby_cli_history                     │
│                   • command, output                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

### Creating a Lobby

```
User clicks "Create Lobby"
        │
        ▼
┌──────────────────────┐
│  LobbyManager        │
│  create_lobby()      │◄─── Generate 8-char ID
└──────┬───────────────┘
       │
       ├─► Create TroubleshootingLobby (in-memory)
       │   • Store in self.lobbies{}
       │   • Add creator to participants
       │
       └─► _save_lobby_to_db()
           │
           ▼
   ┌──────────────────────┐
   │  LobbyPersistence    │
   │  save_lobby()        │
   └──────┬───────────────┘
          │
          ▼
   INSERT INTO collaboration_lobby ✅
   INSERT INTO lobby_participant ✅
   INSERT INTO lobby_chat_message ✅ (welcome)
```

### Joining a Lobby

```
User enters lobby code
        │
        ▼
┌──────────────────────┐
│  LobbyManager        │
│  join_lobby()        │
└──────┬───────────────┘
       │
       ├─► Validate lobby exists
       ├─► Check not full
       ├─► Check not locked
       │
       ├─► lobby.add_participant()
       │   • Add to participants{}
       │   • Generate user color
       │
       └─► Save to Database
           │
           ▼
   INSERT INTO lobby_participant ✅
   INSERT INTO lobby_chat_message ✅ (join message)
```

### Real-time Collaboration

```
User moves cursor
        │
        ▼
┌──────────────────────┐
│  Socket.IO Event     │
│  'cursor_position'   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  LobbyManager        │
│  update_participant_ │
│  cursor()            │
└──────┬───────────────┘
       │
       ├─► Update in-memory position
       │
       └─► Periodic save to DB (every 5 min cleanup)
           │
           ▼
   UPDATE lobby_participant 
   SET cursor_x=?, cursor_y=?, last_activity=NOW()
```

---

## 🔄 Server Restart Recovery

```
Server Starts
     │
     ▼
┌──────────────────────────────┐
│  LobbyManager.__init__()     │
│  _load_active_lobbies_from_  │
│  db()                        │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Query PostgreSQL            │
│  SELECT * FROM               │
│  collaboration_lobby         │
│  WHERE is_active = TRUE      │
└──────┬───────────────────────┘
       │
       ▼
For each lobby:
   ├─► Load participants
   ├─► Load chat history
   ├─► Load device locks
   ├─► Load CLI history
   │
   ▼
Create TroubleshootingLobby objects
   ├─► Add to self.lobbies{}
   └─► Rebuild user_lobby_map{}
       │
       ▼
┌──────────────────────────────┐
│  Lobbies Active! ✅          │
│  Users can reconnect         │
└──────────────────────────────┘
```

---

## 📊 Database Relationships

```
                    ┌─────────────────┐
                    │      user       │
                    │  (existing)     │
                    └────┬─────┬──────┘
                         │     │
              ┌──────────┘     └──────────┐
              │                           │
              │ creator_id                │ user_id
              │                           │
              ▼                           ▼
    ┌──────────────────┐        ┌────────────────┐
    │ collaboration_   │◄───────│ lobby_         │
    │ lobby            │1      *│ participant    │
    │                  │        │                │
    │ • id (PK)        │        │ • user_id (FK) │
    │ • name           │        │ • cursor_x/y   │
    │ • scenario_type  │        │ • role         │
    │ • creator_id (FK)│        └────────────────┘
    │ • network_state  │
    └────┬─────┬───┬───┘
         │     │   │
         │1    │1  │1
         │     │   │
         │*    │*  │*
    ┌────▼────┐│  │┌───────────────┐
    │ lobby_  ││  ││ lobby_device_ │
    │ chat_   ││  ││ lock          │
    │ message ││  │└───────────────┘
    └─────────┘│  │
               │  │┌───────────────┐
               │  ││ lobby_cli_    │
               │  ││ history       │
               │  │└───────────────┘
               ▼  ▼
         (Referenced tables)
```

---

## 🔄 Lifecycle of a Lobby

```
1️⃣  CREATE
    ┌────────────────┐
    │ User creates   │
    │ lobby          │
    └───────┬────────┘
            │
            ▼
    ┌────────────────┐
    │ In-Memory      │
    │ + PostgreSQL   │
    └───────┬────────┘
            │
            ▼
    ┌────────────────┐
    │ is_active=TRUE │
    └────────────────┘

2️⃣  ACTIVE
    ┌────────────────┐
    │ Users join     │
    │ Collaborate    │
    └───────┬────────┘
            │
            ├─► Chat messages
            ├─► Lock devices
            ├─► Run CLI commands
            └─► Update topology
                │
                ▼
    ┌────────────────┐
    │ All saved to DB│
    └────────────────┘

3️⃣  CLEANUP
    ┌────────────────┐
    │ After 30 min   │
    │ inactivity     │
    └───────┬────────┘
            │
            ▼
    ┌────────────────┐
    │ Mark inactive  │
    │ participants   │
    └───────┬────────┘
            │
            ▼
    ┌────────────────┐
    │ If empty:      │
    │ is_active=FALSE│
    └────────────────┘

4️⃣  ARCHIVE
    ┌────────────────┐
    │ After 24 hours │
    │ inactive       │
    └───────┬────────┘
            │
            ▼
    ┌────────────────┐
    │ DELETE FROM    │
    │ all tables     │
    └───────┬────────┘
            │
            ▼
    ┌────────────────┐
    │ Lobby removed  │
    └────────────────┘
```

---

## 📊 Table Size Growth Estimation

```
Active Lobby (1 hour session, 4 participants):

collaboration_lobby:        1 row    (~1 KB with JSON)
lobby_participant:          4 rows   (~400 bytes)
lobby_chat_message:        50 rows   (~5 KB)
lobby_device_lock:          3 rows   (~300 bytes)
lobby_cli_history:        100 rows   (~10 KB)
                          ────────
                          ~16.7 KB per lobby

Daily (100 lobbies):
  • Storage: ~1.67 MB/day
  • Monthly: ~50 MB/month
  • Yearly: ~600 MB/year

With cleanup (24 hours):
  • Max storage: ~1.67 MB + active lobbies
  • Very manageable! ✅
```

---

## 🎯 Performance Optimization

```
┌────────────────────────────────────────┐
│         Optimization Strategy          │
├────────────────────────────────────────┤
│                                        │
│  1️⃣  In-Memory First                  │
│     • Fast read/write                 │
│     • Real-time performance           │
│                                        │
│  2️⃣  Async DB Saves                   │
│     • Non-blocking writes             │
│     • Batch operations                │
│                                        │
│  3️⃣  Periodic Cleanup                 │
│     • Remove old data                 │
│     • Prevent bloat                   │
│                                        │
│  4️⃣  Indexed Queries                  │
│     • Fast lookups                    │
│     • Efficient joins                 │
│                                        │
└────────────────────────────────────────┘
```

---

## 🔍 Monitoring Dashboard (Future)

```
┌────────────────────────────────────────┐
│      Lobby Analytics Dashboard         │
├────────────────────────────────────────┤
│                                        │
│  📊 Active Lobbies:     12             │
│  👥 Total Participants: 47             │
│  💬 Messages Today:     1,234          │
│  🔧 CLI Commands:       3,456          │
│                                        │
│  📈 Peak Hours:                        │
│     ████████ 2-4 PM                   │
│     ██████ 6-8 PM                     │
│                                        │
│  🏆 Most Active Users:                 │
│     1. Alice    - 15 lobbies          │
│     2. Bob      - 12 lobbies          │
│     3. Charlie  - 10 lobbies          │
│                                        │
│  🎮 Popular Scenarios:                 │
│     • Network Troubleshooting  35%    │
│     • Device Configuration     28%    │
│     • Passive Discovery       22%    │
│     • Hard Scenarios          15%    │
│                                        │
└────────────────────────────────────────┘
```

---

## 🚀 Scalability Path

```
Current: Single Server + PostgreSQL
   ↓
   ├─► Add Redis Cache (future)
   │   • Cache active lobbies
   │   • Reduce DB load
   │
   ├─► Read Replicas (future)
   │   • Distribute reads
   │   • Faster queries
   │
   ├─► Horizontal Scaling (future)
   │   • Multiple app servers
   │   • Load balancer
   │
   └─► Message Queue (future)
       • Async operations
       • Better reliability
```

---

## ✅ Implementation Checklist

- [x] Create 5 database tables
- [x] Add persistence service layer
- [x] Integrate with lobby manager
- [x] Automatic save on create/join/leave
- [x] Server restart recovery
- [x] Auto cleanup (30 min / 24 hours)
- [x] Complete documentation
- [ ] Admin dashboard for lobbies
- [ ] Analytics and reports
- [ ] Export/archive functionality

---

**The lobby database system is now fully implemented and production-ready! 🎉**
