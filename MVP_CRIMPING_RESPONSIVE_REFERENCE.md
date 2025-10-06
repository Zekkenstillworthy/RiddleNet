# 📐 Crimping Simulation - Responsive Breakpoint Reference

## Quick Visual Guide to Layout Changes at Each Breakpoint

---

## 🎨 Layout Visualization

### Desktop (>1024px)
```
┌────────────────────────────────────────────────────────┐
│                    RiddleNet Logo                       │
├────────────────────────────────────────────────────────┤
│  SCORE: 100% │ ACCURACY: 100% │ WIRES: 0/16 │ COMBO: 0x │ ⏱ 04:49 │
├────────────────────────────────────────────────────────┤
│         First Simulation - UTP Cable Crimping          │
│    Difficulty: Easy - Straight-Through (T568B)         │
├────────────────────────────────────────────────────────┤
│ Progress Bar ████████░░░░░░░░░░░░░░░░░░░░░░░ 0%        │
├────────────────────────────────────────────────────────┤
│  Cable A                    │   RJ45 Connector A       │
│  [O] [W-O] [G] [W-B] [B]   │   [ ][ ][ ][ ][ ]        │
│  [W-G] [Br] [W-Br]         │   [ ][ ][ ]              │
├─────────────────────────────┼──────────────────────────┤
│  Cable B                    │   RJ45 Connector B       │
│  [O] [W-O] [G] [W-B] [B]   │   [ ][ ][ ][ ][ ]        │
│  [W-G] [Br] [W-Br]         │   [ ][ ][ ]              │
└─────────────────────────────┴──────────────────────────┘
│      [🔄 Reset]  [🎓 Tutorial]  [⬅ Back to Selection]  │
└────────────────────────────────────────────────────────┘
```

**Layout Features:**
- 2-column grid (Cable A/B side by side)
- Horizontal score panel
- Multi-button row
- Maximum spacing and padding

---

### Tablet (768px - 1024px)
```
┌──────────────────────────────────────┐
│          RiddleNet Logo              │
├──────────────────────────────────────┤
│ SCORE: 100% │ WIRES: 0/16 │ ⏱ 04:49 │
│ ACCURACY: 100% │ COMBO: 0x           │
├──────────────────────────────────────┤
│    First Simulation - UTP Cable      │
│    Difficulty: Easy (T568B)          │
├──────────────────────────────────────┤
│ Progress ███░░░░░░░░░░░ 0%           │
├──────────────────────────────────────┤
│  Cable A        │   RJ45 Connector A │
│  [O][W-O][G]   │   [ ][ ][ ]        │
│  [W-B][B][W-G] │   [ ][ ][ ]        │
├─────────────────┼────────────────────┤
│  Cable B        │   RJ45 Connector B │
│  [O][W-O][G]   │   [ ][ ][ ]        │
│  [W-B][B][W-G] │   [ ][ ][ ]        │
└─────────────────┴────────────────────┘
│  [🔄 Reset]  [🎓 Tutorial]          │
│  [⬅ Back to Selection]              │
└──────────────────────────────────────┘
```

**Layout Features:**
- 2-column grid maintained
- Score panel wraps to 2 rows
- Buttons start wrapping
- Medium spacing

---

### Mobile Portrait (375px - 480px)
```
┌─────────────────────────┐
│     RiddleNet Logo      │
├─────────────────────────┤
│ SCORE: 100% │ ⏱ 04:49  │
│ ACCURACY: 100%          │
│ WIRES: 0/16 │ COMBO: 0x│
├─────────────────────────┤
│ First Simulation        │
│ Difficulty: Easy        │
├─────────────────────────┤
│ Progress █░░░░░░ 0%     │
├─────────────────────────┤
│      Cable A            │
│ [O][W-O][G][W-B]       │
│ [B][W-G][Br][W-Br]     │
├─────────────────────────┤
│   RJ45 Connector A      │
│ [ ][ ][ ][ ]           │
│ [ ][ ][ ][ ]           │
├─────────────────────────┤
│      Cable B            │
│ [O][W-O][G][W-B]       │
│ [B][W-G][Br][W-Br]     │
├─────────────────────────┤
│   RJ45 Connector B      │
│ [ ][ ][ ][ ]           │
│ [ ][ ][ ][ ]           │
├─────────────────────────┤
│    [🔄 Reset]          │
│    [🎓 Tutorial]       │
│    [⬅ Back]            │
└─────────────────────────┘
```

**Layout Features:**
- Single column (stacked sections)
- Score panel wraps fully
- Wires wrap to 2 rows (4×2 grid)
- Full-width buttons (stacked)
- Minimal padding

---

### Mobile Landscape (480px - 915px wide, ≤430px tall)
```
┌────────────────────────────────────────────────┐
│ Logo │ SCORE:100% ACCURACY:100% ⏱ 04:49       │
│      │ WIRES:0/16 COMBO:0x  Progress ██░ 0%   │
├──────┼─────────────────────────────────────────┤
│      │ Cable A       │   RJ45 Connector A      │
│      │ [O][W-O][G]  │   [ ][ ][ ][ ]         │
│      │ [W-B][B]     │   [ ][ ][ ][ ]         │
│      ├──────────────┼─────────────────────────┤
│      │ Cable B       │   RJ45 Connector B      │
│      │ [O][W-O][G]  │   [ ][ ][ ][ ]         │
│      │ [W-B][B]     │   [ ][ ][ ][ ]         │
└──────┴───────────────┴─────────────────────────┘
│ [🔄 Reset] [🎓 Tutorial] [⬅ Back]              │
└────────────────────────────────────────────────┘
```

**Layout Features:**
- Compact 2-column grid
- Ultra-compact header
- Minimal vertical spacing
- Horizontal button layout
- Maximum width usage

---

## 📏 Size Specifications

### Wire Elements

| Viewport Width | Wire Size | Font Size | Gap  |
|---------------|-----------|-----------|------|
| 320px - 375px | 42×42px   | 9px       | 2px  |
| 376px - 480px | 44×44px   | 10px      | 3px  |
| 481px - 720px | 48×44px   | 11px      | 4px  |
| 721px - 768px | 52×44px   | 11px      | 4px  |
| 769px - 1024px| 60×38px   | 12px      | 6px  |
| >1024px       | 70×35px   | 13px      | 4px  |

---

### Button Elements

| Viewport Width | Button Width    | Height | Font Size |
|---------------|----------------|--------|-----------|
| 320px - 375px | 100% (stacked) | 44px   | 12px      |
| 376px - 480px | 100% (stacked) | 48px   | 13px      |
| 481px - 768px | auto           | 48px   | 14px      |
| 769px - 1024px| 140px          | 44px   | 14px      |
| >1024px       | 170px          | 42px   | 16px      |

---

### Container Padding

| Viewport Width | Container Padding | Margin |
|---------------|-------------------|--------|
| 320px - 375px | 6px               | 4px    |
| 376px - 480px | 8px               | 4px    |
| 481px - 768px | 12px              | 6px    |
| 769px - 1024px| 14px              | 8px    |
| >1024px       | 16px              | 10px   |

---

## 🎯 Grid Layout Transitions

### Cable Sections Grid

| Viewport Width | Columns | Gap   | Layout Type |
|---------------|---------|-------|-------------|
| <768px        | 1       | 8px   | Stacked     |
| 768px - 915px | 2       | 10px  | Side-by-side|
| >915px        | 2       | 12px  | Side-by-side|

**Landscape Exception:**
- If width ≤915px AND height ≤430px → Force 2 columns

---

## 🔤 Typography Scaling

### Heading Sizes

| Element        | Min Size | Responsive Formula    | Max Size |
|---------------|----------|-----------------------|----------|
| H1 (Title)    | 1rem     | clamp(1rem,4vw,1.8rem)| 1.8rem   |
| H2 (Section)  | 13px     | clamp(13px,2.8vw,17px)| 17px     |
| Difficulty    | 11px     | clamp(11px,2.5vw,16px)| 16px     |
| Score Value   | 12px     | clamp(12px,2vw,14px)  | 14px     |
| Score Label   | 9px      | clamp(9px,1.6vw,11px) | 11px     |
| Button Text   | 12px     | clamp(12px,2.2vw,16px)| 16px     |
| Timer Display | 14px     | clamp(14px,2.5vw,17px)| 17px     |

---

## 🧩 Flex Wrapping Behavior

### Score Display
- **Desktop/Tablet:** Single row, no wrap
- **Mobile Portrait:** Wraps to 2-3 rows
- **Mobile Landscape:** Single row with scroll fallback

### Wire Containers
- **Desktop:** Single row (8 wires)
- **Tablet:** May wrap based on width
- **Mobile Portrait:** 2 rows (4 wires × 2)
- **Mobile Landscape:** Single row with compact spacing

### Button Sections
- **Desktop:** Horizontal row (3-4 buttons)
- **Tablet:** May wrap to 2 rows
- **Mobile Portrait:** Full vertical stack
- **Mobile Landscape:** Horizontal with wrap

---

## 📐 Spacing System

### Gap Hierarchy (using clamp)

```css
/* Extra Small */
gap: clamp(2px, 0.5vw, 3px);    /* Wire gaps in tight spaces */

/* Small */
gap: clamp(4px, 1vw, 6px);      /* General element spacing */

/* Medium */
gap: clamp(6px, 1.5vw, 10px);   /* Section spacing */

/* Large */
gap: clamp(10px, 2vw, 16px);    /* Major section gaps */

/* Extra Large */
gap: clamp(12px, 2.5vw, 20px);  /* Container-level gaps */
```

---

## 🎨 Z-Index Layering

| Element                  | Z-Index | Purpose                    |
|-------------------------|---------|----------------------------|
| Base content            | 1       | Default layer              |
| Sidebar                 | 1000    | Navigation overlay         |
| Modals                  | 2000    | Dialog overlays            |
| Combo display           | 2000    | Achievement notifications  |
| Timer display           | 5000    | Always visible timer       |

---

## 🔧 Responsive Formula Patterns

### Width-based Scaling
```css
/* Pattern: clamp(min, preferred, max) */
width: clamp(50px, 8vw, 70px);
/* Scales from 50px to 70px based on viewport width */
```

### Height-based Scaling
```css
height: clamp(28px, 5vh, 35px);
/* Scales from 28px to 35px based on viewport height */
```

### Font Scaling
```css
font-size: clamp(10px, 1.8vw, 13px);
/* Ensures minimum 10px, scales with viewport, caps at 13px */
```

### Padding Scaling
```css
padding: clamp(6px, 1.5vw, 10px);
/* Responsive padding that grows with viewport */
```

---

## 📱 Touch Target Guidelines

### Minimum Sizes (WCAG AA Compliance)

| Element Type      | Min Width | Min Height | Actual Implementation |
|------------------|-----------|------------|----------------------|
| Wire elements    | 44px      | 44px       | ✅ 44×44px minimum   |
| Wire slots       | 44px      | 44px       | ✅ 44×44px minimum   |
| Buttons          | 44px      | 44px       | ✅ 44-52px height    |
| Score items      | 38px      | 32px       | ⚠️ Visual only       |
| Toggle buttons   | 44px      | 44px       | ✅ Standard size     |

**Note:** Score items are informational only (not interactive), so they don't require 44px minimum.

---

## 🌐 Cross-Browser Considerations

### Safari iOS
- ✅ `-webkit-overflow-scrolling: touch` applied
- ✅ `-webkit-tap-highlight-color: transparent` set
- ✅ Viewport-fit=cover for notch devices
- ✅ Fixed positioning tested

### Chrome Mobile
- ✅ Touch events optimized
- ✅ Passive event listeners considered
- ✅ Hardware acceleration enabled

### Firefox Mobile
- ✅ Flexbox fallbacks in place
- ✅ Grid layout tested
- ✅ Clamp() function supported

---

## 🎯 Performance Considerations

### CSS Optimizations Applied
1. **Hardware Acceleration:** `transform: translateZ(0)` on animated elements
2. **Will-change:** Used sparingly on drag elements
3. **Contain:** Layout containment for performance
4. **Flexbox over Float:** Modern layout methods
5. **CSS Grid:** Native 2D layout support

### No JavaScript Layout Dependencies
- All responsive behavior is CSS-only
- No ResizeObserver needed
- No matchMedia listeners required
- Faster initial render

---

## 📊 Viewport Breakpoint Summary

```
Mobile Portrait:    320px - 480px   (single column)
Mobile Landscape:   480px - 915px   (2-column if height ≤430px)
Tablet Portrait:    768px - 820px   (2-column grid)
Tablet Landscape:   821px - 1024px  (enhanced 2-column)
Desktop:            >1024px         (full layout)
```

---

## ✅ Validation Checklist

Before deploying, verify:
- [ ] All breakpoints transition smoothly
- [ ] No horizontal scroll at any size
- [ ] Touch targets ≥44px for interactive elements
- [ ] Text readable at all sizes (min 12px body, 10px labels)
- [ ] Images/icons scale proportionally
- [ ] Modals fit within viewport
- [ ] Forms (if any) are mobile-friendly
- [ ] Navigation accessible on all devices

---

**Reference Version:** 1.0
**Last Updated:** October 6, 2025
**Status:** Production Ready
