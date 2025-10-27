# Production Live Quiz Setup Guide

## 🎯 Problem Statement

The Live Quiz button is not visible on production because **no active or waiting sessions exist in the database**. This is not a bug - the feature is designed to only show when sessions are available.

## 🔍 Root Cause

The Live Quiz UI conditionally renders based on database state:

1. **Backend Query** (`user/routes/universal_class_routes.py:850-870`)
   - Queries `LiveQuizSession` for `status='active'` or `status='waiting'`
   - Filters by `class_id` and `module_id`

2. **Frontend Logic** (`templates/user/module_detail.html:4323`)
   - If query returns empty → button hidden (`display: none`)
   - If query returns sessions → button visible with appropriate styling

## ✅ Solution: Seed Database with Sessions

### Option 1: Quick Fix (Recommended for Testing)

Create sessions for all modules in one command:

```bash
# On production server
cd /path/to/RiddleNet
source venv/bin/activate

# Seed all modules with waiting sessions
python scripts/seed_live_quiz_sessions.py

# Restart application
sudo systemctl restart riddlenet
```

**Result:** All modules will show "Live Quiz Starting Soon" button

### Option 2: Create One Active Session (Instant Testing)

For immediate visibility with a live session:

```bash
# Create one active session
python scripts/seed_live_quiz_sessions.py --active

# Restart application
sudo systemctl restart riddlenet
```

**Result:** First module will show "Join Live Quiz Now!" button with pulse animation

### Option 3: Target Specific Class/Module

Seed only specific classes or modules:

```bash
# Seed only Networking 1 (class 7)
python scripts/seed_live_quiz_sessions.py --class 7

# Seed only Module 1
python scripts/seed_live_quiz_sessions.py --module 1

# Create active session for specific class
python scripts/seed_live_quiz_sessions.py --class 7 --active
```

### Option 4: Clean and Reseed

Remove all existing sessions and start fresh:

```bash
# Clean all sessions, then seed with active status
python scripts/seed_live_quiz_sessions.py --clean
python scripts/seed_live_quiz_sessions.py --status active
```

## 🚀 Production Deployment Steps

### Step 1: Verify Database State

```bash
# Check current session count
python scripts/check_live_quiz_sessions.py
```

Expected output if empty:
```
⚠️  NO LIVE QUIZ SESSIONS FOUND IN DATABASE
   This is why the Live Quiz button is not appearing!
```

### Step 2: Run Production Readiness Check

```bash
python scripts/production_deployment_check.py
```

This verifies:
- ✅ Database tables exist
- ✅ Instructors available
- ✅ Question groups available
- ✅ Classes and modules configured

### Step 3: Seed Sessions

Choose appropriate seeding strategy:

```bash
# For production - seed all modules with waiting status
python scripts/seed_live_quiz_sessions.py

# For demo/testing - create active sessions
python scripts/seed_live_quiz_sessions.py --status active
```

### Step 4: Restart Application

```bash
# Using systemd
sudo systemctl restart riddlenet

# Or using supervisor
sudo supervisorctl restart riddlenet

# Or kill and restart manually
pkill -f "python run.py"
python run.py &
```

### Step 5: Verify Button Appears

1. Navigate to any module page: `/class/{class_id}/module/{module_id}`
2. Look for Live Quiz button in the module header
3. Check browser console: `console.log(window.currentLiveQuizSessions)`

## 📋 Script Options Reference

### Seeding Script (`seed_live_quiz_sessions.py`)

```bash
# Show help
python scripts/seed_live_quiz_sessions.py --help

# Seed all modules (default: waiting status)
python scripts/seed_live_quiz_sessions.py

# Create one active session
python scripts/seed_live_quiz_sessions.py --active

# Clean existing sessions first
python scripts/seed_live_quiz_sessions.py --clean

# Seed specific class
python scripts/seed_live_quiz_sessions.py --class 7

# Seed specific module
python scripts/seed_live_quiz_sessions.py --module 1

# Override status to active
python scripts/seed_live_quiz_sessions.py --status active

# Combine options
python scripts/seed_live_quiz_sessions.py --class 7 --status active
python scripts/seed_live_quiz_sessions.py --clean --active
```

### Diagnostic Script (`check_live_quiz_sessions.py`)

```bash
# Check all sessions and their distribution
python scripts/check_live_quiz_sessions.py
```

Shows:
- Total session count
- Status distribution (active/waiting/completed)
- Which modules have sessions
- Participant counts

### Deployment Check (`production_deployment_check.py`)

```bash
# Comprehensive deployment readiness check
python scripts/production_deployment_check.py
```

Verifies:
- Database tables migrated
- Active/waiting sessions exist
- Session distribution across classes/modules
- Instructor accounts configured
- Question groups available

## 🎨 Button Behavior After Seeding

### Status: `'waiting'`
```
┌────────────────────────────────────┐
│  Live Quiz Starting Soon  ⏳WAITING │
└────────────────────────────────────┘
```
- No animation
- Click shows "hasn't started yet" message
- Automatically updates when instructor starts session

### Status: `'active'`
```
┌──────────────────────────────┐
│  ⚡ Join Live Quiz Now! 🔴LIVE │  ← Pulsing animation
└──────────────────────────────┘
```
- Pulse animation
- Immediate join on click
- Auto-notification popup
- Real-time updates

## 🔧 Instructor Workflow

After seeding, instructors can manage sessions via API:

### Start a Session (waiting → active)

```bash
POST /instructor/api/live-quiz/<session_id>/start
```

This changes:
- Status: `'waiting'` → `'active'`
- Sets `started_at` timestamp
- Emits Socket.IO event to notify students

### Advance Questions

```bash
POST /instructor/api/live-quiz/<session_id>/next-question
```

### End Session

```bash
POST /instructor/api/live-quiz/<session_id>/end
```

This changes:
- Status: `'active'` → `'completed'`
- Button disappears for students
- Final leaderboard sent

## 📊 Expected Results

### Before Seeding
- ❌ No Live Quiz button visible
- ❌ `live_quiz_sessions = []` in template
- ❌ Database query returns 0 results

### After Seeding (waiting status)
- ✅ "Live Quiz Starting Soon" button visible
- ✅ `live_quiz_sessions` populated with session data
- ✅ Badge shows "⏳ WAITING"

### After Seeding (active status)
- ✅ "Join Live Quiz Now!" button visible
- ✅ Button has pulsing animation
- ✅ Badge shows "🔴 LIVE"
- ✅ Auto-notification popup appears

## 🐛 Troubleshooting

### Button Still Not Showing

1. **Check database:**
   ```bash
   python scripts/check_live_quiz_sessions.py
   ```

2. **Check route logs:**
   Look for: `Found X live quiz sessions for module Y`

3. **Check browser console:**
   ```javascript
   console.log(window.currentLiveQuizSessions)
   ```

4. **Verify correct module:**
   - Sessions exist for Class 7, Module 1
   - But you're viewing Class 9, Module 5 (no sessions)

### Sessions Created but Button Hidden

1. **Check status:**
   - Only `'active'` and `'waiting'` show button
   - `'completed'` and `'paused'` hide button

2. **Check class/module match:**
   - Session: `class_id=7, module_id=1`
   - URL: `/class/7/module/2` ← Mismatch!

3. **Clear browser cache:**
   ```bash
   Ctrl+Shift+R  # Hard refresh
   ```

### Database Shows Sessions but Query Returns Empty

1. **Check migrations:**
   ```bash
   # Verify tables exist
   python -c "from __init__ import create_app, db; app = create_app(); app.app_context().push(); from user.models.live_quiz import LiveQuizSession; print(LiveQuizSession.query.count())"
   ```

2. **Check filters:**
   ```python
   # In Python shell
   from user.models.live_quiz import LiveQuizSession
   
   # All sessions
   print(LiveQuizSession.query.count())
   
   # Active/waiting only
   sessions = LiveQuizSession.query.filter(
       LiveQuizSession.status.in_(['active', 'waiting'])
   ).all()
   print(f"Active/waiting: {len(sessions)}")
   ```

## 📈 Monitoring

### Check Session Activity

```python
# In Flask shell
from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant

# Active sessions
active = LiveQuizSession.query.filter_by(status='active').all()
for s in active:
    participant_count = LiveQuizParticipant.query.filter_by(
        session_id=s.id, is_active=True
    ).count()
    print(f"{s.session_code}: {s.title} ({participant_count} participants)")
```

### Clean Up Old Sessions

```python
# Mark completed sessions older than 7 days as archived
from datetime import datetime, timedelta

old_cutoff = datetime.utcnow() - timedelta(days=7)
old_sessions = LiveQuizSession.query.filter(
    LiveQuizSession.status == 'completed',
    LiveQuizSession.ended_at < old_cutoff
).all()

print(f"Found {len(old_sessions)} old sessions to archive")
```

## 🎯 Summary

**Fix the production issue in 3 commands:**

```bash
cd /path/to/RiddleNet
python scripts/seed_live_quiz_sessions.py --status active
sudo systemctl restart riddlenet
```

**Result:** Live Quiz buttons appear immediately on all module pages!

---

**Last Updated:** October 27, 2025  
**Status:** Production-Ready Solution  
**Effort:** < 2 minutes to deploy
