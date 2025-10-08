# 🧪 MVP Troubleshooting - Visual Testing Guide

## Quick Test Procedure

### 1. Start the Application
```bash
cd c:\Users\gilbe\OneDrive\Desktop\RiddleNet
python run.py
```

### 2. Navigate to Troubleshooting
```
URL: http://127.0.0.1:5001/troubleshooting
```

### 3. Select a Scenario
Click any "Start Scenario" button on a troubleshooting card

---

## Visual Checklist

### ✅ Connection Visibility Tests

#### Test 1: Line Thickness
- [ ] Connections are clearly visible (thick lines)
- [ ] Lines are 3-4px thick (thicker than before)
- [ ] Lines don't blend into background

**Expected**: Thick, clearly visible connection lines

#### Test 2: Color Distinction
Check that different connection types have distinct colors:
- [ ] Ethernet connections are **bright cyan** (#00D9FF)
- [ ] Fiber connections are **neon green** (#39FF14)
- [ ] Serial connections are **bright orange** (#F59E0B)
- [ ] Wireless connections are **purple** (#8B5CF6)

**Expected**: Each connection type has a vibrant, unique color

#### Test 3: Midpoint Indicators
- [ ] Each connection has a visible circle at midpoint
- [ ] Midpoint circles are 5-6px in size
- [ ] Midpoint circles have a subtle glow effect
- [ ] Midpoint circles match connection color

**Expected**: Clear midpoint markers on all connections

#### Test 4: Hover Effects on Connections
Move mouse over a connection:
- [ ] Cursor changes to **pointer** (hand icon)
- [ ] Connection line glows **cyan** (#00D9FF)
- [ ] Glow effect is visible (10px halo)
- [ ] Tooltip appears showing connection type
- [ ] Line becomes slightly thicker (4px)

**Expected**: Clear hover feedback with glow and tooltip

#### Test 5: Connection Selection
Click on a connection:
- [ ] Connection glows **neon green** (#39FF14)
- [ ] Selection glow is 8px wide
- [ ] Selected state is clearly visible
- [ ] Other connections remain normal
- [ ] Click empty space clears selection

**Expected**: Clear green glow on selected connection

---

### ✅ Device Visibility Tests

#### Test 6: Device Size and Clarity
- [ ] Devices are 50px in size (larger than before)
- [ ] Devices have clear borders (2-3px)
- [ ] Device colors are vibrant and distinct
- [ ] Devices don't overlap connections

**Expected**: Clear, well-sized device rendering

#### Test 7: Device Icons
Check that devices show correct emoji icons:
- [ ] Router shows: 🔀
- [ ] Switch shows: 🔌
- [ ] PC/Computer shows: 🖥️
- [ ] Laptop shows: 💻
- [ ] Printer shows: 🖨️
- [ ] Server shows: 🖥️
- [ ] Access Point shows: 📶

**Expected**: Each device type has recognizable icon

#### Test 8: Device Colors
Verify device colors match type:
- [ ] Router: **Bright Red** (#EF4444)
- [ ] Switch: **Bright Blue** (#3B82F6)
- [ ] PC/Computer: **Bright Green** (#10B981)
- [ ] Server: **Purple** (#8B5CF6)
- [ ] Printer: **Orange** (#F59E0B)

**Expected**: Vibrant, type-specific colors

#### Test 9: Device Labels
- [ ] Labels have dark background boxes
- [ ] Label text is white/light colored
- [ ] Labels are readable
- [ ] Labels don't overlap other elements

**Expected**: Clear, readable labels

#### Test 10: Device Hover Effects
Move mouse over a device:
- [ ] Cursor changes to **pointer**
- [ ] Device glows **cyan** (#00D9FF)
- [ ] Border becomes cyan (3px)
- [ ] Tooltip shows device type above device
- [ ] Hover state is clearly visible

**Expected**: Clear cyan hover feedback with tooltip

#### Test 11: Device Selection
Click on a device:
- [ ] Device glows **neon green** (#39FF14)
- [ ] Border becomes green (3px)
- [ ] Selection is clearly visible
- [ ] Click empty space clears selection

**Expected**: Clear green glow on selected device

---

### ✅ Interactive Feature Tests

#### Test 12: Cursor Behavior
Test cursor changes:
- [ ] Default cursor on empty canvas
- [ ] **Pointer** cursor when over device
- [ ] **Pointer** cursor when over connection
- [ ] Immediate cursor response (no lag)

**Expected**: Context-aware cursor changes

#### Test 13: Connection Badges
If devices have connections:
- [ ] Badge appears on device (top-right corner)
- [ ] Badge is cyan circle with number
- [ ] Number shows correct connection count
- [ ] Badge is visible but not obtrusive

**Expected**: Connection count badges on devices

#### Test 14: Status Indicators
If any connections are down/inactive:
- [ ] Red ✕ appears on connection
- [ ] Connection line is semi-transparent (50%)
- [ ] Status is clearly visible

**Expected**: Clear status indicators for inactive connections

#### Test 15: Multi-Element Interaction
Test with multiple devices and connections:
- [ ] Only one element highlighted at a time
- [ ] Hover works on all elements
- [ ] Selection works on all elements
- [ ] No visual glitches or overlaps
- [ ] Performance is smooth

**Expected**: Clean interaction with multiple elements

---

### ✅ Performance Tests

#### Test 16: Mouse Tracking
Move mouse continuously over canvas:
- [ ] No lag or stuttering
- [ ] Smooth hover detection
- [ ] Instant cursor changes
- [ ] No dropped frames

**Expected**: Smooth, responsive mouse tracking

#### Test 17: Rendering Performance
With multiple devices and connections:
- [ ] Canvas renders instantly
- [ ] No delay when hovering
- [ ] No delay when selecting
- [ ] Tooltips appear immediately

**Expected**: Fast, lag-free rendering

#### Test 18: State Changes
Rapidly hover and click elements:
- [ ] Smooth state transitions
- [ ] No visual artifacts
- [ ] No stuck states
- [ ] Proper cleanup on state changes

**Expected**: Clean state management

---

### ✅ Edge Case Tests

#### Test 19: Overlapping Elements
With overlapping connections:
- [ ] Can hover over specific connection
- [ ] Can select intended connection
- [ ] Tooltips don't overlap confusingly
- [ ] Hit detection is accurate

**Expected**: Accurate detection even with overlap

#### Test 20: Canvas Boundaries
Test near canvas edges:
- [ ] Tooltips stay within canvas
- [ ] Devices near edges are clickable
- [ ] Hover works at boundaries
- [ ] No rendering outside canvas

**Expected**: Clean rendering within boundaries

#### Test 21: Empty States
With no connections or few devices:
- [ ] Canvas renders correctly
- [ ] No console errors
- [ ] Hover still works on devices
- [ ] No null reference errors

**Expected**: Handles empty/sparse scenarios

---

## Browser Compatibility Tests

### Chrome/Edge (Chromium)
- [ ] All features work
- [ ] Emoji icons display
- [ ] Colors render correctly
- [ ] Performance is good

### Firefox
- [ ] All features work
- [ ] Emoji icons display
- [ ] Colors render correctly
- [ ] Performance is good

### Safari (if available)
- [ ] All features work
- [ ] Emoji icons display
- [ ] Colors render correctly
- [ ] Performance is good

---

## Console Error Check

Open Developer Tools (F12) → Console:
- [ ] No JavaScript errors
- [ ] No warnings (except expected)
- [ ] No network errors
- [ ] Clean console output

**Expected**: No errors in browser console

---

## Screenshot Checklist

Take screenshots for documentation:
1. [ ] Connections with vibrant colors
2. [ ] Device with hover effect (cyan glow)
3. [ ] Connection with hover effect (cyan glow)
4. [ ] Device with selection (green glow)
5. [ ] Connection with selection (green glow)
6. [ ] Tooltip showing connection type
7. [ ] Tooltip showing device type
8. [ ] Connection badges on devices
9. [ ] Full scenario view with multiple elements
10. [ ] Before/after comparison

---

## Issue Reporting Template

If you find issues, report using this template:

```
**Issue**: [Brief description]

**Test**: [Which test number]

**Browser**: [Chrome/Firefox/etc]

**Expected**: [What should happen]

**Actual**: [What actually happened]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Screenshot**: [Attach if possible]

**Console Errors**: [Any errors from F12 console]
```

---

## Success Criteria

The MVP is successful if:

### Critical (Must Pass)
- ✅ All connections are clearly visible
- ✅ Colors are vibrant and distinguishable
- ✅ Hover effects work on all elements
- ✅ Selection works correctly
- ✅ No JavaScript errors
- ✅ Performance is smooth

### Important (Should Pass)
- ✅ Tooltips display correctly
- ✅ Icons are recognizable
- ✅ Connection badges show
- ✅ Cursor changes appropriately
- ✅ Works in all major browsers

### Nice to Have
- ✅ Labels are perfectly positioned
- ✅ Glow effects are beautiful
- ✅ Edge cases handled gracefully

---

## Final Approval

After completing all tests:

```
[ ] All critical tests pass
[ ] All important tests pass
[ ] No blocking issues found
[ ] Performance is acceptable
[ ] Visual quality is good
[ ] Ready for deployment

Tester: ___________________
Date: _____________________
Signature: ________________
```

---

## Quick Video Demo Script

If recording a demo:

1. **Open troubleshooting page** (5 sec)
2. **Show clear connection visibility** (10 sec)
3. **Hover over connection** - show glow and tooltip (10 sec)
4. **Click connection** - show selection (5 sec)
5. **Hover over device** - show glow and tooltip (10 sec)
6. **Click device** - show selection (5 sec)
7. **Show multiple elements** - demonstrate clarity (15 sec)
8. **Show connection badges** on devices (10 sec)

**Total**: ~70 seconds demo

---

**Testing Guide Version**: 1.0  
**Last Updated**: October 7, 2025  
**Status**: Ready for Testing ✅
