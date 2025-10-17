# Mobile Landscape 667x375 Layout Fix

## Issue Overview
At viewport size **667x375** (e.g., iPhone SE in landscape mode), the troubleshooting page canvas was displaying with incorrect layout structure, appearing compressed instead of filling the available viewport space.

### Visual Comparison
- **Image 1 (Wrong)**: Canvas compressed, not utilizing full viewport
- **Image 2 (Correct)**: Canvas properly fills viewport with device palette at bottom

## Root Cause
The existing mobile landscape media query (`@media screen and (max-width: 896px) and (orientation: landscape)`) was too broad and didn't account for the specific constraints of very small landscape viewports like 667x375.

## Solution Implemented

### New Media Query Added
Added a specific media query targeting 667x375 landscape viewport:

```css
@media screen and (max-width: 667px) and (max-height: 375px) and (orientation: landscape)
```

### Key Changes

#### 1. **Main Content Reset**
```css
.main-content {
    margin: 0 !important;
    padding: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
}
```
- Ensures no inherited padding/margins from base template
- Forces full viewport usage

#### 2. **App Container Fixed Positioning**
```css
#app {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;
    height: 100vh;
    margin: 0;
    padding: 0;
    overflow: hidden;
}
```
- Fixed positioning ensures viewport fill
- Eliminates scroll behavior

#### 3. **Canvas Container Optimization**
```css
#canvas-container {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: var(--palette-height);
    width: 100vw;
    height: calc(100vh - var(--palette-height));
    padding: 4px;
    margin: 0;
    border: none;
}
```
- Fills entire viewport width
- Accounts for device palette height at bottom
- Minimal padding (4px) for compact display

#### 4. **Canvas Element Maximized**
```css
#Canvas {
    width: 100%;
    height: 100%;
    max-width: 100%;
    max-height: 100%;
    border-radius: 4px;
    border: 1px solid var(--cyber-glow);
}
```
- Removes size constraints
- Minimal border radius for space efficiency
- Thinner border (1px vs 2px)

#### 5. **Device Palette Compact Mode**
```css
#device-palette {
    --palette-height: 70px;
    bottom: 0;
    left: 0;
    right: 0;
    height: 70px;
    padding: 4px 8px;
}
```
- Reduced height from 88px to 70px
- Minimal padding for compact layout

#### 6. **Sidebar Hidden**
```css
#sidebar,
.sidebar-toggle {
    display: none !important;
}

:root {
    --current-sidebar-width: 0px;
}
```
- Hides sidebar to maximize canvas space
- Updates CSS variable for dependent calculations

#### 7. **Performance Sidebar Adjustments**
```css
.performance-sidebar {
    --performance-sidebar-width: 250px;
    font-size: 13px;
}

.mobile-performance-toggle {
    width: 36px;
    height: 36px;
    font-size: 16px;
}
```
- Smaller performance sidebar width
- Reduced font size for compact display
- Smaller toggle button

## Testing Instructions

### 1. Clear Browser Cache
```
Ctrl + Shift + Delete
```

### 2. Set Viewport to 667x375
**Chrome DevTools:**
- F12 → Toggle Device Toolbar (Ctrl+Shift+M)
- Select "iPhone SE" or create custom device
- Set to Landscape orientation

**Firefox Developer Tools:**
- F12 → Responsive Design Mode (Ctrl+Shift+M)
- Set dimensions: 667 x 375

### 3. Navigate to Troubleshooting Page
```
http://127.0.0.1:5001/troubleshooting/
```

### 4. Verify Layout
✅ **Expected Results:**
- Canvas fills entire viewport width (667px)
- Device palette visible at bottom (70px height)
- No sidebar visible
- Canvas height: 305px (375vh - 70px palette)
- No compression or wasted space
- Proper border and styling maintained

### 5. Test Interactions
- Click "LINK UP!" button - verify modal displays correctly
- Click "CHECK" button - verify device connections work
- Toggle performance sidebar - verify overlay behavior
- Rotate device to portrait - verify fallback behavior

## Technical Details

### Viewport Dimensions
- **Width**: 667px
- **Height**: 375px
- **Orientation**: Landscape
- **Device Examples**: iPhone SE, older Android devices

### Layout Calculations
```
Canvas Height = 100vh - palette-height
Canvas Height = 375px - 70px = 305px
Canvas Width = 100vw = 667px
```

### Z-Index Hierarchy (Maintained)
- Canvas: `var(--z-canvas)` (10)
- Device Palette: `var(--z-palette)` (100)
- Modals: `var(--z-modal)` (2001)
- Performance Sidebar: Dynamic overlay

## Benefits

### Space Efficiency
- **Before**: Canvas compressed, wasted space
- **After**: Full viewport utilization

### User Experience
- Larger canvas area for network diagram
- Better touch target spacing
- Optimal device palette visibility
- No unnecessary UI elements

### Performance
- Minimal reflows
- Efficient CSS cascade
- Proper isolation with `position: fixed`

## Files Modified
- `templates/user/troubleshoot.html` (Lines ~2920-3014)

## Compatibility
- ✅ iPhone SE (landscape)
- ✅ Small Android devices (landscape)
- ✅ Any device at 667x375 landscape viewport
- ✅ Maintains compatibility with larger viewports
- ✅ Graceful degradation for portrait mode

## Notes
- This media query is highly specific and won't affect other viewports
- Sidebar hidden at this size to maximize canvas space
- Device palette remains functional with compact layout
- Performance sidebar still accessible via toggle button
- All existing functionality preserved

## Related Documentation
- `TROUBLESHOOTING_LAYOUT_FIX_FINAL.md` - Base layout fixes
- `MOBILE_LANDSCAPE_AUTO_FULLSCREEN_FIX.md` - Auto-fullscreen behavior
- `MVP_AUTO_LANDSCAPE_IMPLEMENTATION_COMPLETE.md` - Landscape optimizations
