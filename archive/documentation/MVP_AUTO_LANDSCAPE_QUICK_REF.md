# 🚀 Quick Reference - Auto Landscape Orientation

## For Developers - Quick Start

### Adding to New Challenge Pages

#### 1. Add CSS (in `<head>` block)
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/auto-landscape-orientation.css') }}">
```

#### 2. Add JavaScript (before `{% endblock %}`)
```html
<script src="{{ url_for('static', filename='js/auto-landscape-orientation.js') }}"></script>
```

#### 3. Test
- Open page on mobile device (or DevTools mobile view)
- Rotate device between portrait and landscape
- Verify overlay shows in portrait, hides in landscape

**That's it!** No additional configuration needed.

---

## Console Debugging Commands

```javascript
// Check device type
window.AutoLandscape.getDeviceInfo()

// Check orientation
window.AutoLandscape.getOrientation()

// Manually test overlay
window.AutoLandscape.showOverlay()
window.AutoLandscape.hideOverlay()

// Force refresh
window.AutoLandscape.refresh()
```

---

## CSS Customization

Edit `static/css/auto-landscape-orientation.css`:

### Change Overlay Colors
```css
:root {
    --cyber-glow: #00D9FF;      /* Icon color */
    --background: #020617;       /* Overlay background */
    --text-primary: #F8FAFC;    /* Text color */
}
```

### Change Animation Speed
```css
.rotate-icon {
    animation: rotateDevice 2s ease-in-out infinite; /* Change 2s */
}
```

### Adjust Breakpoints
```css
@media screen and (max-width: 768px) and (orientation: portrait) {
    /* Mobile portrait styles */
}
```

---

## Common Customizations

### Change Overlay Message
Edit `static/js/auto-landscape-orientation.js`:

```javascript
overlay.innerHTML = `
    <div class="device-icon">
        <i class="fas fa-mobile-screen rotate-icon"></i>
    </div>
    <div class="portrait-message">
        <h2>Your Custom Title</h2>
        <p>Your custom message here</p>
    </div>
`;
```

### Disable for Specific Page
Remove the CSS/JS includes from that page's template.

### Desktop Testing
Resize browser window to mobile dimensions (< 768px width) and make taller than wide.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Overlay doesn't show | Check console for errors; verify JS file loaded |
| Overlay shows on desktop | Expected if window is mobile-sized; resize window |
| Layout breaks | Check for CSS conflicts; inspect element styles |
| Rapid rotation glitches | Events are debounced; check console logs |

---

## File Locations

```
static/
├── css/
│   └── auto-landscape-orientation.css    ← Main styles
└── js/
    └── auto-landscape-orientation.js     ← Main logic

templates/user/
├── osi-simulation.html           ← Updated ✅
├── crimping-simulation.html      ← Updated ✅
├── troubleshoot.html             ← Updated ✅
└── quiz_challenge.html           ← Updated ✅
```

---

## Testing Checklist

- [ ] Portrait mode shows overlay
- [ ] Landscape mode hides overlay
- [ ] Smooth transition when rotating
- [ ] Works on iOS Safari
- [ ] Works on Android Chrome
- [ ] Desktop unaffected
- [ ] No console errors

---

## Quick Test URLs

1. http://localhost:5000/osi-simulation
2. http://localhost:5000/crimping-simulation
3. http://localhost:5000/troubleshooting/
4. http://localhost:5000/quiz/

Open in mobile DevTools or on actual device.

---

**Need more details?** See `MVP_AUTO_LANDSCAPE_IMPLEMENTATION_SUMMARY.md`  
**Testing guide?** See `MVP_AUTO_LANDSCAPE_TESTING_GUIDE.md`
