# Live Quiz Logging - Quick Reference

## 🎯 Where to Look

### Instructor Console (Browser F12)
```
[INSTRUCTOR START]     - Start quiz button clicked ✅
[INSTRUCTOR NEXT]      - Next question button clicked ✅
[INSTRUCTOR LEADERBOARD] - Leaderboard fetched/displayed ✅
[INSTRUCTOR SOCKET]    - Socket events received ✅
```

### Student Console (Browser F12)
```
[STUDENT SOCKET]       - All socket events (quiz_started, next_question, etc.) ✅
[STUDENT LEADERBOARD]  - Leaderboard display updates ✅
```

### Server Terminal (Python)
```
[INSTRUCTOR START QUIZ]     - Instructor started quiz ✅
[INSTRUCTOR NEXT QUESTION]  - Instructor advanced question ✅
[INSTRUCTOR LEADERBOARD]    - Leaderboard API called ✅
[STUDENT JOIN]              - Student join attempt (with blocking) ✅
```

---

## 🔍 Console Color Guide

| Color | Event | Component |
|-------|-------|-----------|
| 🟢 Green | Quiz Started | Both instructor & student |
| 🔵 Cyan | Next Question | Both instructor & student |
| 🟣 Magenta | Participant Joined | Both instructor & student |
| 🟠 Orange | Answer Result | Student |
| 🔶 Dark Orange | Leaderboard Update | Student |
| 🔴 Red | Quiz Ended | Student |
| 💜 Purple | Quiz State | Student |
| 🟩 Light Green | Leaderboard Display | Student function |

---

## ✅ Key Success Indicators

### Instructor Starts Quiz
```
✅ [INSTRUCTOR START] Quiz started successfully
✅ [INSTRUCTOR START QUIZ] Session started successfully
✅ [INSTRUCTOR START QUIZ] Emitted quiz_started to room: live_quiz_123
```

### Student Joins After Start
```
✅ [STUDENT JOIN] Student joined successfully
✅ [STUDENT JOIN] Participant count: 1
✅ [STUDENT SOCKET] quiz_started event received!
```

### Question Advancement
```
✅ [INSTRUCTOR NEXT] Advanced to next question
✅ [INSTRUCTOR NEXT QUESTION] Successfully advanced to next question
✅ [STUDENT SOCKET] next_question event received!
```

### Leaderboard Updates
```
✅ [INSTRUCTOR LEADERBOARD] Leaderboard retrieved successfully
✅ [STUDENT LEADERBOARD] Leaderboard display updated
```

---

## ❌ Common Error Patterns

### Student Joins Before Instructor Starts
```
❌ [STUDENT JOIN] Blocking join - session not active
❌ [STUDENT JOIN] Students must wait for instructor to start
```

### Empty Leaderboard
```
⚠️ [STUDENT LEADERBOARD] No participants to display
```

### Socket Not Connected
```
⚠️ [STUDENT SOCKET] socketClient not connected yet
```

---

## 🐛 Quick Debug Workflow

1. **Instructor Starts Quiz**
   - Check browser console for `[INSTRUCTOR START]` (green)
   - Check terminal for `[INSTRUCTOR START QUIZ]`
   - Verify socket broadcast logged

2. **Student Tries to Join**
   - Check terminal for `[STUDENT JOIN]`
   - If blocked: Look for `❌ Blocking join` message
   - If successful: Look for `✅ Student joined successfully`

3. **Check Socket Connection**
   - Student console should show `[STUDENT SOCKET] quiz_started` (green)
   - Verify question loaded automatically

4. **Advance Question**
   - Instructor console shows `[INSTRUCTOR NEXT]` (cyan)
   - Terminal shows `[INSTRUCTOR NEXT QUESTION]`
   - Student console shows `[STUDENT SOCKET] next_question` (cyan)

5. **Verify Leaderboard**
   - Check `[INSTRUCTOR LEADERBOARD]` in both console and terminal
   - Check `[STUDENT LEADERBOARD]` in student console
   - Verify top 3 participants logged

---

## 📋 Testing Checklist

### Before Testing
- [ ] Server running with debug output
- [ ] Browser console open (F12) for both instructor and student
- [ ] Network tab ready to check API calls

### Instructor Flow
- [ ] Click Start → See green `[INSTRUCTOR START]` logs
- [ ] Verify terminal shows `[INSTRUCTOR START QUIZ]`
- [ ] Click Next → See cyan `[INSTRUCTOR NEXT]` logs
- [ ] Verify terminal shows `[INSTRUCTOR NEXT QUESTION]`
- [ ] Check leaderboard updates

### Student Flow
- [ ] Try joining before start → See blocking message
- [ ] Join after start → See green `[STUDENT SOCKET] quiz_started`
- [ ] Wait for next question → See cyan `[STUDENT SOCKET] next_question`
- [ ] Check leaderboard displays

### Socket Synchronization
- [ ] Instructor sees new participants immediately (`[INSTRUCTOR SOCKET]` magenta)
- [ ] Student receives quiz_started event
- [ ] Student receives next_question events
- [ ] Both see updated leaderboard

---

## 🔧 Log Filtering Tips

### Browser Console
```javascript
// Show only instructor logs
[INSTRUCTOR

// Show only student logs
[STUDENT

// Show only socket events
SOCKET]

// Show only leaderboard
LEADERBOARD]
```

### Terminal Output
```bash
# Save all logs to file
python run.py > debug.log 2>&1

# Filter for specific component
python run.py 2>&1 | grep "INSTRUCTOR START"
python run.py 2>&1 | grep "STUDENT JOIN"
```

---

## 📊 Expected Log Sequence

### Happy Path: Instructor Starts → Student Joins → Question Advances

1. **Instructor Clicks Start**
   ```
   [INSTRUCTOR START] 🚀 Starting Live Quiz
   [INSTRUCTOR START QUIZ] Session ID: 123
   [INSTRUCTOR START QUIZ] ✅ Session started successfully
   ```

2. **Student Joins**
   ```
   [STUDENT JOIN] User ID: 456
   [STUDENT JOIN] Session Status: active
   [STUDENT JOIN] ✅ Student joined successfully
   [STUDENT SOCKET] 🚀 quiz_started event received!
   ```

3. **Instructor Advances**
   ```
   [INSTRUCTOR NEXT] ⏭️ Moving to next question
   [INSTRUCTOR NEXT QUESTION] Before: question_index = 0
   [INSTRUCTOR NEXT QUESTION] After: question_index = 1
   [STUDENT SOCKET] ⏭️ next_question event received!
   ```

4. **Leaderboard Updates**
   ```
   [INSTRUCTOR LEADERBOARD] 📊 Fetching instructor leaderboard
   [INSTRUCTOR LEADERBOARD] Found 1 participants
   [STUDENT LEADERBOARD] 📊 Updating leaderboard display
   [STUDENT LEADERBOARD] Total participants: 1
   ```

---

## 💡 Pro Tips

1. **Use Console Timestamps**: Enable timestamps in browser console settings
2. **Split Screens**: Have instructor console, student console, and terminal visible simultaneously
3. **Filter Early**: Use console filters to focus on specific flows
4. **Save Logs**: Redirect terminal output to file for later analysis
5. **Color Codes**: Use color-coded separators to quickly identify component

---

## 📞 Quick Troubleshooting

| Symptom | Check | Expected Log |
|---------|-------|--------------|
| Student can't join | Terminal `[STUDENT JOIN]` | Should show blocking if quiz not started |
| Leaderboard empty | Browser console | Should show participant count > 0 |
| Question doesn't advance | Terminal `[INSTRUCTOR NEXT QUESTION]` | Should show index incrementing |
| Socket not working | Browser console | Should show socket connection logs |

---

**Last Updated**: Session with comprehensive logging implementation
**See Also**: `LIVE_QUIZ_LOGGING_GUIDE.md` for detailed documentation
