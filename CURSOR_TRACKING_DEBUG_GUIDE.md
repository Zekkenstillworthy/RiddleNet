# 🐛 Cursor Tracking Debug Guide

## Overview
Comprehensive debug logging has been added to all cursor tracking methods to diagnose visibility issues. All debug messages use the prefix `🖱️ [CURSOR DEBUG]` for easy filtering in the browser console.

---

## 🔍 Debug Log Locations

### 1. **Initialization (`initializeCursorTracking`)**
**What it logs:**
- Current user information
- Session ID
- Throttle settings (100ms)
- Mouse movement coordinates
- Initialization success

**Example Output:**
```
🖱️ [CURSOR DEBUG] Initializing cursor tracking system
🖱️ [CURSOR DEBUG] Current user: {id: 123, username: "Alice"}
🖱️ [CURSOR DEBUG] Session ID: "abc123"
🖱️ [CURSOR DEBUG] Setting up mousemove listener with throttle: 100ms
🖱️ [CURSOR DEBUG] Mouse moved to: {x: 450, y: 320}
✅ [CURSOR DEBUG] Cursor tracking initialized successfully
```

**What to check:**
- ✅ Does initialization run?
- ✅ Is currentUser populated correctly?
- ✅ Is sessionId present?
- ✅ Do mousemove events fire?

---

### 2. **Container Setup (`setupCursorContainer`)**
**What it logs:**
- Container creation process
- Whether container already exists
- DOM attachment verification
- Container element reference

**Example Output:**
```
🖱️ [CURSOR DEBUG] Setting up cursor container...
🖱️ [CURSOR DEBUG] Cursor container created and appended to body
🖱️ [CURSOR DEBUG] Container element: <div id="collaboration-cursor-container">
🖱️ [CURSOR DEBUG] Container in DOM: <div id="collaboration-cursor-container">
```

**What to check:**
- ✅ Is container created?
- ✅ Is container appended to document.body?
- ✅ Can getElementById find it?

---

### 3. **Cursor Updates from Server (`handleCursorUpdate`)**
**What it logs:**
- Raw data received from Socket.IO
- Normalized data structure
- Current user ID comparison
- Own cursor filtering

**Example Output:**
```
🖱️ [CURSOR DEBUG] ============================================
🖱️ [CURSOR DEBUG] Handling cursor update
🖱️ [CURSOR DEBUG] Raw data received: {userId: 456, x: 200, y: 150, username: "Bob"}
🖱️ [CURSOR DEBUG] Normalized data: {userId: 456, username: "Bob", x: 200, y: 150}
🖱️ [CURSOR DEBUG] Current user ID: 123
🖱️ [CURSOR DEBUG] Is own cursor?: false
```

**What to check:**
- ✅ Is handleCursorUpdate being called?
- ✅ Is data structure correct?
- ✅ Is it properly filtering own cursor?

---

### 4. **Cursor Creation (`createCursor`)**
**What it logs:**
- User ID and username
- Color class assignment
- DOM element creation steps
- Map storage count
- Container append operation

**Example Output:**
```
🖱️ [CURSOR DEBUG] ============================================
🖱️ [CURSOR DEBUG] Creating cursor for user: 456
🖱️ [CURSOR DEBUG] Username: Bob
🖱️ [CURSOR DEBUG] Color class: user-2
🖱️ [CURSOR DEBUG] Cursor element created
🖱️ [CURSOR DEBUG] Avatar element created
🖱️ [CURSOR DEBUG] Username label created
🖱️ [CURSOR DEBUG] Cursor stored in map. Total cursors: 1
🖱️ [CURSOR DEBUG] Cursor added to container
🖱️ [CURSOR DEBUG] Container children count: 1
✅ [CURSOR DEBUG] Cursor element created successfully
🖱️ [CURSOR DEBUG] ============================================
```

**What to check:**
- ✅ Is cursor being created?
- ✅ Are elements properly constructed?
- ✅ Is cursor added to DOM?
- ✅ Does container have children?

---

### 5. **Position Updates (`updateCursorPosition`)**
**What it logs:**
- User ID and position
- Current user comparison
- Own cursor skip logic
- Cursor existence in Map
- New cursor creation if needed
- Transform application
- Computed style verification

**Example Output:**
```
🖱️ [CURSOR DEBUG] ============================================
🖱️ [CURSOR DEBUG] Updating cursor position for user: 456
🖱️ [CURSOR DEBUG] Position data: {x: 210, y: 160}
🖱️ [CURSOR DEBUG] Current user ID: 123
🖱️ [CURSOR DEBUG] This is NOT own cursor - proceeding
🖱️ [CURSOR DEBUG] Cursor exists in map? true
🖱️ [CURSOR DEBUG] Cursor transform set to: translate(210px, 160px)
🖱️ [CURSOR DEBUG] Cursor computed style: matrix(1, 0, 0, 1, 210, 160)
✅ [CURSOR DEBUG] Cursor position updated successfully
🖱️ [CURSOR DEBUG] ============================================
```

**What to check:**
- ✅ Is position being updated?
- ✅ Is transform applied correctly?
- ✅ Does computed style match?

---

### 6. **Avatar Loading (`loadUserAvatar`)**
**What it logs:**
- Profile image URL (if provided)
- API fetch attempts
- Image load success/failure
- Fallback letter logic

**Example Output:**
```
🖱️ [CURSOR DEBUG] ============================================
🖱️ [CURSOR DEBUG] Loading avatar for user: 456
🖱️ [CURSOR DEBUG] Profile image provided? true /static/images/profiles/bob.jpg
🖱️ [CURSOR DEBUG] Using provided profile image...
✅ [CURSOR DEBUG] Profile image loaded successfully
🖱️ [CURSOR DEBUG] Image element appended to avatar
🖱️ [CURSOR DEBUG] ============================================
```

**What to check:**
- ✅ Is avatar loading attempted?
- ✅ Does image load successfully?
- ✅ Does fallback work if image fails?

---

### 7. **Socket Emission (`throttledCursorUpdate`)**
**What it logs:**
- Mouse position
- Session ID check
- Throttle timing
- Emit data structure

**Example Output:**
```
🖱️ [CURSOR DEBUG] Throttled cursor update called
🖱️ [CURSOR DEBUG] Position: x= 450 y= 320
🖱️ [CURSOR DEBUG] Session ID: abc123
🖱️ [CURSOR DEBUG] Time since last update: 105 ms
🖱️ [CURSOR DEBUG] Throttle threshold: 100 ms
✅ [CURSOR DEBUG] Emitting cursor position to server:
🖱️ [CURSOR DEBUG] Emit data: {session_id: "abc123", x: 450, y: 320, username: "Alice", user_id: 123}
```

**What to check:**
- ✅ Is throttling working correctly?
- ✅ Is sessionId present?
- ✅ Is Socket.IO emit being called?

---

### 8. **Cursor Removal (`removeCursor`)**
**What it logs:**
- User ID being removed
- Cursor existence in Map
- DOM removal operation
- Remaining cursor count

**Example Output:**
```
🖱️ [CURSOR DEBUG] ============================================
🖱️ [CURSOR DEBUG] Removing cursor for user: 456
🖱️ [CURSOR DEBUG] Cursor found in map? true
🖱️ [CURSOR DEBUG] Cursor element: <div class="collaboration-cursor">
✅ [CURSOR DEBUG] Cursor removed successfully
🖱️ [CURSOR DEBUG] Remaining cursors: 0
🖱️ [CURSOR DEBUG] ============================================
```

**What to check:**
- ✅ Is cursor being removed properly?
- ✅ Is Map being cleared?

---

### 9. **Color Assignment (`getUserColorClass`)**
**What it logs:**
- User ID
- Calculated color index (1-6)
- Final color class

**Example Output:**
```
🖱️ [CURSOR DEBUG] Getting color class for user: 456
🖱️ [CURSOR DEBUG] Calculated color index: 2
🖱️ [CURSOR DEBUG] Color class: user-2
```

---

## 🧪 Testing Procedure

### Step 1: Open Browser Console
1. Open your application
2. Press **F12** to open DevTools
3. Go to **Console** tab
4. Filter logs by typing: `🖱️`

### Step 2: Test with 2 Users
1. **User 1** (Your browser):
   - Start a collaboration session
   - Move your mouse
   - Check console for throttled emit logs

2. **User 2** (Another browser/incognito):
   - Join the same session
   - Move your mouse
   - Both users should see logs

### Step 3: Verify Each Stage

**Stage 1: Initialization**
- [ ] See "Initializing cursor tracking system"
- [ ] See "Current user" with valid ID
- [ ] See "Session ID" populated

**Stage 2: Mouse Movement (Your Browser)**
- [ ] See "Mouse moved to: {x, y}" when you move
- [ ] See "Throttled cursor update called"
- [ ] See "Emitting cursor position to server"

**Stage 3: Receiving Updates (Your Browser)**
- [ ] See "Handling cursor update" when other user moves
- [ ] See "Creating cursor for user: X"
- [ ] See "Cursor element created successfully"
- [ ] See "Cursor added to container"

**Stage 4: Visual Verification**
- [ ] Open Elements tab in DevTools
- [ ] Find `<div id="collaboration-cursor-container">`
- [ ] Check for child divs with class `collaboration-cursor`
- [ ] Verify CSS styles (position: fixed, transform values)

---

## 🚨 Common Issues & Diagnosis

### Issue 1: No Logs at All
**Symptom:** Console is empty, no cursor debug logs
**Possible Causes:**
- CollaborationRealTime not instantiated
- Script not loaded
- JavaScript error before initialization

**Check:**
```javascript
console.log(window.collaborationSystem);
// Should show CollaborationRealTime instance
```

---

### Issue 2: Init Logs But No Mouse Logs
**Symptom:** See initialization, but no "Mouse moved to" logs
**Possible Causes:**
- Event listener not attached
- Throttling issue
- Session ID missing

**Check:**
```javascript
console.log(window.collaborationSystem.sessionId);
// Should show session ID
```

---

### Issue 3: Socket Emit But No Receive
**Symptom:** See "Emitting cursor position" but no "Handling cursor update"
**Possible Causes:**
- Backend not forwarding events
- Socket.IO connection issue
- Event name mismatch

**Check:**
```javascript
// Check socket connection
console.log(window.collaborationSystem.socket.connected);
// Should be true
```

---

### Issue 4: Cursor Created But Not Visible
**Symptom:** See "Cursor element created" but nothing on screen
**Possible Causes:**
- CSS z-index conflict
- Container not in DOM
- Position off-screen

**Check in DevTools:**
1. Find cursor element in Elements tab
2. Check computed styles:
   - `position: fixed` ✓
   - `z-index: high value` ✓
   - `transform: translate(X, Y)` ✓
   - `display: block` ✓
3. Try manually setting:
   ```javascript
   document.querySelector('.collaboration-cursor').style.zIndex = '99999';
   ```

---

### Issue 5: Own Cursor Showing
**Symptom:** See your own cursor duplicate
**Possible Causes:**
- User ID mismatch (string vs number)
- currentUser not set correctly

**Check:**
```javascript
console.log('Current user:', window.collaborationSystem.currentUser);
console.log('Session ID:', window.collaborationSystem.sessionId);
```

---

## 📊 Expected Log Flow (2 Users)

### User Alice (ID: 123) - Starting Session:
```
🖱️ Initializing cursor tracking system
🖱️ Current user: {id: 123, username: "Alice"}
🖱️ Setting up cursor container...
🖱️ Cursor container created and appended to body
🖱️ Mouse moved to: {x: 100, y: 100}
🖱️ Throttled cursor update called
✅ Emitting cursor position to server
```

### User Bob (ID: 456) - Joining Session:
```
🖱️ Initializing cursor tracking system
🖱️ Current user: {id: 456, username: "Bob"}
🖱️ Handling cursor update (receives Alice's position)
🖱️ Creating cursor for user: 123
✅ Cursor element created successfully
🖱️ Updating cursor position for user: 123
🖱️ Cursor transform set to: translate(100px, 100px)
```

---

## 🎯 Quick Checklist

Run this in console to see system state:
```javascript
// Debug cursor tracking state
console.log('=== CURSOR TRACKING STATE ===');
console.log('Collaboration System:', window.collaborationSystem);
console.log('Current User:', window.collaborationSystem?.currentUser);
console.log('Session ID:', window.collaborationSystem?.sessionId);
console.log('Socket Connected:', window.collaborationSystem?.socket?.connected);
console.log('Cursors Map:', window.collaborationSystem?.cursors);
console.log('Cursor Container:', document.getElementById('collaboration-cursor-container'));
console.log('Cursor Elements:', document.querySelectorAll('.collaboration-cursor'));
console.log('============================');
```

---

## 📝 Next Steps

1. **Test with 2 browsers** to see complete log flow
2. **Identify where logs stop** - that's where the issue is
3. **Check DOM elements** if cursors are created but not visible
4. **Verify Socket.IO events** if no updates are received
5. **Report findings** with relevant log excerpts for targeted debugging

---

## 🔧 Manual Tests

### Test 1: Force Create Cursor
```javascript
window.collaborationSystem.createCursor(999, 'TestUser', 'user-1');
// Should see cursor creation logs and element in DOM
```

### Test 2: Force Update Position
```javascript
window.collaborationSystem.updateCursorPosition(999, {
    x: 200,
    y: 200,
    username: 'TestUser'
});
// Should see position update logs
```

### Test 3: Check Container
```javascript
const container = document.getElementById('collaboration-cursor-container');
console.log('Container exists:', !!container);
console.log('Container children:', container?.children.length);
console.log('Container style:', window.getComputedStyle(container));
```

---

## ✅ Success Indicators

When working correctly, you should see:
1. ✅ Initialization logs on page load
2. ✅ Mouse movement logs (throttled to 100ms)
3. ✅ Socket emit logs when moving
4. ✅ Cursor update logs when other users move
5. ✅ Cursor creation logs for new users
6. ✅ Position update logs with transform values
7. ✅ Cursor elements in DOM (`collaboration-cursor-container` with children)
8. ✅ **VISUAL**: Other users' cursors visible on screen with avatars and usernames

---

**Debug logging added:** December 2024  
**All cursor methods now have comprehensive logging**  
**Filter console by `🖱️` to see all cursor-related logs**
