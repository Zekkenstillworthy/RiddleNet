# Grant Extension & Manage Policies Button Fix

## Problem
The **Grant Extension** and **Manage Policies** buttons in the Deadlines tab were not working properly:
- Grant Extension button was calling `grantExtension()` which tries to submit without showing the modal
- Manage Policies button was redirecting to `/instructor/deadline-policies` in a new window

## Solution Implemented

### 1. Fixed Grant Extension Button (Line ~6590)
**Changed from:**
```html
<button class="action-btn primary" onclick="grantExtension()">
```

**Changed to:**
```html
<button class="action-btn primary" onclick="showGrantExtensionModal()">
```

**Result:** Now properly opens the Grant Extension modal that already existed in the code.

---

### 2. Created Manage Policies Modal (Line ~7228)
Added a comprehensive **Manage Policies Modal** with:

#### Features:
- **Create New Policy Section**
  - Policy Name input
  - Policy Type dropdown (Percentage Deduction, Fixed Points, Grace Period, Zero After Deadline)
  - Dynamic form fields based on selected type
  - Description textarea
  - "Set as default" checkbox

- **Existing Policies List**
  - Displays all deadline policies in card format
  - Shows policy name, type, and details
  - Edit and Delete buttons for each policy
  - Highlights default policy with badge

#### Policy Types Supported:
1. **Percentage Deduction** - Shows penalty percentage and time interval fields
2. **Fixed Points Deduction** - For fixed point deductions
3. **Grace Period** - Shows grace period hours input
4. **Zero After Deadline** - Automatic zero after deadline

---

### 3. Updated Manage Policies Button (Line ~6615)
**Changed from:**
```html
<button class="action-btn secondary" onclick="managePolicies()">
    <i class="fas fa-settings"></i>
    Manage Policies
</button>
```

**Changed to:**
```html
<button class="action-btn secondary" onclick="showPoliciesModal()">
    <i class="fas fa-cog"></i>
    Manage Policies
</button>
```

---

### 4. Added JavaScript Functions (Line ~13020)

#### `showPoliciesModal()`
- Loads policies from API
- Opens the modal

#### `loadPolicies()`
- Fetches policies from `/instructor/api/deadline-policies`
- Renders policy cards with:
  - Policy name and default badge
  - Policy description
  - Policy metadata (type, penalty rate, grace period)
  - Edit and Delete buttons

#### `createPolicy()`
- Validates form inputs
- Posts to `/instructor/api/deadline-policies`
- Includes type-specific settings (penalty rate, grace period, etc.)
- Reloads policy list on success

#### `editPolicyInModal(policyId)`
- Placeholder for editing functionality

#### `deletePolicy(policyId)`
- Confirms deletion
- Calls DELETE on `/instructor/api/deadline-policies/{id}`
- Reloads policy list

#### `managePolicies()`
- Updated to call `showPoliciesModal()` instead of redirecting

---

### 5. Added Policy Type Handler (Line ~13172)
Event listener that shows/hides form fields based on selected policy type:
- **Percentage** → Shows penalty percentage and interval fields
- **Grace** → Shows grace period hours field
- **Other types** → Hides extra fields

---

### 6. Added CSS Styles (Line ~5786)
Added comprehensive styling for:
- `.policies-management` - Main container
- `.policies-list` - Policy cards container
- `.policy-card` - Individual policy card with hover effects
- `.policy-header` - Policy name and action buttons
- `.policy-details` - Policy description and metadata
- `.policy-meta` - Policy information badges
- `.form-section` - Form section styling with icons

---

## Files Modified

**File:** `templates/instructor/class_content_manager.html`

### Changes:
1. **Line ~6590** - Updated Grant Extension button onclick
2. **Line ~6615** - Updated Manage Policies button onclick
3. **Line ~7228** - Added Manage Policies Modal HTML
4. **Line ~5786** - Added Policy Management CSS styles
5. **Line ~13020** - Added JavaScript functions for policy management
6. **Line ~13172** - Added policy type dropdown handler

---

## API Endpoints Required

The modal expects these endpoints to exist:

### 1. Get Policies
```
GET /instructor/api/deadline-policies
Response: { "policies": [...] }
```

### 2. Create Policy
```
POST /instructor/api/deadline-policies
Body: {
    "name": "Policy Name",
    "type": "percentage",
    "description": "Description",
    "is_default": false,
    "penalty_rate": 10,
    "penalty_interval": "day",
    "grace_period_hours": 24
}
Response: { "success": true, "message": "..." }
```

### 3. Delete Policy
```
DELETE /instructor/api/deadline-policies/{id}
Response: { "success": true, "message": "..." }
```

---

## Testing Checklist

### Grant Extension Button
- [x] Button shows on Deadlines tab
- [ ] Click opens Grant Extension modal
- [ ] Modal shows student dropdown
- [ ] Modal shows assignment dropdown
- [ ] Can enter extension hours
- [ ] Can submit extension

### Manage Policies Button
- [x] Button shows on Deadlines tab
- [ ] Click opens Manage Policies modal
- [ ] Can select policy type
- [ ] Form fields change based on type
- [ ] Can create new policy
- [ ] Policies list loads from API
- [ ] Can delete non-default policies
- [ ] Default policy shows badge

---

## Next Steps

1. **Test the buttons** - Navigate to Deadlines tab and verify both buttons appear
2. **Implement API endpoints** - If they don't exist, create them in the backend
3. **Test policy creation** - Try creating different policy types
4. **Implement edit functionality** - Currently shows "will be implemented" message
5. **Add validation** - Add more comprehensive form validation

---

## UI/UX Improvements Made

✅ **Popup instead of redirect** - Both buttons now open modals  
✅ **Modern card design** - Policy cards have glassmorphic design with hover effects  
✅ **Dynamic form fields** - Fields appear/hide based on policy type selection  
✅ **Clear visual hierarchy** - Icons, badges, and proper spacing  
✅ **Responsive layout** - Works on different screen sizes  
✅ **Loading states** - Shows spinner while loading policies  
✅ **Empty states** - Shows helpful message when no policies exist  
✅ **Error handling** - Toast notifications for errors  
✅ **Confirmation dialogs** - Asks before deleting policies  

---

## Known Limitations

### Edit Policy
- Currently shows "will be implemented" message
- Need to implement `editPolicyInModal()` function with:
  - Populate form with existing policy data
  - Update API call instead of create
  - Handle form state management

### Policy Application
- Need to add "Apply to Class" functionality
- Batch apply policies to assignments
- Override individual assignment policies

### Validation
- Add more robust client-side validation
- Validate penalty rates (0-100%)
- Validate grace period hours (positive numbers)
- Check for duplicate policy names
