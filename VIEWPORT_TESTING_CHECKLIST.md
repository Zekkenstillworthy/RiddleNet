# Viewport Tracking - Testing Checklist

## 🎯 Testing Overview
This checklist covers all scenarios to verify viewport tracking works correctly.

---

## ✅ Pre-Test Setup

### 1. Environment Preparation
- [ ] Flask application restarted (`python run.py`)
- [ ] Browser cache cleared (Ctrl+Shift+Del) or hard refresh (Ctrl+F5)
- [ ] Console open in DevTools (F12)
- [ ] Multiple browser windows ready (2-3 minimum)

### 2. Login & Access
- [ ] Multiple test accounts logged in
- [ ] All users joined the same lobby
- [ ] Dynamic simulation page loaded for all users

---

## 📱 Core Functionality Tests

### Test 1: Initial Viewport Display
**Objective**: Verify viewports appear when users join

**Steps**:
1. User A joins lobby
2. User B joins same lobby

**Expected Results**:
- [ ] User A sees User B's viewport rectangle appear
- [ ] User B sees User A's viewport rectangle appear
- [ ] Each viewport has correct username label
- [ ] Viewport colors are different for each user
- [ ] Console shows: `👁️ [VIEWPORT DEBUG] Updating viewport for user: X`

**Pass/Fail**: ___________

---

### Test 2: Scroll Tracking
**Objective**: Verify viewport updates when scrolling

**Steps**:
1. User A scrolls down on canvas
2. Observe User B's screen

**Expected Results**:
- [ ] User A's viewport rectangle moves down on User B's screen
- [ ] Movement is smooth (0.3s transition)
- [ ] Updates occur within 500ms of scroll
- [ ] Console shows viewport data updates
- [ ] Rectangle stays same size

**Pass/Fail**: ___________

---

### Test 3: Window Resize
**Objective**: Verify viewport size changes on resize

**Steps**:
1. User A resizes browser window (make narrower)
2. Observe User B's screen

**Expected Results**:
- [ ] User A's viewport rectangle shrinks on User B's screen
- [ ] Width and height update correctly
- [ ] Position remains correct
- [ ] Smooth transition occurs
- [ ] Console shows new dimensions

**Pass/Fail**: ___________

---

### Test 4: Multiple Users
**Objective**: Test with 3+ simultaneous users

**Steps**:
1. Users A, B, and C all join lobby
2. Each user scrolls to different area
3. Each user has different screen size

**Expected Results**:
- [ ] All viewports visible simultaneously
- [ ] No viewport overlap conflicts
- [ ] Each user has unique color
- [ ] All viewport labels readable
- [ ] Performance remains smooth

**Pass/Fail**: ___________

---

### Test 5: Cursor + Viewport Interaction
**Objective**: Verify cursors and viewports work together

**Steps**:
1. User A moves cursor inside their viewport
2. User A moves cursor outside their viewport
3. Observe User B's screen

**Expected Results**:
- [ ] Cursor visible when inside viewport
- [ ] Cursor visible when outside viewport
- [ ] Cursor appears above viewport (z-index correct)
- [ ] Both update independently
- [ ] No performance issues

**Pass/Fail**: ___________

---

## 🎨 Visual Tests

### Test 6: Color Assignment
**Objective**: Verify color cycling works

**Steps**:
1. Join users sequentially (User 1, 2, 3, 4, 5, 6, 7)
2. Note each user's viewport color

**Expected Results**:
- [ ] User 1: Red (`rgba(255, 107, 107, 0.6)`)
- [ ] User 2: Teal (`rgba(78, 205, 196, 0.6)`)
- [ ] User 3: Yellow (`rgba(255, 230, 109, 0.6)`)
- [ ] User 4: Pink (`rgba(255, 140, 148, 0.6)`)
- [ ] User 5: Magenta (`rgba(196, 69, 105, 0.6)`)
- [ ] User 6: Blue (`rgba(64, 115, 158, 0.6)`)
- [ ] User 7: Red (cycles back)

**Pass/Fail**: ___________

---

### Test 7: Label Visibility
**Objective**: Test viewport labels in various positions

**Steps**:
1. User A scrolls to top of page
2. User A scrolls to middle of page
3. User A scrolls to bottom of page

**Expected Results**:
- [ ] Label always visible above viewport
- [ ] Label doesn't get cut off at edges
- [ ] Username text readable
- [ ] Background color matches viewport
- [ ] Font size appropriate (11px)

**Pass/Fail**: ___________

---

### Test 8: Transparency & Blur
**Objective**: Verify visual effects work

**Steps**:
1. Viewport overlays canvas content
2. Check for backdrop blur effect

**Expected Results**:
- [ ] Canvas visible through viewport (5% opacity)
- [ ] Slight blur visible (`backdrop-filter: blur(2px)`)
- [ ] Border clearly visible (2px dashed)
- [ ] Not too intrusive
- [ ] Maintains visibility

**Pass/Fail**: ___________

---

## 🔄 Edge Case Tests

### Test 9: User Leaves
**Objective**: Test viewport cleanup

**Steps**:
1. User A and B in lobby
2. User A closes browser/leaves lobby
3. Observe User B's screen

**Expected Results**:
- [ ] User A's viewport disappears immediately
- [ ] User A's cursor also disappears
- [ ] No orphaned DOM elements
- [ ] Console shows cleanup logs
- [ ] No console errors

**Pass/Fail**: ___________

---

### Test 10: Rapid Scrolling
**Objective**: Test throttling under stress

**Steps**:
1. User A rapidly scrolls up and down
2. Observe User B's screen
3. Check for performance issues

**Expected Results**:
- [ ] Viewport updates smoothly (not every frame)
- [ ] No jitter or lag
- [ ] Throttle limits to 500ms intervals
- [ ] No console errors
- [ ] CPU usage reasonable

**Pass/Fail**: ___________

---

### Test 11: Extreme Scroll Positions
**Objective**: Test edge scroll positions

**Steps**:
1. User A scrolls to very top (y=0)
2. User A scrolls to very bottom (y=max)
3. User A scrolls far right (x=max)

**Expected Results**:
- [ ] Viewport positioned correctly at top
- [ ] Viewport positioned correctly at bottom
- [ ] Viewport positioned correctly at far right
- [ ] No overflow issues
- [ ] Label always visible

**Pass/Fail**: ___________

---

### Test 12: Small Screen Sizes
**Objective**: Test on mobile/small viewports

**Steps**:
1. User A opens in mobile view (375x667)
2. User B views on desktop

**Expected Results**:
- [ ] Small viewport rectangle visible
- [ ] Correct dimensions (375x667)
- [ ] Label readable
- [ ] Scroll tracking still works
- [ ] No layout breaks

**Pass/Fail**: ___________

---

## 🔌 Network Tests

### Test 13: Socket.IO Connection
**Objective**: Verify data transmission

**Steps**:
1. Open Network tab in DevTools
2. Filter for WebSocket connections
3. Trigger viewport update (scroll)
4. Inspect WebSocket frames

**Expected Results**:
- [ ] `update_cursor_position` event sent with viewport data
- [ ] Payload includes: `{viewport: {x, y, width, height}}`
- [ ] Server responds with `cursor_moved` event
- [ ] Data size reasonable (~80 bytes)
- [ ] No connection errors

**Pass/Fail**: ___________

---

### Test 14: Slow Network
**Objective**: Test under poor conditions

**Steps**:
1. Throttle network to "Slow 3G" in DevTools
2. User A scrolls
3. Observe delays on User B's screen

**Expected Results**:
- [ ] Viewport updates eventually
- [ ] No errors due to lag
- [ ] Graceful degradation
- [ ] No duplicate viewports
- [ ] Catches up when network improves

**Pass/Fail**: ___________

---

### Test 15: Reconnection
**Objective**: Test after connection loss

**Steps**:
1. User A disconnects WiFi briefly
2. User A reconnects
3. Observe viewport behavior

**Expected Results**:
- [ ] Viewport disappears during disconnect
- [ ] Viewport reappears after reconnect
- [ ] Position and size accurate
- [ ] No duplicate viewports
- [ ] Console shows reconnection logs

**Pass/Fail**: ___________

---

## 🐛 Debugging Tests

### Test 16: Console Logging
**Objective**: Verify debug output

**Steps**:
1. Trigger viewport updates
2. Review console logs

**Expected Results**:
- [ ] `👁️ [VIEWPORT DEBUG] Updating viewport for user: X`
- [ ] Viewport data logged: `{x, y, width, height, scrollWidth, scrollHeight}`
- [ ] `✅ [VIEWPORT DEBUG] Viewport indicator created/updated`
- [ ] Backend logs show: `[CURSOR DEBUG] Broadcasting to room: lobby_X`
- [ ] No error messages

**Pass/Fail**: ___________

---

### Test 17: DOM Inspection
**Objective**: Verify correct DOM structure

**Steps**:
1. Open Elements tab in DevTools
2. Find `.viewport-indicator` elements
3. Inspect attributes and styles

**Expected Results**:
- [ ] Element class: `viewport-indicator user-{N}`
- [ ] `data-user-id` attribute present
- [ ] Inline styles: `left`, `top`, `width`, `height`
- [ ] Child element: `.viewport-label` with username
- [ ] No duplicate elements

**Pass/Fail**: ___________

---

## 🎭 User Experience Tests

### Test 18: Visual Clarity
**Objective**: Subjective UX assessment

**Steps**:
1. Use feature naturally
2. Get feedback from test users

**Evaluation Criteria**:
- [ ] Viewports easy to distinguish
- [ ] Labels readable at a glance
- [ ] Colors differentiate users well
- [ ] Not distracting from main task
- [ ] Helpful for coordination

**Pass/Fail**: ___________

---

### Test 19: Performance Impact
**Objective**: Ensure no lag introduced

**Steps**:
1. Measure page performance before/after feature
2. Monitor CPU/memory usage
3. Check frame rate

**Expected Results**:
- [ ] No noticeable FPS drop
- [ ] CPU increase < 5%
- [ ] Memory increase < 10MB
- [ ] Canvas interactions still smooth
- [ ] No UI freezes

**Pass/Fail**: ___________

---

### Test 20: Accessibility
**Objective**: Test keyboard and screen readers

**Steps**:
1. Navigate using keyboard only
2. Test with screen reader (optional)

**Expected Results**:
- [ ] Viewports don't block keyboard nav
- [ ] Tab order not affected
- [ ] Pointer-events: none works
- [ ] No focus traps
- [ ] Doesn't interfere with canvas controls

**Pass/Fail**: ___________

---

## 📊 Integration Tests

### Test 21: Chat Integration
**Objective**: Test viewport with chat open

**Steps**:
1. Open chat sidebar
2. Scroll canvas
3. Send chat messages

**Expected Results**:
- [ ] Viewports update with chat open
- [ ] No layout conflicts
- [ ] Chat doesn't block viewports
- [ ] Both features work simultaneously
- [ ] No z-index issues

**Pass/Fail**: ___________

---

### Test 22: Device Drag & Drop
**Objective**: Test with canvas interactions

**Steps**:
1. User A drags device
2. User B watches
3. Observe viewport during drag

**Expected Results**:
- [ ] Viewport stays in place during drag
- [ ] Doesn't interfere with drag operation
- [ ] Cursor still updates
- [ ] Both features independent
- [ ] No click blocking

**Pass/Fail**: ___________

---

### Test 23: Lobby Switching
**Objective**: Test joining different lobbies

**Steps**:
1. User A joins Lobby 1
2. User A leaves and joins Lobby 2
3. Observe viewport cleanup/recreation

**Expected Results**:
- [ ] Old viewports cleaned up
- [ ] New viewports created
- [ ] No cross-lobby viewports
- [ ] Room isolation maintained
- [ ] No memory leaks

**Pass/Fail**: ___________

---

## 🚀 Stress Tests

### Test 24: Maximum Users
**Objective**: Test with many users (6+)

**Steps**:
1. Join 10 users to same lobby
2. All users scroll/resize simultaneously
3. Monitor performance

**Expected Results**:
- [ ] All viewports visible (colors cycle)
- [ ] Performance acceptable
- [ ] No viewport overlap issues
- [ ] Labels remain readable
- [ ] System doesn't crash

**Pass/Fail**: ___________

---

### Test 25: Long Session
**Objective**: Test stability over time

**Steps**:
1. Keep lobby active for 30+ minutes
2. Periodically trigger viewport updates
3. Monitor for memory leaks

**Expected Results**:
- [ ] Memory usage stable
- [ ] No degradation in performance
- [ ] Viewports still accurate
- [ ] No accumulated errors
- [ ] Clean disconnect at end

**Pass/Fail**: ___________

---

## 📝 Final Checklist

### Overall Assessment
- [ ] All core functionality tests passed
- [ ] Visual appearance satisfactory
- [ ] Edge cases handled gracefully
- [ ] Network communication reliable
- [ ] Performance impact acceptable
- [ ] No console errors
- [ ] User experience positive
- [ ] Ready for production

### Known Issues
List any failures or bugs found:
1. ___________________________________
2. ___________________________________
3. ___________________________________

### Recommendations
- [ ] Feature working as designed
- [ ] Minor tweaks needed (list above)
- [ ] Major issues require fixing
- [ ] Further testing recommended

---

## 🎯 Quick Reference

### Common Test Scenarios
| Scenario | Expected Behavior |
|----------|-------------------|
| User joins | Viewport appears immediately |
| User scrolls | Viewport moves within 500ms |
| User resizes | Viewport size updates smoothly |
| User leaves | Viewport disappears instantly |
| 3+ users | All viewports visible, unique colors |
| Network lag | Updates delayed but no errors |
| Fast scrolling | Throttled to 500ms, smooth |

### Debug Commands
```javascript
// Check viewport indicators
console.log(window.viewportIndicators);

// Check cursor data
console.log(window.cursors);

// Force viewport update
window.dispatchEvent(new Event('scroll'));
```

### Console Filters
- Filter by: `VIEWPORT DEBUG` - See only viewport logs
- Filter by: `CURSOR DEBUG` - See only cursor logs
- Filter by: `Error` - See only errors

---

**Testing by**: ___________________
**Date**: ___________________
**Session ID**: ___________________
**Overall Result**: ⭐ PASS / ❌ FAIL

