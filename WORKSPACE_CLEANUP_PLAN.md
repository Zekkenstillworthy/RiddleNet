# RiddleNet Workspace Cleanup Plan

## Files to Remove

### 1. Test Files and Debug Scripts
- `test_duplicate_fix.py` - Test script for notification debugging (not part of main app)
- `regenerate_class_7.py` - Development utility script
- `test_route_registration.py` - Development testing script

### 2. Empty/Unused Directories
- `models/` - Empty directory (models are in user/models/ and admin/models/)

### 3. Unused Generated Class Routes
Based on the dynamic route registry, only classes 7 and 9 are actively being used:
- `user/routes/generated/class_1_routes.py` - Unused class route
- `user/routes/generated/class_26_routes.py` - Unused class route  
- `user/routes/generated/class_27_routes.py` - Unused class route

### 4. Corresponding Unused Class Templates
- `templates/user/classes/class_1_net101.html` - If exists
- `templates/user/classes/class_26_qrdb2w.html` - If exists
- `templates/user/classes/class_27_2eju6t.html` - If exists

## Files to Keep (Core Application)

### Main Application
- `run.py` ✅
- `__init__.py` ✅
- `socket_manager.py` ✅
- `socket_events.py` ✅
- `requirements.txt` ✅

### Active Content
- `networking1_corrected_content.py` ✅
- `networking2_updated_content.py` ✅

### Core Modules
- `admin/` ✅ (complete module)
- `user/` ✅ (complete module) 
- `services/` ✅ (notification_service.py, feedback_service.py)
- `utils/` ✅ (utility functions)
- `templates/` ✅ (active templates only)
- `static/` ✅ (active assets)
- `docs/` ✅ (documentation)
- `modules/` ✅ (course content)
- `instance/` ✅ (configuration)

### Active Class Routes (Keep)
- `user/routes/generated/class_7_routes.py` ✅ (Networking 1)
- `user/routes/generated/class_9_routes.py` ✅ (Networking 2)

## Benefits of Cleanup
- Reduced workspace complexity
- Easier navigation and maintenance
- Faster loading times
- Cleaner code structure
- Elimination of orphaned files
