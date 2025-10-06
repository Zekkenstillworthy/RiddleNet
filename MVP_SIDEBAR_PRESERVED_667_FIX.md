# MVP - Troubleshooting Layout: Sidebar Preserved on 667×375+

## 🎯 Problem Solved

**Before (Distorted - Image 2):**
- Sidebar was being forcibly hidden on 667×375+ landscape viewports
- `--current-sidebar-width` was set to `0px`, causing layout collapse
- Canvas and palette were positioned from `left: 0`, ignoring sidebar space
- Visual artifacts and distortion from conflicting layout rules

**After (Clean - Image 1):**
- Sidebar remains visible and functional on 667×375+ landscape viewports
- Canvas and palette respect sidebar space using `var(--current-sidebar-width)`
- Clean 3-section device palette layout: LINK UP!/CHECK | ROUTER/SWITCH/PC | CONNECT/RESET
- No layout distortion or visual artifacts

---

## 📐 Layout Structure

```
┌──────────────┬────────────────────────────────────────┐
│              │          CANVAS AREA                   │
│   SIDEBAR    │       (Network Diagram)                │
│  (Preserved) │                                        │
│              ├────────────────────────────────────────┤
│              │ LINK UP! │ ROUTER SWITCH PC │ CONNECT │
└──────────────┴────────────────────────────────────────┘
   ← sidebar →  ←──── Canvas & Palette Respect ────→
    width              Sidebar Space
```

---

## 🔧 Implementation Details

### Media Query Target
```css
@media screen and (orientation: landscape) and (min-width: 667px)
```

### Key Changes

#### 1. **CSS Variables - Sidebar Preserved**
```css
:root {
    --palette-height: 80px;
    /* --current-sidebar-width is NOT set to 0px */
    /* Sidebar width remains dynamic based on global state */
}
```

#### 2. **Canvas Container - Respects Sidebar**
```css
#canvas-container {
    position: fixed;
    top: 0;
    left: var(--current-sidebar-width);    /* ✅ Starts after sidebar */
    right: 0;
    bottom: var(--palette-height);
    width: calc(100vw - var(--current-sidebar-width));  /* ✅ Accounts for sidebar */
    height: calc(100vh - var(--palette-height));
    z-index: var(--z-canvas);
}
```

#### 3. **Device Palette - Respects Sidebar**
```css
#device-palette {
    position: fixed;
    left: var(--current-sidebar-width);    /* ✅ Starts after sidebar */
    bottom: 0;
    right: 0;
    width: calc(100vw - var(--current-sidebar-width));  /* ✅ Accounts for sidebar */
    height: var(--palette-height);
    z-index: var(--z-palette);
}
```

#### 4. **3-Section Distribution (Image 1 Style)**
```css
/* Left Section - Actions */
.left-section {
    flex: 0 0 auto;
    min-width: 180px;
    /* Contains: LINK UP!, CHECK */
}

/* Center Section - Devices */
.center-section {
    flex: 1 1 auto;
    justify-content: center;
    /* Contains: ROUTER, SWITCH, PC */
}

/* Right Section - Actions */
.right-section {
    flex: 0 0 auto;
    min-width: 180px;
    justify-content: flex-end;
    /* Contains: CONNECT, RESET */
}
```

---

## 🎨 Visual Comparison

### Image 1 (Target - Clean Layout) ✅
```
┌──────────────┬─────────────────────────────────┐
│   SIDEBAR    │        CANVAS (Network)         │
│              │                                 │
│   [Stats]    │      [Network Topology]         │
│   [Hints]    │                                 │
│   [Timer]    │                                 │
│              ├─────────────────────────────────┤
│              │ LINK UP! │ R S P │ CONNECT     │
└──────────────┴─────────────────────────────────┘
```

### Image 2 (Distorted - FIXED) ❌ → ✅
```
BEFORE (Hidden Sidebar):
┌──────────────────────────────────────────────┐
│ [≡]              CANVAS (Network)            │  ← Sidebar hidden
│                                              │
│  LINK UP!  │  ROUTER SWITCH PC  │ ...       │  ← Distorted
└──────────────────────────────────────────────┘

AFTER (Preserved Sidebar):
┌──────────┬────────────────────────────────────┐
│ SIDEBAR  │        CANVAS (Network)            │  ← Sidebar visible
│          │                                    │
│          │  LINK UP!  │  R S P  │  CONNECT   │  ← Clean
└──────────┴────────────────────────────────────┘
```

---

## ✅ Success Criteria

### Layout Requirements
- [x] **Sidebar visible** on 667×375+ landscape viewports
- [x] **Canvas positioned** with `left: var(--current-sidebar-width)`
- [x] **Palette positioned** with `left: var(--current-sidebar-width)`
- [x] **Width calculations** use `calc(100vw - var(--current-sidebar-width))`
- [x] **3-section distribution** matches Image 1 structure

### No Distortion
- [x] **Removed** `--current-sidebar-width: 0px` override
- [x] **Removed** sidebar hiding rules (`display: none !important`)
- [x] **Removed** `#app` full-viewport positioning conflicts
- [x] **Clean** flex layout without visual artifacts

---

## 🧪 Testing Guide

### Test Viewports

#### 1. **iPhone SE Landscape (667×375)**
```bash
Chrome DevTools → Responsive → 667 × 375 → Landscape
```
**Expected:**
- Sidebar visible on left
- Canvas in center-right area
- Device palette at bottom with 3 sections
- No overlap or distortion

#### 2. **iPad Mini Landscape (1024×768)**
```bash
Chrome DevTools → iPad Mini → Landscape
```
**Expected:**
- Sidebar visible on left
- Full canvas area above palette
- Device palette cleanly distributed

#### 3. **Custom Landscape (896×414)**
```bash
Chrome DevTools → Responsive → 896 × 414
```
**Expected:**
- Sidebar visible and functional
- Canvas properly sized
- Palette buttons accessible

### Visual Checks

#### ✅ Canvas Area
```javascript
// Browser Console
const canvas = document.getElementById('canvas-container');
console.log('Canvas Left:', canvas.style.left || getComputedStyle(canvas).left);
console.log('Canvas Width:', canvas.style.width || getComputedStyle(canvas).width);
// Should show: left = sidebar width, width = viewport - sidebar
```

#### ✅ Device Palette
```javascript
const palette = document.getElementById('device-palette');
console.log('Palette Left:', palette.style.left || getComputedStyle(palette).left);
console.log('Palette Width:', palette.style.width || getComputedStyle(palette).width);
// Should show: left = sidebar width, width = viewport - sidebar
```

#### ✅ Sidebar
```javascript
const sidebar = document.getElementById('sidebar');
console.log('Sidebar Display:', getComputedStyle(sidebar).display);
console.log('Sidebar Width:', getComputedStyle(sidebar).width);
// Should show: display = block/flex (NOT none), width = sidebar width
```

---

## 🐛 Debug Commands

### Check Media Query Application
```javascript
// Verify landscape media query is active
console.log('Viewport:', window.innerWidth, 'x', window.innerHeight);
console.log('Orientation:', window.matchMedia('(orientation: landscape)').matches ? 'Landscape' : 'Portrait');
console.log('Min-width 667px:', window.matchMedia('(min-width: 667px)').matches);
console.log('Media Query Active:', 
    window.matchMedia('(orientation: landscape) and (min-width: 667px)').matches
);
```

### Check CSS Variables
```javascript
const root = getComputedStyle(document.documentElement);
console.log('--palette-height:', root.getPropertyValue('--palette-height').trim());
console.log('--current-sidebar-width:', root.getPropertyValue('--current-sidebar-width').trim());
console.log('--z-canvas:', root.getPropertyValue('--z-canvas').trim());
console.log('--z-palette:', root.getPropertyValue('--z-palette').trim());
```

### Verify Layout Calculations
```javascript
const sidebarWidth = getComputedStyle(document.documentElement)
    .getPropertyValue('--current-sidebar-width').trim();
console.log('Sidebar Width:', sidebarWidth);

const canvas = document.getElementById('canvas-container');
console.log('Canvas Computed Left:', getComputedStyle(canvas).left);
console.log('Canvas Computed Width:', getComputedStyle(canvas).width);

const palette = document.getElementById('device-palette');
console.log('Palette Computed Left:', getComputedStyle(palette).left);
console.log('Palette Computed Width:', getComputedStyle(palette).width);
```

---

## 📊 Comparison Table

| Aspect | Before (Distorted) | After (MVP Fixed) |
|--------|-------------------|-------------------|
| **Sidebar on 667×375+** | Hidden (`display: none`) | ✅ Visible |
| **`--current-sidebar-width`** | Forced to `0px` | ✅ Dynamic (preserved) |
| **Canvas `left` position** | `0` (full viewport) | ✅ `var(--current-sidebar-width)` |
| **Palette `left` position** | `0` (full viewport) | ✅ `var(--current-sidebar-width)` |
| **Width calculations** | `100vw` (ignores sidebar) | ✅ `calc(100vw - sidebar)` |
| **Layout Structure** | Distorted (Image 2) | ✅ Clean (Image 1) |
| **3-Section Distribution** | Collapsed/Overlapping | ✅ Proper flex layout |

---

## 🎯 Key Takeaways

### What Was Removed (Causing Distortion)
```css
/* ❌ REMOVED - These were causing layout distortion */
--current-sidebar-width: 0px;  /* Forced sidebar collapse */

#sidebar,
.sidebar-toggle,
.mobile-performance-toggle {
    display: none !important;        /* Hid sidebar */
    visibility: hidden !important;
    opacity: 0 !important;
}

#app {
    width: 100vw;  /* Full viewport without sidebar consideration */
}

#canvas-container {
    left: 0;       /* Started at viewport edge */
    width: 100vw;  /* Ignored sidebar */
}

#device-palette {
    left: 0;       /* Started at viewport edge */
    width: 100vw;  /* Ignored sidebar */
}
```

### What Was Added (Clean Layout)
```css
/* ✅ ADDED - Clean layout respecting sidebar */
#canvas-container {
    left: var(--current-sidebar-width);              /* Respect sidebar */
    width: calc(100vw - var(--current-sidebar-width)); /* Account for sidebar */
    z-index: var(--z-canvas);                        /* Proper layering */
}

#device-palette {
    left: var(--current-sidebar-width);              /* Respect sidebar */
    width: calc(100vw - var(--current-sidebar-width)); /* Account for sidebar */
    z-index: var(--z-palette);                       /* Proper layering */
}

/* Clean 3-section distribution */
.left-section { min-width: 180px; }
.center-section { flex: 1 1 auto; }
.right-section { min-width: 180px; justify-content: flex-end; }
```

---

## 📝 Files Modified

### `templates/user/troubleshoot.html`
- **Line ~3002**: Media query `@media screen and (orientation: landscape) and (min-width: 667px)`
- **Changed**: Removed sidebar-hiding rules, added sidebar-respecting positioning
- **Impact**: Sidebar now visible on 667×375+ landscape viewports

---

## 🚀 Running the Fix

1. **Start the application:**
   ```bash
   python run.py
   ```

2. **Navigate to troubleshooting page:**
   ```
   http://127.0.0.1:5001/troubleshooting/
   ```

3. **Test on 667×375 landscape:**
   - Open Chrome DevTools (F12)
   - Click device toolbar icon
   - Select "Responsive"
   - Set dimensions: 667 × 375
   - Rotate to landscape

4. **Verify:**
   - ✅ Sidebar visible on left
   - ✅ Canvas in center area
   - ✅ Device palette at bottom with clean 3-section layout
   - ✅ No distortion or overlap

---

## 📌 MVP Summary

**Goal:** Preserve sidebar on 667×375+ landscape viewports while maintaining clean Image 1 layout

**Solution:**
1. Removed `--current-sidebar-width: 0px` override
2. Removed sidebar hiding rules
3. Updated canvas to use `left: var(--current-sidebar-width)`
4. Updated palette to use `left: var(--current-sidebar-width)`
5. Added `calc(100vw - var(--current-sidebar-width))` for width calculations
6. Maintained clean 3-section flex distribution

**Result:** Sidebar preserved, layout clean, no distortion ✅

---

## 🔗 Related Documentation

- `MVP_CLEAN_LAYOUT_FIX.md` - Previous simplification (removed complex queries)
- `MVP_DEVICE_PALETTE_NON_OVERLAP_FIX.md` - Initial overlap fix
- `LANDSCAPE_667x375_QUICK_REF.md` - Landscape optimization guide

---

**Implementation Date:** October 7, 2025  
**Status:** ✅ Complete  
**Testing Status:** Ready for user validation
