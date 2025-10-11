# Device Images Visual Reference

## Device Images Used in Troubleshooting

### 1. Desktop PC 🖥️
**File:** `static/img/PC.png`
- **Description:** Desktop computer with monitor, tower, keyboard, and mouse
- **Color Scheme:** Dark blue tones matching the application theme
- **Usage:** Represents end-user devices in network diagrams

### 2. Wireless Router 📡
**File:** `static/img/Router.png`
- **Description:** Wireless router with dual antennas and WiFi indicator
- **Color Scheme:** Dark blue with WiFi symbol and LED indicators
- **Usage:** Represents routers that route traffic between networks

### 3. Network Switch 🔌
**File:** `static/img/Switch.png`
- **Description:** 16-port network switch with multiple Ethernet ports
- **Color Scheme:** Dark blue with visible port layout
- **Usage:** Represents switches that connect devices within a network

## Implementation Details

### Palette Display
- **Size in Palette:** 48x48 pixels
- **Hover Effect:** 
  - Brightness: 0.9 → 1.1
  - Cyan drop-shadow glow
  - Scale: 1.0 → 1.1
  
### Canvas Display
- **Size on Canvas:** 60x60 pixels
- **Background:** Cyan circle (35px radius)
- **Border:** 2px cyan (#00D9FF)
- **Label Position:** 50px below center

### CSS Classes
```css
.device-icon.device-image {
    width: 48px;
    height: 48px;
    object-fit: contain;
    filter: brightness(0.9);
}

.device:hover .device-icon.device-image {
    filter: brightness(1.1) drop-shadow(0 0 8px rgba(0, 217, 255, 0.5));
    transform: scale(1.1);
}
```

### HTML Structure
```html
<div class="device" draggable="true" data-type="router">
    <img src="/static/img/Router.png" alt="Router" class="device-icon device-image">
    <span class="device-label">Router</span>
    <div class="device-tooltip">Network Router - Routes traffic between networks</div>
</div>
```

### JavaScript Rendering
```javascript
// In Device class constructor
switch (type) {
    case 'pc':
        this.imagePath = "/static/img/PC.png";
        break;
    case 'router':
        this.imagePath = "/static/img/Router.png";
        break;
    case 'switch':
        this.imagePath = "/static/img/Switch.png";
        break;
}

// Preload the image
if (this.imagePath) {
    this.image = new Image();
    this.image.src = this.imagePath;
}

// In draw() method
if (this.image && this.image.complete) {
    const imageSize = 60;
    ctx.drawImage(
        this.image,
        this.x - imageSize / 2,
        this.y - imageSize / 2,
        imageSize,
        imageSize
    );
}
```

## Color Theme Integration

All device images use a consistent dark blue color palette that matches the application's cyber theme:
- **Background:** #0F172A (primary dark)
- **Accent:** #00D9FF (cyber glow)
- **Highlights:** Cyan and teal tones

## Accessibility Features

1. **Alt Text:** Each image has descriptive alt text
2. **Tooltips:** Hover tooltips provide device descriptions
3. **Fallback:** Text rendering if images fail to load
4. **High Contrast:** Images maintain visibility on dark backgrounds

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+
- ✅ Mobile browsers (responsive design)

## Performance Optimization

1. **Image Preloading:** Images loaded when Device objects are created
2. **Canvas Caching:** Efficient rendering with `drawImage()`
3. **File Sizes:** PNG format with reasonable compression
4. **Lazy Loading:** Images only loaded when needed

## Future Device Types

Additional device images that could be added:

| Device Type | Suggested Image | Priority |
|------------|-----------------|----------|
| Firewall | firewall.png | High |
| Access Point | access-point.png | Medium |
| Server | server.png | Medium |
| Hub | hub.png | Low |
| Modem | modem.png | Low |
| Load Balancer | load-balancer.png | Low |

## Testing Checklist

- [x] Images display in device palette
- [x] Images display when dragged to canvas
- [x] Hover effects work correctly
- [x] Images scale properly on canvas
- [x] Labels appear below devices
- [x] Fallback rendering works if images fail
- [x] Responsive design maintained
- [x] Dark background compatibility
- [x] Cross-browser compatibility
