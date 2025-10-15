# Collaboration Lobby Database Implementation

## 📋 Overview

This implementation adds **PostgreSQL persistence** to the collaborative lobby system, ensuring that lobbies are saved to the database and can survive server restarts.

## 🗄️ Database Tables

### 1. **collaboration_lobby**
Main table for lobby/session information.

| Column | Type | Description |
|--------|------|-------------|
| id | String(8) | Primary key - 8-character lobby code |
| name | String(200) | Lobby display name |
| scenario_type | String(50) | Difficulty: 'easy', 'medium', 'hard' |
| scenario_id | String(100) | Specific scenario identifier |
| max_participants | Integer | Maximum number of participants (default: 6) |
| class_id | Integer | Optional - restrict to specific class |
| creator_id | Integer | Foreign key to user table |
| creator_name | String(80) | Display name of creator |
| is_active | Boolean | Whether lobby is currently active |
| is_locked | Boolean | Whether new participants can join |
| created_at | DateTime | When lobby was created |
| last_activity_at | DateTime | Last activity timestamp |
| closed_at | DateTime | When lobby was closed (nullable) |
| network_state | JSON | Network topology state |
| progress | JSON | Team progress tracking |

**Relationships:**
- Has many: participants, chat_messages, device_locks, cli_history
- Belongs to: creator (User)

---

### 2. **lobby_participant**
Tracks participants in each lobby.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| lobby_id | String(8) | Foreign key to collaboration_lobby |
| user_id | Integer | Foreign key to user table |
| username | String(80) | Display name |
| profile_image | String(255) | Profile picture URL |
| role | String(20) | 'creator', 'moderator', 'participant' |
| cursor_x | Integer | Real-time cursor X position |
| cursor_y | Integer | Real-time cursor Y position |
| selected_device | String(100) | Currently selected device |
| user_color | String(7) | Hex color code for user |
| is_active | Boolean | Currently in lobby |
| individual_score | Integer | User's individual score |
| team_contribution | Integer | Team contribution score |
| joined_at | DateTime | When user joined |
| last_activity | DateTime | Last activity timestamp |
| left_at | DateTime | When user left (nullable) |

**Relationships:**
- Belongs to: lobby, user

---

### 3. **lobby_chat_message**
Stores chat messages within lobbies.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| lobby_id | String(8) | Foreign key to collaboration_lobby |
| user_id | String(20) | User ID or 'system' |
| username | String(80) | Display name |
| profile_image | String(255) | Profile picture URL |
| message | Text | Message content |
| message_type | String(20) | 'text', 'system', 'action', 'progress' |
| timestamp | DateTime | When message was sent |

**Relationships:**
- Belongs to: lobby

---

### 4. **lobby_device_lock**
Tracks device locks for exclusive editing.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| lobby_id | String(8) | Foreign key to collaboration_lobby |
| device_id | String(100) | Device identifier |
| locked_by | Integer | Foreign key to user table |
| username | String(80) | Display name of lock owner |
| locked_at | DateTime | When device was locked |
| auto_unlock_at | DateTime | When lock expires (5 minutes) |

**Constraints:**
- Unique constraint on (lobby_id, device_id)

**Relationships:**
- Belongs to: lobby, user

---

### 5. **lobby_cli_history**
Stores CLI command history for devices.

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| lobby_id | String(8) | Foreign key to collaboration_lobby |
| device_id | String(100) | Device identifier |
| command | Text | CLI command executed |
| output | Text | Command output |
| executed_by | Integer | Foreign key to user table |
| username | String(80) | Display name |
| timestamp | DateTime | When command was executed |

**Relationships:**
- Belongs to: lobby, user

---

## 🔧 Installation & Setup

### Step 1: Run Migration Script

```bash
python create_lobby_tables.py
```

This will create all 5 tables in your PostgreSQL database.

### Step 2: Verify Tables Created

Connect to your PostgreSQL database and verify:

```sql
-- List all lobby-related tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_name LIKE 'lobby%' OR table_name = 'collaboration_lobby';

-- View table structure
\d collaboration_lobby
\d lobby_participant
\d lobby_chat_message
\d lobby_device_lock
\d lobby_cli_history
```

---

## 🚀 How It Works

### Automatic Persistence

The system now automatically saves lobby data to the database:

1. **Lobby Creation**: When a lobby is created, it's immediately saved to `collaboration_lobby` table
2. **Participant Join**: When users join, they're added to `lobby_participant` table
3. **Chat Messages**: Every chat message is saved to `lobby_chat_message` table
4. **Device Locks**: When devices are locked, locks are saved to `lobby_device_lock` table
5. **CLI Commands**: All CLI commands are logged to `lobby_cli_history` table

### Server Restart Recovery

When the server restarts:

1. `LobbyManager.__init__()` calls `_load_active_lobbies_from_db()`
2. All active lobbies are loaded from the database
3. In-memory `TroubleshootingLobby` objects are recreated
4. User mappings are rebuilt
5. Lobbies continue where they left off

### Cleanup & Maintenance

Automated cleanup runs every 5 minutes:

- **Inactive Participants**: Removed after 30 minutes of inactivity
- **Empty Lobbies**: Marked as inactive when last participant leaves
- **Old Lobbies**: Deleted from database after 24 hours of inactivity

---

## 📊 Usage Examples

### Query Active Lobbies

```python
from user.models.collaboration_lobby import CollaborationLobby

# Get all active lobbies
active_lobbies = CollaborationLobby.query.filter_by(is_active=True).all()

# Get lobby with participants
lobby = CollaborationLobby.query.get('ABC12345')
participants = lobby.participants.filter_by(is_active=True).all()

# Get recent chat messages
recent_messages = lobby.chat_messages.order_by(
    LobbyChatMessage.timestamp.desc()
).limit(20).all()
```

### User Lobby History

```python
from services.lobby_persistence import lobby_persistence

# Get user's participation history
history = lobby_persistence.get_user_lobby_history(user_id=123, limit=10)

for entry in history:
    print(f"Lobby: {entry['lobby_name']}")
    print(f"Role: {entry['role']}")
    print(f"Score: {entry['individual_score']}")
```

### Manual Cleanup

```python
from services.lobby_persistence import lobby_persistence

# Clean up lobbies older than 48 hours
lobby_persistence.cleanup_old_lobbies(hours=48)
```

---

## 🔍 Monitoring & Analytics

### Lobby Statistics

```python
# Get lobby manager stats
stats = lobby_manager.get_stats()
print(f"Total lobbies: {stats['total_lobbies']}")
print(f"Active lobbies: {stats['active_lobbies']}")
print(f"Total participants: {stats['total_participants']}")
print(f"Avg participants/lobby: {stats['avg_participants_per_lobby']}")
```

### Database Queries

```sql
-- Most active lobbies by participant count
SELECT l.id, l.name, COUNT(p.id) as participant_count
FROM collaboration_lobby l
LEFT JOIN lobby_participant p ON l.id = p.lobby_id AND p.is_active = TRUE
WHERE l.is_active = TRUE
GROUP BY l.id, l.name
ORDER BY participant_count DESC
LIMIT 10;

-- User activity in lobbies
SELECT u.username, COUNT(DISTINCT p.lobby_id) as lobbies_joined,
       SUM(p.individual_score) as total_score
FROM lobby_participant p
JOIN user u ON p.user_id = u.id
WHERE p.joined_at >= NOW() - INTERVAL '7 days'
GROUP BY u.id, u.username
ORDER BY total_score DESC;

-- Chat activity by lobby
SELECT l.name, COUNT(m.id) as message_count,
       COUNT(DISTINCT m.user_id) as active_chatters
FROM lobby_chat_message m
JOIN collaboration_lobby l ON m.lobby_id = l.id
WHERE m.timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY l.id, l.name
ORDER BY message_count DESC;
```

---

## 🛠️ Configuration

### Enable/Disable Persistence

In `services/troubleshooting_lobbies.py`:

```python
class LobbyManager:
    def __init__(self):
        # Set to False to disable database persistence
        self._persistence_enabled = True
```

### Cleanup Intervals

Adjust cleanup timing:

```python
# In start_cleanup_timer()
self._cleanup_timer = threading.Timer(300, cleanup_task)  # 300 seconds = 5 minutes

# In _cleanup_old_db_lobbies()
lobby_persistence.cleanup_old_lobbies(hours=24)  # Delete after 24 hours
```

---

## 🔒 Security Considerations

1. **User ID Validation**: Always validate user IDs before queries
2. **SQL Injection**: Using SQLAlchemy ORM prevents SQL injection
3. **Access Control**: Lobby class restrictions enforced
4. **Data Privacy**: Profile images and usernames are stored
5. **Cleanup**: Automatic deletion of old data prevents database bloat

---

## 🐛 Troubleshooting

### Issue: Tables Not Created

**Solution:**
```bash
# Ensure PostgreSQL is running
# Check connection in instance/config.py
python create_lobby_tables.py
```

### Issue: Lobbies Not Persisting

**Check:**
```python
# Verify persistence is enabled
lobby_manager._persistence_enabled  # Should be True

# Check logs for errors
tail -f logs/application.log | grep "lobby"
```

### Issue: Old Lobbies Not Cleaning Up

**Manually trigger cleanup:**
```python
from services.lobby_persistence import lobby_persistence
lobby_persistence.cleanup_old_lobbies(hours=1)  # Aggressive cleanup
```

---

## 📈 Performance Considerations

- **Indexes**: Primary keys and foreign keys are automatically indexed
- **JSON Columns**: PostgreSQL handles JSON efficiently
- **Cleanup**: Regular cleanup prevents table bloat
- **Pagination**: Use `.limit()` for large result sets
- **Connection Pooling**: Handled by SQLAlchemy

---

## 🎉 Benefits

✅ **Durability**: Lobbies survive server restarts  
✅ **Analytics**: Historical data for user engagement  
✅ **Recovery**: Participants can reconnect to active lobbies  
✅ **Audit Trail**: Complete history of CLI commands and chat  
✅ **Scalability**: Database handles concurrent access  

---

## 📝 Next Steps

1. ✅ Create database tables
2. ✅ Integrate with existing lobby manager
3. ✅ Test lobby creation and persistence
4. ✅ Verify server restart recovery
5. 🔄 Add admin dashboard for lobby management
6. 🔄 Implement lobby analytics and reports
7. 🔄 Add lobby archiving for historical analysis

---

## 📞 Support

For issues or questions:
- Check logs: `logs/application.log`
- Review database: Use PostgreSQL client
- Test persistence: Create lobby → restart server → verify lobby still exists

**Happy Collaborating! 🚀**
