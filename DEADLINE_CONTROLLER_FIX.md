# Deadline Controller 404 Fix

## Problem
The front-end was getting 404 errors when trying to access `/instructor/assignment/7/deadline-settings`:
```
Failed to load resource: the server responded with a status of 404 (NOT FOUND)
Error loading deadline settings: Error: Assignment not found
```

## Root Cause
The `deadline_controller_bp` blueprint was defined in `instructor/controllers/deadline_controller.py` but **never registered** with the Flask application in `application.py`.

## Solution
Added the deadline controller blueprint to the `admin_blueprints` list in `application.py`:

```python
('instructor.controllers.deadline_controller', 'deadline_controller_bp', None),
```

This was inserted at line 161, right before the API routes.

## Impact
The following routes are now accessible:
- `/instructor/deadline-management` - Deadline management dashboard
- `/instructor/deadline-policies` - List all deadline policies
- `/instructor/deadline-policies/create` - Create new deadline policy
- `/instructor/deadline-extensions` - View deadline extensions
- `/instructor/assignment/<assignment_id>/deadline-settings` - Get deadline settings for specific assignment (AJAX)
- `/instructor/deadlines/<assignment_id>/preview` - Preview deadline calculations
- `/instructor/api/deadline-activity` - Get deadline activity feed

## Verification
Assignment 7 ("Network Security Assessment" in class 9) exists in the database. The route should now respond correctly.

## Next Steps
1. Test the deadline settings modal for assignment 7
2. Verify the grant extension functionality works end-to-end
3. Test creating deadline policies from the instructor dashboard
