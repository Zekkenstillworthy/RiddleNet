# Viewport Tracking - Quick Visual Reference

## 🎯 What It Does
Shows a **colored rectangle** around each collaborator's visible screen area in real-time!

## 🎨 Visual Layout

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR SCREEN                          │
│                                                         │
│    [Alice's view] ← Username Label                      │
│    ╔══════════════════════════════╗                     │
│    ║  🔴 Alice                    ║ ← Red Rectangle     │
│    ║                              ║   (Alice's viewport)│
│    ║      Device Icons            ║                     │
│    ║         ↓                    ║                     │
│    ║      [Router] ━━ [Switch]   ║                     │
│    ║                              ║                     │
│    ╚══════════════════════════════╝                     │
│                                                         │
│                                    [Bob's view]         │
│    Your Cursor 🖱️                  ╔══════════════╗    │
│                                    ║  🔵 Bob      ║    │
│                                    ║              ║    │
│                                    ╚══════════════╝    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🌈 User Colors

| User | Color | Border | Background |
|------|-------|--------|------------|
| User 1 | 🔴 Red | `rgba(255, 107, 107, 0.6)` | `rgba(255, 107, 107, 0.05)` |
| User 2 | 🔵 Teal | `rgba(78, 205, 196, 0.6)` | `rgba(78, 205, 196, 0.05)` |
| User 3 | 🟡 Yellow | `rgba(255, 230, 109, 0.6)` | `rgba(255, 230, 109, 0.05)` |
| User 4 | 🌸 Pink | `rgba(255, 140, 148, 0.6)` | `rgba(255, 140, 148, 0.05)` |
| User 5 | 💜 Magenta | `rgba(196, 69, 105, 0.6)` | `rgba(196, 69, 105, 0.05)` |
| User 6 | 🔷 Blue | `rgba(64, 115, 158, 0.6)` | `rgba(64, 115, 158, 0.05)` |

## 📊 Component Breakdown

### Viewport Rectangle
```
╔═════════════════════╗  ← Dashed border (2px)
║                     ║
║   Visible Area      ║  ← Semi-transparent fill (5% opacity)
║                     ║
╚═════════════════════╝
```

### Viewport Label
```
┌─────────────┐
│ Alice's view │  ← Position: Above viewport (top: -26px)
└─────────────┘     Background: User color (90% opacity)
                    Font: 11px, weight 500
                    Padding: 4px 10px
```

### Complete Element
```
[Username's view]  ← Label (colored background)
╔═════════════╗
║             ║
║  🟦 Cursor  ║    ← User's cursor inside viewport
║             ║
╚═════════════╝
```

## 🔄 Real-time Updates

### When Viewport Updates
1. **User scrolls** → Rectangle moves to new scroll position
2. **User resizes window** → Rectangle changes size
3. **User moves to different area** → Rectangle repositions
4. **User leaves** → Rectangle disappears

### Update Frequency
- **Cursor**: Updates every ~100ms (smooth)
- **Viewport**: Updates every ~500ms (efficient)

## 📱 Responsive Behavior

### Desktop (1920x1080)
```
Wide viewport rectangles
┌────────────────────────────────┐
│ [User's view]                  │
│ ╔═════════════════════════════╗│
│ ║          Large area         ║│
│ ╚═════════════════════════════╝│
└────────────────────────────────┘
```

### Tablet (768x1024)
```
Medium viewport rectangles
┌──────────────────┐
│ [User's view]    │
│ ╔═══════════════╗│
│ ║ Medium area   ║│
│ ╚═══════════════╝│
└──────────────────┘
```

### Mobile (375x667)
```
Small viewport rectangles
┌──────────┐
│[View]    │
│╔════════╗│
│║ Small  ║│
│╚════════╝│
└──────────┘
```

## 🎭 Use Cases

### 1. **Collaborative Design**
```
Designer A is placing devices
╔═══════════════╗
║  📱 → 🖥️      ║  ← Designer A's viewport
╚═══════════════╝

Designer B is configuring cables
                ╔═══════════╗
                ║  🔌━━━━━━║  ← Designer B's viewport
                ╚═══════════╝
```

### 2. **Review & Feedback**
```
Student working on topology
╔═════════════════════╗
║  [Network Diagram]  ║  ← Student's focus area
╚═════════════════════╝

Instructor observing
╔═══════════════════════════╗
║  [Viewing student work]   ║  ← Instructor's viewport
╚═══════════════════════════╝
```

### 3. **Pair Programming**
```
Driver (writing code)
╔══════════════╗
║ Config panel ║  ← Driver's viewport
╚══════════════╝

Navigator (reviewing)
        ╔═══════════╗
        ║ Overview  ║  ← Navigator's viewport
        ╚═══════════╝
```

## 🎨 Visual States

### Normal State
```css
border: 2px dashed rgba(0, 217, 255, 0.5);
background: rgba(0, 217, 255, 0.05);
backdrop-filter: blur(2px);
```
Result: Subtle, non-intrusive rectangle

### Active User (Moving)
```
╔═════════════╗  ← Smooth transitions (0.3s ease)
║    Moving   ║
╚═════════════╝
```

### Inactive User (Idle)
```
╔═════════════╗  ← Still visible but no movement
║    Idle     ║
╚═════════════╝
```

## 🔍 Z-Index Layering

```
Layer 5: Modals (z-index: 10000)
Layer 4: Cursors (z-index: 9999)
Layer 3: Viewports (z-index: 9998)  ← Viewports below cursors
Layer 2: Canvas (z-index: 1)
Layer 1: Background (z-index: 0)
```

## 🎯 Interaction Behavior

### Pointer Events
```javascript
pointer-events: none;  // Viewports don't block clicks
```
- You can click **through** viewport rectangles
- Viewport indicators are **visual only**
- No interference with canvas interactions

### Hover Effects
- **None** - Viewports are purely informational
- Cursor avatars show on hover (separate feature)

## 📐 Size Examples

### Viewport Dimensions
```javascript
{
    width: 1920,   // User's screen width
    height: 1080,  // User's screen height
    x: 0,          // Horizontal scroll position
    y: 150         // Vertical scroll position (scrolled down 150px)
}
```

### On Screen
```
Document (3000px tall)
┌─────────────────┐
│                 │ ← y: 0
│   Scrolled to   │
│     ╔════╗      │ ← y: 150 (viewport starts here)
│     ║ VP ║      │
│     ╚════╝      │ ← y: 1230 (viewport ends, 150 + 1080)
│                 │
└─────────────────┘ ← y: 3000
```

## 🎬 Animation Examples

### Smooth Scroll
```
Frame 1: ╔══╗       (y: 0)
Frame 2:   ╔══╗     (y: 100)
Frame 3:     ╔══╗   (y: 200)
Frame 4:       ╔══╗ (y: 300)
```
Transition: `all 0.3s ease`

### Window Resize
```
Before: ╔══════════════╗ (1920px wide)
After:  ╔═══════╗       (1024px wide)
```
Smooth transition with CSS

## 🐛 Debug Visualization

### Console Logs
```
👁️ [VIEWPORT DEBUG] Updating viewport for user: 1 Alice
👁️ [VIEWPORT DEBUG] Viewport data: {
    x: 0,
    y: 150,
    width: 1920,
    height: 1080
}
✅ [VIEWPORT DEBUG] Viewport indicator updated
```

### DOM Inspector
```html
<div class="viewport-indicator user-1" 
     data-user-id="1" 
     style="left: 0px; top: 150px; width: 1920px; height: 1080px;">
    <div class="viewport-label">Alice's view</div>
</div>
```

## 🎨 Customization Tips

### Make More Visible
```css
.viewport-indicator {
    background: rgba(0, 217, 255, 0.15);  /* Increase opacity */
    border-width: 3px;                     /* Thicker border */
}
```

### Make More Subtle
```css
.viewport-indicator {
    background: rgba(0, 217, 255, 0.02);  /* Decrease opacity */
    border-style: dotted;                  /* Softer border */
}
```

### Add Glow Effect
```css
.viewport-indicator {
    box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
}
```

## 📊 Performance Metrics

### Network Usage
- **Viewport data size**: ~80 bytes per update
- **Update frequency**: 2 updates/second (max)
- **Bandwidth**: ~160 bytes/sec per user

### CPU Usage
- **DOM updates**: Minimal (CSS transforms)
- **Transition overhead**: Negligible (GPU accelerated)
- **Memory**: ~1KB per viewport indicator

## ✅ Feature Checklist

- [x] Real-time viewport tracking
- [x] Color-coded user identification
- [x] Username labels
- [x] Scroll synchronization
- [x] Window resize handling
- [x] Multiple user support (up to 6 colors)
- [x] Smooth animations
- [x] Non-intrusive design
- [x] Automatic cleanup on leave
- [x] Backend relay system

## 🚀 Quick Test

1. Open two browsers
2. Join same lobby
3. Scroll in Browser 1
4. See colored rectangle in Browser 2 showing Browser 1's view
5. Success! 🎉

Visual representation:
```
Browser 1 (You)        Browser 2 (Teammate)
┌──────────────┐      ┌──────────────┐
│ Scrolling... │      │ [Your view]  │
│      ↓       │  →   │ ╔══════════╗ │
│              │      │ ║ Moving!  ║ │
└──────────────┘      │ ╚══════════╝ │
                      └──────────────┘
```

---

**Pro Tip**: The viewport indicator helps teams coordinate work by showing who's looking at what part of the canvas in real-time! 🎯
