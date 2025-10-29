# Live Quiz MVP - Quick Test Guide

## 🧪 Quick Test Steps

### Setup (5 minutes)
1. **Instructor:** Navigate to Class Content Manager
2. **Instructor:** Click "Questions" tab
3. **Instructor:** Click ⚡ "Start Live Quiz" on any question group
4. **Instructor:** Note the session code (e.g., "ABC123")

### Test Scenario 1: Waiting Screen
**Goal:** Verify students see waiting message before instructor starts

1. **Student:** Open module view (different browser/incognito)
2. **Student:** Click "Join Live Quiz" button
3. **Student:** Enter session code
4. ✅ **Expected:** Student sees:
   - "MVP: Please Wait"
   - "Your instructor will start the live quiz shortly"
   - Participant count updates
   - Status badge: "Waiting for Instructor" (yellow)

5. **Instructor:** Verify participant count shows "1 participant"
6. **Student:** Verify leaderboard shows student name with 0 score

---

### Test Scenario 2: Synchronized Start
**Goal:** Verify all students see Q1 when instructor starts

1. **Instructor:** Click "Start Live Quiz" button
2. ✅ **Expected (All Students Simultaneously):**
   - Question 1 appears with timer
   - Status badge: "Active" (green)
   - Timer starts counting down from 30
   - Answer options are visible

3. ✅ **Expected (Instructor):**
   - Button changes to "Next Question"
   - Can see participant count
   - Can view live leaderboard

---

### Test Scenario 3: Next Question Sync
**Goal:** Verify all students advance together

1. **Student 1:** Answer Question 1 (select any option)
2. **Student 1:** Verify sees answer feedback and score
3. **Instructor:** Wait for students to answer (or timeout)
4. **Instructor:** Click "Next Question"
5. ✅ **Expected (All Students Simultaneously):**
   - Question 2 appears
   - Timer resets to 30 seconds
   - Previous answer feedback cleared
   - Leaderboard updated with latest scores

---

### Test Scenario 4: Leaderboard Real-Time Updates
**Goal:** Verify leaderboard syncs across all participants

1. **Student 2:** Join the quiz (add another student)
2. ✅ **Expected (All Existing Participants):**
   - Participant count updates: "2 participants"
   - Leaderboard shows Student 2 with 0 score

3. **Student 1:** Answer current question
4. ✅ **Expected (All Participants):**
   - Leaderboard updates immediately
   - Student 1's score increases
   - Ranks adjust automatically

5. **Student 2:** Answer same question
6. ✅ **Expected (All Participants):**
   - Leaderboard updates again
   - Both students' scores visible
   - Rank order updates based on speed+accuracy

---

### Test Scenario 5: Cannot Skip Ahead
**Goal:** Verify students cannot navigate independently

1. **Student:** Try to manually advance to next question
2. ✅ **Expected:**
   - No navigation controls available to student
   - Only instructor's "Next Question" advances quiz
   - Students must wait for instructor

3. **Instructor:** Click "Next Question"
4. ✅ **Expected:**
   - All students advance together
   - No student is on different question

---

## ✅ Success Criteria Checklist

### Instructor Start Control
- [ ] Students see waiting screen before start
- [ ] "Start Live Quiz" button triggers Q1 for all students
- [ ] Status changes from "Waiting" to "Active"
- [ ] Timer starts for all students simultaneously

### Next Question Control
- [ ] Only instructor can advance questions
- [ ] All students see same question at same time
- [ ] Leaderboard updates before next question
- [ ] Previous question feedback cleared

### Live Leaderboard Sync
- [ ] New joiners appear in leaderboard instantly
- [ ] Scores update in real-time when students answer
- [ ] Ranks adjust automatically
- [ ] Participant count accurate

### Session Validation
- [ ] Cannot start already-active session
- [ ] Students cannot skip ahead
- [ ] Late joiners see current question state

---

## 🐛 Common Issues & Fixes

### Issue: Student sees blank screen after joining
**Fix:** Refresh page, ensure socket connection established

### Issue: Leaderboard not updating
**Fix:** Check browser console for socket errors, verify network connection

### Issue: Questions not advancing
**Fix:** Instructor must click "Next Question" - students have no control

### Issue: Timer not synchronized
**Fix:** This is expected - timers start when question loads, may have 1-2 second variance

---

## 📊 Console Logs to Monitor

### Student Side:
```
[MVP LiveQuiz] User joining session X with status: waiting
[MVP LiveQuiz] Showing waiting screen
[MVP LiveQuiz] Instructor started quiz - loading first question
[MVP LiveQuiz] Loading question index 0
[MVP LiveQuiz] Instructor advanced to next question: 1
```

### Instructor Side:
```
[MVP LiveQuiz] Instructor starting session X
[MVP LiveQuiz] Broadcast quiz_started to room live_quiz_X
[MVP LiveQuiz] Instructor advancing session X from Q0
[MVP LiveQuiz] Broadcast next_question to room live_quiz_X - Now showing Q1
```

---

## 🎯 MVP Test Complete
If all checkboxes pass, the Live Quiz synchronization is working correctly!
