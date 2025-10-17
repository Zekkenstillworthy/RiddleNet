# MVP Sidebar Toggle - Quick Reference

## 🎯 One-Line Summary
Single shared CSS file (`sidebar-toggle-mvp.css`) with per-page color variable overrides—no duplicate code.

## 🚀 Quick Start

### To Use on New Pages:
1. Extend `base.html` (already includes shared CSS)
2. Add color overrides in your `<style>` block:

```html
{% block head %}
<style>
:root {
    --toggle-color-start: #yourcolor;
    --toggle-color-end: #yourcolor;
    --toggle-ring: rgba(r,g,b,0.55);
    --toggle-glow: 0 6px 28px rgba(r,g,b,0.55);
}
</style>
{% endblock %}
```

That's it! Toggle automatically works.

## 📐 Specifications

| Property | Value | Notes |
|----------|-------|-------|
| **Size** | 50px × 50px | Fixed, no min/max needed |
| **Position (Desktop)** | `calc(var(--current-sidebar-width) - 25px)` | Auto-adjusts on collapse |
| **Position (Mobile)** | `16px, 16px` (top-left) | Touch-friendly corner |
| **Z-Index** | 1001 | Above content, below modals |
| **Transition** | 0.32s cubic-bezier | Smooth, no jitter |
| **Hover Scale** | 1.08 (desktop), 1.05 (mobile) | Subtle feedback |

## 🎨 Current Themes

### OSI Model (Cyan/Blue)
```css
--toggle-color-start: #00d4ff;
--toggle-color-end: #006ea1;
--toggle-ring: rgba(0,212,255,0.55);
--toggle-glow: 0 6px 30px rgba(0,212,255,0.6);
```

### Crimping (Green)
```css
--toggle-color-start: #7dd71d;
--toggle-color-end: #3fa312;
--toggle-ring: rgba(125,215,29,0.55);
--toggle-glow: 0 6px 28px rgba(125,215,29,0.55);
```

## 📱 Breakpoints

| Screen Size | Behavior |
|-------------|----------|
| **>1024px** | Sidebar full width, toggle at edge |
| **768px-1024px** | Sidebar collapsed, toggle at collapsed edge |
| **<768px** | Toggle at top-left (16px,16px) |

## ⚡ Optional Features

### Add Pulse Animation
```javascript
document.querySelector('.sidebar-toggle')?.classList.add('pulse');
```

### Remove Pulse Animation
```javascript
document.querySelector('.sidebar-toggle')?.classList.remove('pulse');
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Toggle not visible | Check `base.html` includes `sidebar-toggle-mvp.css` |
| Wrong colors | Add `:root` overrides in page `<style>` block |
| Doesn't collapse | Verify `#sidebar.collapsed` class toggles |
| Mobile positioning off | Check viewport meta tag exists |
| Icon doesn't rotate | Ensure icon uses `<i>` tag inside `.sidebar-toggle` |

## 📦 File Locations

```
static/css/sidebar-toggle-mvp.css    ← Shared styles
templates/user/base.html             ← Includes shared CSS
templates/user/osi-simulation.html   ← Cyan theme override
templates/user/crimping-simulation.html ← Green theme override
```

## 🎓 Key Concepts

1. **CSS Variables** = Runtime theming without JavaScript
2. **DRY Principle** = Write once, use everywhere
3. **Progressive Enhancement** = Works without JS, enhanced with it
4. **Mobile-First** = Touch targets prioritized
5. **Accessibility** = Respects user motion preferences

## ✅ Validation

Test on:
- [ ] Chrome DevTools device toolbar (various sizes)
- [ ] Real iOS device (Safari)
- [ ] Real Android device (Chrome)
- [ ] Desktop Firefox/Edge
- [ ] Check `prefers-reduced-motion` in OS settings

## 🆘 Need Help?

See full documentation: `MVP_SIDEBAR_TOGGLE_IMPLEMENTATION.md`

---
**Last Updated:** October 5, 2025  
**Version:** 1.0.0 (MVP)
