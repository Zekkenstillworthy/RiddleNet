# MVP Device Palette Quick Test Guide

## 🚀 Quick Start

To verify the device palette no longer overlaps content on screen sizes **667×375 and above**.

---

## Test Setup

### Option 1: Start RiddleNet Application
```bash
python run.py
```
Navigate to: **http://127.0.0.1:5001/troubleshooting/**

### Option 2: Use VS Code Task
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Run Task"
3. Select: **"Start RiddleNet Application"**

---

## 5-Minute Test Checklist

### ✅ Test 1: Small Landscape (667x375)
**Device**: iPhone SE Landscape

1. Open Chrome DevTools (`F12`)
2. Toggle Device Toolbar (`Ctrl+Shift+M`)
3. Select "iPhone SE"
4. Rotate to landscape (click rotate icon)
5. Refresh page

**Expected**:
- ✅ Canvas visible in top area (305px height)
- ✅ Device palette at bottom (70px, compact)
- ✅ No overlap
- ✅ ROUTER, SWITCH, PC buttons all clickable

---

### ✅ Test 2: Medium Landscape (750x375)
**Device**: Custom Responsive

1. DevTools → Responsive mode
2. Set width: `750px`, height: `375px`
3. Refresh page

**Expected**:
- ✅ Canvas fills top (287px height)
- ✅ Device palette at bottom (88px, standard)
- ✅ Buttons have neon borders (2px cyan glow)
- ✅ Touch targets at least 70px

---

### ✅ Test 3: Tablet Portrait (768x1024)
**Device**: iPad Mini

1. Select "iPad Mini" in DevTools
2. Portrait orientation
3. Refresh page

**Expected**:
- ✅ Canvas fills space above palette
- ✅ Sidebar hidden
- ✅ Device palette fixed at bottom (88px)
- ✅ All controls accessible

---

### ✅ Test 4: Tablet Landscape (1024x768)
**Device**: iPad

1. Select "iPad" in DevTools
2. Landscape orientation
3. Refresh page

**Expected**:
- ✅ Canvas properly sized
- ✅ Device palette spans full width
- ✅ Touch targets optimal (72px)
- ✅ No content covered

---

### ✅ Test 5: Desktop (1920x1080)
**Device**: Responsive (Desktop)

1. Set viewport: `1920 x 1080`
2. Refresh page

**Expected**:
- ✅ Canvas respects sidebar width
- ✅ Device palette at bottom
- ✅ Large spacious layout
- ✅ All interactions smooth

---

## Visual Checks

### Neon Borders ✨
- All buttons should have **2px solid cyan border** (`var(--cyber-glow)`)
- Hover effect: **glowing shadow** (0 4px 16px rgba(0, 217, 255, 0.4))
- Active state: **bright glow** (0 0 25px rgba(0, 217, 255, 0.7))

### Spacing & Alignment 📐
- Palette sections evenly distributed (left, center, right)
- Consistent gaps between buttons (4-8px on mobile, 8-16px on desktop)
- No overlapping elements

### Touch Targets 👆
- Minimum size on small devices: **60px × 60px**
- Standard size: **70px × 70px**
- Desktop size: **80px × 80px**
- All buttons easily clickable/tappable

---

## Common Issues & Solutions

### Issue: Palette Still Overlaps Canvas
**Solution**: Clear browser cache and hard refresh (`Ctrl+Shift+R`)

### Issue: Buttons Too Small on Mobile
**Solution**: Check viewport is correctly set to landscape orientation

### Issue: No Neon Borders Visible
**Solution**: Ensure `--cyber-glow` CSS variable is defined (should be `#00d9ff`)

### Issue: Sidebar Visible on Mobile
**Solution**: Media query should hide sidebar on viewports ≤768px

---

## Success Criteria Summary

| Criterion | Status |
|-----------|--------|
| Canvas visible without overlap | ✅ |
| Palette fixed at bottom | ✅ |
| Neon borders consistent | ✅ |
| Touch targets accessible (44px+) | ✅ |
| Responsive across all viewports | ✅ |
| Aligned with other modules | ✅ |

---

## Debug Commands (If Needed)

### Check Current Palette Height
Open browser console and run:
```javascript
const palette = document.getElementById('device-palette');
console.log('Palette height:', palette.offsetHeight);
console.log('Palette bottom:', palette.getBoundingClientRect().bottom);
```

### Check Canvas Position
```javascript
const canvas = document.getElementById('canvas-container');
console.log('Canvas bottom:', canvas.getBoundingClientRect().bottom);
console.log('Canvas height:', canvas.offsetHeight);
```

### Check Z-Index Layering
```javascript
const palette = document.getElementById('device-palette');
const canvas = document.getElementById('canvas-container');
console.log('Palette z-index:', getComputedStyle(palette).zIndex); // Should be 100
console.log('Canvas z-index:', getComputedStyle(canvas).zIndex);   // Should be 10
```

---

## Report Issues

If you encounter any layout issues:

1. **Take a screenshot** showing the overlap
2. **Note the viewport size** (width × height)
3. **Check browser console** for errors
4. **Document the device/orientation** being tested
5. **Share the browser** (Chrome/Firefox/Safari + version)

---

**Test Duration**: ~5 minutes  
**Browser**: Chrome (recommended), Firefox, Safari  
**Status**: Ready for testing ✅
