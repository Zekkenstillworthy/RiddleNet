# Responsive Design Quick Reference

## 📐 Breakpoints

| Breakpoint | Width | Device Type | Layout Strategy |
|------------|-------|-------------|-----------------|
| **XL** | > 1200px | Desktop | Full horizontal layout |
| **LG** | 1024-1200px | Large Tablet | Condensed horizontal |
| **MD** | 768-1024px | Tablet | Floating controls |
| **SM** | 600-768px | Mobile Large | Vertical stack |
| **XS** | < 600px | Mobile Small | Ultra-compact |

## 🎯 Layout Changes by Breakpoint

### Desktop (> 1200px)
- **Device Palette**: Fixed bottom bar, full width
- **Steps Panel**: Right sidebar (420px)
- **Canvas**: Flexible center area
- **Sidebars**: Hidden (toggle tabs on left)

### Tablet (768-1024px)
- **Device Palette**: Fixed bottom, condensed
- **Steps Panel**: Narrower sidebar (320-360px)
- **Canvas**: Adjusted margins
- **Sidebars**: Floating toggle buttons appear

### Mobile (< 768px) ⭐
- **Device Palette**: LEFT slide-in panel (280px)
- **Steps Panel**: BELOW canvas, full width
- **Canvas**: 50vh height, full width
- **Sidebars**: Full-screen overlays

### Small Mobile (< 600px)
- **Device Palette**: Narrower (260px), 2 columns
- **Everything**: More compact
- **Buttons**: Smaller (45px)

## 🎨 Component Behavior

### Device Palette
| Screen Size | Position | Width | Columns | Activation |
|-------------|----------|-------|---------|------------|
| Desktop | Bottom | 100% | 4 | Always visible |
| Tablet | Bottom | 100% | 3-4 | Always visible |
| Mobile | Left slide-in | 280px | 3 | Purple FAB |
| Small Mobile | Left slide-in | 260px | 2 | Purple FAB |

### Floating Action Buttons (FABs)
Appear at: **< 1024px**

| Button | Color | Icon | Position | Function |
|--------|-------|------|----------|----------|
| Performance | Cyan | 📊 | Top | Performance sidebar |
| Collaboration | Green | 👥 | Middle | Collaboration sidebar |
| Device Palette | Purple | 📦 | Bottom | Device selection |

**Mobile Positions** (< 768px):
- Performance: `bottom: 160px` (140px on small mobile)
- Collaboration: `bottom: 100px` (90px on small mobile)
- Palette: `bottom: 40px`

### Sidebars
| Screen Size | Behavior | Size | z-index |
|-------------|----------|------|---------|
| Desktop | Left toggle tabs | 350px | 1400-1500 |
| Tablet | Same as desktop | 300px | 1400-1500 |
| Mobile | Full-screen overlay | 100vw × 100vh | 1400-1500 |

## 📏 Key Measurements

### Touch Targets (Mobile)
- Minimum: **44px × 44px** (WCAG 2.1)
- FABs: **50-56px** diameter
- Device Items: **Min 75-80px** height
- Buttons: **Min 44px** height

### Canvas Heights
| Screen Size | Height | Min Height |
|-------------|--------|------------|
| Desktop | Auto (fills space) | N/A |
| Tablet | Auto (fills space) | N/A |
| Mobile | 50vh | 400px |
| Small Mobile | 45vh | 350px |
| Mobile Landscape | 70vh | 300px |

### Panel Widths
| Component | Desktop | Tablet | Mobile |
|-----------|---------|--------|--------|
| Steps Panel | 420px | 320-360px | 100% |
| Performance Sidebar | 350px | 300px | 100vw |
| Collaboration Sidebar | 350px | 300px | 100vw |
| Device Palette | 100% | 100% | 280px |

## 🔧 CSS Custom Properties

```css
:root {
    --sidebar-width-desktop: 350px;
    --sidebar-width-tablet: 300px;
    --steps-width-desktop: 420px;
    --steps-width-tablet: 320px;
    --palette-width-mobile: 280px;
    --palette-width-small: 260px;
    --fab-size: 56px;
    --fab-size-small: 45px;
    --touch-target-min: 44px;
}
```

## 🎬 Animations & Transitions

All transitions: **0.3s ease**

### Slide Animations
- Device Palette (mobile): `transform: translateX(-100%)` → `translateX(0)`
- Sidebars (mobile): `transform: translateX(100%)` → `translateX(0)`
- FABs: `transform: scale(1.1)` on hover

### States
- **Closed**: `transform: translateX(-100%)` or `translateX(100%)`
- **Open**: `transform: translateX(0)`
- **Active**: `opacity: 1`, visible
- **Inactive**: `opacity: 0`, hidden

## 📱 Media Query Reference

```css
/* Desktop Large */
@media (max-width: 1200px) { }

/* Tablet Landscape */
@media (max-width: 1024px) { }

/* Tablet Portrait / Mobile Large */
@media (max-width: 768px) { }

/* Mobile Small */
@media (max-width: 600px) { }

/* Mobile Landscape */
@media (max-width: 896px) and (orientation: landscape) { }
```

## 🎯 Common Classes

### Layout Classes
- `.simulation-wrapper` - Main container
- `.simulation-header` - Top header bar
- `.simulation-content` - Main content area
- `.simulation-main` - Canvas container parent

### Component Classes
- `.canvas-container` - Network diagram area
- `.steps-panel` - Step-by-step guide
- `.device-palette` - Device selection panel
- `.performance-sidebar` - Performance tracking
- `.collaboration-sidebar` - Team collaboration

### State Classes
- `.active` - Component is visible/open
- `.collapsed` - Component is minimized
- `.minimized` - Palette is condensed
- `.flash` - Highlight animation

### Mobile Classes
- `.mobile-performance-toggle` - Performance FAB
- `.mobile-collaboration-toggle` - Collaboration FAB
- `.mobile-palette-toggle` - Device Palette FAB

## 🐛 Debugging Tips

### Check Current Breakpoint
```javascript
console.log('Width:', window.innerWidth);
// < 600: Small Mobile
// 600-768: Mobile Large
// 768-1024: Tablet
// > 1024: Desktop
```

### Force Mobile View
```javascript
// Add to browser console
document.body.style.width = '375px';
window.dispatchEvent(new Event('resize'));
```

### Toggle Device Palette
```javascript
document.getElementById('device-palette').classList.toggle('active');
```

### Check Media Query Match
```javascript
const isMobile = window.matchMedia('(max-width: 768px)').matches;
console.log('Is Mobile:', isMobile);
```

## ✅ Testing Checklist

Quick verification for each breakpoint:

### Desktop ✓
- [ ] Device palette at bottom
- [ ] Steps panel on right
- [ ] No FABs visible
- [ ] Full horizontal layout

### Tablet ✓
- [ ] FABs visible
- [ ] Condensed layout
- [ ] Palette still at bottom
- [ ] Sidebars toggle properly

### Mobile ✓
- [ ] Vertical stack layout
- [ ] Canvas 50% height
- [ ] Device palette LEFT slide
- [ ] Three FABs visible
- [ ] Steps below canvas

### Small Mobile ✓
- [ ] 2-column device grid
- [ ] Smaller FABs
- [ ] Compact text
- [ ] All accessible

## 🔗 Related Files

- `/templates/user/dynamic_simulation.html` - Main template
- `/static/css/network-device-configurator.css` - Device styling
- `/static/css/collaboration-manager.css` - Collaboration UI
- `/static/css/unified-chat.css` - Chat interface
- `/static/css/force-landscape.css` - Orientation lock

## 📚 Documentation

- `MOBILE_RESPONSIVE_UPDATE.md` - Full implementation details
- `MOBILE_TESTING_GUIDE.md` - Step-by-step testing guide
- `QUICK_REFERENCE.md` - This file

---
**Last Updated**: 2025-10-15
**Version**: 1.0
**Status**: ✅ Production Ready
