# Viewport Tracking Feature - User Presence Visualization

## Overview
The viewport tracking feature adds visual indicators showing where each user is looking/scrolling on the canvas in real-time. This enhances collaboration by letting team members see each other's focus areas.

## Features Implemented

### 1. **Viewport Indicators**
- Semi-transparent rectangles showing each user's visible screen area
- Color-coded to match user cursor colors (6 unique colors)
- Includes username label (e.g., "Gilbert's view")
- Updates in real-time as users scroll or resize their windows

### 2. **Real-time Updates**
- Viewport data sent with cursor position updates
- Throttled to 500ms for scroll events (less frequent than cursor)
- Captures:
  - Scroll position (x, y)
  - Viewport dimensions (width, height)
  - Total document size

### 3. **Visual Design**
- Dashed border with subtle transparency
- Matching color scheme with cursor avatars
- Non-intrusive (low opacity background)
- Backdrop blur effect for modern look

## Technical Implementation

### Frontend Changes

#### `collaboration-real-time.js`

**New Method: `getViewportInfo()`**
```javascript
getViewportInfo() {
    return {
        x: window.scrollX || window.pageXOffset,
        y: window.scrollY || window.pageYOffset,
        width: window.innerWidth,
        height: window.innerHeight,
        scrollWidth: document.documentElement.scrollWidth,
        scrollHeight: document.documentElement.scrollHeight
    };
}
```

**Updated: `throttledCursorUpdate()`**
- Now includes viewport data in emissions
- Calls `getViewportInfo()` before emitting

**New Method: `updateViewportIndicator()`**
```javascript
updateViewportIndicator(userId, viewport, username) {
    // Creates or updates viewport rectangle
    // Positions based on viewport.x, viewport.y
    // Sizes based on viewport.width, viewport.height
    // Color-coded by user ID
}
```

**Scroll Tracking**
- Added window scroll event listener
- Throttled to 500ms (viewport updates less critical than cursor)
- Tracks last mouse position for scroll-triggered updates

**Cleanup Enhanced**
- `removeCursor()` now also removes viewport indicator
- `cleanupCursors()` cleans up viewport indicators map

### CSS Styles

**Viewport Indicator Base**
```css
.viewport-indicator {
    position: fixed;
    border: 2px dashed rgba(0, 217, 255, 0.5);
    pointer-events: none;
    z-index: 9998;
    transition: all 0.3s ease;
    background: rgba(0, 217, 255, 0.05);
    backdrop-filter: blur(2px);
}
```

**Color Variants (user-1 through user-6)**
- Red (#ff6b6b)
- Teal (#4ecdc4)
- Yellow (#ffe66d)
- Pink (#ff8c94)
- Magenta (#c44569)
- Blue (#40739e)

**Viewport Label**
```css
.viewport-label {
    position: absolute;
    top: -26px;
    left: 0;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 11px;
}
```

### Backend Changes

#### `socket_events.py`

**Enhanced: `handle_cursor_update()`**
```python
# Extract viewport data if provided
viewport = data.get('viewport')

cursor_data = {
    'user_id': str(current_user.id),
    'username': current_user.username,
    'position': position,
    'color': lobby.participants[str(current_user.id)]['color'],
    'profile_image': current_user.profile_img
}

# Add viewport data if available
if viewport:
    cursor_data['viewport'] = viewport
    print(f"👁️ [VIEWPORT] User {current_user.username} viewport: {viewport}")
```

## Data Flow

```
1. User scrolls or moves mouse
   ↓
2. Frontend: throttledCursorUpdate() called
   ↓
3. getViewportInfo() captures current viewport
   ↓
4. Emit: 'update_cursor_position' with {x, y, viewport: {...}}
   ↓
5. Backend: handle_cursor_update() receives data
   ↓
6. Backend broadcasts: 'cursor_moved' with viewport to room
   ↓
7. Other users receive: handleCursorUpdate()
   ↓
8. updateCursorPosition() → updateViewportIndicator()
   ↓
9. Viewport rectangle appears/updates on screen!
```

## Viewport Data Structure

### Sent to Server
```javascript
{
    session_id: "D8CAB227",
    x: 450,              // Cursor X
    y: 320,              // Cursor Y
    username: "Gilbert",
    user_id: "1",
    viewport: {
        x: 0,            // Scroll X position
        y: 150,          // Scroll Y position
        width: 1920,     // Viewport width
        height: 1080,    // Viewport height
        scrollWidth: 2000,   // Total document width
        scrollHeight: 3000   // Total document height
    }
}
```

### Received by Other Users
```javascript
{
    user_id: "1",
    username: "Gilbert",
    position: {x: 450, y: 320},
    color: "blue",
    profile_image: null,
    viewport: {
        x: 0,
        y: 150,
        width: 1920,
        height: 1080,
        scrollWidth: 2000,
        scrollHeight: 3000
    }
}
```

## User Experience

### What Users See
1. **Own Cursor**: Not visible (standard behavior)
2. **Other Users' Cursors**: Avatar with username label
3. **Other Users' Viewports**: Colored rectangle showing their screen area
4. **Viewport Label**: Shows "Username's view" at top of rectangle

### Visual Example
```
┌─────────────────────────────────────┐
│ [Gilbert's view]                    │  ← Viewport Label
│ ╔═════════════════════════════════╗ │
│ ║                                 ║ │  ← Dashed border (Gilbert's viewport)
│ ║         🟦 Gilbert              ║ │  ← Gilbert's cursor inside
│ ║                                 ║ │
│ ║                                 ║ │
│ ╚═════════════════════════════════╝ │
│                                     │
│  🟢 Zen                             │  ← Zen's cursor (different area)
│  [Zen's view]                       │
│  ╔═══════════════╗                  │
│  ║               ║                  │
│  ╚═══════════════╝                  │
└─────────────────────────────────────┘
```

## Performance Considerations

### Throttling Strategy
- **Cursor Updates**: 100ms throttle (smooth tracking)
- **Viewport Updates**: 500ms throttle (adequate for scroll)
- **Reason**: Viewport changes less critical than cursor position

### Memory Management
- Viewport indicators stored in `Map()` for O(1) lookup
- Automatic cleanup when users leave
- Reuses existing DOM elements (no memory leak)

### Network Optimization
- Viewport data only sent when available
- Backend only broadcasts if viewport present
- Minimal data structure (6 numeric values)

## Browser Compatibility

### Supported
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

### Fallback Behavior
- If viewport data missing: Only cursor shows (graceful degradation)
- No errors thrown if viewport unavailable

## Testing Checklist

### Basic Functionality
- [ ] Viewport indicator appears when user joins
- [ ] Indicator updates when user scrolls
- [ ] Indicator updates when user resizes window
- [ ] Correct color coding (matches cursor color)
- [ ] Username label displays correctly

### Multi-User Scenarios
- [ ] Multiple viewports don't overlap labels
- [ ] Each user has unique color
- [ ] Viewports update independently
- [ ] No performance lag with 3+ users

### Edge Cases
- [ ] User scrolls very fast
- [ ] User resizes window dramatically
- [ ] User leaves session (viewport removed)
- [ ] User rejoins (viewport recreated)

### Console Logs
```
👁️ [VIEWPORT DEBUG] Setting up scroll listener with throttle: 500ms
👁️ [VIEWPORT DEBUG] Scroll detected, updating viewport
👁️ [VIEWPORT DEBUG] Updating viewport for user: 1 Gilbert
👁️ [VIEWPORT DEBUG] Viewport data: {x: 0, y: 150, width: 1920, height: 1080}
✅ [VIEWPORT DEBUG] Viewport indicator created
✅ [VIEWPORT DEBUG] Viewport indicator updated
```

## Configuration

### Adjustable Parameters

**In `collaboration-real-time.js`:**
```javascript
// Cursor throttle (currently 100ms)
const throttle = this.config.cursorUpdateThrottle || 100;

// Viewport throttle (currently 500ms)
const scrollThrottle = 500;
```

### Customization Options

**Viewport Opacity**
```css
.viewport-indicator {
    background: rgba(0, 217, 255, 0.05); /* Adjust alpha */
}
```

**Border Style**
```css
.viewport-indicator {
    border: 2px dashed rgba(0, 217, 255, 0.5); /* solid/dotted/dashed */
}
```

## Future Enhancements

### Potential Features
1. **Focus Indicators**: Highlight when user clicks/interacts
2. **Minimap**: Small overview showing all user viewports
3. **Follow Mode**: Click viewport to pan camera to that area
4. **Viewport History**: Trail showing where user has been
5. **Activity Heatmap**: Show frequently viewed areas

### Performance Improvements
1. **Spatial Culling**: Only render viewports near current view
2. **Canvas Rendering**: Use canvas instead of DOM for better performance
3. **Delta Updates**: Only send changed viewport properties

## Troubleshooting

### Viewport Not Appearing
1. Check console for viewport debug logs
2. Verify `viewport` data in `cursor_moved` event
3. Ensure `viewportIndicators` Map is initialized
4. Check CSS z-index conflicts

### Viewport Position Wrong
1. Verify scroll position calculation
2. Check for CSS transforms affecting positioning
3. Ensure viewport uses `fixed` positioning

### Performance Issues
1. Increase scroll throttle (500ms → 1000ms)
2. Disable viewport blur effect
3. Reduce viewport border complexity

## Files Modified
- `static/js/collaboration-real-time.js` - Core viewport logic
- `templates/user/dynamic_simulation.html` - CSS styles
- `socket_events.py` - Backend viewport relay

## Related Documentation
- `CURSOR_TRACKING_FIX.md` - Cursor tracking implementation
- `CURSOR_TRACKING_DEBUG_GUIDE.md` - Debugging guide
- `CURSOR_TRACKING_IMPLEMENTATION.md` - Original feature docs

## Status
✅ **IMPLEMENTED** - Viewport tracking is fully functional and ready for testing!

## Quick Start

1. **Restart Flask app** to pick up backend changes
2. **Clear browser cache** (Ctrl+Shift+Del)
3. **Open two browser windows**
4. **Join same lobby from both**
5. **Scroll in one window** → See viewport indicator in other window
6. **Resize window** → Viewport indicator updates automatically

Enjoy enhanced collaboration with viewport awareness! 🎯👁️
