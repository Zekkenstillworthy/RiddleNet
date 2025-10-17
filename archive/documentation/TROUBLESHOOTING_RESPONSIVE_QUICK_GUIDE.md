# Troubleshooting Page - Responsive Design Quick Reference

## 📐 Visual Breakpoint Guide

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RESPONSIVE BREAKPOINTS                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  320px ─────────────────────────────────────────────────────►      │
│  └─ Ultra Small Mobile (320-480px)                                 │
│     • 90px palette height                                          │
│     • 45px devices                                                 │
│     • 60px action buttons                                          │
│     • Single column modals                                         │
│                                                                     │
│  480px ─────────────────────────────────────────────────────►      │
│  └─ Small Mobile (481-768px)                                       │
│     • 100px palette height                                         │
│     • 50px devices                                                 │
│     • 70px action buttons                                          │
│     • No sidebar (full width)                                      │
│                                                                     │
│  768px ─────────────────────────────────────────────────────►      │
│  └─ Tablet (769-1024px)                                            │
│     • 95px palette height                                          │
│     • 55px devices                                                 │
│     • 85px action buttons                                          │
│     • 60px collapsed sidebar                                       │
│     • 2-column grids                                               │
│                                                                     │
│  1024px ────────────────────────────────────────────────────►      │
│  └─ Desktop (1025-1440px)                                          │
│     • 100px palette height                                         │
│     • 65px devices                                                 │
│     • 100px action buttons                                         │
│     • Full sidebar                                                 │
│     • Auto-fit grids (250px min)                                   │
│                                                                     │
│  1440px ────────────────────────────────────────────────────►      │
│  └─ Large Desktop (1441-2559px)                                    │
│     • 110px palette height                                         │
│     • 70px devices                                                 │
│     • 110px action buttons                                         │
│     • 3-column grids                                               │
│     • 380px performance sidebar                                    │
│                                                                     │
│  2560px ────────────────────────────────────────────────────►      │
│  └─ Ultra-Wide (2560px+)                                           │
│     • 120px palette height                                         │
│     • 80px devices                                                 │
│     • 120px action buttons                                         │
│     • 16px base font size                                          │
│     • Extra spacing everywhere                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 📱 Mobile Layout (≤768px)

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│          CANVAS AREA                    │
│      (Network Diagram)                  │
│                                         │
│   Touches screen edges                  │
│   No sidebar on mobile                  │
│                                         │
│                                         │
├─────────────────────────────────────────┤
│  [Dev] [Dev] [Dev] | Actions | Tools   │ ← 100px Device Palette
└─────────────────────────────────────────┘
```

## 💻 Desktop Layout (≥1025px)

```
┌──┬────────────────────────────────────────┬──┐
│  │                                        │P │
│S │                                        │e │
│i │          CANVAS AREA                   │r │
│d │      (Network Diagram)                 │f │
│e │                                        │  │
│b │                                        │S │
│a │                                        │i │
│r │                                        │d │
│  │                                        │e │
├──┼────────────────────────────────────────┤  │
│  │ [Dev] [Dev] [Dev] | Actions | Tools   │  │
└──┴────────────────────────────────────────┴──┘
    ↑                                          ↑
  280px                                      350px
  Sidebar                              Performance
                                          (Optional)
```

## 📊 Component Sizing Chart

### Device Palette

| Breakpoint | Height | Left Offset | Width |
|-----------|--------|-------------|-------|
| ≤480px | 90px | 0 | 100vw |
| 481-768px | 100px | 0 | 100vw |
| 769-1024px | 95px | 60px | calc(100vw - 60px) |
| 1025-1440px | 100px | var(--sidebar) | calc(100vw - var(--sidebar)) |
| 1441-2559px | 110px | var(--sidebar) | calc(100vw - var(--sidebar)) |
| 2560px+ | 120px | var(--sidebar) | calc(100vw - var(--sidebar)) |

### Device Icons

| Breakpoint | Width | Icon Size | Label Size |
|-----------|-------|-----------|------------|
| ≤480px | 45px | 0.9rem | 0.5rem |
| 481-768px | 50px | 1rem | 0.55rem |
| 769-1024px | 55px | 1.2rem | 0.65rem |
| 1025-1440px | 65px | 1.4rem | 0.75rem |
| 1441-2559px | 70px | 1.5rem | 0.8rem |
| 2560px+ | 80px | 1.6rem | 0.85rem |

### Action Buttons

| Breakpoint | Min Width | Height | Font Size |
|-----------|-----------|--------|-----------|
| ≤480px | 60px | 40px | 10px |
| 481-768px | 70px | 44px | 11px |
| 769-1024px | 85px | 46px | 13px |
| 1025-1440px | 100px | 48px | 14px |
| 1441-2559px | 110px | 52px | 14px |
| 2560px+ | 120px | 56px | 15px |

### Modal Widths

| Breakpoint | Modal Width | Padding | Grid Columns |
|-----------|------------|---------|--------------|
| ≤480px | 95vw | 12px | 1 |
| 481-768px | 95vw | 16px | 1 |
| 769-1024px | 85vw (max 700px) | 24px | 2 |
| 1025-1440px | 80vw (max 800px) | 28px | auto-fit (250px) |
| 1441-2559px | 70vw (max 1200px) | 32px | 3 |
| 2560px+ | 60vw (max 1100px) | 40px | auto-fit (350px) |

## 🎯 Touch Target Guidelines

### Minimum Sizes (WCAG 2.1 Level AAA)

```
┌────────────────────────────────────┐
│  Minimum: 44x44px                  │
│  ┌─────────────┐                   │
│  │   Button    │ ← 44px height    │
│  └─────────────┘                   │
│       44px                          │
│                                     │
│  Optimal: 48x48px (Better UX)      │
│  ┌──────────────┐                  │
│  │   Button     │ ← 48px height   │
│  └──────────────┘                  │
│       48px                          │
│                                     │
│  Spacing: 8px minimum               │
│  ┌────────┐ 8px ┌────────┐         │
│  │ Button │ ←─→ │ Button │         │
│  └────────┘     └────────┘         │
└────────────────────────────────────┘
```

## 🌈 Color & Contrast

### Text Contrast Ratios
- Primary Text: 7:1 (AAA)
- Secondary Text: 4.5:1 (AA)
- Disabled Text: 3:1 (Minimum)

### Interactive States
```css
/* Normal */
background: rgba(255, 255, 255, 0.08);
border: 2px solid rgba(255, 255, 255, 0.2);

/* Hover (Desktop) */
background: rgba(0, 217, 255, 0.15);
border-color: var(--cyber-glow);

/* Active (Touch) */
transform: scale(0.95);
opacity: 0.8;

/* Focus (Keyboard) */
box-shadow: 0 0 0 3px rgba(0, 217, 255, 0.3);
```

## 📐 Spacing System (8px Base)

```
┌────────────────────────────────────┐
│  --space-xs:   4px  (0.5 × 8)      │
│  --space-sm:   8px  (1 × 8)        │
│  --space-md:   16px (2 × 8)        │
│  --space-lg:   24px (3 × 8)        │
│  --space-xl:   32px (4 × 8)        │
│  --space-2xl:  48px (6 × 8)        │
└────────────────────────────────────┘

Example Usage:
├─ 4px  ─ Gap between icons
├─ 8px  ─ Button spacing
├─ 16px ─ Section padding
├─ 24px ─ Modal margins
├─ 32px ─ Large element spacing
└─ 48px ─ Major section breaks
```

## 🔄 Orientation Changes

### Portrait Mobile
```
┌──────────┐
│          │
│  Canvas  │
│          │
│          │
│          │
├──────────┤
│ Palette  │
└──────────┘
```

### Landscape Mobile (Short Height)
```
┌───────────────────────────┬──────┐
│                           │Tools │
│        Canvas             │      │
│                           │      │
├───────────────────────────┴──────┤
│      Compact Palette (80px)      │
└──────────────────────────────────┘
```

## 🧪 Testing URLs

### Desktop
- http://127.0.0.1:5001/troubleshooting/

### Mobile Simulation (Chrome DevTools)
1. Open DevTools (F12)
2. Toggle Device Toolbar (Ctrl+Shift+M)
3. Select Device:
   - iPhone SE (375x667)
   - iPhone 12 Pro (390x844)
   - iPad (768x1024)
   - Responsive (Custom)

### Test Scenarios
1. **Modal Opening** → Check centering on all sizes
2. **Device Palette** → Scroll horizontally on mobile
3. **Performance Sidebar** → Toggle on mobile/tablet
4. **Difficulty Cards** → Check grid layout at each breakpoint
5. **Touch Targets** → Verify 44px minimum on real devices

## 💡 Pro Tips

### For Developers
- Use CSS variables for consistent sizing
- Test on real devices, not just simulators
- Check touch targets with Chrome's "Show tap targets" overlay
- Verify contrast ratios with browser dev tools

### For Designers
- Design mobile-first, enhance for desktop
- Use 8px spacing grid consistently
- Maintain 44px minimum touch targets
- Test with actual content, not lorem ipsum

### For QA
- Test all breakpoints (not just mobile/desktop)
- Verify landscape orientation on mobile
- Check performance sidebar on tablet
- Test keyboard navigation on desktop
- Verify zoom levels (up to 200%)

---

**Quick Access**: `TROUBLESHOOTING_RESPONSIVE_IMPROVEMENTS.md` for full details
