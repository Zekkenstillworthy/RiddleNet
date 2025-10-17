# 🧪 Cursor Tracking Testing Guide

## 🎯 Quick Test (2 minutes)

### Setup
1. Open 2 browser windows (or 2 different browsers)
2. Window 1: Login as **Gilbert**
3. Window 2: Login as **Zen** (or another user)

### Test Steps

#### ✅ Test 1: Basic Cursor Visibility
```
Window 1: Start team session
Window 2: Join same session
Window 1: Move mouse around
```

**Expected:** Window 2 shows Gilbert's cursor with avatar and name

---

#### ✅ Test 2: Bidirectional Tracking
```
Window 2: Move mouse around
```

**Expected:** Window 1 shows Zen's cursor (different color)

---

#### ✅ Test 3: Color Coding
```
Check cursor border colors:
- User 1 (Gilbert): Blue
- User 2: Red
- User 3: Green
- etc.
```

**Expected:** Each user has distinct color

---

#### ✅ Test 4: Smooth Movement
```
Window 1: Move mouse in circles rapidly
```

**Expected:** 
- Window 2 cursor follows smoothly
- No jerky movements
- ~10 updates per second

---

#### ✅ Test 5: Cleanup on Disconnect
```
Window 2: Leave session or close tab
```

**Expected:** 
- Gilbert's cursor disappears from Window 1
- No orphaned cursors
- Console shows: 🖱️ Removing cursor for user X

---

## 🐛 Debug Console

### Check Initialization
```javascript
// Should see these logs on page load:
🖱️ Initializing cursor tracking system
✅ Cursor container created
✅ Cursor tracking initialized
```

### Check Container
```javascript
document.getElementById('collaboration-cursors')
// Should return: <div id="collaboration-cursors">
```

### Check Active Cursors
```javascript
CollaborationRealTime.instance.cursors.size
// Should return: 1 (or number of other users in session)
```

### Monitor Socket Events
```javascript
// Receiving cursors:
socket.on('cursor_moved', console.log)

// Sending cursor:
socket.on('update_cursor_position', console.log)
```

---

## ✅ Success Criteria

| Criteria | Pass |
|----------|------|
| Cursor appears for other users | ☐ |
| Own cursor NOT visible | ☐ |
| Username displayed correctly | ☐ |
| Avatar or letter initial shows | ☐ |
| Movement is smooth | ☐ |
| Different colors per user | ☐ |
| Cursor removed on disconnect | ☐ |
| No console errors | ☐ |

---

## 🎨 Visual Checklist

```
Expected Cursor Appearance:

   ┌────────┐
   │   G    │  ← Avatar (image or letter)
   │  ●     │  ← Blue border (user-1)
   └────────┘
    Gilbert   ← Username label

```

### Color Scheme
- User 1: Blue (#3498db)
- User 2: Red (#e74c3c)
- User 3: Green (#2ecc71)
- User 4: Orange (#f39c12)
- User 5: Purple (#9b59b6)
- User 6: Teal (#1abc9c)

---

## 🚨 Common Issues

### Issue: No Cursor Visible

**Check:**
1. Both users in same session?
2. Browser console for errors?
3. Container exists: `document.getElementById('collaboration-cursors')`

**Fix:** Refresh page with cache clear (Ctrl+Shift+R)

---

### Issue: Cursor Not Moving

**Check:**
1. Console shows: `🖱️ Updating cursor for user X at (x, y)`
2. Coordinates changing?

**Fix:** Check socket connection, verify backend is broadcasting

---

### Issue: Own Cursor Visible

**Check:**
Console shows: `🖱️ Skipping own cursor`

**Fix:** Should filter by user ID automatically

---

## 📊 Performance Check

### Throttling Verification
```javascript
// Count updates per second
let count = 0;
socket.on('cursor_moved', () => count++);
setTimeout(() => console.log('Updates/sec:', count), 1000);

// Expected: ~10 updates per second
```

### DOM Performance
```javascript
// Check cursor count
document.querySelectorAll('.collaboration-cursor').length
// Should equal: (number of other users in session)
```

---

## 🎥 Testing Scenarios

### Scenario 1: Single Other User
```
Users: Gilbert + Zen
Expected: 1 cursor visible on each screen
```

### Scenario 2: Multiple Users
```
Users: Gilbert + Zen + Alex
Expected: 
- Gilbert sees 2 cursors (Zen + Alex)
- Each cursor has different color
- All move independently
```

### Scenario 3: User Joins Mid-Session
```
1. Gilbert + Zen already in session
2. Alex joins
Expected: Alex's cursor appears immediately
```

### Scenario 4: User Leaves
```
1. Gilbert + Zen + Alex in session
2. Zen leaves
Expected: Zen's cursor disappears from Gilbert and Alex
```

---

## 🎯 Manual Test Script

```javascript
// Run in browser console to test manually

// 1. Check system initialized
CollaborationRealTime.instance.cursors

// 2. Create test cursor manually
CollaborationRealTime.instance.createCursor(999, 'Test User', 'user-1')

// 3. Update test cursor position
CollaborationRealTime.instance.updateCursorPosition(999, {
    x: 300,
    y: 200,
    username: 'Test User'
})

// 4. Remove test cursor
CollaborationRealTime.instance.removeCursor(999)
```

---

## 📸 Screenshot Checklist

Take screenshots to verify:

1. [ ] Cursor with avatar visible
2. [ ] Username label below cursor
3. [ ] Correct color border
4. [ ] Multiple cursors (different colors)
5. [ ] Smooth positioning

---

## ✅ Final Acceptance Test

Run through all 5 tests in sequence:

1. ✅ Basic Visibility
2. ✅ Bidirectional Tracking  
3. ✅ Color Coding
4. ✅ Smooth Movement
5. ✅ Cleanup on Disconnect

**All tests pass?** → Feature is complete! 🎉

**Any test fails?** → Check debug console and common issues section

---

**Testing Time:** 2-5 minutes  
**Required Users:** 2 minimum, 3+ recommended  
**Status:** Ready for testing
