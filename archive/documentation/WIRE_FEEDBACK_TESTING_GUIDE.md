# 🧪 Wire Feedback Visibility - Testing Guide

## Quick Test Checklist

### ✅ Test 1: Correct Wire Placement
1. Start crimping simulation
2. Select T568A or T568B wiring type
3. Drag correct wire to correct slot
4. **Expected**: Green "✓ Correct!" tooltip appears ABOVE slot
5. **Verify**: Tooltip is fully visible, not cut off
6. **Duration**: Disappears after 2 seconds

### ✅ Test 2: Incorrect Wire Placement
1. Drag wrong wire to a slot
2. **Expected**: Red "ERROR" tooltip appears ABOVE slot
3. **Verify**: 
   - Error text fully visible
   - Red background with border
   - Positioned higher than success tooltip
   - Larger and more prominent
4. **Duration**: Disappears after 2 seconds

### ✅ Test 3: Multiple Rapid Placements
1. Quickly drag multiple wires (correct and incorrect)
2. **Expected**: Each feedback shows independently
3. **Verify**: No feedback overlap or disappearing
4. **Check**: Each tooltip positioned above respective slot

### ✅ Test 4: Screen Resize
1. Place a wire (show feedback)
2. Resize browser window while feedback showing
3. **Expected**: Feedback remains visible
4. **Verify**: No cutoff at any screen size

### ✅ Test 5: Scroll Position
1. Scroll page if possible
2. Place a wire
3. **Expected**: Feedback appears at correct position
4. **Verify**: Fixed positioning calculates correctly

## Visual Inspection Points

### Success Feedback (Green)
```
✓ Correct!
- Background: Green gradient (#10b981 → #059669)
- Font size: 15px
- Font weight: 700
- Padding: 10px 18px
- Border: 2px white (30% opacity)
- Shadow: Green glow
- Position: 80px above slot
```

### Error Feedback (Red)
```
ERROR
- Background: Red gradient (#ef4444 → #dc2626)
- Font size: 18px
- Font weight: 800
- Padding: 14px 24px
- Border: 3px #fca5a5
- Shadow: Red glow (stronger)
- Position: 90px above slot
```

## Browser DevTools Debug

### Check Z-Index
```javascript
// Open Console, run when feedback appears:
const feedback = document.querySelector('.wire-placement-feedback');
console.log('Z-Index:', getComputedStyle(feedback).zIndex);
// Should output: "9999"
```

### Check Position
```javascript
const feedback = document.querySelector('.wire-placement-feedback');
console.log('Position:', getComputedStyle(feedback).position);
// Should output: "fixed"
console.log('Parent:', feedback.parentElement.tagName);
// Should output: "BODY"
```

### Check Coordinates
```javascript
const feedback = document.querySelector('.wire-placement-feedback');
console.log('Left:', feedback.style.left);
console.log('Top:', feedback.style.top);
// Should show pixel values like "450px", "200px"
```

## Mobile Testing

### iPhone SE (375px)
- [ ] Feedback visible in portrait
- [ ] No horizontal scroll
- [ ] Feedback doesn't overlap UI

### iPad Mini (768px)
- [ ] Feedback positioned correctly
- [ ] Touch interactions work
- [ ] No layout shift

### Android (720px)
- [ ] Feedback fully visible
- [ ] Proper spacing from edges
- [ ] No performance lag

## Common Issues & Solutions

### Issue: Feedback Still Cut Off
**Solution**: Check parent containers for `overflow: hidden`
```javascript
// Debug: Find all parent elements with overflow hidden
const feedback = document.querySelector('.wire-placement-feedback');
let parent = feedback.parentElement;
while (parent) {
  const overflow = getComputedStyle(parent).overflow;
  if (overflow === 'hidden') {
    console.log('Found overflow:hidden on:', parent.className);
  }
  parent = parent.parentElement;
}
```

### Issue: Feedback Wrong Position
**Solution**: Verify `getBoundingClientRect()` values
```javascript
// In showWireFeedback function, add:
console.log('Slot rect:', rect);
console.log('Feedback left:', feedbackLeft, 'top:', feedbackTop);
```

### Issue: Feedback Not Appearing
**Solution**: Check if function is called
```javascript
// Add at start of showWireFeedback:
console.log('showWireFeedback called:', correct, customMessage);
```

## Performance Monitoring

### Frame Rate Check
```javascript
// Check if feedback affects performance
let lastTime = performance.now();
function checkFPS() {
  const now = performance.now();
  const fps = 1000 / (now - lastTime);
  console.log('FPS:', Math.round(fps));
  lastTime = now;
  requestAnimationFrame(checkFPS);
}
checkFPS();
// Should stay at ~60 FPS
```

## Expected Behavior Summary

| Action | Expected Result | Pass/Fail |
|--------|-----------------|-----------|
| Correct wire placement | Green "✓ Correct!" 80px above | ⬜ |
| Incorrect wire placement | Red "ERROR" 90px above | ⬜ |
| Multiple placements | All feedback visible | ⬜ |
| Screen resize | Feedback stays visible | ⬜ |
| Mobile portrait | No cutoff | ⬜ |
| Mobile landscape | Proper positioning | ⬜ |
| Touch interaction | Smooth feedback | ⬜ |
| Scroll test | Fixed position works | ⬜ |

## Regression Tests

### Before Starting Game
- [ ] No feedback elements in DOM
- [ ] No z-index conflicts
- [ ] Clean slate

### During Game
- [ ] Feedback appears on wire drop
- [ ] Correct styling applied
- [ ] Proper timing (2s duration)
- [ ] Clean removal from DOM

### After Feedback
- [ ] Element removed from body
- [ ] No memory leaks
- [ ] Slot z-index reset to 1

## Sign-Off Criteria

✅ **All tests must pass:**
- Correct feedback fully visible
- Error feedback fully visible  
- No cutoff on any device
- Proper z-index stacking
- Smooth animations
- No performance issues

---

**Test Date**: _____________  
**Tester**: _____________  
**Device/Browser**: _____________  
**Result**: ✅ PASS / ❌ FAIL  
**Notes**: _____________
