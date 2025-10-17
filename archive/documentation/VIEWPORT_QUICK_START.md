# 🚀 Viewport Tracking - Quick Start Guide

## What You'll See

When multiple users join the same troubleshooting lobby, you'll see:
- **Colored rectangles** showing where each user is looking on the canvas
- **Username labels** above each viewport rectangle
- **Real-time updates** as users scroll or resize their windows

---

## 5-Minute Setup & Test

### Step 1: Restart Flask (30 seconds)
```bash
# Stop current Flask server (Ctrl+C in terminal)
# Then restart:
python run.py
```
✅ **Check**: Server starts without errors

---

### Step 2: Clear Browser Cache (30 seconds)
**Option A - Hard Refresh**:
- Press **Ctrl + F5** (or Cmd + Shift + R on Mac)

**Option B - Clear Cache**:
1. Press **Ctrl + Shift + Del**
2. Select "Cached images and files"
3. Click "Clear data"

✅ **Check**: Page reloads with fresh JavaScript/CSS

---

### Step 3: Open Two Browsers (1 minute)
**Browser 1**:
1. Navigate to RiddleNet
2. Login as User A
3. Go to Troubleshooting Scenarios
4. Join a lobby

**Browser 2**:
1. Open private/incognito window (Ctrl + Shift + N)
2. Navigate to RiddleNet
3. Login as different user (User B)
4. Join the **same lobby** as User A

✅ **Check**: Both users see the canvas

---

### Step 4: Open Developer Console (30 seconds)
In both browsers:
1. Press **F12** to open DevTools
2. Go to **Console** tab
3. Look for debug messages

✅ **Check**: You see messages like:
```
👁️ [VIEWPORT DEBUG] Updating viewport for user: 1
✅ [VIEWPORT DEBUG] Viewport indicator created
```

---

### Step 5: Test Viewport Tracking (2 minutes)

#### Test 1: See Other User's Viewport
**In Browser 1**:
- Look at the canvas
- You should see a **colored rectangle** with Browser 2's username

**Expected**:
```
┌─────────────────────────────────┐
│         Your Canvas             │
│                                 │
│  [User B's view] ← Label        │
│  ╔═══════════════════╗          │
│  ║                   ║ ← Rectangle
│  ║                   ║          │
│  ╚═══════════════════╝          │
│                                 │
└─────────────────────────────────┘
```

✅ **Pass**: See colored viewport rectangle
❌ **Fail**: No rectangle visible → See Troubleshooting below

---

#### Test 2: Watch Rectangle Move
**In Browser 2**:
- Scroll up and down on the canvas

**In Browser 1**:
- Watch Browser 2's viewport rectangle move
- Should update within **500ms** of scrolling
- Movement should be **smooth** (0.3s transition)

✅ **Pass**: Rectangle moves when user scrolls
❌ **Fail**: Rectangle doesn't move → See Troubleshooting below

---

#### Test 3: Watch Rectangle Resize
**In Browser 2**:
- Make browser window narrower/wider
- Resize window height

**In Browser 1**:
- Watch Browser 2's viewport rectangle change size
- Should match new window dimensions

✅ **Pass**: Rectangle resizes when window resizes
❌ **Fail**: Rectangle size doesn't change → See Troubleshooting below

---

## 🎨 What Each User Sees

### User 1 (Red Viewport)
```
YOUR SCREEN:
┌─────────────────────────────────┐
│                                 │
│  [User 2's view] ← Teal label   │
│  ╔═══════════════════╗          │
│  ║ Teal rectangle    ║          │
│  ╚═══════════════════╝          │
│                                 │
│              [User 3's view]    │
│              ╔═══════════╗      │
│              ║ Yellow    ║      │
│              ╚═══════════╝      │
└─────────────────────────────────┘
```

### User 2 (Teal Viewport)
```
YOUR SCREEN:
┌─────────────────────────────────┐
│  [User 1's view] ← Red label    │
│  ╔═══════════════════╗          │
│  ║ Red rectangle     ║          │
│  ╚═══════════════════╝          │
│                                 │
│              [User 3's view]    │
│              ╔═══════════╗      │
│              ║ Yellow    ║      │
│              ╚═══════════╝      │
└─────────────────────────────────┘
```

**Note**: You **don't** see your own viewport (only others' viewports)

---

## 🐛 Troubleshooting

### Problem: No Viewports Visible

**Check 1 - Users in Same Lobby**:
```
Browser 1 Console:
> window.location.href
"http://localhost:5000/troubleshooting/lobby/123"

Browser 2 Console:
> window.location.href
"http://localhost:5000/troubleshooting/lobby/123"
       ← Should match! ────────────────┘
```

**Check 2 - Socket Connected**:
```javascript
// In console:
socket.connected
// Should return: true
```

**Check 3 - Viewport Data Sent**:
Look for console message:
```
👁️ [VIEWPORT DEBUG] Sending viewport data: {x: 0, y: 0, width: 1920, height: 1080}
```
❌ Missing? → JavaScript not loaded, hard refresh (Ctrl+F5)

**Check 4 - Backend Relaying**:
Check Flask console for:
```
[CURSOR DEBUG] Broadcasting to room: lobby_123
```
❌ Missing? → Backend not receiving data, restart Flask

---

### Problem: Viewports Don't Update

**Check 1 - Scroll Event Working**:
```javascript
// In console, type:
window.addEventListener('scroll', () => console.log('Scrolled!'));
// Then scroll. Should see "Scrolled!" messages
```

**Check 2 - Throttle Not Blocking**:
Wait at least **500ms** between scrolls (updates throttled to prevent spam)

**Check 3 - Viewport Data Structure**:
```javascript
// In console:
window.cursors.forEach((cursor, userId) => {
    console.log(`User ${userId}:`, cursor);
});
// Should show viewport data for each user
```

---

### Problem: Viewports Look Wrong

**Issue: Colors Not Showing**:
- Hard refresh: **Ctrl + F5**
- Clear cache and reload
- Check CSS loaded: Inspect element → Styles tab

**Issue: Labels Missing**:
```javascript
// In console:
document.querySelectorAll('.viewport-label');
// Should return NodeList with label elements
```

**Issue: Rectangles Overlap**:
- Normal behavior when users viewing same area
- Each user has unique color to distinguish

**Issue: Viewport Too Large/Small**:
- Should match actual user's browser dimensions
- Check viewport data in console:
  ```javascript
  console.log('Viewport size:', window.innerWidth, window.innerHeight);
  ```

---

### Problem: Performance Issues

**Symptom**: Page laggy with viewports

**Fix 1 - Check Update Rate**:
Viewports update max **2 times per second** (500ms throttle)
```javascript
// Verify throttle in collaboration-real-time.js:
const VIEWPORT_THROTTLE_DELAY = 500; // ms
```

**Fix 2 - Check Number of Users**:
```javascript
window.cursors.size; // How many users in lobby?
```
- 1-6 users: Should be smooth
- 6+ users: May see slight lag (normal)

**Fix 3 - Disable Blur Effect**:
If GPU struggling, temporarily disable:
```css
.viewport-indicator {
    backdrop-filter: none; /* Disable blur */
}
```

---

## 📊 Success Criteria

Your viewport tracking is working if:
- ✅ See colored rectangles for other users
- ✅ Rectangles move when users scroll
- ✅ Rectangles resize when users resize window
- ✅ Each user has unique color
- ✅ Username labels visible above rectangles
- ✅ Rectangles disappear when users leave
- ✅ Updates within 500ms of changes
- ✅ No console errors
- ✅ Smooth animations (0.3s transitions)
- ✅ Can click through viewports to canvas

---

## 🎓 Use Cases

### 1. **Pair Programming**
- Instructor sees where student is working
- Can guide: "Look at the router configuration above your current view"

### 2. **Collaborative Design**
- Team members see who's working on which part
- Avoid conflicts: "I'm placing devices in the red area, you take the blue area"

### 3. **Code Review**
- Reviewer sees what developer is looking at
- Can ask: "Scroll back to the switch configuration"

### 4. **Remote Assistance**
- Support staff sees user's current focus
- Can guide: "The button is just below your current view"

---

## 🎨 Color Reference

User colors cycle through:
1. 🔴 **Red** - User 1, 7, 13...
2. 🔵 **Teal** - User 2, 8, 14...
3. 🟡 **Yellow** - User 3, 9, 15...
4. 🌸 **Pink** - User 4, 10, 16...
5. 💜 **Magenta** - User 5, 11, 17...
6. 🔷 **Blue** - User 6, 12, 18...

Colors repeat after 6 users.

---

## 📞 Need Help?

### Console Commands

**Check if feature loaded**:
```javascript
typeof updateViewportIndicator === 'function'
// Should return: true
```

**List all viewports**:
```javascript
document.querySelectorAll('.viewport-indicator').forEach(v => {
    console.log(v.dataset.userId, v.style.left, v.style.top);
});
```

**Force viewport update**:
```javascript
window.dispatchEvent(new Event('scroll'));
```

**Check Socket.IO connection**:
```javascript
console.log('Connected:', socket.connected);
console.log('Room ID:', window.currentLobbyId);
```

---

## 📚 More Resources

- **Full Documentation**: `VIEWPORT_TRACKING_FEATURE.md`
- **Visual Guide**: `VIEWPORT_VISUAL_GUIDE.md`
- **Testing Checklist**: `VIEWPORT_TESTING_CHECKLIST.md`
- **Cursor Fix Details**: `CURSOR_TRACKING_FIX.md`

---

## ✨ Congratulations!

If you can see colored viewport rectangles showing where other users are looking, **the feature is working**! 🎉

Now you can collaborate more effectively by seeing exactly where your teammates are focused on the canvas in real-time.

**Happy collaborating!** 🚀

