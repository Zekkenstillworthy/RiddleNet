# Live Quiz Auto-Restore Feature

## Overview
Added functionality to automatically restore the Live Quiz control modal when the instructor refreshes the page, as long as there's an active or waiting Live Quiz session.

## Problem Solved
**Before:** When an instructor refreshed the page during an active Live Quiz session, the control modal would close and not reopen automatically. The quiz would continue running in the background, but the instructor lost control visibility.

**After:** The page now checks for active/waiting sessions on load and automatically reopens the control modal with the current session state.

## Implementation Details

### File Modified
`templates/instructor/class_content_manager.html`

### New Function Added
`checkAndRestoreActiveLiveQuiz()` - Runs automatically 1 second after page load

### How It Works

#### 1. **Automatic Check on Page Load**
```javascript
setTimeout(() => {
    checkAndRestoreActiveLiveQuiz();
}, 1000);
```
- Runs 1 second after page load to ensure `moduleBuilder` is initialized
- Non-intrusive - runs in background

#### 2. **Fetch Active Sessions**
```javascript
const response = await fetch(`/instructor/api/live-quiz/sessions?class_id=${classId}`);
```
- Uses existing `/instructor/api/live-quiz/sessions` endpoint
- Filters for current class
- Looks for sessions with status: `active` or `waiting`

#### 3. **Session Validation**
Checks for:
- ✅ Active class context exists
- ✅ API call succeeds
- ✅ At least one active/waiting session exists
- ✅ Session belongs to current instructor and class

#### 4. **Modal Restoration**
When an active session is found:
1. Restores `activeLiveQuizSession` variable
2. Fetches question group name from current content
3. Opens Live Quiz modal using `showLiveQuizModal()`
4. Switches from setup panel to active panel
5. Updates all session info (code, question numbers, status)
6. Shows appropriate buttons based on session status

#### 5. **UI State Restoration**
- **Session Code:** Displays the 6-character session code
- **Question Counter:** Shows current question / total questions
- **Button Visibility:**
  - `waiting` status → Shows "Start Quiz" button
  - `active` status → Shows "Next Question" button
- **Leaderboard:** Ready to fetch participant data

## Console Logging

### Success Flow
```
🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍
[LIVE QUIZ RESTORE] Checking for active sessions...
[LIVE QUIZ RESTORE] Current class ID: 5
[LIVE QUIZ RESTORE] Response: {success: true, sessions: [...]}

✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅
[LIVE QUIZ RESTORE] ✅ Active session found!
[LIVE QUIZ RESTORE] Session ID: 42
[LIVE QUIZ RESTORE] Session code: ABC123
[LIVE QUIZ RESTORE] Question group: 15
[LIVE QUIZ RESTORE] Module ID: 8
[LIVE QUIZ RESTORE] Current question: 2
[LIVE QUIZ RESTORE] Status: active
✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅

[LIVE QUIZ RESTORE] 🚀 Reopening Live Quiz modal...
[LIVE QUIZ RESTORE] ✅ Modal restored successfully!
🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍
```

### No Active Sessions
```
🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍
[LIVE QUIZ RESTORE] Checking for active sessions...
[LIVE QUIZ RESTORE] Current class ID: 5
[LIVE QUIZ RESTORE] No active or waiting sessions found
🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍🔍
```

## Testing Instructions

### Test Case 1: Restore Active Session
1. **Instructor starts a Live Quiz**
   - Click "Start Live Quiz" from question group
   - Configure settings and create session
   - Click "Start Quiz" button
   - Session should show "active" with code ABC123

2. **Refresh the page** (F5 or Ctrl+R)

3. **Expected Result:**
   - ✅ Page loads normally
   - ✅ After ~1 second, Live Quiz modal automatically opens
   - ✅ Shows session code (ABC123)
   - ✅ Shows current question number
   - ✅ "Next Question" button is visible
   - ✅ "Start Quiz" button is hidden
   - ✅ Console shows green ✅ success logs

### Test Case 2: Restore Waiting Session
1. **Instructor creates a Live Quiz but doesn't start it**
   - Click "Start Live Quiz" from question group
   - Configure settings and create session
   - **DO NOT** click "Start Quiz" button yet
   - Session should show code and "Start Quiz" button

2. **Refresh the page** (F5 or Ctrl+R)

3. **Expected Result:**
   - ✅ Page loads normally
   - ✅ After ~1 second, Live Quiz modal automatically opens
   - ✅ Shows session code
   - ✅ "Start Quiz" button is visible
   - ✅ "Next Question" button is hidden
   - ✅ Ready to start when instructor clicks "Start Quiz"

### Test Case 3: No Active Session
1. **No Live Quiz running**
   - Ensure no active or waiting sessions exist
   - Or be on a different class page

2. **Load/Refresh the page**

3. **Expected Result:**
   - ✅ Page loads normally
   - ✅ No modal appears (as expected)
   - ✅ Console shows "No active sessions found"

### Test Case 4: Multiple Active Sessions
1. **Create multiple sessions** (edge case)
   - Start Live Quiz #1, then refresh
   - Without ending it, somehow create another session

2. **Refresh the page**

3. **Expected Result:**
   - ✅ Restores the FIRST active/waiting session found
   - ✅ Modal shows correct session details

## Edge Cases Handled

### ✅ Module Builder Not Loaded
- Checks for `moduleBuilder?.currentClass?.id`
- Safely exits if not available

### ✅ API Failure
- Handles HTTP errors gracefully
- Logs error and exits without breaking page

### ✅ No Sessions Found
- Silently exits if no active/waiting sessions
- Doesn't show error to user

### ✅ Question Group Name Not Found
- Falls back to "Live Quiz" as default name
- Still opens modal with session data

### ✅ DOM Elements Not Ready
- 100ms delay after showing modal
- Ensures elements exist before updating

## Session Status Handling

| Status | Button Shown | Auto-Restored? | Description |
|--------|--------------|----------------|-------------|
| `waiting` | "Start Quiz" | ✅ Yes | Session created but not started |
| `active` | "Next Question" | ✅ Yes | Quiz in progress |
| `completed` | None | ❌ No | Quiz finished - not restored |

## Benefits

### For Instructors
- ✅ **Never lose control** - Refresh anytime without losing session
- ✅ **Seamless experience** - Modal reopens automatically
- ✅ **Clear visibility** - Always see current session state
- ✅ **Multiple tabs** - Can have multiple browser tabs open (all show the modal)

### For Students
- ✅ **Uninterrupted quiz** - Student experience not affected by instructor refresh
- ✅ **Continues working** - Quiz keeps running in background
- ✅ **Real-time updates** - Still receive WebSocket events

## Technical Details

### API Endpoint Used
```
GET /instructor/api/live-quiz/sessions?class_id={id}
```

### Response Format
```json
{
  "success": true,
  "sessions": [
    {
      "id": 42,
      "session_code": "ABC123",
      "status": "active",
      "question_group_id": 15,
      "module_id": 8,
      "class_id": 5,
      "current_question_index": 2,
      "question_count": 10,
      "created_by": 2,
      "created_at": "2025-10-29T10:30:00Z"
    }
  ]
}
```

### Timing
- **Delay:** 1000ms after page load
- **Reason:** Ensures `moduleBuilder` is fully initialized
- **Adjustable:** Can be changed if needed

## Future Enhancements (Optional)

### Possible Improvements:
1. **WebSocket Reconnection** - Automatically reconnect to live quiz room for real-time updates
2. **Multi-Session Support** - If multiple active sessions, show dropdown to select which to restore
3. **Session State Sync** - Fetch latest participant count and leaderboard data
4. **Visual Notification** - Toast message: "Restored active Live Quiz session"
5. **Local Storage Backup** - Store session ID in localStorage as backup method

## Conclusion

The auto-restore feature ensures instructors never lose visibility or control over their Live Quiz sessions, even when refreshing the page. This creates a more robust and professional experience for managing live quiz sessions.

**Status:** ✅ Implemented and ready for testing
