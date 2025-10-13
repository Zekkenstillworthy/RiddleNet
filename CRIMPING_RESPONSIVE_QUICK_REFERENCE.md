# Crimping Simulation - Responsive Design Quick Reference

## 📱 Mobile Dimensions Covered

| Device | Dimensions | Orientation | Key Adjustments |
|--------|-----------|-------------|-----------------|
| iPhone SE | 375x667 | Portrait | Single column, 40px wires, compact spacing |
| iPhone SE | 667x375 | Landscape | 98% width, 38px wires, ultra-compact |
| iPhone 12/13/14 | 390x844 | Portrait | 92% width, 44px wires, balanced |
| iPhone 12 Pro Max | 896x414 | Landscape | 96% width, 2-col grid, 40px wires |
| iPhone 14 | 844x390 | Landscape | 96% width, optimized height |
| iPhone 14 Pro Max | 430x932 | Portrait | 90% width, 46px wires, spacious |
| iPhone 14 Pro Max | 932x430 | Landscape | 94% width, 2-col grid, 42px wires |
| Galaxy S20 | 915x412 | Landscape | 95% width, balanced approach |

## 🎯 Key Content Classes

### `.crimping-intro-content`
**Purpose**: Introduction modal with benefits and lightning icon

**Responsive Behavior**:
- Portrait: Single column benefits grid, large icons
- Landscape: Multi-column benefits, compact spacing
- Max height: 85vh with vertical scrolling
- Padding scales: 40px → 30px → 20px → 12px

**Critical Elements**:
```css
.intro-body { width: 100%; overflow: hidden; }
.crimping-benefits { grid-template-columns: responsive }
.proceed-btn { full-width on mobile }
```

### `.scoring-description-content`
**Purpose**: Dual scoring system explanation modal

**Responsive Behavior**:
- Portrait: Single column scoring breakdown
- Landscape: Two column scoring breakdown  
- Max height: 85vh (was 70vh) with scrolling
- Modal body wrapper: auto-height calculation

**Critical Elements**:
```css
.scoring-breakdown { 1fr or 1fr 1fr columns }
.scoring-category { word-wrap, min-width: 0 }
.modal-body-wrapper { overflow-y: auto }
```

### `.wiring-selection-content`
**Purpose**: T568A/T568B selection modal

**Responsive Behavior**:
- Always full-width options on mobile
- Icon sizes scale down in landscape
- Locked state maintains visual hierarchy
- Max height: 85vh with scrolling

**Critical Elements**:
```css
.wiring-option { width: 100%; box-sizing: border-box }
.option-icon { 32px → 24px in landscape }
.difficulty-info { full-width, proper wrapping }
```

### `.game-content`
**Purpose**: Main simulation area with wire arrangement

**Responsive Behavior**:
- Flexible padding: clamp(0px, 0.5vw, 4px)
- Top padding: clamp(60px, 8vh, 80px) for feedback tooltips
- Scales down to 3-4px padding in landscape
- Top padding adjusts: 60px → 50px → 45px → 40px

**Critical Elements**:
```css
.wire, .wire-slot { touch-friendly sizing: 44px min }
.cable-sections { 2-col grid or single column }
.wires, .wire-slots { flexible gap spacing }
```

## 📐 Breakpoint Strategy

### Portrait Modes (Height > Width)
```css
max-width: 375px  → Ultra compact (iPhone SE)
max-width: 390px  → Compact (iPhone 12/13/14)  
max-width: 430px  → Standard (iPhone 14 Pro Max)
max-width: 480px  → Small mobile general
max-width: 768px  → Tablet
```

### Landscape Modes (Width > Height)
```css
max-width: 667px & max-height: 375px  → Compact landscape
max-width: 844px & max-height: 390px  → Standard landscape
max-width: 896px & max-height: 414px  → Large landscape
max-width: 932px & max-height: 430px  → XL landscape
max-width: 915px & max-height: 412px  → Samsung landscape
```

## 🎨 Responsive Pattern Reference

### Modal Sizing Pattern
```css
/* Desktop/Tablet */
max-width: 700px;
width: 90%;
padding: 40px;

/* Mobile Portrait */
max-width: 95%;
width: 95%;
padding: 20px 15px;

/* Mobile Landscape */
max-width: 98%;
width: 98%;
padding: 12px 10px;
```

### Grid Adaptation Pattern
```css
/* Desktop */
grid-template-columns: 1fr 1fr;
gap: 12px;

/* Mobile Portrait */
grid-template-columns: 1fr;
gap: 10px;

/* Mobile Landscape */
grid-template-columns: repeat(2, 1fr);
gap: 8px;
```

### Font Scaling Pattern
```css
/* Headings */
Desktop: 36px → Tablet: 28px → Mobile: 22px → Landscape: 18px

/* Body Text */
Desktop: 18px → Tablet: 16px → Mobile: 14px → Landscape: 13px

/* Small Text */
Desktop: 16px → Tablet: 14px → Mobile: 12px → Landscape: 11px
```

### Spacing Pattern
```css
/* Padding/Margin */
Desktop: 40px → Tablet: 30px → Mobile: 20px → Landscape: 12px

/* Gaps */
Desktop: 20px → Tablet: 15px → Mobile: 12px → Landscape: 10px
```

## 🔍 Testing Quick Check

### Visual Tests
1. Open DevTools responsive mode
2. Set to each target dimension
3. Verify no horizontal scrollbar
4. Check modal fits in viewport
5. Confirm text is readable
6. Ensure buttons are tappable

### Interaction Tests
1. Tap/click all buttons (44x44px min)
2. Scroll modals if content exceeds viewport
3. Switch between portrait/landscape
4. Test with increased browser font size
5. Verify tooltips don't get clipped

### Content Tests
1. Long text doesn't overflow
2. Grids reflow properly
3. Icons maintain aspect ratio
4. Images don't cause horizontal scroll
5. All content remains accessible

## 🚨 Common Issues & Solutions

### Issue: Horizontal scroll appears
**Solution**: Check for fixed widths, add `overflow-x: hidden`

### Issue: Modal too tall for viewport
**Solution**: Verify `max-height: 85vh` and `overflow-y: auto`

### Issue: Text truncated
**Solution**: Add `word-wrap: break-word` and remove `white-space: nowrap`

### Issue: Touch targets too small
**Solution**: Ensure minimum 44x44px for all interactive elements

### Issue: Grid doesn't reflow
**Solution**: Change to single column on mobile with media query

## ⚡ Performance Tips

1. Use `transform` for animations (GPU-accelerated)
2. Minimize `box-shadow` complexity on mobile
3. Use `will-change` sparingly for known animations
4. Optimize backdrop-filter usage (can be expensive)
5. Test with Chrome DevTools Performance panel

## 📝 Code Snippets

### Add Responsive Modal
```css
.your-modal-content {
  max-width: 900px;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
  box-sizing: border-box;
  padding: 40px;
}

@media (max-width: 768px) {
  .your-modal-content {
    padding: 25px 18px;
    max-width: 92%;
  }
}

@media (max-width: 480px) {
  .your-modal-content {
    padding: 20px 15px;
    max-width: 96%;
  }
}
```

### Add Responsive Grid
```css
.your-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (max-width: 768px) {
  .your-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}
```

### Add Responsive Text
```css
.your-text {
  font-size: clamp(13px, 2.5vw, 18px);
  line-height: 1.6;
  word-wrap: break-word;
}
```

## 🎯 Maintenance Checklist

When adding new content:
- [ ] Test on all target dimensions
- [ ] Add appropriate media queries
- [ ] Use `clamp()` for fluid typography
- [ ] Set `box-sizing: border-box`
- [ ] Add `overflow` handling
- [ ] Verify touch target sizes
- [ ] Test landscape and portrait
- [ ] Check with increased font size

## 🌟 Best Practices Applied

✅ Mobile-first approach with progressive enhancement  
✅ Touch-friendly interface (44px minimum)  
✅ Flexible units (vh, vw, %, clamp)  
✅ Proper overflow management  
✅ Accessible font sizes (minimum 11px)  
✅ Semantic breakpoints based on actual devices  
✅ No horizontal scrolling  
✅ Smooth scrolling experience  
✅ Maintains visual hierarchy on all sizes  
✅ Consistent spacing system  

---

**Last Updated**: 2025-10-14  
**File Modified**: `templates/user/crimping-simulation.html`  
**Lines Added**: ~200 lines of responsive CSS
