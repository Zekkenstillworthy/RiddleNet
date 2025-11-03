# Live Quiz - Quick Test Checklist

## ✅ Pre-Test Setup
- [ ] Server is running
- [ ] Database is up to date
- [ ] At least 10 questions in a question group
- [ ] Browser console open (F12)
- [ ] Incognito window ready for second student

---

## 🔍 Test 1: Duplicate Rendering Check
**What we're testing:** Questions should load only once, not twice.

**Steps:**
1. [ ] Instructor: Start live quiz
2. [ ] Student: Join quiz with session code
3. [ ] Student: Open browser console (F12)
4. [ ] Student: Search for text `[LOAD_QUESTION]`

**Expected Result:**
- ✅ Should see `[LOAD_QUESTION] 📖 Loading question index: 0` **exactly once**
- ✅ Should see `hasLoadedQuestion = true` log
- ❌ Should NOT see duplicate loading

**If Failed:**
- Check if `liveQuizState.hasLoadedQuestion` flag is properly set
- Check console for duplicate socket event handlers

---

## ⏰ Test 2: Automatic Progression (No Answer)
**What we're testing:** System should auto-advance even if no one answers.

**Steps:**
1. [ ] Instructor: Start quiz
2. [ ] Student: Join quiz
3. [ ] Student: **Do NOT answer** question 1
4. [ ] Both: Wait 30 seconds (watch timer countdown)
5. [ ] Both: Wait 3 more seconds

**Expected Result:**
- ✅ At 30s: Console shows `[TIMER EXPIRED] ⏰ Timer expired`
- ✅ At 30s: Correct answer appears automatically
- ✅ At 33s: Question 2 loads automatically
- ✅ Instructor counter updates to "Question 2 of 10"
- ✅ Student and instructor see same question

**If Failed:**
- Check server console for `[AUTO-ADVANCE]` logs
- Verify `auto_advance_question()` is running in socket_events.py
- Check if timer was started when quiz began

---

## 🎯 Test 3: Automatic Progression (With Answer)
**What we're testing:** Even if student answers, system should wait for timer.

**Steps:**
1. [ ] Instructor: Start quiz  
2. [ ] Student: Join quiz
3. [ ] Student: Answer question 1 **immediately** (in 2 seconds)
4. [ ] Student: Wait (do nothing)
5. [ ] Both: Observe for 30 seconds total from question start

**Expected Result:**
- ✅ At 2s: Student sees "Correct!" or "Incorrect!" feedback
- ✅ At 30s: System shows correct answer (even though already answered)
- ✅ At 33s: System advances to question 2
- ✅ All students see question 2 at exact same time (sync)

**If Failed:**
- Check if backend timer continues even after answer submission
- Verify `timer_expired` event is emitted regardless of answers

---

## 🏆 Test 4: Leaderboard Break (Every 5 Questions)
**What we're testing:** Leaderboard should show every 5 questions automatically.

**Steps:**
1. [ ] Instructor: Start quiz with 10+ questions
2. [ ] Student: Join quiz
3. [ ] Student: Answer questions 1-4 quickly (or let timer expire)
4. [ ] Both: Wait for question 5 timer to expire
5. [ ] Both: Observe screen

**Expected Result:**
- ✅ After Q5: Leaderboard appears **in question area** (not separate div)
- ✅ Leaderboard shows top 10 students with scores
- ✅ Console shows `[STUDENT SOCKET] 🏆 Showing leaderboard break for 5s`
- ✅ Countdown timer shows "Next question in 5s..."
- ✅ After 5s: Question 6 loads automatically
- ✅ Same behavior repeats at questions 10, 15, 20, etc.

**If Failed:**
- Check if `show_leaderboard_break` is true in socket event
- Verify `(question_number % 5 == 0)` logic in backend
- Check if `showLeaderboardBreakScreen()` is being called

---

## 👥 Test 5: Multi-Student Synchronization
**What we're testing:** All students should be in perfect sync.

**Steps:**
1. [ ] Instructor: Start quiz
2. [ ] Student A: Join in normal window
3. [ ] Student B: Join in incognito window
4. [ ] Student C: Join on phone/tablet
5. [ ] Student A: Answer question 1 in 5 seconds
6. [ ] Student B: Answer question 1 in 15 seconds
7. [ ] Student C: Don't answer at all
8. [ ] All: Wait for 30 seconds from question start
9. [ ] All: Observe screens

**Expected Result:**
- ✅ All 3 students see timer expire at **exact same time** (30s mark)
- ✅ All 3 students see correct answer at **exact same time**
- ✅ All 3 students advance to question 2 at **exact same time** (33s mark)
- ✅ No student can advance early by clicking
- ✅ No student gets stuck on old question

**If Failed:**
- Check if all students are in same socket room
- Verify backend emits to room, not individual sockets
- Check network tab for socket events arriving

---

## 🎓 Test 6: Instructor UI Updates
**What we're testing:** Instructor sees updates without clicking.

**Steps:**
1. [ ] Instructor: Open live quiz panel
2. [ ] Student: Join and answer questions
3. [ ] Instructor: **Do NOT click "Next Question"** button
4. [ ] Instructor: Watch the panel

**Expected Result:**
- ✅ Participant count updates when students join
- ✅ Question counter updates automatically ("Question X of Y")
- ✅ Leaderboard updates after each answer
- ✅ Toast notifications show when questions advance
- ✅ "Next Question" button is **hidden** (not visible)
- ✅ Console shows `[INSTRUCTOR SOCKET] ⏭️ next_question` logs

**If Failed:**
- Check if instructor joined the live_quiz room
- Verify instructor is listening to socket events
- Check if `connectToLiveQuizSocket()` was called

---

## 🏁 Test 7: Quiz Completion
**What we're testing:** Quiz should end automatically on last question.

**Steps:**
1. [ ] Instructor: Start quiz with exactly 5 questions
2. [ ] Student: Join quiz
3. [ ] Both: Complete all 5 questions (answer or wait)
4. [ ] Both: Wait for question 5 timer to expire

**Expected Result:**
- ✅ After Q5 timer: Correct answer shows
- ✅ After 3s: `quiz_ended` event fires
- ✅ Student sees final leaderboard
- ✅ Student sees "Quiz Complete!" message
- ✅ Instructor sees toast: "Quiz completed! Final results shown."
- ✅ Console shows `[STUDENT SOCKET] 🏁 quiz_ended`
- ✅ Backend sets session.status = 'completed'

**If Failed:**
- Check if backend detects last question properly
- Verify `is_last_question` logic in auto_advance_question
- Check if session.ended_at is set

---

## 🐛 Test 8: Rejoin After Disconnect
**What we're testing:** Student can rejoin without breaking sync.

**Steps:**
1. [ ] Instructor: Start quiz
2. [ ] Student A: Join quiz
3. [ ] Both: Complete question 1
4. [ ] Student A: Close browser tab (disconnect)
5. [ ] Instructor: Wait for question 2 to start
6. [ ] Student A: Reopen and rejoin with same code
7. [ ] Student A: Check screen

**Expected Result:**
- ✅ Student A sees question 2 (current question)
- ✅ Student A can answer question 2
- ✅ Student A's previous answers are preserved (Q1 score counted)
- ✅ Student A rejoins same socket room
- ✅ Leaderboard shows Student A's score from Q1

**If Failed:**
- Check if `loadQuestionForStudent()` loads correct question
- Verify answered_questions API endpoint works
- Check if participant record persists

---

## 📊 Console Log Verification

### Expected Student Logs (Normal Flow)
```
✅ [STUDENT SOCKET] 🚀 quiz_started event received!
✅ [STUDENT SOCKET] 📝 Loading first question (index 0)
✅ [LOAD_QUESTION] 📖 Loading question index: 0
✅ 🕒 [TIMER] Starting question timer
✅ [TIMER EXPIRED] ⏰ Timer expired for question 0
✅ [STUDENT SOCKET] ⏭️ next_question event received!
✅ [STUDENT SOCKET] Show leaderboard break: false
✅ [LOAD_QUESTION] 📖 Loading question index: 1
```

### Expected Instructor Logs
```
✅ [INSTRUCTOR SOCKET] 👤 participant_joined
✅ [INSTRUCTOR SOCKET] ⏰ timer_expired - backend timer ran out
✅ [INSTRUCTOR SOCKET] ⏭️ next_question - backend auto-advancing
✅ [INSTRUCTOR SOCKET] New question index: 1
```

### Expected Backend Logs (Terminal)
```
✅ [AUTO-ADVANCE] Timer expired for session 123 (Question #1)
✅ [AUTO-ADVANCE] Broadcast timer_expired for Q1
✅ [AUTO-ADVANCE] Advanced session 123 to question index 1
✅ [AUTO-ADVANCE] Emitted next_question (break=False) for session 123
✅ [AUTO-TIMER] Started 30s timer for session 123
```

---

## 🔥 Common Issues & Solutions

### Issue: Questions load twice
**Solution:** Check if `hasLoadedQuestion` flag is working. Search console for duplicate `[LOAD_QUESTION]` logs.

### Issue: Timer doesn't advance automatically
**Solution:** Check server terminal for `[AUTO-ADVANCE]` logs. Verify `auto_advance_question()` is being called.

### Issue: Leaderboard doesn't show at question 5
**Solution:** Check if `show_leaderboard_break: true` in socket data. Verify `(question_number % 5 == 0)` logic.

### Issue: Students out of sync
**Solution:** Check if all students are in same socket room. Verify backend emits to room, not individual clients.

### Issue: Instructor button still visible
**Solution:** Check if button has `style="display: none;"` in HTML. Verify button ID is `next-question-btn`.

---

## ✅ Test Completion Checklist

- [ ] Test 1: Duplicate Rendering (PASS/FAIL)
- [ ] Test 2: Auto Progression No Answer (PASS/FAIL)
- [ ] Test 3: Auto Progression With Answer (PASS/FAIL)
- [ ] Test 4: Leaderboard Break (PASS/FAIL)
- [ ] Test 5: Multi-Student Sync (PASS/FAIL)
- [ ] Test 6: Instructor UI Updates (PASS/FAIL)
- [ ] Test 7: Quiz Completion (PASS/FAIL)
- [ ] Test 8: Rejoin After Disconnect (PASS/FAIL)

**Overall Status:** ⏳ PENDING

**Tested By:** _____________  
**Date:** _____________  
**Notes:** _____________________________________________

---

**Need Help?**
- Check `LIVE_QUIZ_AUTO_ADVANCE_FIX.md` for implementation details
- Check `LIVE_QUIZ_CHANGES_SUMMARY.md` for code changes
- Check server console and browser console for detailed logs
