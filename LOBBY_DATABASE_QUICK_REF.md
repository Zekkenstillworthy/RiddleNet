# Lobby Database - Quick Reference

## 🚀 Quick Start

### 1. Create Tables
```bash
python create_lobby_tables.py
```

### 2. Restart Application
```bash
python run.py
```

## 📊 5 New Tables

1. **collaboration_lobby** - Main lobby data
2. **lobby_participant** - Participants & cursor positions  
3. **lobby_chat_message** - Chat history
4. **lobby_device_lock** - Device locks
5. **lobby_cli_history** - CLI command history

## ✨ Key Features

### Automatic Saving
- ✅ Lobby created → Saved to DB
- ✅ User joins → Participant saved
- ✅ Chat message → Saved to DB
- ✅ Device locked → Lock saved
- ✅ CLI command → Command logged

### Server Restart Recovery
- ✅ Server restarts → Active lobbies reload
- ✅ Participants reconnect → Continue where left off
- ✅ Chat history preserved
- ✅ Network state maintained

### Auto Cleanup
- Every 5 minutes: Inactive users removed
- After 24 hours: Old lobbies deleted

## 🔍 Quick Queries

### Python
```python
from user.models.collaboration_lobby import CollaborationLobby

# Get active lobbies
lobbies = CollaborationLobby.query.filter_by(is_active=True).all()

# Get lobby with participants
lobby = CollaborationLobby.query.get('ABC12345')
participants = lobby.participants.filter_by(is_active=True).all()
```

### SQL
```sql
-- Active lobbies
SELECT * FROM collaboration_lobby WHERE is_active = TRUE;

-- Lobby participants
SELECT * FROM lobby_participant WHERE lobby_id = 'ABC12345' AND is_active = TRUE;

-- Recent chat
SELECT * FROM lobby_chat_message WHERE lobby_id = 'ABC12345' ORDER BY timestamp DESC LIMIT 20;
```

## 🛠️ Troubleshooting

### Tables not created?
```bash
python create_lobby_tables.py
```

### Lobbies not saving?
Check logs:
```bash
tail -f logs/application.log | grep "lobby"
```

### Manual cleanup?
```python
from services.lobby_persistence import lobby_persistence
lobby_persistence.cleanup_old_lobbies(hours=1)
```

## 📝 Data Flow

```
User creates lobby
    ↓
TroubleshootingLobby created (in-memory)
    ↓
_save_lobby_to_db() called
    ↓
CollaborationLobby saved (PostgreSQL)
    ↓
Lobby survives restarts ✅
```

## 🎯 Testing Checklist

- [ ] Create lobby → Check database
- [ ] Join lobby → Check participants table
- [ ] Send chat → Check messages table
- [ ] Lock device → Check locks table
- [ ] Run CLI → Check history table
- [ ] Restart server → Lobbies still active
- [ ] Wait 30 min → Inactive users removed
- [ ] Wait 24 hrs → Old lobbies deleted

## 🔧 Configuration

In `troubleshooting_lobbies.py`:
```python
self._persistence_enabled = True  # Enable/disable DB saving
```

Cleanup intervals:
```python
Timer(300, cleanup_task)  # 5 minutes
cleanup_old_lobbies(hours=24)  # 24 hours
```

## ✅ Success Indicators

Look for in logs:
- `✅ Saved lobby ABC12345 to database`
- `✅ Loaded 3 active lobbies from database`
- `🧹 Cleaned up 5 old lobbies`

## 📊 Sample Database Schema

```
collaboration_lobby (id, name, scenario_type, creator_id, is_active, ...)
├── lobby_participant (id, lobby_id, user_id, username, cursor_x, cursor_y, ...)
├── lobby_chat_message (id, lobby_id, user_id, message, timestamp, ...)
├── lobby_device_lock (id, lobby_id, device_id, locked_by, auto_unlock_at, ...)
└── lobby_cli_history (id, lobby_id, device_id, command, output, ...)
```

## 🎉 Done!

Lobbies now persist to PostgreSQL and survive server restarts!
