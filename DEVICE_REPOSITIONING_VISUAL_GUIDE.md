# Device Repositioning - Visual Flow Diagram

## 🎨 User Interaction Flow

```
┌─────────────────────────────────────────────────────────┐
│                   DEVICE REPOSITIONING                   │
│                    Complete Flow                         │
└─────────────────────────────────────────────────────────┘

Step 1: INITIAL STATE
┌──────────────────┐
│   Canvas Area    │
│                  │
│      ⭕         │  ← Device on canvas
│     /🖥️\        │
│    ( PC )       │
│     ──┘         │
│   "PC-01"       │
└──────────────────┘
Cursor: default


Step 2: HOVER OVER DEVICE
┌──────────────────┐
│   Canvas Area    │
│                  │
│      ⭕         │  
│     /🖥️\   ✋   │  ← Cursor changes to "grab"
│    ( PC )       │
│     ──┘         │
│   "PC-01"       │
└──────────────────┘
Cursor: grab
Action: Move mouse over device


Step 3: CLICK & HOLD (Dragging Starts)
┌──────────────────┐
│   Canvas Area    │
│                  │
│    ┌─────┐       │
│   ╱  ⭕   ╲      │  ← Green dashed circle
│  │  /🖥️\  │ 🤚  │  ← Cursor: grabbing
│  │ ( PC ) │     │  ← Glow effect active
│   ╲  ──┘ ╱      │
│    └─────┘       │
│   "PC-01"       │
└──────────────────┘
Cursor: grabbing
Visual: Green (#00FF88) dashed outline + glow
State: isDragging = true


Step 4: DRAGGING IN PROGRESS
┌──────────────────┐
│   Canvas Area    │
│        ╱──→      │  ← Device follows mouse
│    ┌─────┐       │
│   ╱  ⭕   ╲ 🤚   │  ← Smooth movement
│  │  /🖥️\  │     │
│  │ ( PC ) │     │
│   ╲  ──┘ ╱      │
│    └─────┘       │
│   "PC-01"       │
└──────────────────┘
Connections: Update in real-time
Boundaries: Constrained to 40px margin


Step 5: RELEASE (Drop Device)
┌──────────────────┐
│   Canvas Area    │
│                  │
│                  │
│          ⭕      │  ← Device at new position
│         /🖥️\     │
│        ( PC )    │
│         ──┘      │
│       "PC-01"    │
└──────────────────┘
Cursor: default
Visual: Returns to normal state
State: isDragging = false
Event: 'device_repositioned' tracked
```

---

## 🎭 Visual State Comparison

### Normal State
```
     ⭕
    /🖥️\
   ( PC )
    ──┘
  "PC-01"

Border: Cyan (#00D9FF)
Glow: None
Cursor: default
```

### Hover State
```
     ⭕
    /🖥️\  ← Cursor: grab ✋
   ( PC )
    ──┘
  "PC-01"

Border: Cyan (#00D9FF)
Glow: None
Cursor: grab
```

### Dragging State
```
   ┌─────┐
  ╱  ⭕   ╲  ← Green dashed
 │  /🖥️\  │    + Glow effect
 │ ( PC ) │    Cursor: grabbing 🤚
  ╲  ──┘ ╱
   └─────┘
  "PC-01"

Border: Green (#00FF88)
Style: Dashed (5px, 5px)
Glow: 15px blur
Cursor: grabbing
```

### Selected State
```
   ┌─────┐
  ╱  ⭕   ╲  ← Golden
 │  /🖥️\  │
 │ ( PC ) │
  ╲  ──┘ ╱
   └─────┘
  "PC-01"

Border: Gold (#FFD700)
Width: 9px
Cursor: default
```

---

## 🔗 Connection Behavior During Drag

### Before Dragging
```
Device A          Device B
   ⭕ ─────────── ⭕
  /🖥️\           /📡\
 ( PC )         (Router)
```

### During Dragging
```
Device A moves →
   
   ┌─────┐  
  ╱  ⭕   ╲ 🤚      Device B
 │  /🖥️\  │  ╲      ⭕
 │ ( PC ) │    ───── /📡\
  ╲  ──┘ ╱         (Router)
   └─────┘

Connection automatically follows!
```

### After Dropping
```
           Device A
              ⭕
   ╱─────── /🖥️\
  ╱        ( PC )
 ╱
⭕ Device B
/📡\
(Router)

Connection remains intact
```

---

## 🎯 Cursor States Diagram

```
┌─────────────────────────────────────┐
│         Cursor State Flow           │
└─────────────────────────────────────┘

 default
    │
    ├──→ Mouse over device → grab ✋
    │         │
    │         ├──→ Click → grabbing 🤚
    │         │       │
    │         │       ├──→ Drag → grabbing 🤚
    │         │       │       │
    │         │       │       ├──→ Release → default
    │         │       │       │
    │         │       │       └──→ Leave canvas → default
    │         │       │
    │         │       └──→ (dragging active)
    │         │
    │         └──→ Move away → default
    │
    └──→ Connection mode → default
```

---

## 📏 Boundary Constraints Diagram

```
┌─────────────────────────────────────────┐
│ CANVAS (800x600)                        │
│                                         │
│  ←40px→                       ←40px→    │
│  ┌─────────────────────────────┐  ↑    │
│  │                             │  40px  │
│  │   SAFE DRAGGING AREA        │  ↓    │
│  │                             │       │
│  │    Devices can be moved     │  ↑    │
│  │    anywhere in this zone    │  40px  │
│  │                             │  ↓    │
│  │    ⭕  ←device              │       │
│  │   /🖥️\                      │       │
│  │  ( PC )                     │       │
│  │                             │       │
│  └─────────────────────────────┘       │
│                                         │
└─────────────────────────────────────────┘

Constraints:
• X: 40px ≤ device.x ≤ (width - 40px)
• Y: 40px ≤ device.y ≤ (height - 40px)
```

---

## 🔄 Event Loop Diagram

```
┌─────────────────────────────────────────┐
│         DRAG EVENT LOOP                 │
└─────────────────────────────────────────┘

mousedown
    ↓
┌─────────────────┐
│ isDragging ← true│
│ draggedDevice ← │
│   clicked device│
│ Store offsets   │
└─────────────────┘
    ↓
mousemove (loop)
    ↓
┌──────────────────┐
│ Update device.x  │
│ Update device.y  │
│ Apply boundaries │
│ redrawCanvas()   │ ← Continuous loop
└──────────────────┘
    ↓
mouseup OR mouseleave
    ↓
┌──────────────────┐
│isDragging ← false│
│draggedDevice ← null│
│ Track event      │
│ Reset cursor     │
└──────────────────┘
    ↓
  Complete!
```

---

## 🎨 Highlight Colors Reference

```
┌─────────────────────────────────────────┐
│          COLOR CODING SYSTEM            │
└─────────────────────────────────────────┘

DEVICE STATES:
• Default Border:    #00D9FF  ⭕ (Cyan)
• Hover:            #00D9FF  ⭕ + grab cursor
• Dragging:         #00FF88  ⭕ (Bright Green)
• Selected:         #FFD700  ⭕ (Gold)
• Connection Mode:  #00D9FF or #8B5CF6 (Cyan/Purple)

CONNECTION TYPES:
• Wired:           #00D9FF ─── (Cyan solid)
• Wireless:        #8B5CF6 ╌╌╌ (Purple dashed)

HIGHLIGHTS:
• Drag Glow:       #00FF88 with 15px blur
• Drag Border:     3px dashed (5,5 pattern)
• Select Border:   9px solid
```

---

## 📋 Quick Checklist

**Device Repositioning:**
- [x] Click on device
- [x] Cursor → grabbing
- [x] Green highlight appears
- [x] Drag to new position
- [x] Device follows mouse
- [x] Stay within 40px margins
- [x] Release to drop
- [x] Connections update
- [x] Cursor resets

**Edge Cases:**
- [x] Leave canvas → Drag cancels
- [x] Connection mode → Drag disabled
- [x] Rapid click → No conflict
- [x] Multiple devices → One at a time

---

## 🚀 Testing Workflow

```
1. Load Page
   ↓
2. Place device on canvas
   ↓
3. Hover over device
   ├→ ✓ Cursor = grab
   ↓
4. Click and hold
   ├→ ✓ Cursor = grabbing
   ├→ ✓ Green circle appears
   ↓
5. Move mouse (drag)
   ├→ ✓ Device follows
   ├→ ✓ Stays in bounds
   ├→ ✓ Connections update
   ↓
6. Release mouse
   ├→ ✓ Device placed
   ├→ ✓ Cursor = default
   ├→ ✓ Green highlight gone
   ↓
7. Success! ✅
```

---

**Status: ✅ Feature Complete**
**Visual Feedback: ✅ Fully Implemented**
**User Experience: ✅ Intuitive & Smooth**
