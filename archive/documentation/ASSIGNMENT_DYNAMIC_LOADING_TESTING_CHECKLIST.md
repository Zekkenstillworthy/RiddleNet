# ✅ Assignment Dynamic Loading - Testing Checklist

## Pre-Flight Checks

- [ ] Server is running on `http://127.0.0.1:5001`
- [ ] Database is accessible
- [ ] User is logged in
- [ ] Browser console is open (F12)
- [ ] Network tab is open for debugging

---

## 🧪 Functional Testing

### Test 1: Basic Assignment Loading
**URL**: `http://127.0.0.1:5001/class/7/module/1?lesson_id=2`

**Steps**:
1. [ ] Navigate to the module detail page
2. [ ] Locate "Assignments" section in left sidebar
3. [ ] Click on the first assignment item
4. [ ] Observe loading spinner appears
5. [ ] Wait for content to load
6. [ ] Verify assignment details display in main content area

**Expected Result**:
- Assignment content replaces lesson content
- Title, description, instructions visible
- Due date and points displayed
- Status badge shows correct color

---

### Test 2: Active State Management
**Steps**:
1. [ ] Click on "Assignment 1"
2. [ ] Verify "Assignment 1" has cyan glow (active state)
3. [ ] Verify lesson items lose active state
4. [ ] Click on "Assignment 2"
5. [ ] Verify "Assignment 2" now has active state
6. [ ] Verify "Assignment 1" loses active state

**Expected Result**:
- Only one assignment is active at a time
- Active assignment has brighter background and cyan border
- Lesson items are not highlighted when assignment is active

---

### Test 3: Status Badges
**Steps**:
1. [ ] Find assignment with "NOT SUBMITTED" status
2. [ ] Verify badge is gray/muted color
3. [ ] Find assignment with "SUBMITTED" status (if any)
4. [ ] Verify badge is blue color
5. [ ] Find assignment with "GRADED" status (if any)
6. [ ] Verify badge is green color

**Expected Result**:
- Each status has distinct color
- Icons match status (circle, check, star, etc.)

---

### Test 4: API Endpoint
**Browser Console Test**:
```javascript
// Run this in browser console
fetch('/api/assignments/1')
  .then(r => r.json())
  .then(d => console.log(d));
```

**Steps**:
1. [ ] Open browser console (F12)
2. [ ] Paste above code
3. [ ] Press Enter
4. [ ] Verify JSON response appears

**Expected Result**:
```json
{
  "id": 1,
  "title": "...",
  "description": "...",
  "status": "...",
  ...
}
```

---

### Test 5: Error Handling
**Steps**:
1. [ ] Modify onclick to use invalid ID: `loadAssignment(99999)`
2. [ ] Click the modified assignment item
3. [ ] Verify error message appears
4. [ ] Verify retry button is visible
5. [ ] Click retry button
6. [ ] Verify error persists (expected for invalid ID)

**Expected Result**:
- Red warning triangle icon
- Error message displayed
- Blue retry button appears
- Button triggers loadAssignment() again

---

### Test 6: Loading State
**Steps**:
1. [ ] Open Network tab in DevTools
2. [ ] Throttle network to "Slow 3G"
3. [ ] Click an assignment
4. [ ] Observe loading spinner
5. [ ] Wait for content to load

**Expected Result**:
- Cyan spinner appears immediately
- "Loading Assignment..." text visible
- Content loads after network delay
- Spinner disappears when content renders

---

### Test 7: Submission Details Display
**Steps** (requires existing submission):
1. [ ] Click assignment with submission
2. [ ] Verify "YOUR SUBMISSION" section appears
3. [ ] Check submitted date is displayed
4. [ ] If graded, verify grade shows (e.g., "95/100")
5. [ ] If feedback exists, verify it's displayed

**Expected Result**:
- Green-tinted submission section
- All submission details visible
- Grade highlighted in neon green
- Feedback text readable

---

### Test 8: Requirements Grid
**Steps**:
1. [ ] Click any assignment
2. [ ] Scroll to "Submission Requirements" section
3. [ ] Verify grid layout displays correctly
4. [ ] Check file upload requirements (if enabled)
5. [ ] Check text submission option (if enabled)
6. [ ] Check late submission policy (if enabled)

**Expected Result**:
- Grid with 2-3 cards depending on settings
- Each card has icon, title, description
- File limits clearly stated (e.g., "Max 5 files, 10MB each")

---

### Test 9: Breadcrumb Navigation
**Steps**:
1. [ ] Click any assignment
2. [ ] Locate breadcrumb at top of content
3. [ ] Verify path: Dashboard > Class Name > Assignments > Assignment Title
4. [ ] Click "Dashboard" link
5. [ ] Verify navigation works

**Expected Result**:
- Breadcrumb shows full path
- Links are clickable
- Chevrons separate items
- Current item not underlined

---

### Test 10: Smooth Scrolling
**Steps**:
1. [ ] Scroll down page to bottom
2. [ ] Click an assignment in sidebar
3. [ ] Observe page scroll behavior

**Expected Result**:
- Page smoothly scrolls to top of content
- No jarring jumps
- Animation takes ~500ms

---

## 🔍 Browser Console Checks

### Check 1: No JavaScript Errors
**Steps**:
1. [ ] Open Console tab
2. [ ] Click multiple assignments
3. [ ] Look for red error messages

**Expected Result**:
- No errors appear
- Only info logs like "📋 Loading assignment: 1"

---

### Check 2: Network Requests
**Steps**:
1. [ ] Open Network tab
2. [ ] Click an assignment
3. [ ] Find request to `/api/assignments/1`
4. [ ] Check Status Code = 200
5. [ ] Check Response is JSON

**Expected Result**:
- Request appears in Network tab
- Status: 200 OK
- Type: xhr (AJAX request)
- Response: JSON with assignment data

---

### Check 3: Console Logs
**Expected Console Output**:
```
📋 Loading assignment: 1
✅ Assignment data loaded: {id: 1, title: "...", ...}
```

---

## 🎨 Visual Checks

### Visual 1: Assignment Item Hover
**Steps**:
1. [ ] Hover over assignment item
2. [ ] Verify background lightens
3. [ ] Verify cyan border appears
4. [ ] Verify slight slide-right animation

**Expected Result**:
- Smooth hover transition
- Visual feedback on hover
- Cursor changes to pointer

---

### Visual 2: Active State Glow
**Steps**:
1. [ ] Click assignment
2. [ ] Verify active item has:
   - [ ] Brighter background
   - [ ] Cyan glowing border
   - [ ] Box shadow effect

**Expected Result**:
- Clear visual distinction
- Matches design system colors

---

### Visual 3: Content Layout
**Steps**:
1. [ ] Click assignment
2. [ ] Verify layout sections:
   - [ ] Breadcrumb at top
   - [ ] Large title with icon
   - [ ] Metadata row (type, date, points, status)
   - [ ] Description section
   - [ ] Instructions section
   - [ ] Requirements grid
   - [ ] Info message at bottom

**Expected Result**:
- Clean, organized layout
- Proper spacing between sections
- Readable text sizes
- Consistent styling

---

## 🌐 Cross-Browser Testing

### Browser: Chrome/Edge
- [ ] All features work
- [ ] No console errors
- [ ] Smooth animations

### Browser: Firefox
- [ ] All features work
- [ ] No console errors
- [ ] Smooth animations

### Browser: Safari (if available)
- [ ] All features work
- [ ] No console errors
- [ ] Smooth animations

---

## 📱 Responsive Testing

### Desktop (1920x1080)
- [ ] Sidebar visible
- [ ] Content area wide
- [ ] All elements fit

### Tablet (768x1024)
- [ ] Sidebar narrower
- [ ] Content readable
- [ ] Grid responsive

### Mobile (375x667)
- [ ] Sidebar collapses (if implemented)
- [ ] Content full width
- [ ] Touch-friendly buttons

---

## 🔒 Security Testing

### Test: Unauthorized Access
**Steps**:
1. [ ] Log out
2. [ ] Try to access: `/api/assignments/1` directly
3. [ ] Verify 401 Unauthorized response

**Expected Result**:
- API requires authentication
- Error message returned

---

### Test: Invalid Assignment ID
**Steps**:
1. [ ] Try: `/api/assignments/99999`
2. [ ] Verify 404 Not Found response

**Expected Result**:
- Invalid IDs return 404
- No server error

---

### Test: XSS Prevention
**Steps**:
1. [ ] Create assignment with title: `<script>alert('XSS')</script>`
2. [ ] Click assignment
3. [ ] Verify no alert appears
4. [ ] Verify script tags are escaped

**Expected Result**:
- HTML properly escaped
- No script execution
- Content displays safely

---

## ⚡ Performance Testing

### Test: Load Time
**Steps**:
1. [ ] Open Network tab
2. [ ] Click assignment
3. [ ] Measure time to "DOMContentLoaded"

**Expected Result**:
- Total time < 500ms on good connection
- Total time < 2s on slow connection

---

### Test: Memory Usage
**Steps**:
1. [ ] Open Performance tab
2. [ ] Click 10 different assignments
3. [ ] Check memory usage

**Expected Result**:
- No memory leaks
- Memory returns to baseline
- No significant increase

---

## 📊 Acceptance Criteria Verification

- [x] When user clicks assignment, fetch data via AJAX
- [x] Replace content in `.lesson-content` div
- [x] Update active state in sidebar
- [x] Maintain existing layout structure
- [x] Display title, description, instructions, due date
- [x] Show submission status
- [x] NO submission functionality (out of scope)
- [x] NO file upload features (out of scope)

---

## ✅ Final Checklist

- [ ] All functional tests pass
- [ ] No console errors
- [ ] Network requests successful
- [ ] Visual styling correct
- [ ] Cross-browser compatible
- [ ] Responsive on all sizes
- [ ] Security measures in place
- [ ] Performance acceptable
- [ ] Documentation complete

---

## 🐛 Known Issues

_Document any issues found during testing:_

1. Issue: ___________________________
   - Steps to reproduce: ___________________________
   - Expected: ___________________________
   - Actual: ___________________________
   - Priority: [ ] Low [ ] Medium [ ] High
   - Status: [ ] Open [ ] Fixed

---

## 📝 Test Results Summary

**Date**: _______________  
**Tester**: _______________  
**Browser**: _______________  
**OS**: _______________

**Tests Passed**: _____ / _____  
**Tests Failed**: _____ / _____  
**Issues Found**: _____

**Overall Status**: [ ] PASS [ ] FAIL [ ] NEEDS WORK

**Notes**:
_________________________________
_________________________________
_________________________________

---

## 🎯 Next Steps

After all tests pass:
- [ ] Create pull request
- [ ] Request code review
- [ ] Merge to main branch
- [ ] Deploy to production
- [ ] Monitor for issues
- [ ] Gather user feedback

---

**Testing Complete!** ✅

