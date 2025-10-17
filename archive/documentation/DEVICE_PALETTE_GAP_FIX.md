# Device Palette Gap & Cutoff Fix

## Problem
The device palette was leaving unnecessary gaps between sections and some buttons were getting cut off on mobile/tablet devices.

## Root Cause
The base `.palette-section` style had `gap: var(--space-md)` (16px) which was creating spacing between devices. While the responsive breakpoints were setting specific gap values (6px, 8px, 10px, 12px), these still created unwanted spacing.

## Solution

### Changed Gap Values to Zero
Updated all `.palette-section` styles across ALL screen sizes to use `gap: 0`:

**Base Style (Desktop & All Screens):**
- Changed `gap: var(--space-md)` (16px) → `gap: 0`

**Mobile Portrait (≤430px):**
- Changed `gap: 6px` → `gap: 0`

**Mobile Landscape (667-932px):**
- Changed `gap: 8px` → `gap: 0`

**Tablet Portrait (768-834px):**
- Changed `gap: 10px` → `gap: 0`

**Tablet Landscape (1024-1112px):**
- Changed `gap: 12px` → `gap: 0`

### Spacing Control Strategy
Instead of using flexbox `gap`, spacing is now controlled by:
- Individual device margins: `margin: 0 4px`, `margin: 0 5px`, `margin: 0 6px`
- Action button margins: `margin: 0 4px`, `margin: 0 5px`, `margin: 0 6px`
- This provides precise control and prevents unwanted gaps

### Existing Cutoff Prevention
Already implemented (from previous fixes):
- `flex-shrink: 0` on all devices and buttons
- `white-space: nowrap` on labels and buttons
- `overflow: hidden` and `text-overflow: ellipsis` on device labels
- Horizontal scrolling: `overflow-x: auto` on palette

## File Modified
- `templates/user/troubleshoot.html` (lines 4277-4555)

## Result
✅ No gaps between sections  
✅ All buttons display completely (no cutoffs)  
✅ Horizontal scrolling works smoothly  
✅ Precise spacing control via margins  
✅ Clean, professional appearance on all devices

## Testing Devices
- iPhone SE/8 (667 x 375) - Portrait & Landscape
- iPhone XR/11 (896 x 414) - Portrait & Landscape
- iPhone 14 Pro (844 x 390) - Portrait & Landscape
- iPhone 14 Pro Max (932 x 430) - Portrait & Landscape
- Pixel 6/7 (915 x 412) - Portrait & Landscape
- iPad (768-834px) - Portrait & Landscape
- iPad Pro (1024-1112px) - Portrait & Landscape

## Technical Details

### Before
```css
.palette-section {
    gap: 6px; /* or 8px, 10px, 12px */
    /* Created spacing between all child elements */
}
```

### After
```css
.palette-section {
    gap: 0; /* No flexbox gap */
    /* Spacing controlled by individual element margins */
}

.device {
    margin: 0 4px; /* Precise spacing */
    flex-shrink: 0; /* Prevent cutoffs */
}

.action-btn {
    margin: 0 4px; /* Precise spacing */
    flex-shrink: 0; /* Prevent cutoffs */
    white-space: nowrap; /* Prevent text wrapping */
}
```

## Notes
- This fix complements the horizontal scroll layout implemented earlier
- Combined with `flex-shrink: 0`, ensures perfect display across all device sizes
- Maintains visual consistency while eliminating unwanted gaps
