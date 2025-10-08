# 🧪 Quick Test Guide - Drag & Drop Fix

## Test Now! (Takes 2 minutes)

### Step 1: Hard Refresh
```
Press: Ctrl + F5
```
This clears the browser cache and reloads everything.

---

### Step 2: Open Console
```
Press: F12
Then click: Console tab
```

---

### Step 3: Check for Setup Log

**Look for this line**:
```
🔧 Setting up drag and drop for devices: 3 devices found
```

**What it means**:
- ✅ **"3 devices found"** = PERFECT! Drag-and-drop is ready
- ❌ **"0 devices found"** = Still broken (report this)
- ❌ **Log missing** = Script error (report console errors)

You should also see:
```
  📦 Device 1: {dataType: "router", draggable: true, children: 3}
  📦 Device 2: {dataType: "switch", draggable: true, children: 3}
  📦 Device 3: {dataType: "pc", draggable: true, children: 3}
```

---

### Step 4: Try Dragging

1. **Click and hold** the Router icon (📡)
2. **Drag** it over to the canvas
3. **Release** the mouse button

**Expected behavior**:
- ✅ Icon becomes semi-transparent while dragging
- ✅ Device appears on canvas where you dropped it
- ✅ Console shows drag event logs

---

### Step 5: Check Console Logs

**Successful drag sequence should show**:
```javascript
🚀 Drag Start Event: {currentTarget: div.device, ...}
📋 Device Info: {deviceType: "router", hasDataType: true}
✅ DataTransfer set with type: router
🎨 Visual feedback applied
↔️ Drag Over Canvas at: {x: 150, y: 100}
💧 Drop Event on Canvas: {offsetX: 150, offsetY: 100}
📦 Retrieved device type from dataTransfer: router
✅ Creating device: {type: "router", x: 150, y: 100}
🎨 Canvas redrawn after device addition
🏁 Drag End Event
🔄 Visual feedback reset
```

---

## ✅ Pass/Fail Checklist

### Visual Tests
- [ ] Device icon becomes semi-transparent when dragging
- [ ] Device icon returns to normal after drop/cancel
- [ ] Router appears on canvas after drop
- [ ] Switch can be dragged and dropped
- [ ] PC can be dragged and dropped
- [ ] Tooltip appears on hover (before drag)

### Console Tests
- [ ] "3 devices found" in console
- [ ] Drag start logs appear
- [ ] Drop logs appear
- [ ] No red error messages during drag

---

## 🐛 If It Doesn't Work

### Report These Details:

1. **Console Output** (copy all text from console)
2. **What happens when you drag**:
   - Nothing happens?
   - Icon moves but doesn't drop?
   - Console errors?
3. **Browser** (Chrome, Firefox, Edge?)
4. **Device type** (Desktop, tablet, mobile?)

---

## 🎯 Expected Result

**WORKING** ✅:
- Console shows "3 devices found"
- Drag creates device on canvas
- No errors in console
- Visual feedback works

**NOT WORKING** ❌:
- Console shows "0 devices found"
- Or drag doesn't create device
- Or console shows errors

---

## Quick Commands

### Clear Console
```
Ctrl + L (in console)
```

### Hard Refresh
```
Ctrl + F5
```

### Open DevTools
```
F12
```

### Close DevTools
```
F12 again
```

---

**Test Now** → Report results! 🚀
