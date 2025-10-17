# Quick Testing Guide - Session Poisoning Fix

## Testing the Fix

### Step 1: Clear Everything
1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Close all browser tabs** with RiddleNet
3. **Server was restarted** (in-memory cache cleared)

### Step 2: Open Console
1. Open http://127.0.0.1:5001/dynamic/simulation/70
2. Press **F12** to open Developer Console
3. Go to **Console tab**

### Step 3: Check User Info
Run this command in console:
```javascript
debugUserInfo()
```

**Expected Output**:
```
🔍 [DEBUG] ============= USER INFO DEBUG =============
🔍 [DEBUG] window.currentUser: {id: '1', username: 'Gilbert', ...}
🔍 [DEBUG] collaborationRealTime.currentUser: {id: '1', username: 'Gilbert', ...}
🔍 [DEBUG] session-data element found:
🔍 [DEBUG]   - userId: 1
🔍 [DEBUG]   - username: Gilbert
```

✅ **If you see your correct username (Gilbert), proceed to Step 4**
❌ **If you see wrong username, refresh page and try again**

### Step 4: Join Lobby
1. Click the **collaboration toggle** (people icon on right sidebar)
2. Click **"Browse Sessions"**
3. Click **"Join"** on the available lobby

### Step 5: Send Test Message
In the console, run:
```javascript
debugSendTestMessage("Testing session fix")
```

**Watch the console output - you should see**:
```
🔍 [DEBUG] Preparing to send chat message...
🔍 [DEBUG] Current user: {id: '1', username: 'Gilbert'}
💬 [DEBUG] Sending chat message: {user_id: '1', username: 'Gilbert', message: 'Testing session fix'}
💬 [DEBUG] Received chat message: {user_id: '1', username: 'Gilbert', message: 'Testing session fix'}
✅ [DEBUG] This is OWN message - adding own-message class
```

### Step 6: Check Backend Logs
Look at the **terminal/server logs**, you should see:
```
💬 [DEBUG] ============================================
💬 [DEBUG] Received collaboration chat message
💬 [DEBUG] current_user.id: 1
💬 [DEBUG] current_user.username: Gilbert
💬 [DEBUG] Created chat_message with TRUSTED data:
💬 [DEBUG]   - user_id: 1
💬 [DEBUG]   - username: Gilbert
💬 [DEBUG] TeamSession.send_chat_message called
💬 [DEBUG]   - user_id: 1
💬 [DEBUG]   - Cached username: [old username if any]
💬 [DEBUG]   - Fresh username from DB: Gilbert
✅ [DEBUG] Chat message created successfully
```

### Step 7: Visual Verification
1. Look at the **chat panel** in the collaboration sidebar
2. Your message should show **"You"** (not your username)
3. Your message should have a **different style** (blue/highlighted)
4. Other users' messages should show **their username** (not "You")

## What to Look For

### ✅ SUCCESS Indicators:
- Console shows correct user_id (1) and username (Gilbert)
- Backend logs show "Fresh username from DB: Gilbert"
- Chat displays "You" for your own messages
- No "Jemar A. Banawa" appears anywhere

### ❌ FAILURE Indicators:
- Console shows wrong user_id (3) or wrong username
- Backend logs show different username than expected
- Chat displays wrong username
- "Jemar A. Banawa" still appears

## Troubleshooting

### If you still see wrong username:

1. **Clear browser cache again**
   - Hard refresh: Ctrl+Shift+R
   - Clear all site data

2. **Check database**
   ```javascript
   // Run in console:
   fetch('/api/user/current')
     .then(r => r.json())
     .then(d => console.log('Current user from API:', d))
   ```

3. **Check Flask session**
   - Look at server logs when you load the page
   - Should see: "User Gilbert logged in" or similar

4. **Restart server again**
   ```bash
   taskkill /F /IM python.exe
   python run.py
   ```

## Additional Debug Commands

```javascript
// View all chat messages with ownership info
debugChatHistory()

// Compare user IDs manually
debugUserComparison('3')  // Replace with actual message user_id

// Refresh user from DOM
debugRefreshUser()

// Send multiple test messages
for(let i = 1; i <= 3; i++) {
  debugSendTestMessage(`Test message ${i}`)
}
```

## Expected vs Actual

### BEFORE FIX:
```
Sent:     {user_id: '1', username: 'Gilbert'}
Received: {user_id: '3', username: 'Jemar A. Banawa'} ❌
```

### AFTER FIX:
```
Sent:     {user_id: '1', username: 'Gilbert'}
Received: {user_id: '1', username: 'Gilbert'} ✅
```

---

**If the issue persists after following all steps, check:**
1. Are you logged in as user ID 1 (Gilbert)?
2. Is the database up to date?
3. Are there multiple Python processes running?
4. Is the browser using cached JavaScript files?

**Quick nuclear option:**
```bash
# Kill all Python
taskkill /F /IM python.exe

# Clear browser cache completely
# Ctrl+Shift+Delete > All time > Everything

# Restart server
python run.py

# Open in incognito/private window
```
