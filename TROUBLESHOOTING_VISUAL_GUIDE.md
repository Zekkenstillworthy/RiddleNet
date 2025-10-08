# Troubleshooting Page - Visual Guide

## Updated Device & Connection Display

### Device Palette (Bottom Bar)
Now displays Font Awesome icons with labels:

```
┌─────────┬─────────┬─────────┬─────────┐
│   🔀    │   🔌    │   🖥️    │   🖥️    │
│  Router │ Switch  │   PC    │ Server  │
└─────────┴─────────┴─────────┴─────────┘
```

**Icon Colors:**
- Router: Red (#EF4444)
- Switch: Blue (#3B82F6)
- PC: Green (#10B981)
- Server: Purple (#8B5CF6)

---

### Connection Palette (Bottom Bar)
Now displays Font Awesome icons with labels:

```
┌──────────┬──────────┬──────────┐
│    🔌    │    ⚡    │    🔌    │
│ Ethernet │  Fiber   │  Serial  │
└──────────┴──────────┴──────────┘
```

**Icon Colors:**
- Ethernet: Cyan (#00D9FF)
- Fiber: Green (#39FF14)
- Serial: Orange (#F59E0B)

---

### Canvas Device Rendering
Devices on the canvas now show:

```
┌──────────────┐
│              │
│     RTR      │  ← 3-letter abbreviation
│      ⟷       │  ← ASCII symbol
│              │
│    Router    │  ← Full label below
└──────────────┘
```

**Device Abbreviations:**
- RTR = Router
- SW = Switch
- HUB = Hub
- PC = PC/Computer
- LPT = Laptop
- SRV = Server
- PRN = Printer
- AP = Access Point
- FW = Firewall
- CLD = Cloud
- NET = Internet

**Device Symbols:**
- Router: ⟷ (bidirectional arrows)
- Switch: ╬ (cross connector)
- Hub: ✦ (star)
- PC: ▣ (filled square)
- Laptop: ▢ (empty square)
- Server: ▦ (stacked boxes)
- Printer: ⎙ (printer symbol)
- Access Point: ⚡ (lightning bolt)
- Firewall: ◈ (diamond)
- Cloud: ☁ (cloud)
- Internet: ◯ (circle)

---

### Visual States

#### Normal State
```
┌──────────────┐
│   #3B82F6    │  ← Device color
│     SW       │
│      ╬       │
│              │
│    Switch    │
└──────────────┘
```

#### Hovered State
```
┌──────────────┐
│   #00D9FF    │  ← Cyan glow
│     SW       │  ← Highlighted
│      ╬       │
│              │
│    Switch    │
└──────────────┘
```

#### Selected State
```
┌──────────────┐
│   #39FF14    │  ← Green glow
│     SW       │  ← Bright highlight
│      ╬       │
│              │
│    Switch    │
└──────────────┘
```

---

### Connection Rendering

#### Wired Connection (Solid Line)
```
Device A ━━━━━━━━━● ━━━━━━━━━ Device B
                   ↑
              Midpoint (clickable)
```

#### Wireless Connection (Dashed Line)
```
Device A ┄┄┄┄┄┄┄┄●┄┄┄┄┄┄┄┄ Device B
                 ↑
            Midpoint (clickable)
```

**Connection Colors:**
- Ethernet: Cyan (#00D9FF)
- Fiber: Green (#39FF14)
- Serial: Orange (#F59E0B)
- Wireless: Purple (#8B5CF6)

---

## User Interactions

### Palette Items
1. **Click** - Select device/connection type
2. **Hover** - Shows icon and label highlighted

### Canvas Devices
1. **Hover** - Shows cyan glow + device type tooltip
2. **Click** - Selects device (green glow)
3. **Displays**:
   - Connection count badge (top-right corner)
   - Device abbreviation (center)
   - ASCII symbol (below abbreviation)
   - Full name (below device box)

### Canvas Connections
1. **Hover** - Shows type (Wired/Wireless) in tooltip
2. **Click** - Selects connection
3. **Status** - Active (full opacity) or Down (50% opacity with X)

---

## Accessibility Features

✅ **High Contrast** - White text on colored backgrounds
✅ **Clear Labels** - Both abbreviated and full text labels
✅ **Visual Feedback** - Distinct hover and selection states
✅ **Symbol Support** - ASCII symbols work with screen readers
✅ **Touch-Friendly** - Large clickable areas (50px boxes)

---

## Browser Compatibility

✅ **Chrome/Edge** - Full support
✅ **Firefox** - Full support
✅ **Safari** - Full support
✅ **Mobile Browsers** - Full support (touch optimized)

No image loading required - all visual elements are:
- Font Awesome icons (vector)
- Canvas-rendered shapes
- ASCII/Unicode text symbols
