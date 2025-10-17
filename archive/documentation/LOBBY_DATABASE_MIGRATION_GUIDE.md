# Lobby Database Migration Guide

## Overview
This guide explains how to migrate existing collaboration lobbies to the PostgreSQL database using the migration script.

## Files Created

### 1. **create_lobby_tables.py**
- Creates the 5 database tables for lobby persistence
- Run once during initial setup
- Safe to run multiple times (won't duplicate tables)

### 2. **migrate_lobbies_to_db.py**
- Migrates active in-memory lobbies to database
- Can be used for:
  - Testing the database system
  - Migrating lobbies after deployment
  - Recovering from crashes
  - Data persistence operations

## Database Tables Created

✅ **collaboration_lobby** - Main lobby/session data
✅ **lobby_participant** - User participation tracking
✅ **lobby_chat_message** - Team chat history
✅ **lobby_device_lock** - Device locking system
✅ **lobby_cli_history** - CLI command audit trail

## Usage Instructions

### Initial Setup (First Time)

```bash
# 1. Create the database tables
python create_lobby_tables.py

# Output:
# ✅ Successfully created lobby tables
```

### Migrating Active Lobbies

#### Test Mode (Dry Run)
```bash
# See what would be migrated without actually writing to database
python migrate_lobbies_to_db.py --test
```

**Example Output:**
```
🔄 Starting lobby migration...
   Mode: TEST (dry-run)

📊 Found 3 active lobbies to migrate

[1/3] Migrating lobby 'Network Lab Session' (ID: ABC123XY)...
   [TEST MODE] Skipping database write
   ✅ Success

============================================================
📊 MIGRATION SUMMARY
============================================================
Mode:                    TEST (dry-run)
Total Lobbies Found:     3
Successfully Migrated:   3
Failed:                  0

Total Participants:      10
Total Chat Messages:     35
Total Device Locks:      5
Total CLI Commands:      24
============================================================

✅ Test run completed successfully!
   No data was written to the database.
```

#### Production Mode (Actual Migration)
```bash
# Actually migrate lobbies to database
python migrate_lobbies_to_db.py
```

**Example Output:**
```
🔄 Starting lobby migration...
   Mode: PRODUCTION

📊 Found 3 active lobbies to migrate

[1/3] Migrating lobby 'Network Lab Session' (ID: ABC123XY)...
   - Saving lobby data... ✓
   - Saving 4 participants... ✓
   - Saving 12 chat messages... ✓
   - Saving 2 device locks... ✓
   - Saving 8 CLI commands... ✓
   ✅ Success

[2/3] Migrating lobby 'Troubleshooting Team' (ID: DEF456ZW)...
   - Saving lobby data... ✓
   - Saving 3 participants... ✓
   - Saving 15 chat messages... ✓
   - Saving 1 device locks... ✓
   - Saving 10 CLI commands... ✓
   ✅ Success

[3/3] Migrating lobby 'Config Practice' (ID: GHI789UV)...
   - Saving lobby data... ✓
   - Saving 3 participants... ✓
   - Saving 8 chat messages... ✓
   - Saving 2 device locks... ✓
   - Saving 6 CLI commands... ✓
   ✅ Success

============================================================
📊 MIGRATION SUMMARY
============================================================
Mode:                    PRODUCTION
Total Lobbies Found:     3
Successfully Migrated:   3
Failed:                  0

Total Participants:      10
Total Chat Messages:     35
Total Device Locks:      5
Total CLI Commands:      24
============================================================

✅ Migration completed successfully!
   All lobbies have been saved to the database.

🔍 Verifying migration...
✅ Found 3 active lobbies in database
   - Network Lab Session (ID: ABC123XY) - 4 participants
   - Troubleshooting Team (ID: DEF456ZW) - 3 participants
   - Config Practice (ID: GHI789UV) - 3 participants

============================================================
🎉 Migration script completed
============================================================
```

## On Server (Production)

### Setup on AWS EC2

```bash
# SSH into server
ssh -i riddlenetv1.pem ubuntu@54.66.229.118

# Navigate to project
cd RiddleNet

# Activate virtual environment
source venv/bin/activate

# Run table creation (first time only)
python create_lobby_tables.py

# Test migration (dry-run)
python migrate_lobbies_to_db.py --test

# Actual migration (when ready)
python migrate_lobbies_to_db.py
```

## When to Use Migration Script

### Use Cases:

1. **Initial Setup**
   - After deploying database persistence features
   - To migrate existing active lobbies

2. **Testing**
   - Verify database system is working
   - Test migration process without affecting data

3. **Data Recovery**
   - After server crashes
   - When lobbies exist in memory but not database

4. **Regular Maintenance**
   - Periodic backups of active lobbies
   - Ensuring data consistency

## What Gets Migrated

For each lobby, the script migrates:

- ✅ **Lobby metadata** (name, type, settings, creator)
- ✅ **All participants** (username, cursor position, role, scores)
- ✅ **Chat history** (all messages up to last 100)
- ✅ **Device locks** (who has exclusive access to which devices)
- ✅ **CLI history** (last 50 commands per device)
- ✅ **Network state** (shared topology and device configurations)
- ✅ **Progress data** (team progress tracking)

## Automatic Persistence

After initial migration, the system **automatically** saves:

- New lobby creation
- User joins/leaves
- Chat messages
- Device locks/unlocks
- CLI commands
- Network state changes

You typically only need to run the migration script **once** after deploying the database persistence feature.

## Server Restart Recovery

The system **automatically** loads active lobbies from the database when the server starts:

```python
# This happens automatically on server start
lobby_manager._load_active_lobbies_from_db()
```

Check logs for:
```
✅ Loaded N active lobbies from database
```

## Troubleshooting

### No Lobbies Found
```
ℹ️  No active lobbies found in memory
```
**Solution:** This is normal if no users have created lobbies yet.

### Database Connection Error
```
❌ Error loading lobbies from database: ...
```
**Solution:** 
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database credentials in config
- Ensure tables exist: `python create_lobby_tables.py`

### Migration Failed
```
❌ Failed: ...
```
**Solution:**
- Check the error message in the output
- Verify database has sufficient permissions
- Run in test mode first to identify issues

## Verification

### Check Database Tables
```bash
# Connect to PostgreSQL
psql -U postgres -d riddlenet

# List tables
\dt

# View lobby data
SELECT * FROM collaboration_lobby;
SELECT * FROM lobby_participant;
SELECT * FROM lobby_chat_message;

# Exit
\q
```

### Check Application Logs
```bash
# View application logs
tail -f logs/riddlenet.log

# Look for:
# "✅ Loaded N active lobbies from database"
# "Created lobby ABC123XY by user ..."
```

## Best Practices

1. **Always test first**
   ```bash
   python migrate_lobbies_to_db.py --test
   ```

2. **Run during low traffic**
   - Migration locks lobbies briefly
   - Best during maintenance windows

3. **Verify after migration**
   - Check database has records
   - Test lobby functionality
   - Verify users can join lobbies

4. **Monitor logs**
   - Watch for errors during migration
   - Check automatic persistence is working

5. **Regular backups**
   - PostgreSQL database backups
   - Migration script can help recover from backups

## Summary

✅ **One-time setup:** `python create_lobby_tables.py`
✅ **Test migration:** `python migrate_lobbies_to_db.py --test`
✅ **Actual migration:** `python migrate_lobbies_to_db.py`
✅ **Automatic after that:** System handles all persistence

The migration script is primarily for **initial deployment** and **testing**. After that, the system automatically persists all lobby activities to the database!
