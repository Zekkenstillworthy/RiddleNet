# 🎯 Device Repositioning - Quick Reference

## How It Works

### User Actions
1. **Hover** over device → Cursor shows "grab" ✋
2. **Click & Hold** → Device highlights green 🟢
3. **Drag** → Move device around canvas 🖱️
4. **Release** → Device placed at new position ✅

---

## Visual Feedback

| State | Visual | Cursor |
|-------|--------|--------|
| **Normal** | Cyan circle | default |
| **Hover** | Cyan circle | grab |
| **Dragging** | Green dashed circle + glow | grabbing |
| **Selected** | Golden circle | default |

---

## Key Features

✅ **Smooth Dragging** - Real-time position updates
✅ **Auto Boundaries** - Can't drag outside canvas (40px margin)
✅ **Connection Updates** - Connections follow device automatically
✅ **Mode Aware** - Disabled during connection mode
✅ **Visual Feedback** - Green glow while dragging

---

## Code Implementation

### Variables
```javascript
let isDragging = false;
let draggedDevice = null;
```

### Event Flow
```
mousedown → Start drag + highlight
    ↓
mousemove → Update position + redraw
    ↓
mouseup → End drag + track event
```

### Highlight Effect
```javascript
// Green dashed circle + glow
ctx.strokeStyle = "#00FF88";
ctx.lineWidth = 3;
ctx.setLineDash([5, 5]);
ctx.shadowBlur = 15;
```

---

## Constraints

**Boundary Limits:**
- Top: 40px
- Bottom: 40px from edge
- Left: 40px  
- Right: 40px from edge

**Mode Restrictions:**
- ✅ Enabled in normal mode
- ❌ Disabled in connection mode

---

## Edge Cases

✅ **Mouse Leaves Canvas** → Drag cancelled
✅ **Click After Drag** → Click ignored
✅ **Connection Mode** → Drag disabled
✅ **Edge Position** → Constrained to margin

---

## Files Modified

📄 `templates/user/troubleshoot.html`
- Added mousedown handler
- Enhanced mousemove handler  
- Added mouseup handler
- Added mouseleave handler
- Updated drawDevice() function

---

## Quick Test

1. Open: http://127.0.0.1:5001/troubleshooting/
2. Drop a device on canvas
3. Hover over it (cursor → grab)
4. Click and drag (green highlight)
5. Release (device repositioned)
6. Connections follow automatically ✓

---

## Cursor States

```
default  → No device nearby
grab     → Hovering over device
grabbing → Actively dragging
```

---

**Status: ✅ Complete & Working**
