# Student Live Quiz Auto-Restore Feature

## Overview
Added functionality to automatically restore the Live Quiz interface for students when they refresh the page during an active quiz session.

## Problem Solved
**Before:** When a student refreshed the page while participating in a Live Quiz, they would lose their quiz interface and have to rejoin manually. This disrupted their quiz experience and could cause them to miss questions.

**After:** The page now detects if the student has an active quiz participation and automatically restores the quiz interface with their current progress, including:
- Current question display
- Score and statistics
- Leaderboard
- WebSocket connection for real-time updates

## Implementation Details

### Files Modified

#### 1. `api/live_quiz_api.py`
Added new API endpoint: `/api/live-quiz-mvp/my-active-session`

**Purpose:** Check if the current user (student) has joined any active Live Quiz sessions.

**Query Parameters:**
- `class_id` (optional): Filter by specific class
- `module_id` (optional): Filter by specific module

**Response:**
```json
{
  "success": true,
  "has_active_session": true,
  "session": {
    "session_id": "6",
    "class_id": 7,
    "module_id": 1,
    "lesson_id": 2,
    "title": "Chapter 3 Quiz",
    "status": "active",
    "current_question_index": 2,
    "total_questions": 10,
    "participant_stats": {
      "total_score": 2500,
      "total_correct": 3,
      "total_answered": 3
    }
  }
}
```

**How It Works:**
1. Queries database for active/waiting sessions in the specified class/module
2. Checks in-memory session store to see if current user is a participant
3. Returns session details and participant stats if found

#### 2. `templates/user/module_detail.html`
Added new function: `checkAndRestoreStudentLiveQuiz()`

**Purpose:** Automatically restore the Live Quiz interface on page load if student has an active participation.

**Flow:**
1. Runs 1.5 seconds after page load
2. Fetches active session via new API endpoint
3. If found, reconstructs quiz state and UI
4. Reconnects to WebSocket for real-time updates
5. Displays current question or appropriate state

## How It Works

### 1. **Automatic Check on Page Load**
```javascript
setTimeout(() => {
    checkAndRestoreStudentLiveQuiz();
}, 1500);
```
- Runs 1.5 seconds after page load
- Ensures all page resources are loaded
- Non-blocking and invisible to user

### 2. **Session Detection**
```javascript
const response = await fetch(`/api/live-quiz-mvp/my-active-session?class_id=${classId}&module_id=${moduleId}`);
```
- Checks if student is currently participating in a quiz
- Scoped to current class and module
- Returns session details and participant progress

### 3. **State Restoration**
When an active session is found:
```javascript
liveQuizState.sessionId = session.session_id;
liveQuizState.questions = formattedQuestions;
liveQuizState.currentQuestionIndex = session.current_question_index || 0;
liveQuizState.hasJoined = true;
liveQuizState.quizEnded = (session.status === 'completed');
```

### 4. **UI Reconstruction**
- **Show quiz container:** `liveQuizContainer.style.display = 'block'`
- **Hide lesson content:** `lessonContent.style.display = 'none'`
- **Display current question:** Calls `displayQuestion()` with current question
- **Update leaderboard:** Fetches and displays latest rankings

### 5. **WebSocket Reconnection**
```javascript
connectLiveQuizSocket(session.session_id);
```
- Reconnects to live quiz room
- Receives real-time updates (new questions, timer, leaderboard changes)
- Ensures student stays synchronized with instructor

### 6. **Status-Based Display**

| Session Status | What Student Sees |
|----------------|-------------------|
| `waiting` | "Waiting for instructor..." message |
| `active` | Current question with answer options |
| `completed` | "Quiz Complete!" with final leaderboard |

## Console Logging

### Success Flow (Student Has Active Quiz)
```
🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮
[STUDENT QUIZ RESTORE] Checking for active quiz participation...
[STUDENT QUIZ RESTORE] Context: {classId: 7, moduleId: 1, lessonId: 2}
[STUDENT QUIZ RESTORE] Response: {success: true, has_active_session: true, ...}

✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅
[STUDENT QUIZ RESTORE] ✅ Active quiz participation found!
[STUDENT QUIZ RESTORE] Session ID: 6
[STUDENT QUIZ RESTORE] Title: Chapter 3 Quiz
[STUDENT QUIZ RESTORE] Status: active
[STUDENT QUIZ RESTORE] Current question: 3 / 10
[STUDENT QUIZ RESTORE] Score: 2500
[STUDENT QUIZ RESTORE] Correct answers: 3 / 3
✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅

[STUDENT QUIZ RESTORE] Lesson questions available: 10
[STUDENT QUIZ RESTORE] 🚀 Reinitializing Live Quiz interface...
[STUDENT QUIZ RESTORE] 🔌 Reconnecting to Live Quiz WebSocket...
[STUDENT QUIZ RESTORE] ✅ Displaying current question: 3
[STUDENT QUIZ RESTORE] ✅ Leaderboard updated
[STUDENT QUIZ RESTORE] ✅ Live Quiz restored successfully!
🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮
```

### No Active Quiz
```
🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮
[STUDENT QUIZ RESTORE] Checking for active quiz participation...
[STUDENT QUIZ RESTORE] Context: {classId: 7, moduleId: 1, lessonId: 2}
[STUDENT QUIZ RESTORE] No active quiz participation found
🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮🎮
```

## Testing Instructions

### Test Case 1: Restore Active Quiz
1. **Student joins a Live Quiz**
   - Instructor starts a Live Quiz
   - Student clicks "JOIN LIVE QUIZ" button
   - Student sees question 1 and answers it
   - Student is on question 2

2. **Refresh the page** (F5 or Ctrl+R)

3. **Expected Result:**
   - ✅ Page loads normally
   - ✅ After ~1.5 seconds, quiz interface reappears
   - ✅ Current question (question 2) is displayed
   - ✅ Answer options are shown and clickable
   - ✅ Timer starts (if active)
   - ✅ Leaderboard shows current rankings
   - ✅ Score displays correctly (from previous answers)
   - ✅ Console shows green ✅ success logs
   - ✅ Student can continue participating normally

### Test Case 2: Restore Mid-Quiz (Answered Some Questions)
1. **Student answers 5 out of 10 questions**
   - Join quiz and answer questions 1-5
   - Currently on question 6

2. **Refresh the page**

3. **Expected Result:**
   - ✅ Quiz interface restores
   - ✅ Shows question 6 (current question)
   - ✅ Score shows points from questions 1-5
   - ✅ Leaderboard reflects current standings
   - ✅ Can answer question 6 and continue

### Test Case 3: Restore Waiting State
1. **Student joins but quiz hasn't started**
   - Student joins a "waiting" quiz
   - Instructor hasn't clicked "Start Quiz" yet

2. **Refresh the page**

3. **Expected Result:**
   - ✅ Quiz interface restores
   - ✅ Shows "Waiting for instructor..." message
   - ✅ No questions displayed yet
   - ✅ When instructor starts, student receives first question

### Test Case 4: Restore Completed Quiz
1. **Student completes entire quiz**
   - Answer all 10 questions
   - Quiz shows "Quiz Complete!"

2. **Refresh the page**

3. **Expected Result:**
   - ✅ Quiz interface restores
   - ✅ Shows "Quiz Complete!" message
   - ✅ Leaderboard shows final rankings
   - ✅ No answer options (quiz ended)

### Test Case 5: No Active Quiz
1. **Student is NOT in any quiz**
   - Either never joined or quiz ended earlier

2. **Load/Refresh the page**

3. **Expected Result:**
   - ✅ Page loads normally
   - ✅ Regular lesson content is displayed
   - ✅ No quiz interface appears
   - ✅ Console shows "No active quiz participation found"

### Test Case 6: Different Module/Class
1. **Student has active quiz in Module 1**
   - Join quiz in Module 1

2. **Navigate to Module 2** and refresh

3. **Expected Result:**
   - ✅ No quiz interface appears (different module)
   - ✅ Shows normal lesson content
   - ✅ API filters by module_id correctly

## Edge Cases Handled

### ✅ No Module Context
- Checks for `classId` and `moduleId`
- Silently exits if context missing
- Doesn't break page load

### ✅ API Failure
- Handles HTTP errors gracefully
- Logs error to console
- Continues with normal page display

### ✅ No Lesson Questions
- Checks if `window.__lessonQuestions` exists
- Cannot restore without questions
- Shows warning but doesn't crash

### ✅ Session Ended Between Check and Restore
- Handles status changes gracefully
- Shows appropriate completion state
- Doesn't try to display questions

### ✅ WebSocket Connection Issues
- Continues even if WebSocket fails
- Student can still see question
- May miss real-time updates but quiz still works

### ✅ Multiple Active Sessions (Edge Case)
- API returns first matching active session
- Only one quiz at a time per student
- Prevents confusion

## Data Flow Diagram

```
┌─────────────────┐
│  Page Loads     │
└────────┬────────┘
         │ 1.5s delay
         ▼
┌─────────────────────────────┐
│ checkAndRestoreStudentLive  │
│        Quiz()               │
└────────┬────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ GET /api/live-quiz-mvp/        │
│     my-active-session          │
└────────┬───────────────────────┘
         │
         ▼
    ┌────────────┐
    │ Has Active │
    │  Session?  │
    └─────┬──────┘
          │
    ┌─────┴─────┐
    │           │
   YES         NO
    │           │
    ▼           ▼
┌────────┐  ┌──────────────┐
│Restore │  │ Do Nothing   │
│  Quiz  │  │ (Normal Page)│
└───┬────┘  └──────────────┘
    │
    ├─► Restore State
    ├─► Show Container
    ├─► Hide Lesson Content
    ├─► Display Question
    ├─► Connect WebSocket
    ├─► Fetch Leaderboard
    └─► ✅ Done
```

## Benefits

### For Students
- ✅ **Seamless Experience** - Can refresh without losing progress
- ✅ **No Missed Questions** - Always see current question after refresh
- ✅ **Preserved Score** - All previous answers counted
- ✅ **Real-Time Sync** - WebSocket reconnects automatically
- ✅ **Stress-Free** - Accidental refresh won't ruin their quiz
- ✅ **Mobile-Friendly** - Works when browser backgrounds on mobile

### For Instructors
- ✅ **Fair for Students** - Technical issues don't penalize students
- ✅ **Less Support Needed** - Students don't lose progress
- ✅ **Better Data** - More complete participation records
- ✅ **Professional System** - Robust quiz platform

## Technical Details

### Session Storage
- Sessions stored in-memory Python dict: `_sessions`
- Keyed by `session_id` (string)
- Contains `participants` dict with user stats
- Persists for duration of server uptime

### Participant Tracking
```python
_sessions[session_id]['participants'][user_id] = {
    'display_name': 'student123',
    'total_score': 2500,
    'total_correct': 3,
    'total_answered': 3,
    'total_time_sec': 45.2,
    'last_answer_at': 1698345678.123
}
```

### State Restoration Object
```javascript
liveQuizState = {
  sessionId: "6",
  currentQuestion: { id: 3, question: "...", ... },
  currentQuestionIndex: 2,
  questions: [...],
  answered: false,
  timer: null,
  timeRemaining: 30,
  socket: {...},
  isConnected: true,
  hasJoined: true,
  quizEnded: false
}
```

### Timing
- **Restore Delay:** 1500ms (1.5 seconds) after page load
- **Reason:** Ensures DOM, WebSocket client, and context are ready
- **Adjustable:** Can be changed if needed

## API Endpoint Details

### `/api/live-quiz-mvp/my-active-session`

**Method:** GET  
**Authentication:** Required (login_required)

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| class_id | int | Optional | Filter by specific class |
| module_id | int | Optional | Filter by specific module |

**Success Response (200):**
```json
{
  "success": true,
  "has_active_session": true,
  "session": {
    "session_id": "6",
    "class_id": 7,
    "module_id": 1,
    "lesson_id": 2,
    "title": "Chapter 3 Quiz",
    "status": "active",
    "current_question_index": 2,
    "total_questions": 10,
    "participant_stats": {
      "total_score": 2500,
      "total_correct": 3,
      "total_answered": 3
    }
  }
}
```

**No Active Session Response (200):**
```json
{
  "success": true,
  "has_active_session": false,
  "session": null
}
```

**Error Response (500):**
```json
{
  "success": false,
  "error": "Error message here"
}
```

## Security Considerations

### ✅ User Authentication
- Endpoint requires `@login_required`
- Only authenticated students can check
- User can only see their own participation

### ✅ Session Validation
- Checks database for valid active sessions
- Verifies user is actually a participant
- Prevents unauthorized access to quiz data

### ✅ Scope Filtering
- Filters by class_id and module_id
- Student can't access quizzes from other classes
- Prevents cross-session contamination

## Future Enhancements (Optional)

### Possible Improvements:
1. **Local Storage Backup** - Store session_id in localStorage as fallback
2. **Progress Indicator** - Show "X of Y questions answered" during restore
3. **Answer History** - Display which questions were already answered
4. **Time Tracking** - Show total time spent in quiz
5. **Multi-Device Sync** - Allow student to switch devices mid-quiz
6. **Resume Notification** - Toast: "Resuming quiz at question 3..."
7. **Offline Support** - Queue answers if connection lost

## Conclusion

The Student Live Quiz Auto-Restore feature ensures students can refresh the page at any time without losing their quiz progress. This creates a robust, professional quiz experience that handles technical issues gracefully and keeps students engaged without interruption.

**Status:** ✅ Implemented and ready for testing  
**Compatibility:** Works alongside Instructor Auto-Restore feature
