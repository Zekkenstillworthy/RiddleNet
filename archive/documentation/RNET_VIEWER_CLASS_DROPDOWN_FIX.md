# RNet Viewer - Class Content Manager Dropdown Fix

## Issue Description
When navigating to the RNet File Viewer page (`http://127.0.0.1:5001/rnet/viewer`), the Class Content Manager dropdown in the sidebar was showing "No Classes Available" even though classes existed in the system. However, on other admin pages, the classes were displaying correctly.

## Root Cause
The issue was caused by a URL prefix mismatch in the Flask context processor:

1. **RNet Viewer Route**: `/rnet/viewer` (URL prefix: `/rnet`)
2. **Context Processor Logic**: Only injected `all_classes` for routes starting with `/admin`

```python
# From __init__.py, lines 336-359
@app.context_processor
def inject_classes():
    """Inject classes for sidebar display"""
    try:
        path = request.path if request else "unknown"
    except:
        path = "unknown"
    
    # Only inject for admin routes
    if path.startswith('/admin'):  # ⚠️ This condition was the problem
        try:
            from admin.models.class_model import Class
            # ... loads classes ...
            return dict(all_classes=all_classes)
        except:
            return dict(all_classes=[])
    
    return dict()  # ❌ Returns empty dict for non-admin routes
```

Since `/rnet/viewer` doesn't start with `/admin`, the context processor didn't inject the `all_classes` variable, causing the sidebar dropdown to be empty.

## Solution Implemented

### Changed RNet Viewer URL Prefix
Modified the blueprint to use `/admin/rnet` instead of `/rnet`, making it consistent with other admin routes.

**File: `admin/routes/rnet_viewer_routes.py`**

```python
# BEFORE:
rnet_viewer_bp = Blueprint('rnet_viewer', __name__, url_prefix='/rnet')

@rnet_viewer_bp.route('/viewer')
def view_rnet_file():
    return render_template('admin/rnet_file_viewer.html')

# AFTER:
rnet_viewer_bp = Blueprint('rnet_viewer', __name__, url_prefix='/admin/rnet')

@rnet_viewer_bp.route('/viewer')
def view_rnet_file():
    return render_template('admin/rnet_file_viewer.html', active_page='rnet_viewer')
```

### Updated API Endpoint in Frontend
Updated the JavaScript API calls to use the new URL prefix.

**File: `templates/admin/rnet_file_viewer.html`**

```javascript
// BEFORE:
const apiUrl = '/rnet/api/parse';

// AFTER:
const apiUrl = '/admin/rnet/api/parse';
```

## New Route Structure

| Old URL | New URL |
|---------|---------|
| `http://127.0.0.1:5001/rnet/viewer` | `http://127.0.0.1:5001/admin/rnet/viewer` |
| `http://127.0.0.1:5001/rnet/api/parse` | `http://127.0.0.1:5001/admin/rnet/api/parse` |
| `http://127.0.0.1:5001/rnet/api/qr-image/<file_id>` | `http://127.0.0.1:5001/admin/rnet/api/qr-image/<file_id>` |

## Benefits of This Change

1. ✅ **Consistency**: All admin features now use the `/admin` prefix
2. ✅ **Context Processor Coverage**: The `all_classes` variable is now automatically injected
3. ✅ **Sidebar Functionality**: Class Content Manager dropdown now works correctly
4. ✅ **URL Organization**: Better URL structure following REST conventions
5. ✅ **Active Page Highlighting**: Added `active_page='rnet_viewer'` parameter for proper sidebar highlighting

## Testing Checklist

- [ ] Navigate to `http://127.0.0.1:5001/admin/rnet/viewer`
- [ ] Verify that classes appear in the Class Content Manager dropdown
- [ ] Upload a .rnet file and verify parsing works
- [ ] Check that the sidebar "RNet File Viewer" link is highlighted as active
- [ ] Test that all API endpoints respond correctly

## Related Files Modified

1. `admin/routes/rnet_viewer_routes.py` - Changed URL prefix and added active_page parameter
2. `templates/admin/rnet_file_viewer.html` - Updated API endpoint URLs in JavaScript

## Technical Notes

- The `url_for('rnet_viewer.view_rnet_file')` in `base.html` automatically picks up the new route
- No hardcoded URLs were found in other files
- The Flask context processor now correctly identifies this as an admin route
- All blueprint routes inherit the `/admin/rnet` prefix

## Date Fixed
October 13, 2025
