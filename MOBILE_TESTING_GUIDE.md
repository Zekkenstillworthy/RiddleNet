# Visual Testing Guide - Mobile Responsive Simulation

## Quick Visual Verification Checklist

### 🖥️ Desktop View (1200px+)
```
Expected Layout:
┌──────────────────────────────────────────────────┐
│ [← Back]  Network Simulation      [Submit] [🔧] │ ← Header
├──────────────────────────────────────────────────┤
│ ┌────────────────────────┐ ┌──────────────────┐ │
│ │                        │ │ STEPS PANEL      │ │
│ │   CANVAS AREA          │ │ ✓ Step 1         │ │
│ │   Network Diagram      │ │ ⏺ Step 2        │ │
│ │   [Devices draggable]  │ │ ○ Step 3         │ │
│ │                        │ │                  │ │
│ └────────────────────────┘ └──────────────────┘ │
├──────────────────────────────────────────────────┤
│ 🖧 DEVICE PALETTE (Fixed Bottom)                 │
│ [Router][Switch][Hub][PC][Laptop][Wired]...      │
└──────────────────────────────────────────────────┘

✓ Steps panel on RIGHT side
✓ Device palette at BOTTOM
✓ Canvas takes majority of space
✓ Sidebars hidden (toggle via buttons)
```

### 📱 Mobile View (< 768px)
```
Expected Layout:
┌─────────────────────────┐
│ [←] Network Sim    [🔧] │ ← Compact Header
├─────────────────────────┤
│                         │
│                         │
│    CANVAS AREA          │ ← 50vh height
│    Network Diagram      │
│                         │
│                         │
├─────────────────────────┤
│                         │
│    STEPS PANEL          │ ← Below canvas
│    (Scrollable)         │
│                         │
└─────────────────────────┘

Floating Buttons (Right Edge):
  ┌───┐
  │ 📊 │ ← Performance (Cyan) - Top
  └───┘
  
  ┌───┐
  │ 👥 │ ← Collaboration (Green) - Middle
  └───┘
  
  ┌───┐
  │ 📦 │ ← Device Palette (Purple) - Bottom
  └───┘

Device Palette (Hidden by default):
┌──────────┐
│ 📦 Devices│
│ ────────  │
│ [Router]  │ ← Slides in from LEFT
│ [Switch]  │    when purple button tapped
│ [Hub]     │
│ [PC]      │
│ (scroll)  │
└──────────┘

✓ Vertical stack: Header → Canvas → Steps
✓ Canvas is 50% of viewport height
✓ Steps panel below (not beside)
✓ Device palette slides from LEFT side
✓ Three floating action buttons visible
```

## Step-by-Step Testing

### Test 1: Desktop Layout ✅
1. **Open**: `http://127.0.0.1:5001/dynamic/simulation/70`
2. **Browser width**: > 1200px
3. **Expected**:
   - [ ] Header spans full width
   - [ ] Canvas on left, Steps panel on right
   - [ ] Device palette fixed at bottom
   - [ ] No floating buttons visible
   - [ ] Devices draggable to canvas
   - [ ] Steps panel scrollable if needed

### Test 2: Tablet Landscape (1024px)
1. **Resize**: Browser to 1024px width
2. **Expected**:
   - [ ] Similar to desktop but narrower
   - [ ] Floating buttons appear on right edge
   - [ ] Clicking cyan button opens Performance sidebar
   - [ ] Clicking green button opens Collaboration sidebar
   - [ ] Device palette still at bottom (condensed)
   - [ ] Layout remains horizontal

### Test 3: Tablet Portrait (768px)
1. **Resize**: Browser to 768px width
2. **Expected**:
   - [ ] Layout starts transitioning to vertical
   - [ ] Canvas and steps side-by-side OR stacked
   - [ ] Floating buttons clearly visible
   - [ ] Device palette adapts to narrower space
   - [ ] Touch targets easy to hit

### Test 4: Mobile Portrait (< 768px) ⭐ KEY TEST
1. **Resize**: Browser to 375px width (iPhone size)
2. **Expected**:

   **Header (Top)**
   - [ ] Back button on left (easy to tap)
   - [ ] Title visible but compact
   - [ ] Tools/submit button on right
   - [ ] No overflow or wrapping issues

   **Canvas Area (Middle)**
   - [ ] Full width of screen
   - [ ] Height is ~50% of viewport
   - [ ] Network diagram visible and interactive
   - [ ] Device drag-and-drop still works
   - [ ] No horizontal scrolling

   **Steps Panel (Below Canvas)**
   - [ ] Full width
   - [ ] Scrollable vertically
   - [ ] Not overlapping canvas
   - [ ] Steps clearly readable
   - [ ] Collapse button works

   **Floating Buttons (Right Edge)**
   - [ ] Three circular buttons stacked vertically
   - [ ] From top to bottom: Cyan, Green, Purple
   - [ ] Each button ~50px × 50px
   - [ ] Easy to tap (good spacing)
   - [ ] Visible over all content

3. **Tap Purple Button** (Device Palette)
   - [ ] Panel slides in from LEFT side
   - [ ] Width: ~280px (doesn't cover all screen)
   - [ ] Shows device categories vertically
   - [ ] 3 columns of device icons
   - [ ] Each device icon tappable
   - [ ] Device labels visible
   - [ ] Scrollable vertically if needed
   - [ ] Tap outside palette to close

4. **Tap Cyan Button** (Performance)
   - [ ] Full-screen overlay appears
   - [ ] Slides in from right
   - [ ] Shows current score, metrics, progress
   - [ ] Close button in header works
   - [ ] Tap cyan button again to close

5. **Tap Green Button** (Collaboration)
   - [ ] Full-screen overlay appears
   - [ ] Shows session info, team members
   - [ ] Chat interface visible
   - [ ] Close button works
   - [ ] Tap green button again to close

### Test 5: Small Mobile (< 600px)
1. **Resize**: Browser to 320px width (small phone)
2. **Expected**:
   - [ ] All content still accessible
   - [ ] Device palette: 2 columns instead of 3
   - [ ] Floating buttons slightly smaller (~45px)
   - [ ] Text remains readable
   - [ ] No critical features hidden

### Test 6: Mobile Landscape
1. **Rotate**: Device to landscape mode
2. **Expected**:
   - [ ] Canvas height increases (70vh)
   - [ ] More horizontal space utilized
   - [ ] Floating buttons adjust position
   - [ ] Device palette still functional
   - [ ] Steps panel height optimized

### Test 7: Interaction Testing (Mobile)
**Device Drag and Drop**
- [ ] Tap device in palette
- [ ] Drag to canvas
- [ ] Device places on canvas
- [ ] Device selectable
- [ ] Device deletable

**Touch Targets**
- [ ] All buttons > 44px × 44px
- [ ] Easy to tap without zoom
- [ ] No accidental taps
- [ ] Proper spacing between elements

**Scrolling**
- [ ] Canvas doesn't scroll (fixed height)
- [ ] Steps panel scrolls vertically
- [ ] Device palette scrolls vertically
- [ ] No horizontal scroll anywhere

**Overlay Management**
- [ ] Opening sidebar closes others
- [ ] Back button closes overlays
- [ ] Tap outside closes device palette
- [ ] No multiple overlays open simultaneously

## Common Issues to Check

### ❌ Problem: Device palette still at bottom on mobile
**Fix**: Ensure browser width is < 768px. Hard refresh (Ctrl+Shift+R).

### ❌ Problem: Floating buttons not visible
**Fix**: Check z-index, ensure they're not behind other elements.

### ❌ Problem: Canvas too small on mobile
**Fix**: Check viewport height, should be ~50vh (half screen).

### ❌ Problem: Steps panel overlapping canvas
**Fix**: Verify flex-direction is column, not row.

### ❌ Problem: Device palette too narrow
**Fix**: Should be 280px on mobile, 260px on small mobile.

### ❌ Problem: Sidebars not full screen on mobile
**Fix**: Check width and height are 100vw and 100vh.

## Browser-Specific Testing

### Chrome Mobile
- [ ] Open Chrome DevTools
- [ ] Toggle device toolbar (Ctrl+Shift+M)
- [ ] Select "iPhone 12 Pro" or similar
- [ ] Test all interactions

### Safari iOS (Real Device)
- [ ] Test on actual iPhone
- [ ] Check touch interactions
- [ ] Verify no iOS-specific bugs
- [ ] Test in both orientations

### Firefox Mobile Emulator
- [ ] F12 → Responsive Design Mode
- [ ] Test different device presets
- [ ] Verify rendering consistency

## Visual Indicators of Success

✅ **Desktop**: Traditional sidebar layout, palette at bottom
✅ **Tablet**: Floating buttons appear, condensed layout
✅ **Mobile**: Vertical stack, LEFT-side palette, three FABs
✅ **All Sizes**: No horizontal scrolling
✅ **All Sizes**: All interactive elements accessible
✅ **All Sizes**: Touch targets appropriately sized

## Performance Checks

- [ ] Page loads quickly on mobile network
- [ ] Smooth transitions (no lag)
- [ ] No layout shifts during load
- [ ] Images/icons load properly
- [ ] No console errors

## Screenshot Locations to Test

1. **1920×1080** (Desktop Full HD)
2. **1366×768** (Laptop)
3. **1024×768** (Tablet Landscape)
4. **768×1024** (Tablet Portrait)
5. **414×896** (iPhone 11 Pro Max)
6. **375×667** (iPhone SE)
7. **360×640** (Android Small)

## Final Verification

Before marking as complete:
- [ ] All layouts tested at breakpoints
- [ ] No console errors on any device
- [ ] All interactive elements functional
- [ ] Touch targets meet accessibility standards
- [ ] No content overflow or clipping
- [ ] Floating buttons always accessible
- [ ] Device palette slides smoothly
- [ ] Sidebars open/close properly
- [ ] Original desktop functionality intact

## Sign-off Checklist

- [ ] Desktop: Tested ✅
- [ ] Tablet Landscape: Tested ✅
- [ ] Tablet Portrait: Tested ✅
- [ ] Mobile Portrait: Tested ✅
- [ ] Mobile Landscape: Tested ✅
- [ ] Small Mobile: Tested ✅
- [ ] Touch Interactions: Tested ✅
- [ ] All Browsers: Tested ✅

**Status**: Ready for Production ✅
**Date**: _____________
**Tester**: _____________
