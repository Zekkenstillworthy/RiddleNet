# Live Quiz Auto-Advance & Duplicate Rendering Fix

## Summary
This fix implements automatic question progression controlled by the backend and resolves duplicate question rendering issues.

## Issues Fixed

### 1. **Duplicate Question Rendering**
**Problem:** Questions were being loaded multiple times when students joined or when quiz_state events were received, causing duplicate rendering.

**Root Cause:**
- `loadQuestionForStudent()` was being called from multiple socket events (`quiz_started` and `quiz_state`)
- No flag to track if a question had already been loaded

**Solution:**
- Added `liveQuizState.hasLoadedQuestion` flag
- Set flag to `true` when loading question in `quiz_started` event
- Check flag in `quiz_state` event before loading to prevent duplicate
- Reset flag in `next_question` event for new questions

**Files Changed:**
- `templates/user/module_detail.html` (lines ~5605, ~5670-5695, ~5760-5775)

### 2. **Backend-Controlled Auto-Advance**
**Problem:** Both frontend (instructor) and backend had timers, causing conflicts and race conditions.

**Solution:**
- **Backend (Authoritative):** `socket_events.py` has `auto_advance_question()` function that:
  - Runs server-side timer for each question
  - Emits `timer_expired` when countdown reaches 0
  - Shows correct answer to all students
  - Automatically emits `next_question` after 3 seconds
  - Shows leaderboard break every 5 questions (5 second pause)
  - Advances to next question automatically

- **Frontend (Passive):** Instructor and student UIs now:
  - Listen for `timer_expired`, `next_question`, and `quiz_ended` events
  - Update UI based on backend events
  - No client-side timers for question progression

**Files Changed:**
- `templates/instructor/class_content_manager.html` (lines ~17890-17920, ~18200-18260)
- `socket_events.py` (already implemented - lines ~2727-2870)

### 3. **Leaderboard Break Every 5 Questions**
**Problem:** Leaderboard should automatically show every 5 questions without manual intervention.

**Solution:**
- Backend automatically detects every 5th question
- Sets `show_leaderboard_break: true` in `next_question` event
- Frontend displays leaderboard in `questionArea` for 5 seconds
- Automatically loads next question after break

**Flow:**
1. Question 5 timer expires → `timer_expired` emitted
2. Backend waits 3 seconds (answer reveal)
3. Backend checks: `(question_number % 5 == 0)` → true
4. Backend emits `next_question` with `show_leaderboard_break: true`, `break_duration: 5`
5. Students see leaderboard for 5 seconds
6. Next question loads automatically

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ INSTRUCTOR STARTS QUIZ                                          │
│ - POST /instructor/api/live-quiz/{id}/start                    │
│ - Status: waiting → active                                      │
│ - Backend starts auto_advance_question() timer (30s default)   │
│ - Emit: quiz_started                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│ STUDENTS LOAD FIRST QUESTION                                    │
│ - Receive: quiz_started event                                   │
│ - Set: hasLoadedQuestion = true                                │
│ - Call: loadQuestion(0)                                         │
│ - Start client-side timer (visual countdown only)              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    [30 seconds pass]
                         │
┌────────────────────────▼────────────────────────────────────────┐
│ BACKEND TIMER EXPIRES                                           │
│ - auto_advance_question() detects timer = 0                    │
│ - Emit: timer_expired (question_index, leaderboard)            │
│ - Wait 3 seconds (answer reveal)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│ STUDENTS SEE CORRECT ANSWER                                     │
│ - Receive: timer_expired                                        │
│ - Call: showCorrectAnswerReveal()                              │
│ - Display correct answer with explanation                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    [3 seconds pass]
                         │
┌────────────────────────▼────────────────────────────────────────┐
│ BACKEND AUTO-ADVANCES                                           │
│ - Check if question 5, 10, 15, etc.                           │
│ - If yes: show_leaderboard_break = true                       │
│ - session.current_question_index++                            │
│ - Emit: next_question (question_index, leaderboard, break)    │
└────────────────────────┬────────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
   [If break = false]        [If break = true]
            │                         │
┌───────────▼─────────────┐  ┌───────▼──────────────────────────┐
│ LOAD NEXT QUESTION      │  │ SHOW LEADERBOARD BREAK           │
│ - Set: hasLoadedQuestion│  │ - Display in questionArea        │
│ - Call: loadQuestion()  │  │ - Show top 10 rankings           │
│ - Reset timer           │  │ - Countdown: 5 seconds           │
└─────────────────────────┘  └───────┬──────────────────────────┘
                                     │
                                [5 seconds pass]
                                     │
                            ┌────────▼────────┐
                            │ LOAD NEXT       │
                            │ QUESTION        │
                            └─────────────────┘
```

## Socket Events Reference

### `timer_expired`
- **Emitted by:** Backend (auto_advance_question)
- **Received by:** All students + instructor
- **Purpose:** Show correct answer, prepare for next question
- **Data:**
  ```javascript
  {
    question_index: 0,
    timestamp: "2025-11-03T...",
    leaderboard: [...]
  }
  ```

### `next_question`
- **Emitted by:** Backend (auto_advance_question)
- **Received by:** All students + instructor
- **Purpose:** Advance everyone to next question simultaneously
- **Data:**
  ```javascript
  {
    question_index: 1,
    timestamp: "2025-11-03T...",
    leaderboard: [...],
    show_leaderboard_break: false,  // true every 5 questions
    break_duration: 5               // seconds (if break = true)
  }
  ```

### `quiz_ended`
- **Emitted by:** Backend (auto_advance_question when last question)
- **Received by:** All students + instructor
- **Purpose:** Show final results
- **Data:**
  ```javascript
  {
    session_id: 123,
    ended_at: "2025-11-03T...",
    leaderboard: [...]  // final rankings
  }
  ```

## Testing Checklist

### Duplicate Rendering Test
- [ ] Start quiz as instructor
- [ ] Join as student
- [ ] Check console: Should see only ONE `[LOAD_QUESTION]` log
- [ ] No duplicate question rendering

### Auto-Advance Test
- [ ] Start quiz with 10 questions
- [ ] Do NOT answer question 1
- [ ] Wait 30 seconds
- [ ] Should see correct answer automatically
- [ ] Should advance to question 2 after 3 seconds
- [ ] All students should see same question at same time

### Leaderboard Break Test
- [ ] Answer questions 1-4
- [ ] Wait for question 5 to complete
- [ ] Should see leaderboard for 5 seconds in question area
- [ ] Should automatically load question 6

### Sync Test
- [ ] Student A answers quickly
- [ ] Student B doesn't answer
- [ ] Both should advance to next question at same time (30 seconds after question start)
- [ ] No manual clicking needed

## Configuration

**Question Duration:** 30 seconds (configurable in session creation)
**Answer Reveal Duration:** 3 seconds (hardcoded)
**Leaderboard Break Duration:** 5 seconds (hardcoded)
**Leaderboard Break Frequency:** Every 5 questions

## Backend Code Reference

**File:** `socket_events.py`
**Function:** `auto_advance_question(session_id, question_duration=30, leaderboard_duration=5, app=None)`
**Lines:** ~2727-2870

Key logic:
```python
# Wait for question timer
time.sleep(question_duration)

# Emit timer_expired
socketio.emit('timer_expired', {...}, room=room)

# Wait for answer reveal
time.sleep(3)

# Check for leaderboard break
show_leaderboard_break = (question_number % 5 == 0)

# Advance question
session.current_question_index += 1
socketio.emit('next_question', {
    'show_leaderboard_break': show_leaderboard_break,
    'break_duration': leaderboard_duration if show_leaderboard_break else 0
}, room=room)

# Schedule next timer (with delay if leaderboard break)
delay = leaderboard_duration if show_leaderboard_break else 0
_start_question_timer(session_id, question_duration, leaderboard_duration, app, delay)
```

## Migration Notes

**Deprecated:**
- `nextQuestion()` function in instructor UI (kept for backward compatibility)
- Instructor "Next Question" button (hidden by default)
- Client-side `autoAdvanceTimer` for instructors
- `showLeaderboardBreak()` client-side function

**New Paradigm:**
- Backend is the single source of truth for question progression
- All timing is server-controlled
- Frontend is passive and reactive to socket events
- Synchronization is guaranteed by backend timer

## Known Limitations

1. **Network Lag:** Students with poor connection may see events slightly delayed, but backend ensures order
2. **Clock Skew:** Backend timer is authoritative, client timers are visual only
3. **Rejoin:** If student disconnects and rejoins, they see current question (may miss some)

## Future Enhancements

- [ ] Configurable answer reveal duration
- [ ] Configurable leaderboard break duration
- [ ] Option to disable leaderboard breaks
- [ ] Pause/Resume quiz functionality
- [ ] Jump to specific question (for instructor)
- [ ] Real-time progress bar for instructor

---
**Last Updated:** 2025-11-03
**Tested With:** Python 3.x, Flask-SocketIO, Socket.IO client
