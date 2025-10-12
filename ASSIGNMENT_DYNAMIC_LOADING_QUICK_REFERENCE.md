# 📋 Assignment Dynamic Loading - Quick Reference

## 🚀 Quick Start

### How to Use
1. Navigate to: `http://127.0.0.1:5001/class/{class_id}/module/{module_id}?lesson_id={lesson_id}`
2. Look for "Assignments" section in the left sidebar
3. Click any assignment item
4. Assignment content loads in the main `.lesson-content` area

---

## 🔌 API Endpoint

**URL**: `/api/assignments/<int:assignment_id>`  
**Method**: `GET`  
**Auth**: Required (`@flexible_login_required`)

**Example Request**:
```javascript
fetch('/api/assignments/1')
  .then(response => response.json())
  .then(data => console.log(data));
```

**Example Response**:
```json
{
  "id": 1,
  "title": "Network Architecture Assignment",
  "description": "Complete the network diagram",
  "instructions": "Create a network topology...",
  "due_date": "October 15, 2025 at 11:59 PM",
  "points": 100,
  "status": "not_submitted"
}
```

---

## 💻 JavaScript Functions

### Load Assignment
```javascript
loadAssignment(assignmentId)
```
- Fetches assignment data
- Updates UI with assignment content
- Manages loading/error states

### Update Active State
```javascript
updateAssignmentActiveState(assignmentId)
```
- Highlights selected assignment
- Removes highlighting from other items

### Render Content
```javascript
renderAssignmentContent(assignment)
```
- Generates assignment HTML
- Displays all assignment details
- Adds status-specific styling

---

## 🎨 CSS Classes

### Status Badges
```css
.status-not-submitted  /* Gray - Not yet submitted */
.status-submitted      /* Blue - Submitted */
.status-graded        /* Green - Graded */
.status-overdue       /* Red - Past due date */
.status-resubmitted   /* Orange - Resubmitted */
```

### Active State
```css
.assignment-item.active  /* Highlighted assignment */
```

---

## 📊 Assignment Status Flow

```
NOT_SUBMITTED → SUBMITTED → GRADED
       ↓
   OVERDUE
       ↓
  RESUBMITTED → GRADED
```

---

## 🔍 Troubleshooting

### Assignment not loading?
1. Check browser console for errors
2. Verify assignment ID exists in database
3. Confirm user is authenticated
4. Check network tab for API response

### Active state not updating?
1. Ensure onclick handler exists on assignment item
2. Check JavaScript console for errors
3. Verify `updateAssignmentActiveState()` is called

### Content not displaying?
1. Check `.lesson-content` div exists
2. Verify `renderAssignmentContent()` completes
3. Inspect HTML structure in DevTools

---

## 📁 Files Modified

### Backend
- `user/routes/universal_class_routes.py` (API endpoint)

### Frontend
- `templates/user/module_detail.html` (UI + JavaScript + CSS)

---

## 🎯 Key Features

✅ Click-to-load assignment content  
✅ AJAX-based (no page reload)  
✅ Active state management  
✅ Loading & error states  
✅ Status badges  
✅ Submission details display  
✅ Requirements grid  
✅ Breadcrumb navigation  

---

## 🔄 Workflow Diagram

```
[User Clicks Assignment]
         ↓
[Remove active from lessons]
         ↓
[Add active to assignment]
         ↓
[Show loading spinner]
         ↓
[Fetch: /api/assignments/{id}]
         ↓
    [Success?]
    ↙        ↘
  YES        NO
   ↓          ↓
[Render]  [Show Error]
   ↓          ↓
[Scroll]  [Retry Button]
```

---

## 📝 Example HTML Structure

```html
<!-- Sidebar Assignment Item -->
<div class="assignment-item" onclick="loadAssignment(1)" style="cursor: pointer;">
  <div class="assignment-header">
    <h4 class="assignment-title">Assignment 1</h4>
    <span class="assignment-status not_submitted">NOT SUBMITTED</span>
  </div>
</div>

<!-- Main Content Area -->
<div class="lesson-content">
  <!-- Assignment content loads here dynamically -->
</div>
```

---

## 🧪 Testing Commands

### Manual Test
1. Open: `http://127.0.0.1:5001/class/7/module/1`
2. Click any assignment in sidebar
3. Verify content loads
4. Check active state changes

### Browser Console Test
```javascript
// Test API endpoint
fetch('/api/assignments/1')
  .then(r => r.json())
  .then(console.log);

// Test load function
loadAssignment(1);

// Check current assignment
console.log(currentAssignmentId);
```

---

## ⚡ Performance Tips

- API response cached in browser
- Single AJAX call per assignment
- Minimal DOM manipulation
- Smooth scroll for better UX

---

## 🔐 Security Notes

- Authentication required for API
- User can only see their own submissions
- XSS protection via proper escaping
- CSRF tokens on future submit forms

---

## 📚 Related Docs

- Full documentation: `ASSIGNMENT_DYNAMIC_LOADING_IMPLEMENTATION.md`
- API routes: `user/routes/universal_class_routes.py`
- Template: `templates/user/module_detail.html`

---

**Last Updated**: October 11, 2025  
**Status**: ✅ Production Ready
