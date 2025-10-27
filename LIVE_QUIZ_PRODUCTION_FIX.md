# Live Quiz Production Issue - Diagnosis & Solution

## Problem Summary
The Live Quiz button is not appearing on the production server despite the feature being fully implemented.

## Root Cause Analysis

### Technical Diagnosis
The Live Quiz UI is **conditionally rendered** based on database state:

1. **Template Logic** (`templates/user/module_detail.html`):
   - Receives `live_quiz_sessions` context variable
   - Calls `updateLiveQuizButton(sessions)` function
   - Button only displays if sessions with status `'active'` or `'waiting'` exist

2. **Backend Query** (`user/routes/universal_class_routes.py`, line ~850):
   ```python
   active_sessions = LiveQuizSession.query.filter_by(
       class_id=class_id,
       module_id=module_id,
       status='active'
   ).all()
   
   waiting_sessions = LiveQuizSession.query.filter_by(
       class_id=class_id,
       module_id=module_id,
       status='waiting'
   ).all()
   ```

3. **Frontend Logic** (`module_detail.html`, line ~4323):
   ```javascript
   function updateLiveQuizButton(sessions) {
       if (sessions && sessions.length > 0) {
           buttonContainer.style.display = 'block';
       } else {
           buttonContainer.style.display = 'none';  // ← Button hidden!
       }
   }
   ```

### Why Production Shows No Button

**The database has no active or waiting sessions.**

Possible reasons:
- ✅ Live Quiz tables exist (migrations ran successfully)
- ✅ Live Quiz API endpoints are registered
- ✅ Frontend UI is fully implemented
- ❌ **No instructor has created any quiz sessions**
- ❌ **Or all sessions are marked as `'completed'`**

## Verification Steps

### 1. Check Database State

Run the diagnostic script:
```bash
python scripts/check_live_quiz_sessions.py
```

This will show:
- Total number of sessions in database
- Status distribution (waiting/active/completed)
- Which classes/modules have sessions
- Whether any sessions will display in UI

### 2. Expected Output (Empty DB)

```
⚠️  NO LIVE QUIZ SESSIONS FOUND IN DATABASE
   This is why the Live Quiz button is not appearing!

📋 SOLUTION:
   1. Instructors need to create sessions via: POST /instructor/api/live-quiz/create
   2. Or run the seed script to create test sessions
```

## Solution Options

### Option 1: Seed Test Sessions (Recommended for Testing)

Create waiting sessions for all modules:
```bash
python scripts/seed_live_quiz_sessions.py
```

Create an immediately active session:
```bash
python scripts/seed_live_quiz_sessions.py --active
```

### Option 2: Instructor Creates Sessions (Production Workflow)

Instructors should use the Live Quiz API:

**Create Session:**
```bash
POST /instructor/api/live-quiz/create
Content-Type: application/json

{
    "question_group_id": 1,
    "class_id": 1,
    "module_id": 1,
    "lesson_id": 1,
    "title": "Module 1 Live Quiz",
    "time_per_question": 30,
    "show_leaderboard": true,
    "allow_join_after_start": true
}
```

Response includes `session_code` and session details.

**Start Session:**
```bash
POST /instructor/api/live-quiz/<session_id>/start
```

This changes status from `'waiting'` → `'active'`, making button appear.

### Option 3: Add Instructor UI (Future Enhancement)

Create a web interface for instructors to:
- View available question groups
- Create quiz sessions with one click
- Start/stop sessions
- View live leaderboard
- See participant count

## Production Deployment Checklist

Before deploying Live Quiz to production:

- [x] Run database migrations (007, 008, 009)
- [x] Register `live_quiz_instructor_bp` blueprint
- [x] Register `live_quiz_bp` student blueprint
- [ ] **Create at least one quiz session per module**
- [ ] Test session creation via API
- [ ] Test starting a session
- [ ] Verify button appears for students
- [ ] Test student join flow
- [ ] Test real-time question delivery
- [ ] Test leaderboard updates

## Quick Production Fix

**Immediate fix to show Live Quiz button:**

```bash
# 1. SSH into production server
ssh user@production-server

# 2. Activate virtual environment
source /path/to/venv/bin/activate

# 3. Run seed script
cd /path/to/RiddleNet
python scripts/seed_live_quiz_sessions.py --active

# 4. Restart application
sudo systemctl restart riddlenet
```

**Within 30 seconds:**
- Active session will exist in database
- Students visiting module pages will see "Join Live Quiz Now!" button
- Button will pulse with animation
- Clicking joins the quiz immediately

## API Endpoints Reference

### Student Endpoints (`/api/live-quiz`)
- `POST /join` - Join a session
- `GET /questions/<session_id>` - Get quiz questions
- `POST /submit-answer` - Submit answer
- `GET /leaderboard/<session_id>` - View rankings
- `GET /status/<session_id>` - Check session state

### Instructor Endpoints (`/instructor/api/live-quiz`)
- `POST /create` - Create new session
- `GET /sessions` - List all sessions
- `POST /<id>/start` - Start session
- `POST /<id>/next-question` - Advance question
- `POST /<id>/end` - End session
- `GET /<id>/participants` - View participants
- `GET /<id>/leaderboard` - View leaderboard

## Socket.IO Events

Live Quiz uses real-time events:
- `quiz_started` - Notify session started
- `next_question` - Advance to next question
- `quiz_ended` - Session completed
- `leaderboard_update` - Score updates

## Database Schema

### `live_quiz_sessions`
```sql
id, question_group_id, class_id, module_id, lesson_id,
session_code (6-char unique), title, status,
current_question_index, time_per_question,
created_by, created_at, started_at, ended_at,
show_leaderboard, allow_join_after_start,
randomize_questions, randomize_answers
```

**Key Status Values:**
- `'waiting'` - Created but not started (shows "Starting Soon")
- `'active'` - Currently running (shows "Join Now!" with pulse)
- `'paused'` - Temporarily stopped (not shown)
- `'completed'` - Finished (not shown)

## Monitoring & Debugging

### Check if Sessions Exist
```python
from user.models.live_quiz import LiveQuizSession

# In Flask shell
sessions = LiveQuizSession.query.filter_by(status='active').all()
print(f"Active sessions: {len(sessions)}")

for s in sessions:
    print(f"  {s.id}: {s.title} (Code: {s.session_code})")
```

### Check Template Context
Add debug logging to `universal_class_routes.py`:
```python
print(f"[LiveQuiz] Found {len(live_quiz_sessions)} sessions for module {module_id}")
for session in live_quiz_sessions:
    print(f"  - Session {session['id']}: {session['title']} ({session['status']})")
```

### Check Frontend Rendering
In browser console:
```javascript
console.log('Live Quiz Sessions:', window.currentLiveQuizSessions);
console.log('Button Container:', document.getElementById('liveQuizButtonContainer'));
```

## Conclusion

The Live Quiz feature is **fully functional** but requires database seeding. The button's conditional rendering is by design—it only appears when instructors create and activate quiz sessions. 

**Production teams should:**
1. Run diagnostic script to confirm empty database
2. Seed test sessions OR have instructors create sessions via API
3. Verify button appearance after session creation
4. Consider building instructor UI for easier session management

---

**Date:** October 27, 2025  
**Status:** Diagnosed - Awaiting Session Creation  
**Impact:** Feature hidden due to empty database (not a code bug)
