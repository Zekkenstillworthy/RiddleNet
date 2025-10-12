# Assignment Dynamic Content Loading - MVP Implementation

## Overview
This MVP enables clicking on an assignment in the sidebar to dynamically load and display the assignment content in the main `.lesson-content` area, replacing the current view without page navigation.

## Current State Analysis

### Existing Components
- ✅ Assignments displayed in sidebar (`#assignments-sidebar`)
- ✅ Main content area (`.main-content`)
- ✅ API endpoint exists: `/assignments/<int:assignment_id>/api/details`
- ✅ Assignment view function: `viewAssignmentModal()` and `loadAssignmentDetails()`
- ✅ Assignment rendering logic in place

### Current Behavior
- Assignments are listed in sidebar with "View" and "Submit" buttons
- "View" button calls `viewAssignmentModal()` which loads into main content
- "Submit" button calls `submitAssignmentModal()` which opens a modal

## MVP Implementation Plan

### Phase 1: Make Assignment Items Clickable (Similar to Module Selection)

#### 1.1 Update HTML Template
**File:** `templates/user/dynamic_class_universal.html`

**Change:** Make entire assignment item clickable (similar to module items)

```html
<!-- BEFORE (around line 1358) -->
<div class="assignment-item">
  <div class="assignment-header">
    <div class="assignment-title">{{ assignment.title }}</div>
    ...
  </div>
  ...
</div>

<!-- AFTER -->
<div class="assignment-item" onclick="selectAssignment({{ assignment.id }})" style="cursor: pointer;">
  <div class="assignment-header">
    <div class="assignment-title">{{ assignment.title }}</div>
    ...
  </div>
  ...
</div>
```

#### 1.2 Add Active State Styling
**File:** `templates/user/dynamic_class_universal.html` (CSS section)

```css
/* Add to existing assignment-item styles (around line 142) */
.assignment-item {
  background: rgba(26, 35, 126, 0.4);
  border: 1px solid var(--border-glow);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
  cursor: pointer;  /* NEW */
}

.assignment-item.active {  /* NEW */
  background: linear-gradient(135deg, rgba(0, 217, 255, 0.2), rgba(139, 92, 246, 0.2));
  border-color: var(--cyber-glow);
  box-shadow: 0 4px 15px rgba(0, 217, 255, 0.3);
}

.assignment-item:hover {
  background: rgba(0, 217, 255, 0.15);
  border-color: var(--cyber-glow);
  transform: translateX(5px);
}
```

### Phase 2: Create Assignment Selection Function

#### 2.1 Add JavaScript Function
**File:** `templates/user/dynamic_class_universal.html`

**Location:** Add after `selectModule()` function (around line 1560)

```javascript
// Assignment selection function - similar to selectModule
function selectAssignment(assignmentId) {
  console.log('selectAssignment called with ID:', assignmentId);
  
  // Update active state in sidebar
  const assignmentItems = document.querySelectorAll('.assignment-item');
  assignmentItems.forEach(item => {
    item.classList.remove('active');
  });
  
  // Find and activate the clicked assignment
  const clickedItem = event.currentTarget;
  if (clickedItem) {
    clickedItem.classList.add('active');
  }
  
  // Load assignment content into main area (reuse existing function)
  loadAssignmentDetails(assignmentId, 'view');
}
```

### Phase 3: API Endpoint Verification

#### 3.1 Verify User-Facing Route Exists
**File:** `user/routes/assignment_routes.py` (or create if doesn't exist)

**Required Route:**
```python
@assignment_bp.route('/assignments/<int:assignment_id>/api/details')
@user_required
def get_assignment_details(assignment_id):
    """Get assignment details for user view"""
    try:
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        
        # Check if user has access to this assignment
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        # Get user's submission if exists
        submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=current_user.id
        ).first()
        
        # Check if past due
        is_past_due = assignment.due_date and assignment.due_date < datetime.now()
        
        # Can submit if not past due or already submitted
        can_submit = not is_past_due or (submission is not None)
        
        return jsonify({
            'success': True,
            'assignment': {
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'instructions': getattr(assignment, 'instructions', ''),
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'points': assignment.points,
                'class_id': assignment.class_id
            },
            'submission': {
                'id': submission.id,
                'submitted_at': submission.submitted_at.isoformat(),
                'grade': submission.grade,
                'feedback': submission.feedback,
                'file_url': submission.file_url
            } if submission else None,
            'can_submit': can_submit,
            'is_past_due': is_past_due
        })
        
    except Exception as e:
        current_app.logger.error(f"Error loading assignment {assignment_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

#### 3.2 Register Blueprint (if new file created)
**File:** `application.py`

```python
# Add to blueprint registration section
from user.routes.assignment_routes import assignment_bp
app.register_blueprint(assignment_bp)
```

### Phase 4: Update Button Actions to Prevent Double-Click

#### 4.1 Modify View/Submit Buttons
**File:** `templates/user/dynamic_class_universal.html`

```html
<!-- Update button onclick to stop event propagation (around line 1393) -->
<button onclick="event.stopPropagation(); viewAssignmentModal({{ assignment.id }})" 
   class="assignment-btn assignment-btn-primary">
  <i class="fas fa-eye"></i>
  View
</button>

<button onclick="event.stopPropagation(); submitAssignmentModal({{ assignment.id }})" 
   class="assignment-btn assignment-btn-secondary">
  <i class="fas fa-upload"></i>
  {% if status == 'submitted' %}Re-submit{% else %}Submit{% endif %}
</button>
```

**Explanation:** `event.stopPropagation()` prevents the click from bubbling up to the parent `.assignment-item` onclick handler, so clicking the buttons won't also trigger `selectAssignment()`.

## Testing Checklist

### Manual Testing Steps

1. **Assignment Click Test**
   - [ ] Navigate to class page with assignments
   - [ ] Click on an assignment item in sidebar
   - [ ] Verify main content area updates with assignment details
   - [ ] Verify clicked assignment has active styling
   - [ ] Click another assignment, verify previous one loses active state

2. **Button Isolation Test**
   - [ ] Click "View" button on an assignment
   - [ ] Verify only the button action fires (not the item click)
   - [ ] Click "Submit" button
   - [ ] Verify modal opens without main content changing

3. **Active State Test**
   - [ ] Click assignment item
   - [ ] Verify blue/cyan glow effect appears
   - [ ] Click different assignment
   - [ ] Verify active state moves to new assignment

4. **API Response Test**
   - [ ] Open browser DevTools Network tab
   - [ ] Click an assignment
   - [ ] Verify API call to `/assignments/{id}/api/details`
   - [ ] Verify JSON response contains assignment data
   - [ ] Check for any 401/403/500 errors

5. **Content Display Test**
   - [ ] Verify assignment title displays
   - [ ] Verify assignment description renders
   - [ ] Verify due date shows correctly
   - [ ] Verify point value displays
   - [ ] If submitted, verify submission info shows

## File Changes Summary

### Files to Modify
1. ✏️ `templates/user/dynamic_class_universal.html`
   - Add `onclick` to `.assignment-item`
   - Add `.assignment-item.active` CSS
   - Add `selectAssignment()` JavaScript function
   - Add `event.stopPropagation()` to buttons

### Files to Create (if needed)
2. ✨ `user/routes/assignment_routes.py`
   - Create assignment API endpoint
   - Add user authentication checks

### Files to Update (if new route)
3. ✏️ `application.py`
   - Register assignment blueprint

## MVP Scope

### In Scope ✅
- Click assignment item to load content
- Display assignment details in main content area
- Active state highlighting in sidebar
- Reuse existing API and rendering logic
- Basic error handling

### Out of Scope ❌
- Assignment submission (already exists via modal)
- File uploads (already exists)
- Grade display (already exists)
- Assignment creation/editing (admin feature)
- Real-time updates
- Assignment filtering/sorting

## Success Metrics

### User Experience
- ✅ Single click loads assignment content
- ✅ Visual feedback shows selected assignment
- ✅ No page reload required
- ✅ Consistent with module selection UX

### Technical
- ✅ API response time < 500ms
- ✅ No console errors
- ✅ Proper error messages for failures
- ✅ Compatible with existing assignment submission flow

## Rollback Plan

If issues occur:
1. Remove `onclick` from `.assignment-item` elements
2. Remove `selectAssignment()` function
3. Keep existing "View" button functionality
4. Revert to modal-based viewing

## Future Enhancements (Post-MVP)

1. **Assignment Navigation**
   - Previous/Next assignment buttons
   - Keyboard shortcuts (arrow keys)

2. **Enhanced Display**
   - File preview for submission attachments
   - Inline comments/feedback
   - Assignment completion progress indicator

3. **Smart Loading**
   - Preload next assignment in background
   - Cache assignment data locally
   - Optimistic UI updates

4. **Accessibility**
   - Screen reader announcements
   - Focus management
   - Keyboard navigation support

## Implementation Timeline

- **Phase 1 (HTML/CSS):** 15 minutes
- **Phase 2 (JavaScript):** 20 minutes
- **Phase 3 (API Verification):** 30 minutes
- **Phase 4 (Button Updates):** 10 minutes
- **Testing:** 30 minutes
- **Total Estimated Time:** ~2 hours

## Notes

- The existing `loadAssignmentDetails()` function already handles loading assignment content into `.main-content` when mode is 'view'
- This MVP leverages existing infrastructure, minimizing new code
- Pattern matches the existing `selectModule()` implementation for consistency
- API endpoint may already exist from admin side, need to verify user access permissions
