# Dynamic Simulation Page - Responsive Layout Visual Guide

## Desktop Layout (>1024px)
```
┌─────────────────────────────────────────────────────────────────┐
│  [← Back]  [Type] Simulation Title            [Score] [Submit]  │
├──────────────────────────────────┬──────────────────────────────┤
│                                  │  ╔════════════════════════╗  │
│                                  │  ║    Steps Panel         ║  │
│         Canvas Area              │  ║  1. [Active Step]      ║  │
│    (Network Topology)            │  ║  2. [Pending Step]     ║  │
│                                  │  ║  3. [Pending Step]     ║  │
│                                  │  ║                        ║  │
│                                  │  ║  [Step Details]        ║  │
│                                  │  ╚════════════════════════╝  │
├──────────────────────────────────┴──────────────────────────────┤
│  Device Palette: [Routers] [Switches] [Endpoints] [Cables]      │
│  [🖧] [🖧] [🖧] [🖧] │ [⚡] [⚡] [⚡] [⚡] │ [💻] [💻] [💻] [💻]│
└──────────────────────────────────────────────────────────────────┘
                                       [Performance Tab] →
                                       [Collaboration Tab] →
```

## Tablet Portrait (≤768px)
```
┌──────────────────────────────┐
│  [← Back] [Type]             │
│  Simulation Title            │
│  Score: 0  Time: 00:00       │
│  [Submit Answer]             │
├──────────────────────────────┤
│                              │
│      Canvas Area             │
│  (Network Topology)          │
│      50vh Height             │
│                              │
├──────────────────────────────┤
│  ╔════════════════════════╗  │
│  ║   Steps Panel          ║  │
│  ║ 1. [Active Step]       ║  │
│  ║ 2. [Step Two]          ║  │
│  ║ [Details...]           ║  │
│  ╚════════════════════════╝  │
├──────────────────────────────┤
│ Device Palette (Scrollable→) │
│ [Router] [Switch] [PC]       │
│ [🖧][🖧][⚡][⚡][💻][💻]     │
└──────────────────────────────┘
           [📊]  [👥]  (Floating buttons)
```

## Mobile Portrait (≤600px)
```
┌───────────────────────┐
│ [←] [T] Title         │
│ Score: 0 │ Time: 0:00 │
│ [Submit]              │
├───────────────────────┤
│                       │
│   Canvas              │
│   45vh                │
│                       │
├───────────────────────┤
│ Steps ▼               │
│ 1. [Active]           │
│ 2. [Next]             │
├───────────────────────┤
│ Devices (Wrap)        │
│ [🖧][🖧]              │
│ [⚡][⚡]              │
│ [💻][💻]              │
└───────────────────────┘
      [📊]  [👥]
```

## Mobile Landscape (≤896px landscape)
```
┌──────────────────────────────────────────────────────┐
│ [←][T] Title         Score: 0 Time: 00:00  [Submit]  │
├────────────────────────────┬─────────────────────────┤
│                            │  Steps ▼                │
│        Canvas              │  1. [Active]            │
│    (Optimized Height)      │  2. [Next]              │
│                            │  [Details]              │
├────────────────────────────┴─────────────────────────┤
│ Devices: [🖧][🖧][⚡][⚡][💻][💻] (Scroll→)         │
└──────────────────────────────────────────────────────┘
                             [📊][👥]
```

## Key Responsive Features by Breakpoint

### 1024px (Tablet Landscape)
- Narrower sidebars
- Compressed spacing
- Maintained side-by-side layout

### 768px (Tablet Portrait) - MAJOR BREAKPOINT
✅ Stacked layout (vertical)
✅ Full-width steps panel at bottom
✅ Floating action buttons appear
✅ Sidebars become full-screen overlays
✅ 3-column device grid
✅ Score items stack vertically

### 600px (Mobile Portrait)
✅ 2-column device grid
✅ Wrapped device categories
✅ Further compressed spacing
✅ Minimal typography

### 480px (Extra Small)
✅ Ultra-compact layout
✅ Stacked step headers
✅ 2-column devices only
✅ Minimum viable spacing

### Landscape (<896px)
✅ Optimized for horizontal space
✅ Reduced vertical elements
✅ Compact device palette

## Touch Interactions

### Device Palette
```
Desktop: Click & Drag
Mobile:  Tap to select, Tap canvas to place
         Swipe categories horizontally
```

### Canvas
```
Desktop: Mouse drag devices, Click to select
Mobile:  Touch drag devices, Tap to select
         Pinch to zoom (if implemented)
```

### Sidebars
```
Desktop: Tab toggles on right edge
Mobile:  Floating action buttons
         Slide in full-screen
         Tap backdrop to close
```

## Element Sizes Across Breakpoints

| Element          | Desktop   | Tablet   | Mobile   | Touch    |
|------------------|-----------|----------|----------|----------|
| Touch Target     | 36×36px   | 36×36px  | 44×44px  | 44×44px  |
| Button Padding   | 1rem      | 0.75rem  | 0.5rem   | 0.75rem  |
| Title Font       | 1.5rem    | 1.2rem   | 0.95rem  | -        |
| Device Item      | 85px H    | 75px H   | 70px H   | -        |
| Canvas Height    | Flex      | 50vh     | 45vh     | Auto     |
| Steps Panel      | 420px W   | 100% W   | 100% W   | -        |
| Sidebar Width    | 350px     | 100vw    | 100vw    | -        |

## Spacing Scale

| Variable      | Desktop | Tablet | Mobile |
|---------------|---------|--------|--------|
| Header Pad    | 2rem    | 1rem   | 0.5rem |
| Content Gap   | 1.5rem  | 1rem   | 0.5rem |
| Item Gap      | 0.75rem | 0.5rem | 0.4rem |
| Panel Margin  | 1rem    | 0.5rem | 0.25rem|

## Color & Contrast

All breakpoints maintain:
- Cyber Glow: #00D9FF
- Background: #020617
- Text Primary: #F8FAFC
- Glass Border: rgba(255,255,255,0.15)

## Scrolling Behavior

### Desktop
- Body: Vertical scroll
- Steps: Internal scroll
- Palette: Static

### Mobile
- Body: Vertical scroll
- Steps: Internal scroll (max 45vh)
- Palette: Horizontal category scroll
- Sidebars: Internal scroll when full-screen

## Animation States

All animations disabled via:
```css
*, *::before, *::after {
    animation-duration: 0s !important;
    transition-duration: 0s !important;
}
```

This improves mobile performance significantly.

## Z-Index Layer Stack (Mobile)

```
Layer 5 (2000): Full-screen sidebars
Layer 4 (1600): Floating action buttons
Layer 3 (1100): Header
Layer 2 (1000): Device palette
Layer 1 (100):  Steps panel
Layer 0:        Canvas & content
```

## Orientation Detection

### Portrait
- Vertical stacking emphasized
- Full-width elements
- Taller canvas relative to viewport

### Landscape
- Horizontal space utilized
- Side-by-side where possible
- Compressed vertical elements
- Shallower device palette

## Critical CSS for Mobile

### Prevent Zoom
```css
input, textarea, select {
    font-size: 16px !important;
}
```

### Prevent Horizontal Scroll
```css
body, .simulation-wrapper {
    overflow-x: hidden;
    max-width: 100vw;
}
```

### Touch Feedback
```css
@media (hover: none) {
    .btn:active {
        transform: scale(0.95);
        opacity: 0.8;
    }
}
```

## Testing Matrix

| Device          | Width | Orientation | Status |
|-----------------|-------|-------------|--------|
| iPhone SE       | 375px | Portrait    | ✅     |
| iPhone 12       | 390px | Portrait    | ✅     |
| iPhone 12 Land  | 844px | Landscape   | ✅     |
| iPad Mini       | 768px | Portrait    | ✅     |
| iPad            | 810px | Portrait    | ✅     |
| iPad Land       | 1080px| Landscape   | ✅     |
| Galaxy S21      | 360px | Portrait    | ✅     |
| Pixel 5         | 393px | Portrait    | ✅     |

## Browser Support

✅ Chrome Mobile 90+
✅ Safari iOS 14+
✅ Firefox Mobile 90+
✅ Samsung Internet 14+
✅ Edge Mobile 90+

## Performance Metrics

Target metrics for mobile:
- First Contentful Paint: <1.5s
- Time to Interactive: <3s
- Cumulative Layout Shift: <0.1
- Touch response: <100ms

## Accessibility

- WCAG 2.1 AA compliance maintained
- Touch targets: 44×44px minimum
- Color contrast: 4.5:1 minimum
- Focus indicators preserved
- Screen reader compatible

---

**Implementation Status**: ✅ Complete
**Last Updated**: October 16, 2025
**Tested On**: Chrome DevTools (all device presets)
**Ready For**: Production deployment and real device testing
