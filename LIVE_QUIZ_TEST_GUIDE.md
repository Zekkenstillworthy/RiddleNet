# 🚀 Live Quiz MVP - Quick Test Guide

## Pre-Test Checklist

- [ ] Server is running: `python run.py`
- [ ] Database migrations applied (008, 009)
- [ ] At least 1 question group with multiple-choice questions exists
- [ ] At least 1 instructor account exists
- [ ] At least 1 student account exists
- [ ] Class ID 7 exists (or update test URLs)
- [ ] Module ID 1 exists (or update test URLs)

## 🎯 5-Minute MVP Test

### Test 1: Instructor Creates Quiz ✅

1. **Login**: `http://127.0.0.1:5001/instructor/login`
2. **Navigate**: `http://127.0.0.1:5001/instructor/class-content-selector?class_id=7`
3. **Go to**: Classwork tab → Question Groups
4. **Click**: ⚡ "Start Live Quiz" button on any question group
5. **Expected**: Modal appears with quiz settings
6. **Fill**: Leave defaults or customize
7. **Click**: "Create Session"
8. **Expected**: 
   - ✅ Success message
   - ✅ Session code displayed (e.g., "ABC123")
   - ✅ UI switches to "Active Panel"
   - ✅ Shows: Session Code, 0/N questions, 0 participants

### Test 2: Student Sees Notification ✅

1. **Login** (different browser/incognito): `http://127.0.0.1:5001/login`
2. **Navigate**: `http://127.0.0.1:5001/class/7/module/1?lesson_id=2`
3. **Expected**:
   - ❌ If status='waiting': No notification yet (quiz not started)
   - ✅ If status='active': Blue notification banner appears
   - Banner shows: "Live Quiz Active! Join now to compete!"
   - "Join Now" and "Later" buttons visible

### Test 3: Student Joins Quiz ✅

1. **Click**: "Join Now" button
2. **Expected**:
   - ✅ Notification disappears
   - ✅ Live quiz interface appears
   - ✅ Shows "Waiting for quiz to start..." (if status='waiting')
   - ✅ Shows session code
   - ✅ Participant count increments

### Test 4: Instructor Starts Quiz ✅

1. **Switch to**: Instructor browser
2. **Verify**: Participant count = 1 (or more)
3. **Click**: "Start Quiz" button
4. **Expected**:
   - ✅ Button changes to "Next Question"
   - ✅ Current question shows: 1/N
   - ✅ Status badge: "Active"

### Test 5: Student Sees First Question ✅

1. **Switch to**: Student browser
2. **Expected** (auto-triggered by socket event):
   - ✅ First question appears
   - ✅ Timer starts counting down
   - ✅ Multiple choice options appear
   - ✅ Question number: "Question 1 of N"

### Test 6: Student Answers Question ✅

1. **Click**: Any answer option
2. **Expected**:
   - ✅ Option highlights
   - ✅ Answer submits automatically (or shows submit button)
   - ✅ Feedback appears:
     - Green checkmark if correct
     - Red X if incorrect
   - ✅ Points awarded displayed
   - ✅ Leaderboard updates with student's score
   - ✅ Student's rank shown

### Test 7: Instructor Advances Question ✅

1. **Switch to**: Instructor browser
2. **Click**: "Next Question" button
3. **Expected**:
   - ✅ Question counter: 2/N
   - ✅ Leaderboard refreshes

### Test 8: Student Auto-Advances ✅

1. **Switch to**: Student browser
2. **Expected** (auto-triggered by socket event):
   - ✅ Next question appears automatically
   - ✅ Timer resets to 30 seconds
   - ✅ New options displayed
   - ✅ Previous answer feedback cleared

### Test 9: Complete Quiz ✅

1. **Repeat**: Tests 6-8 until all questions answered
2. **Instructor clicks**: "Next Question" on last question
3. **Expected**:
   - ✅ "Next Question" button disappears
   - ✅ Message: "Quiz completed!"
   - ✅ Final leaderboard shown

### Test 10: Final Results ✅

1. **Student browser**:
   - ✅ Quiz completion screen appears
   - ✅ Final score displayed
   - ✅ Rank displayed
   - ✅ Podium shows top 3
   - ✅ Full leaderboard below
   
2. **Instructor browser**:
   - ✅ Final leaderboard visible
   - ✅ All participant scores saved
   - ✅ Can close modal

## 🐛 Common Issues & Fixes

### Issue: 404 on `/instructor/api/live-quiz/session/3/start`
**Status**: ✅ FIXED (route aliases added)
**Test**: Should now work with both URL formats

### Issue: Student doesn't see notification
**Check**:
- [ ] Browser console for errors
- [ ] `live_quiz_sessions` variable in page source
- [ ] Quiz status is 'active' or 'waiting'
- [ ] Student is in correct module/lesson

**Fix**:
```javascript
// Open browser console (F12) and run:
console.log('Live quiz sessions:', liveQuizSessions);
```

### Issue: Socket.IO not connecting
**Check**:
- [ ] Socket.IO loaded: Check for `<script src="/static/socket.io/socket.io.js"></script>`
- [ ] Server logs show: "✅ Connected to collaboration server"

**Fix**:
```javascript
// In browser console:
if (typeof io === 'undefined') {
    console.error('Socket.IO not loaded!');
} else {
    console.log('Socket.IO available');
}
```

### Issue: Leaderboard empty
**Check**:
- [ ] Student submitted at least one answer
- [ ] Database has `live_quiz_participants` entries
- [ ] `is_active=True` for participants

**Fix**: Check database:
```sql
SELECT * FROM live_quiz_participants WHERE session_id = 3;
SELECT * FROM live_quiz_responses WHERE session_id = 3;
```

### Issue: Questions not advancing
**Check**:
- [ ] Socket event `next_question` firing
- [ ] Student is listening to socket events
- [ ] Network tab shows socket connection

**Fix**: Check browser console for socket messages:
```javascript
// Should see:
// "Next question: {question_index: 1, timestamp: ...}"
```

## 📊 Database Verification

### Check Session Created
```sql
SELECT id, session_code, status, title, created_at 
FROM live_quiz_sessions 
ORDER BY created_at DESC 
LIMIT 5;
```

### Check Participants
```sql
SELECT p.id, p.display_name, p.total_score, p.total_correct, p.rank, s.session_code
FROM live_quiz_participants p
JOIN live_quiz_sessions s ON p.session_id = s.id
WHERE s.session_code = 'ABC123';  -- Replace with actual code
```

### Check Responses
```sql
SELECT r.id, p.display_name, r.question_id, r.is_correct, r.points_awarded, r.response_time
FROM live_quiz_responses r
JOIN live_quiz_participants p ON r.participant_id = p.id
WHERE r.session_id = 3  -- Replace with actual session_id
ORDER BY r.created_at;
```

### Check Leaderboard Rankings
```sql
SELECT 
    display_name,
    total_score,
    total_correct,
    total_answered,
    rank,
    (total_correct * 1000 - total_time::int) as rank_score
FROM live_quiz_participants
WHERE session_id = 3
ORDER BY rank_score DESC;
```

## 🔬 Advanced Testing

### Test Multiple Students (3+ browsers)
1. Open 3+ incognito windows
2. Login as different students in each
3. All join same quiz
4. Submit different answers
5. Verify leaderboard ranks correctly

### Test Real-Time Updates
1. Student 1 submits answer
2. Immediately check Student 2's leaderboard
3. Should update within 1 second

### Test Mid-Quiz Join
1. Start quiz with Student 1
2. Advance to question 2
3. Student 2 joins mid-quiz
4. Verify Student 2 can still participate

### Test Speed Scoring
1. Student 1 answers in 5 seconds → ~750 points
2. Student 2 answers in 25 seconds → ~500 points
3. Both correct → Student 1 ranks higher

## 📝 Test Results Template

```
Live Quiz MVP Test Results
==========================
Date: _______________
Tester: _______________

✅ / ❌  Instructor creates quiz
✅ / ❌  Student sees notification
✅ / ❌  Student joins quiz
✅ / ❌  Instructor starts quiz
✅ / ❌  Student sees first question
✅ / ❌  Student answers question
✅ / ❌  Instructor advances question
✅ / ❌  Student auto-advances
✅ / ❌  Quiz completes successfully
✅ / ❌  Final results display

Socket.IO Events:
✅ / ❌  quiz_started fires
✅ / ❌  next_question fires
✅ / ❌  leaderboard_update fires
✅ / ❌  quiz_ended fires

Performance:
- Students tested: ___
- Questions tested: ___
- Total time: ___ minutes
- Errors encountered: ___

Notes:
_________________________________
_________________________________
_________________________________
```

## 🎉 Success Indicators

You know the MVP works when:

1. ✅ Instructor creates quiz in < 30 seconds
2. ✅ Student joins with 1 click
3. ✅ Questions appear instantly when instructor clicks "Start"
4. ✅ Leaderboard updates within 1 second of answer submission
5. ✅ All students advance simultaneously to next question
6. ✅ Final rankings match expected scores
7. ✅ No JavaScript errors in console
8. ✅ No Python errors in server logs
9. ✅ Database has all participant/response records
10. ✅ Can run multiple quizzes sequentially without issues

## 🆘 Emergency Troubleshooting

### Complete Reset
```bash
# Stop server
Ctrl+C

# Restart server
python run.py
```

### Clear Quiz Sessions
```sql
-- Only use if stuck!
DELETE FROM live_quiz_responses;
DELETE FROM live_quiz_participants;
DELETE FROM live_quiz_sessions;
```

### Check Server Logs
Look for:
- ✅ "✅ Quiz created with code: ABC123"
- ✅ "✅ Student joined live quiz"
- ✅ "✅ Instructor started live quiz"
- ✅ "✅ Connected to collaboration server"

### Check Browser Console
Look for:
- ✅ "Connected to live quiz"
- ✅ "Quiz started: {...}"
- ✅ "Next question: {...}"
- ✅ "Leaderboard update: {...}"

---

**Ready to test? Start with Test 1! 🚀**
