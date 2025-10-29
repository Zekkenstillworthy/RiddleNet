# Live Quiz Instructor Control - Quick Test Guide

## 🎯 Test Scenario: Verify Instructor Control Flow

### Prerequisites
- Instructor account logged in
- Student account logged in (use different browser or incognito)
- Module with Question Group available

---

## Test 1: Block Student Join Before Instructor Starts ⏳

### Steps:
1. **Instructor:**
   - Click "Start Live Quiz" on a Question Group
   - Modal opens → Click "Create Session"
   - **DO NOT CLICK "START QUIZ" YET**
   - Note the session code (e.g., "A3X9K2")

2. **Student:**
   - Navigate to the module
   - Click "Join Live Quiz" button
   - Enter session code
   - Click "Join"

### Expected Result: ✅
```
❌ Alert: "MVP: The Live Quiz has not started yet. Please wait for your instructor to begin."
- Student should NOT see quiz interface
- Student remains on module detail page
```

### Server Log Check:
```
[LIVE_QUIZ_MVP][JOIN][BLOCKED] Session not active - instructor has not started it
```

---

## Test 2: Instructor Starts Quiz → Student Can Join ▶️

### Steps:
1. **Instructor:**
   - In the Live Quiz modal, click **"START QUIZ"**
   - Button should hide
   - "Next Question" button should appear
   - Question counter shows "Question 0/10" (or similar)

2. **Student:**
   - Click "Join Live Quiz" again
   - Enter same session code
   - Click "Join"

### Expected Result: ✅
```
✅ Student joins successfully
- Shows "Waiting for Instructor" screen (if instructor hasn't started questions yet)
- Participant count shows in header
- Leaderboard visible (may be empty if no answers yet)
```

### Server Log Check:
```
[MVP LiveQuiz] User <username> joined session <session_id> with status: active
[MVP LiveQuiz] Broadcast participant_joined to room live_quiz_<session_id>
```

---

## Test 3: Student Appears in Instructor Leaderboard Immediately 📊

### Steps:
1. **Student:** (Already joined from Test 2)
   - Wait on "Waiting for Instructor" screen

2. **Instructor:**
   - Look at `id="live-quiz-modal-body"` section
   - Check `id="instructor-leaderboard-list"` element

### Expected Result: ✅
```
✅ Instructor sees in modal:
   - Participant count: "1 Participants" (or more)
   - Leaderboard shows:
     Rank  Name       Points  Correct
     #1    Gilbert    0       0/0

✅ Toast notification:
   "MVP: Gilbert joined the quiz (1 total)"
```

### Browser Console Check (Instructor):
```javascript
[MVP LiveQuiz] Participant joined: Gilbert - Total: 1
[MVP LiveQuiz] Updating instructor leaderboard for session: <session_id>
[MVP LiveQuiz] Leaderboard data received: 1 participants
[MVP LiveQuiz] Displaying leaderboard with 1 participants
```

---

## Test 4: Instructor "Next Question" Advances All Students 🔄

### Steps:
1. **Instructor:**
   - Click **"NEXT QUESTION"** button
   - Question counter should increment: "Question 1/10"

2. **Student:**
   - Watch screen automatically

### Expected Result: ✅
```
✅ Student screen immediately updates:
   - "Waiting for Instructor" screen disappears
   - First question appears
   - Timer starts counting down (30 seconds)
   - Answer options visible
   - Leaderboard still shows on sidebar

✅ Instructor screen:
   - Question counter: "Question 1/10"
   - Leaderboard updates (if any answers submitted)
   - Toast: "MVP: Question 1/10 shown to students"
```

### Browser Console Check (Student):
```javascript
[MVP LiveQuiz] Instructor advanced to next question: 0
[MVP LiveQuiz] Updating leaderboard from next_question event
[MVP LiveQuiz] Loading question index 0
```

### Server Log Check:
```
[MVP LiveQuiz] Advancing session <id> from Q-1
[MVP LiveQuiz] Session <id> now at Q0
[MVP LiveQuiz] Broadcast next_question with leaderboard to room live_quiz_<id> - Q0
```

---

## Test 5: Verify Leaderboard Updates When Student Answers ⭐

### Steps:
1. **Student:**
   - Select an answer (correct or incorrect)
   - Click "Submit"
   - Wait for feedback

2. **Instructor:**
   - Watch leaderboard in modal

### Expected Result: ✅
```
✅ Student sees:
   - Answer feedback (correct/incorrect)
   - Points awarded (e.g., +850 for fast correct answer)
   - Updated total score
   - Leaderboard shows new rank

✅ Instructor sees:
   - Leaderboard auto-updates (via socket event)
   - Student's score increases
   - Rank may change if multiple students
```

### Browser Console Check (Instructor):
```javascript
[MVP LiveQuiz] Leaderboard update received
```

---

## Test 6: Multiple Students Sync on Next Question 👥

### Prerequisites:
- Have 2-3 students joined

### Steps:
1. **Instructor:**
   - Click "NEXT QUESTION" again
   - Question counter: "Question 2/10"

2. **All Students:**
   - Observe screens

### Expected Result: ✅
```
✅ ALL students advance simultaneously:
   - Previous question disappears
   - New question appears
   - Timers reset to 30 seconds
   - Leaderboard shows updated rankings
   - All see same question number
```

### Timing Check:
- All students should see new question within 1-2 seconds max
- No student should be "stuck" on previous question

---

## 🐛 Common Issues & Solutions

### Issue 1: Student Still Blocked After Instructor Starts
**Symptom:** Student gets 403 error even after instructor clicked "Start Quiz"

**Check:**
1. Server logs: Is session status = 'active'?
   ```sql
   SELECT id, status FROM live_quiz_session WHERE id = <session_id>;
   ```
2. Instructor API response: Was `/start` successful?
3. Browser cache: Student may need to refresh page

**Solution:** Instructor should click "Start Quiz" button, not just "Create Session"

---

### Issue 2: Instructor Leaderboard Empty
**Symptom:** `id="instructor-leaderboard-list"` shows "Waiting for participants..." even after students join

**Check:**
1. Network tab: Is `participant_joined` socket event received?
2. Browser console: Any errors in `updateInstructorLeaderboard()`?
3. Socket connection: Is instructor socket connected?

**Solution:**
```javascript
// In browser console (Instructor):
window.socket.connected  // Should be true
```

---

### Issue 3: Students Don't Advance on "Next Question"
**Symptom:** Instructor advances but students stay on current question

**Check:**
1. Student browser console: Is `next_question` event received?
2. Server logs: Is event broadcast to room?
3. Student socket: Is student in the correct room?

**Solution:**
```javascript
// In browser console (Student):
liveQuizState.socket.connected  // Should be true

// Check room membership on server:
# Should see: User <id> joined room live_quiz_<session_id>
```

---

## ✅ Success Criteria Checklist

- [ ] Students CANNOT join before instructor starts (403 error)
- [ ] Students CAN join after instructor starts (200 success)
- [ ] Students appear in `id="instructor-leaderboard-list"` immediately
- [ ] Instructor's "Next Question" advances ALL students simultaneously
- [ ] Leaderboard updates in real-time when students answer
- [ ] Participant count increments when new student joins
- [ ] Question numbers match across all clients (instructor and students)
- [ ] No console errors in browser (student or instructor)
- [ ] No server errors in logs

---

## 📊 Expected Socket Event Sequence

```
1. Instructor Creates Session
   → Status: waiting

2. Student Tries to Join
   → ❌ Blocked (403)

3. Instructor Clicks "Start Quiz"
   → POST /instructor/api/live-quiz/{id}/start
   → Status: waiting → active
   → Socket emit: quiz_started

4. Student Joins
   → POST /api/live-quiz-mvp/join
   → ✅ Success (200)
   → Socket emit: join_live_quiz
   → Socket broadcast: participant_joined (with leaderboard)
   → Socket send: quiz_state (to joiner only)

5. Instructor Clicks "Next Question"
   → POST /instructor/api/live-quiz/{id}/next-question
   → current_question_index++
   → Socket broadcast: next_question (with leaderboard)

6. Student Submits Answer
   → POST /api/live-quiz-mvp/submit-answer
   → Socket broadcast: leaderboard_update
   → Socket send: answer_result (to answerer only)

7. Instructor Clicks "Next Question" Again
   → (Repeat step 5)

8. Quiz Completes
   → Socket broadcast: quiz_ended (with final leaderboard)
```

---

## 🎬 Final Verification

After completing all tests above, confirm:

1. **Instructor Control:** Students can only join and progress when instructor allows ✅
2. **Real-time Sync:** All participants see the same question at the same time ✅
3. **Leaderboard Visibility:** Instructor sees all students in `id="live-quiz-modal-body"` ✅
4. **No Errors:** Clean console logs and server logs ✅

**If all checks pass, the Live Quiz flow is working correctly! 🎉**
