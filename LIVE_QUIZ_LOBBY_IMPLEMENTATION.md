# Live Quiz Lobby/Waiting Room Implementation

## Overview
Implemented a lobby/waiting room experience for students joining Live Quizzes before the instructor starts them. Previously, students were blocked with an MVP alert when clicking the "Live Quiz" button during 'waiting' status. Now they can enter a lobby that shows:
- Waiting message with animated hourglass icon
- Real-time participant count
- Auto-transition to quiz when instructor starts

## Changes Made

### 1. Frontend - Button Click Handler (`templates/user/module_detail.html`)

**Location:** Line ~4911 in `handleLiveQuizClick()`

**Before:**
```javascript
if (status === 'waiting') {
    console.log('[LiveQuiz][MVP] Quiz session is waiting - instructor has not started it yet');
    alert('MVP: The Live Quiz has not started yet. Please wait for your instructor to begin.');
    return;
}

joinLiveQuizSession(sessionId);
```

**After:**
```javascript
// Allow joining 'waiting' or 'active' sessions (lobby flow)
// Block only 'completed' sessions
if (status === 'completed') {
    console.log('[LiveQuiz][MVP] Quiz session has ended');
    alert('This Live Quiz has already ended.');
    return;
}

if (!status || (status !== 'waiting' && status !== 'active')) {
    console.log('[LiveQuiz][MVP] Invalid session status:', status);
    return;
}

console.log('[LiveQuiz][MVP] Joining session with status:', status);
joinLiveQuizSession(sessionId);
```

### 2. Backend - Join Endpoint (`api/live_quiz_api.py`)

**Location:** Line ~146 in `/api/live-quiz-mvp/join` route

**Before:**
```python
if db_session.status != 'active':
    print(f'[STUDENT JOIN] ❌ BLOCKED: Session status is "{db_session.status}" (not "active")')
    return jsonify({
        'success': False,
        'error': 'MVP: The Live Quiz has not started yet. Please wait for your instructor to begin.',
        'status': db_session.status,
        'waiting': True
    }), 403
```

**After:**
```python
# Allow joining 'waiting' or 'active' sessions (lobby flow enabled)
# Block only 'completed' sessions
if db_session.status == 'completed':
    print(f'[STUDENT JOIN] ❌ BLOCKED: Session has ended')
    return jsonify({
        'success': False,
        'error': 'This Live Quiz has already ended.',
        'status': db_session.status
    }), 403

if db_session.status not in ['waiting', 'active']:
    print(f'[STUDENT JOIN] ❌ BLOCKED: Invalid session status "{db_session.status}"')
    return jsonify({
        'success': False,
        'error': 'Cannot join this quiz session.',
        'status': db_session.status
    }), 403

print(f'[STUDENT JOIN] ✅ Status check passed - session is {db_session.status}')
```

### 3. Backend - Include Session Status in Response (`api/live_quiz_api.py`)

**Location:** Line ~217 in join endpoint response

**Added:**
```python
# Get session status from database
session_status = 'active'  # Default fallback
try:
    from user.models.live_quiz import LiveQuizSession
    db_session = LiveQuizSession.query.get(int(session_id))
    if db_session:
        session_status = db_session.status
        print(f'[STUDENT JOIN] Including session status in response: {session_status}')
except Exception as e:
    print(f'[STUDENT JOIN] Could not fetch session status: {e}')

return jsonify({
    'success': True,
    'session': {
        'id': session_id,
        'class_id': class_id,
        'module_id': module_id,
        'lesson_id': lesson_id,
        'status': session_status  # <-- NEW FIELD
    },
    'participant': participants[uid],
    'leaderboard': leaderboard_snapshot
})
```

### 4. Frontend - Join Flow with Status Check (`templates/user/module_detail.html`)

**Location:** Line ~4994 in `joinLiveQuizSession()`

**Added:**
```javascript
// Check session status - show lobby if 'waiting', start quiz if 'active'
const sessionStatus = joinData.session?.status || 'active';
console.log('[LiveQuiz][Join] Session status:', sessionStatus);

if (sessionStatus === 'waiting') {
    console.log('[LiveQuiz][Join] Session is waiting - showing lobby');
    initializeLiveQuizWithLobby(sessionId, formattedQuestions);
} else {
    console.log('[LiveQuiz][Join] Session is active - starting quiz');
    initializeLiveQuiz(sessionId, formattedQuestions);
}
```

### 5. Frontend - New Lobby Initialization Function (`templates/user/module_detail.html`)

**Location:** Line ~5085 (before `initializeLiveQuiz`)

**Added:**
```javascript
// Initialize Live Quiz with Lobby (for 'waiting' status)
function initializeLiveQuizWithLobby(sessionId, questions) {
  console.log('[LiveQuiz][Lobby] Initializing lobby for session:', sessionId);
  console.log('[LiveQuiz][Lobby] Questions ready:', questions.length);
  
  liveQuizState.sessionId = sessionId;
  liveQuizState.questions = questions;
  liveQuizState.hasJoined = false;
  liveQuizState.quizEnded = false;
  
  // Show live quiz container
  const liveQuizContainer = document.getElementById('liveQuizContainer');
  if (liveQuizContainer) {
    liveQuizContainer.style.display = 'block';
  }
  
  // Hide lesson content when Live Quiz is active
  const lessonContent = document.querySelector('.lesson-content');
  if (lessonContent) {
    lessonContent.style.display = 'none';
  }
  
  // Set session code display
  const sessionCodeEl = document.getElementById('liveSessionCode');
  if (sessionCodeEl) {
    sessionCodeEl.textContent = sessionId || '------';
  }
  
  // Hide live quiz button
  const buttonContainer = document.getElementById('liveQuizButtonContainer');
  if (buttonContainer) buttonContainer.style.display = 'none';
  
  // Connect to socket
  connectToLiveQuiz();
  
  // Show waiting lobby UI
  showWaitingForInstructor();
  
  // Fetch initial leaderboard to show participant count
  fetch(`/api/live-quiz-mvp/leaderboard/${sessionId}`)
    .then(res => res.json())
    .then(data => {
      if (data.success && data.leaderboard) {
        console.log('[LiveQuiz][Lobby] Initial leaderboard:', data.leaderboard);
        updateLeaderboard(data.leaderboard);
        
        // Update participant count in lobby
        const participantCountEl = document.getElementById('participantCountWaiting');
        if (participantCountEl) {
          const count = data.leaderboard.length;
          participantCountEl.textContent = `${count} student${count !== 1 ? 's' : ''} waiting`;
        }
      }
    })
    .catch(err => console.error('[LiveQuiz][Lobby] Error fetching initial leaderboard:', err));
}
```

### 6. Frontend - Real-Time Lobby Participant Count (`templates/user/module_detail.html`)

**Location:** Line ~5262 in `participant_joined` event handler

**Added:**
```javascript
// Update lobby participant count if visible
const participantCountEl = document.getElementById('participantCountWaiting');
if (participantCountEl) {
    const count = data.participant_count;
    participantCountEl.textContent = `${count} student${count !== 1 ? 's' : ''} waiting`;
    console.log('[STUDENT SOCKET] ✅ Lobby participant count updated');
}
```

## User Flow

### Before (MVP Alert)
1. Instructor creates Live Quiz → Session status = 'waiting'
2. Student sees pulsing "Live Quiz" button
3. Student clicks button
4. **Alert:** "MVP: The Live Quiz has not started yet. Please wait for your instructor to begin."
5. Student stuck on lesson page, needs to keep clicking button
6. Instructor starts quiz → Session status = 'active'
7. Student clicks button again → Finally enters quiz

### After (Lobby Flow)
1. Instructor creates Live Quiz → Session status = 'waiting'
2. Student sees pulsing "Live Quiz" button
3. Student clicks button
4. **Lobby displayed:**
   - Animated hourglass icon
   - "MVP: Please Wait" message
   - "Your instructor will start the live quiz shortly"
   - Real-time participant count (e.g., "3 students waiting")
5. Other students join → Participant count updates in real-time
6. Instructor starts quiz → Session status = 'active'
7. **Auto-transition:** `quiz_started` WebSocket event triggers `loadQuestion(0)`
8. Student immediately sees first question

## WebSocket Events Leveraged

### Existing Events (No Changes Needed)
- `quiz_started`: Already calls `loadQuestion(0)` to transition from lobby to quiz
- `participant_joined`: Now updates lobby participant count
- `quiz_state`: Already handles status transitions

## Existing Functions Reused

### `showWaitingForInstructor()` (Line ~5342)
- Already implemented lobby UI
- Shows hourglass icon, waiting message, participant count placeholder
- Called by new `initializeLiveQuizWithLobby()` function

### `loadQuestion(index)` (Line ~5470+)
- Transitions from lobby to quiz by loading first question
- Called automatically when `quiz_started` event fires

## Testing Checklist

### Scenario 1: Join Before Start (New Lobby Flow)
- [ ] Instructor creates Live Quiz
- [ ] Student clicks "Live Quiz" button while status='waiting'
- [ ] Lobby displays with hourglass and "Please Wait" message
- [ ] Participant count shows "1 student waiting"
- [ ] Second student joins → Count updates to "2 students waiting"
- [ ] Instructor clicks "Start Live Quiz"
- [ ] Both students auto-transition to first question

### Scenario 2: Join After Start (Existing Flow)
- [ ] Instructor creates and starts Live Quiz (status='active')
- [ ] Student clicks "Live Quiz" button
- [ ] Quiz immediately loads first question (skips lobby)
- [ ] Student can answer and see leaderboard

### Scenario 3: Completed Quiz Block (New Guard)
- [ ] Instructor ends Live Quiz (status='completed')
- [ ] Student clicks "Live Quiz" button
- [ ] Alert: "This Live Quiz has already ended."
- [ ] Button click blocked

### Scenario 4: Real-Time Updates in Lobby
- [ ] Multiple students in lobby (status='waiting')
- [ ] New student joins
- [ ] All students see participant count increment
- [ ] Instructor starts quiz
- [ ] All students see first question simultaneously

## Files Modified
1. `templates/user/module_detail.html`:
   - `handleLiveQuizClick()` - Removed alert, allow waiting/active
   - `joinLiveQuizSession()` - Added status check and lobby routing
   - `initializeLiveQuizWithLobby()` - NEW function for lobby initialization
   - `participant_joined` handler - Added lobby count update

2. `api/live_quiz_api.py`:
   - `/api/live-quiz-mvp/join` - Allow joining waiting/active, block completed
   - Join response - Include `session.status` field

## Dependencies
- WebSocket infrastructure (Socket.IO) - Already implemented
- `showWaitingForInstructor()` function - Already existed
- `quiz_started` event broadcast - Already implemented by instructor API
- Module rooms (`module_{id}`) - Already implemented

## Benefits
✅ **Improved UX**: No more blocking alerts, students wait in lobby  
✅ **Real-Time Awareness**: See other students joining in real-time  
✅ **Auto-Transition**: Seamless start when instructor begins quiz  
✅ **Code Reuse**: Leveraged existing lobby UI and WebSocket events  
✅ **Backward Compatible**: Active sessions still work as before

## No Breaking Changes
- Students joining active quizzes bypass lobby (existing behavior)
- Instructor controls unchanged (create → start → end flow)
- WebSocket events unchanged (existing handlers work as-is)
- Database schema unchanged (uses existing `status` field)
