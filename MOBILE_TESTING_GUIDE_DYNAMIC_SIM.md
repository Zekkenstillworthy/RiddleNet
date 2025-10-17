# Testing Guide: Dynamic Simulation Mobile Responsiveness

## Quick Testing Checklist

### URL to Test
```
http://127.0.0.1:5001/dynamic/simulation/70
```

---

## Chrome DevTools Testing Steps

### 1. Open DevTools
- Press `F12` or `Ctrl+Shift+I` (Windows)
- Click the device toolbar icon or press `Ctrl+Shift+M`

### 2. Test Device Presets

#### Mobile Devices - Portrait
1. **iPhone SE (375×667)**
   - [ ] Header stacks vertically
   - [ ] Canvas is 45vh minimum 300px
   - [ ] Device grid shows 2 columns
   - [ ] Steps panel is full-width at bottom
   - [ ] Floating buttons visible (📊 👥)

2. **iPhone 12 Pro (390×844)**
   - [ ] Similar to iPhone SE
   - [ ] Score display stacks vertically
   - [ ] Device categories wrap properly
   - [ ] Touch targets are 44×44px minimum

3. **Pixel 5 (393×851)**
   - [ ] All elements fit without horizontal scroll
   - [ ] Text is readable (no zoom required)
   - [ ] Buttons are touch-friendly

4. **Samsung Galaxy S21 (360×800)**
   - [ ] Most compact layout works
   - [ ] No elements cut off
   - [ ] Canvas maintains aspect ratio

#### Mobile Devices - Landscape
5. **iPhone 12 Pro Landscape (844×390)**
   - [ ] Canvas optimized for horizontal space
   - [ ] Device palette is shallow (140px max)
   - [ ] Steps panel on right (if space)
   - [ ] Header compressed

#### Tablet Devices - Portrait
6. **iPad Mini (768×1024)**
   - [ ] Major breakpoint transition
   - [ ] Steps panel full-width at bottom
   - [ ] Canvas is 50vh
   - [ ] Device grid shows 3 columns
   - [ ] Sidebars become full-screen overlays

7. **iPad (810×1080)**
   - [ ] Similar to iPad Mini
   - [ ] Proper spacing maintained

#### Tablet Devices - Landscape
8. **iPad Mini Landscape (1024×768)**
   - [ ] Side-by-side layout maintained
   - [ ] Narrower sidebars (360px)
   - [ ] Device palette optimized

9. **iPad Landscape (1080×810)**
   - [ ] Comfortable desktop-like layout
   - [ ] All features accessible

### 3. Custom Breakpoint Testing

Test these specific widths:

| Width  | Expected Behavior |
|--------|-------------------|
| 1200px | Desktop layout, full features |
| 1024px | Tablet landscape, compressed |
| 768px  | **Major change**: stacked layout |
| 600px  | Mobile, 2-column devices |
| 480px  | Extra small, minimal spacing |
| 375px  | iPhone SE, compact view |
| 360px  | Galaxy S21, smallest common |

---

## Manual Testing Checklist

### Header Section
- [ ] Back button visible and functional
- [ ] Title readable and not truncated
- [ ] Simulation type badge displays
- [ ] Score display shows all items
- [ ] Submit button accessible
- [ ] No horizontal overflow

### Canvas Area
- [ ] Canvas renders at proper size
- [ ] Network devices can be added
- [ ] Devices are draggable (touch/mouse)
- [ ] Canvas doesn't shrink below minimum
- [ ] Zoom/pan works (if implemented)
- [ ] No layout shift during interaction

### Steps Panel
- [ ] All steps visible and readable
- [ ] Active step highlighted
- [ ] Scroll works when content overflows
- [ ] Collapse toggle works
- [ ] Step content is interactive
- [ ] No content cut off

### Device Palette
- [ ] All device categories visible
- [ ] Devices in grid layout (4/3/2 columns)
- [ ] Labels readable
- [ ] Icons clear and sized properly
- [ ] Horizontal scroll smooth (mobile)
- [ ] Categories wrap on small screens
- [ ] Minimize/maximize works

### Performance Sidebar
- [ ] Toggle button appears in correct position
- [ ] Sidebar slides in smoothly
- [ ] Full-screen on mobile (≤768px)
- [ ] Partial sidebar on desktop
- [ ] Close button works
- [ ] Content scrollable
- [ ] Metrics display correctly
- [ ] Charts/graphs responsive

### Collaboration Sidebar
- [ ] Toggle button visible
- [ ] Different position from performance
- [ ] Full-screen on mobile
- [ ] Team members list displays
- [ ] Chat input accessible
- [ ] Session controls functional
- [ ] Cursor tracking works (if enabled)

### Touch Interactions (on real device)
- [ ] Tap targets are easy to hit
- [ ] No accidental double-taps
- [ ] Drag works smoothly
- [ ] Scroll doesn't conflict with drag
- [ ] Keyboard doesn't cover inputs
- [ ] No page zoom when typing
- [ ] Active states provide feedback
- [ ] Gestures feel natural

### Typography & Readability
- [ ] All text readable without zoom
- [ ] Font sizes appropriate for device
- [ ] Line heights comfortable
- [ ] No text overflow/ellipsis issues
- [ ] Contrast meets WCAG standards
- [ ] Icons recognizable

### Layout & Spacing
- [ ] No horizontal scrolling
- [ ] Elements don't overlap
- [ ] Proper gaps between items
- [ ] Margins/padding consistent
- [ ] No layout jumps/shifts
- [ ] Footer doesn't cover content

---

## Browser Testing

### Chrome Mobile
1. Open `http://127.0.0.1:5001/dynamic/simulation/70` on phone
2. Test all interactions
3. Check console for errors

### Safari iOS
1. Same URL on iPhone/iPad
2. Test touch interactions
3. Check for iOS-specific issues
4. Verify no text zoom on input focus

### Firefox Mobile
1. Test on Android device
2. Verify layout consistency
3. Check scroll performance

### Samsung Internet
1. Test on Samsung device
2. Verify all features work
3. Check for browser-specific quirks

---

## Performance Testing

### Lighthouse (Chrome DevTools)
1. Open page
2. Go to Lighthouse tab
3. Select "Mobile"
4. Run audit
5. Check scores:
   - [ ] Performance > 80
   - [ ] Accessibility > 90
   - [ ] Best Practices > 80

### Network Throttling
1. DevTools → Network tab
2. Set to "Slow 3G"
3. Reload page
4. [ ] Page loads in reasonable time
5. [ ] Interactive within 5 seconds
6. [ ] No layout shift during load

### CPU Throttling
1. DevTools → Performance tab
2. Set "6x slowdown"
3. Interact with page
4. [ ] Still responsive
5. [ ] No janky animations
6. [ ] Smooth scrolling

---

## Accessibility Testing

### Keyboard Navigation
1. Tab through all interactive elements
2. [ ] Focus visible on all items
3. [ ] Tab order logical
4. [ ] Can activate with Enter/Space
5. [ ] Can escape from modals

### Screen Reader
1. Enable screen reader (VoiceOver/TalkBack)
2. [ ] All elements announced properly
3. [ ] Roles and labels correct
4. [ ] Instructions clear
5. [ ] State changes announced

### Color Contrast
1. Use DevTools or WebAIM checker
2. [ ] Text meets 4.5:1 minimum
3. [ ] Large text meets 3:1
4. [ ] Focus indicators visible
5. [ ] Active states distinguishable

---

## Common Issues to Check

### Layout Issues
- ❌ Horizontal scroll on mobile
- ❌ Content cut off at edges
- ❌ Overlapping elements
- ❌ Fixed elements covering content
- ❌ Canvas too small to interact

### Typography Issues
- ❌ Text too small to read
- ❌ Text overflowing containers
- ❌ Line heights too tight
- ❌ Font not loading

### Interaction Issues
- ❌ Touch targets too small (<44px)
- ❌ Buttons not responding to tap
- ❌ Keyboard covering inputs
- ❌ Page zooms when focusing input
- ❌ Drag conflicts with scroll

### Performance Issues
- ❌ Slow load time
- ❌ Janky scrolling
- ❌ Layout shift during load
- ❌ Animations causing lag
- ❌ Memory leaks

---

## Screenshot Testing

Take screenshots at these widths for comparison:
- 375px (iPhone SE)
- 768px (iPad Portrait)
- 1024px (iPad Landscape)
- 1440px (Desktop)

Compare:
- [ ] Layout consistency
- [ ] Element positioning
- [ ] Typography sizing
- [ ] Spacing proportions

---

## Real Device Testing Priority

### High Priority
1. iPhone (iOS 14+) - Safari
2. Samsung Galaxy S21 (Android 11+) - Chrome
3. iPad (iPadOS 14+) - Safari

### Medium Priority
4. Google Pixel - Chrome
5. OnePlus - Chrome
6. Huawei - Chrome

### Low Priority
7. Older Android (8-10)
8. Older iOS (12-13)

---

## Bug Reporting Template

```markdown
**Device**: [e.g., iPhone 12 Pro]
**OS**: [e.g., iOS 15.4]
**Browser**: [e.g., Safari 15]
**Screen Size**: [e.g., 390×844]
**Orientation**: [Portrait/Landscape]

**Issue Description**:
[Describe what's wrong]

**Steps to Reproduce**:
1. Go to http://127.0.0.1:5001/dynamic/simulation/70
2. [Step 2]
3. [Step 3]

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Screenshot**:
[Attach if applicable]

**Console Errors**:
[Any errors in console]
```

---

## Success Criteria

✅ **Layout**
- No horizontal scroll on any device
- All content visible and accessible
- Proper stacking on mobile
- Appropriate spacing at all sizes

✅ **Interactions**
- All buttons/links work
- Touch targets meet WCAG (44×44px)
- Drag and drop functional
- Form inputs accessible

✅ **Performance**
- Lighthouse mobile score > 80
- No layout shift (CLS < 0.1)
- Smooth scrolling
- Fast interactions (<100ms)

✅ **Accessibility**
- WCAG 2.1 AA compliance
- Keyboard navigable
- Screen reader friendly
- Sufficient color contrast

✅ **Cross-browser**
- Works in Chrome, Safari, Firefox
- No browser-specific bugs
- Consistent appearance
- All features functional

---

## Quick Fix Reference

### Horizontal Scroll
```css
body, .container {
    overflow-x: hidden;
    max-width: 100vw;
}
```

### Small Touch Targets
```css
.btn {
    min-width: 44px;
    min-height: 44px;
}
```

### iOS Input Zoom
```css
input {
    font-size: 16px !important;
}
```

### Canvas Too Small
```css
.canvas-container {
    min-height: 300px;
}
```

### Content Behind Fixed Element
```css
.content {
    padding-bottom: 200px; /* Height of fixed element */
}
```

---

**Testing Status**: Ready
**Last Updated**: October 16, 2025
**Tester**: [Your Name]
**Notes**: Test all breakpoints systematically
