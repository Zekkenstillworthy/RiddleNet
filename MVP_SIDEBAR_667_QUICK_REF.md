# MVP Quick Reference: Sidebar Preserved on 667×375+

## 🎯 One-Line Summary
**Sidebar now visible on 667×375+ landscape viewports** - Canvas and palette respect sidebar space

---

## 📐 Layout Structure

```
┌────────┬──────────────────────────────┐
│SIDEBAR │        CANVAS AREA           │
│        │                              │
│        ├──────────────────────────────┤
│        │ LINK UP! │ R S P │ CONNECT  │
└────────┴──────────────────────────────┘
```

---

## 🔧 Key Changes

### Before (Distorted ❌)
```css
--current-sidebar-width: 0px;        /* Forced to 0 */
#sidebar { display: none !important; } /* Hidden */
#canvas-container { left: 0; }        /* Full viewport */
#device-palette { left: 0; }          /* Full viewport */
```

### After (Clean ✅)
```css
/* --current-sidebar-width preserved (dynamic) */
#canvas-container {
    left: var(--current-sidebar-width);  /* Respects sidebar */
    width: calc(100vw - var(--current-sidebar-width));
}
#device-palette {
    left: var(--current-sidebar-width);  /* Respects sidebar */
    width: calc(100vw - var(--current-sidebar-width));
}
```

---

## ✅ 30-Second Test

1. **Run:** `python run.py`
2. **Open:** http://127.0.0.1:5001/troubleshooting/
3. **DevTools:** F12 → Responsive → 667×375 → Landscape
4. **Check:**
   - [ ] Sidebar visible on left ✓
   - [ ] Canvas starts after sidebar ✓
   - [ ] Palette below canvas, after sidebar ✓
   - [ ] 3 sections: Left | Center | Right ✓

---

## 🐛 Quick Debug

```javascript
// Browser Console - Verify positioning
const sidebar = document.getElementById('sidebar');
const canvas = document.getElementById('canvas-container');
const palette = document.getElementById('device-palette');

console.log('Sidebar visible:', getComputedStyle(sidebar).display !== 'none');
console.log('Canvas left:', getComputedStyle(canvas).left);
console.log('Palette left:', getComputedStyle(palette).left);
// Should show sidebar width (e.g., "250px" or "300px"), NOT "0px"
```

---

## 📊 Success Criteria

| Check | Status |
|-------|--------|
| Sidebar visible on 667×375+ | ✅ |
| Canvas respects sidebar space | ✅ |
| Palette respects sidebar space | ✅ |
| Clean 3-section layout | ✅ |
| No distortion (Image 2 fixed) | ✅ |

---

## 📝 File Changed
- `templates/user/troubleshoot.html` (line ~3002)
- Media query: `@media screen and (orientation: landscape) and (min-width: 667px)`

---

**Date:** October 7, 2025  
**Status:** ✅ Complete  
**Full Docs:** `MVP_SIDEBAR_PRESERVED_667_FIX.md`
