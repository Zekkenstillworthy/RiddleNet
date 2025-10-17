# Current Challenge Display - Testing Checklist

## 🧪 Pre-Test Setup

- [ ] Clear browser cache: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- [ ] Open browser DevTools Console (F12)
- [ ] Navigate to `/troubleshoot` page
- [ ] Ensure Quest Results sidebar is open (click graph icon if closed)

---

## ✅ Test 1: Challenge Activation

### Steps:
1. Click **"Foundation Learning"** button
2. Select **"Point-to-Point Topology"**
3. Look at Quest Results sidebar (right side)

### Expected Results:
- [ ] Current Challenge card appears at TOP of sidebar
- [ ] Title shows: "Point-to-Point Topology"
- [ ] Difficulty badge shows: ⭐ Level 1
- [ ] Status badge shows: "IN PROGRESS" (green)
- [ ] Timer shows: 0:00 (and starts counting)
- [ ] Progress shows: 0/2 or 1/3 Steps Completed
- [ ] Requirements list shows: "2 PCs, 1 Connection"
- [ ] Hint shows: "Place 2 PCs on the canvas" (or similar)

### Console Output:
```
🎯 Topology objectives initialized for: Point-to-Point Topology
📊 Current objectives: {moduleId: "point-to-point-topology", ...}
✅ Challenge tracker activated for: Point-to-Point Topology
```

---

## ✅ Test 2: Progress Updates

### Steps:
1. With active challenge, drag a **PC** from device palette to canvas
2. Wait 5 seconds for auto-refresh
3. Check Quest Results sidebar

### Expected Results:
- [ ] Progress bar fills slightly (e.g., 33% → 50%)
- [ ] Steps counter increases (e.g., 1/3 → 2/3)
- [ ] Timer continues incrementing (0:05, 0:10, etc.)
- [ ] Hint may change to next step
- [ ] Card remains at top of sidebar

### Console Output:
```
✅ Challenge tracker activated for: Point-to-Point Topology
📊 Current objectives: {moduleId: "point-to-point-topology", devicesPlaced: true, ...}
```

---

## ✅ Test 3: Auto-Refresh Verification

### Steps:
1. With active challenge, wait 10-15 seconds without doing anything
2. Watch the timer in Current Challenge card

### Expected Results:
- [ ] Timer increments every 5 seconds (0:05 → 0:10 → 0:15)
- [ ] No page flicker or reload
- [ ] Card remains visible and stable

---

## ✅ Test 4: Challenge Completion

### Steps:
1. Place all required devices (2 PCs for Point-to-Point)
2. Click **"WIRED"** button
3. Connect PC1 to PC2
4. Watch for auto-completion (topology validates automatically)

### Expected Results:
- [ ] Current Challenge card **disappears** from top
- [ ] Challenge moves to "Foundation Learning" completed section
- [ ] Shows ✅ checkmark
- [ ] Shows Score: 100%
- [ ] Shows time spent (e.g., ⏱️ 1:23)
- [ ] Shows completion date (e.g., 📅 10/12/2025)

### Console Output:
```
🎯 === COMPLETING TOPOLOGY MODULE: Point-to-Point Topology ===
📋 Recording result in Challenge Results Tracker...
✅ Topology module completed: Point-to-Point Topology (+15 XP)
```

---

## ✅ Test 5: Debug Commands

### Run in Console:

#### Check Current Challenge:
```javascript
window.debugCurrentChallenge()
```

#### Expected Output (When Challenge Active):
```
═══════════════════════════════════════
🎯 CURRENT CHALLENGE DEBUG (MVP)
═══════════════════════════════════════
✅ Active Challenge Found:
  ID: point-to-point-topology
  Title: Point-to-Point Topology
  Level: 1
  Progress: 1/3
  Requirements: { pc: 2, connections: 1 }
  Time Started: 10/12/2025, 3:45:23 PM
═══════════════════════════════════════
```

#### Expected Output (No Active Challenge):
```
═══════════════════════════════════════
🎯 CURRENT CHALLENGE DEBUG (MVP)
═══════════════════════════════════════
ℹ️ No active challenge found
═══════════════════════════════════════
```

---

#### Check Window Object:
```javascript
console.log(window.currentTopologyObjectives)
```

#### Expected Output (When Challenge Active):
```javascript
{
  moduleId: "point-to-point-topology",
  requirements: { pc: 2, connections: 1 },
  startTime: 1729012345678,
  completed: false,
  devicesPlaced: true
}
```

#### Expected Output (No Challenge):
```
null
```

---

## ✅ Test 6: Multiple Challenges

### Steps:
1. Complete Point-to-Point Topology
2. Immediately start **Bus Topology**
3. Check Quest Results sidebar

### Expected Results:
- [ ] Point-to-Point shows in completed section
- [ ] Bus Topology appears in Current Challenge section
- [ ] Title: "Bus Topology"
- [ ] Difficulty: ⭐⭐ Level 2 (or similar)
- [ ] Requirements: "3 PCs, 1 Switch, 3 Connections"
- [ ] Timer starts at 0:00
- [ ] No overlap or duplicate cards

---

## ✅ Test 7: Browser Compatibility

Test on multiple browsers:

### Chrome/Edge:
- [ ] Current Challenge displays correctly
- [ ] Auto-refresh works (timer updates)
- [ ] Progress bar animates smoothly
- [ ] No console errors

### Firefox:
- [ ] Current Challenge displays correctly
- [ ] Auto-refresh works (timer updates)
- [ ] Progress bar animates smoothly
- [ ] No console errors

### Safari (if available):
- [ ] Current Challenge displays correctly
- [ ] Auto-refresh works (timer updates)
- [ ] Progress bar animates smoothly
- [ ] No console errors

---

## ✅ Test 8: Mobile Responsive

### Steps:
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl + Shift + M)
3. Select mobile device (iPhone, Android)
4. Start a challenge

### Expected Results:
- [ ] Current Challenge card is visible
- [ ] Text is readable (not cut off)
- [ ] Progress bar is visible
- [ ] Hint text wraps properly
- [ ] No horizontal scrolling needed
- [ ] Card fits within viewport

---

## ✅ Test 9: Edge Case - Cancel Challenge

### Steps:
1. Start a topology challenge (don't complete it)
2. Click **"LINK UP!"** button at bottom (or navigate away)
3. Return to troubleshoot page

### Expected Results:
- [ ] Current Challenge card disappears
- [ ] No orphaned challenge data
- [ ] Quest Results shows completed challenges only (if any)
- [ ] No console errors

---

## ✅ Test 10: Performance

### Steps:
1. Start a challenge
2. Leave page open for 2-3 minutes
3. Monitor browser DevTools Performance tab

### Expected Results:
- [ ] No memory leaks (memory stable)
- [ ] CPU usage remains low (<5%)
- [ ] Auto-refresh doesn't cause lag
- [ ] Page remains responsive

---

## 🐛 Known Issues to Watch For

### Issue 1: Card Not Appearing
**Symptoms**: Challenge starts but no Current Challenge card shows  
**Debug**:
```javascript
window.debugCurrentChallenge()
console.log(window.currentTopologyObjectives)
console.log(window.challengeResultsTracker)
```
**Expected Fix**: All three should return valid objects/data

---

### Issue 2: Timer Not Updating
**Symptoms**: Timer stays at 0:00  
**Debug**:
```javascript
console.log(window.currentTopologyObjectives.startTime)
console.log(Date.now())
```
**Expected**: startTime should be a valid timestamp

---

### Issue 3: Progress Not Updating
**Symptoms**: Steps Completed doesn't increase  
**Debug**:
```javascript
console.log(window.currentTopologyObjectives.devicesPlaced)
console.log(devices.length)
```
**Expected**: devicesPlaced should be `true` after placing device

---

## 📊 Test Results Template

### Test Date: __________
### Browser: __________
### OS: __________

| Test # | Test Name | Pass/Fail | Notes |
|--------|-----------|-----------|-------|
| 1 | Challenge Activation | ⬜ | |
| 2 | Progress Updates | ⬜ | |
| 3 | Auto-Refresh | ⬜ | |
| 4 | Challenge Completion | ⬜ | |
| 5 | Debug Commands | ⬜ | |
| 6 | Multiple Challenges | ⬜ | |
| 7 | Browser Compatibility | ⬜ | |
| 8 | Mobile Responsive | ⬜ | |
| 9 | Edge Case - Cancel | ⬜ | |
| 10 | Performance | ⬜ | |

**Overall Status**: ⬜ All Passed | ⬜ Issues Found

---

## 📝 Bug Report Template

If you find issues, report using this format:

```
**Bug Title**: [Short description]

**Test Number**: [Which test from checklist]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**:
[What should happen]

**Actual Result**:
[What actually happened]

**Console Output**:
```
[Paste console errors/logs]
```

**Screenshot**:
[Attach if relevant]

**Browser**: [Chrome 119, Firefox 120, etc.]
**OS**: [Windows 11, macOS 14, etc.]
```

---

## ✅ Final Verification

After all tests pass:

- [ ] Current Challenge displays for all topology types
- [ ] Progress updates in real-time
- [ ] Timer increments correctly
- [ ] Challenges complete and move to completed section
- [ ] No console errors
- [ ] Mobile responsive works
- [ ] Performance is acceptable

**Status**: ⬜ **Ready for Production** | ⬜ **Needs Fixes**

---

**Last Updated**: October 12, 2025  
**Version**: MVP 1.1
