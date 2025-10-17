# Unified Sidebar Visual Guide

## Desktop Layout (> 1024px)

```
┌─────────────────────────────────────────────────────────────────┐
│  Simulation Canvas Area                                         │
│                                                                  │
│  [Network devices, connections, configurations]                 │
│                                                                  │
│                                                                  │
│                                               ┌─────────────────┤
│                                               │ ╔═══════════════╗
│                                               │ ║ PANEL         ║ ← Toggle
│                                               │ ╚═══════════════╝
│                                               │                 │
│                                               │┌───────┬───────┐│
│                                               ││ Perf  │ Collab││ ← Tabs
│                                               │└───────┴───────┘│
│                                               │                 │
│                                               │ ┌─ Close [×]    │
│                                               │ │               │
│                                               │ │ 🏆 Score: 85  │
│                                               │ │               │
│                                               │ │ ⏱ Progress 40%│
│                                               │ │               │
│                                               │ │ 📊 Metrics    │
│                                               │ │   Time: 5:30  │
│                                               │ │   Actions: 12 │
│                                               │ │               │
│                                               │ └───────────────│
│                                               │                 │
└───────────────────────────────────────────────┴─────────────────┘
                                                ↑
                                                380px wide
```

## Mobile Layout (< 768px)

```
┌─────────────────────────────────────┐
│ Simulation Canvas Area              │
│                                     │
│ [Network devices]                   │
│                                     │
│                                     │
│                                     │
│                                     │
│                                     │
│                                     │
│                                ┌───┐│
│                                │ ☰ ││ ← Mobile Toggle
│                                └───┘│
└─────────────────────────────────────┘

When opened (full width):

┌─────────────────────────────────────┐
│┌─────────────┬─────────────────────┐│
││Performance  │  Collaboration      ││ ← Tabs
│└─────────────┴─────────────────────┘│
│                              [×]    │ ← Close
│                                     │
│  🏆 Current Score                   │
│     ┌─────┐                         │
│     │  85 │ pts                     │
│     └─────┘                         │
│                                     │
│  ⏱ Progress                         │
│     ◉ 40%                           │
│                                     │
│  📊 Metrics                         │
│     ⏱ Time: 5:30                    │
│     🖱 Actions: 12                  │
│     ⚠ Errors: 2                     │
│     ❓ Hints: 1                     │
│                                     │
└─────────────────────────────────────┘
         Full width (100%)
```

## Tab Content Comparison

### Performance Tab
```
┌──────────────────────────────────┐
│ [×] Close                         │
│                                   │
│ 🏆 CURRENT SCORE                 │
│   ┌───────────────┐              │
│   │      85       │ pts          │
│   │  Devices: 4/5 │              │
│   │  Config:  2/2 │              │
│   └───────────────┘              │
│                                   │
│ ⏱ PROGRESS                       │
│   ◉──────○  40%                  │
│   Getting Started                │
│   Est. 15 min                    │
│                                   │
│ 📊 METRICS                       │
│   ┌──────┐ ┌──────┐              │
│   │ ⏱ 5:30│ │🖱  12│              │
│   │ Time  │ │Action│              │
│   └──────┘ └──────┘              │
│   ┌──────┐ ┌──────┐              │
│   │ ⚠  2 │ │❓  1 │              │
│   │Errors│ │Hints │              │
│   └──────┘ └──────┘              │
│                                   │
└──────────────────────────────────┘
```

### Collaboration Tab
```
┌──────────────────────────────────┐
│ [×] Close                         │
│                                   │
│ 📡 CONNECTION STATUS             │
│   🟢 Connected                   │
│   Solo Mode • Ready              │
│                                   │
│ 👥 CURRENT SESSION               │
│   Solo Session  #SOLO            │
│   👤 1/1  ⏱ 00:00  🏆 0 pts     │
│   [Browse Sessions]              │
│   [Settings] [Refresh]           │
│                                   │
│ 👥 SESSION MEMBERS               │
│   ┌──────┐ ┌──────┐             │
│   │ 👤   │ │  +   │             │
│   │ You  │ │Join? │             │
│   │ Solo │ │Browse│             │
│   └──────┘ └──────┘             │
│                                   │
│ 💬 TEAM CHAT                     │
│   ┌─────────────────────┐       │
│   │ Welcome to chat!    │       │
│   └─────────────────────┘       │
│   [Type message...] [Send]      │
│                                   │
│ 🚀 QUICK JOIN                    │
│   [Code...] [Join]               │
│                                   │
└──────────────────────────────────┘
```

## Interaction Flow

### Opening the Sidebar

**Desktop:**
```
1. User clicks toggle button on right edge
   ┌───┐
   │ ☰ │ ← Click
   └───┘

2. Sidebar slides in from right
   ← ← ← ← 
   
3. Shows Performance tab by default
```

**Mobile:**
```
1. User taps floating button (bottom-right)
            ┌───┐
            │ ☰ │ ← Tap
            └───┘

2. Sidebar slides up/in full width
   ↑↑↑↑↑↑↑↑↑

3. Shows Performance tab by default
```

### Switching Tabs

```
Current: Performance        Click Collaboration
┌─────────────┬──────────┐  ┌──────────┬─────────────┐
│Performance ▼│Collaboration│→│Performance│Collaboration▼│
└─────────────┴──────────┘  └──────────┴─────────────┘
     Active                        Active
```

### Closing the Sidebar

```
Option 1: Click [×] button (top-right)
   ┌──────────────────[×]┐ ← Click
   │                     │
   
Option 2: Click toggle again
   ┌───┐
   │ ☰ │ ← Click
   └───┘
   
Option 3: (Mobile) Tap outside
   Tap anywhere → → → → →
```

## Z-Index Layers

```
Layer 1500: Unified Sidebar (highest)
    ┌────────────────┐
    │ Sidebar Panel  │
    └────────────────┘

Layer 1400: Mobile Toggle Button
            ┌───┐
            │ ☰ │
            └───┘

Layer 1200: Device Palette
┌──────────────────────────┐
│ Device Palette           │
└──────────────────────────┘

Layer 1000: Canvas Content
┌──────────────────────────┐
│ Network Devices          │
└──────────────────────────┘
```

## Color Scheme

```
┌─────────────────────────────────────┐
│ Sidebar Background:                 │
│ rgba(15, 23, 42, 0.98)              │ ← Dark blue-gray
│   with backdrop-filter blur         │
│                                     │
│ ┌─────────────────────────────┐   │
│ │ Tabs Background:            │   │
│ │ rgba(0, 0, 0, 0.3)          │   │ ← Darker black
│ └─────────────────────────────┘   │
│                                     │
│ ┌─────────────────────────────┐   │
│ │ Active Tab:                 │   │
│ │ rgba(0, 217, 255, 0.1)      │   │ ← Cyan glow
│ │ border-bottom: var(--cyber-glow)│
│ └─────────────────────────────┘   │
│                                     │
│ Content Text:                       │
│ var(--text-primary) - White         │
│ var(--text-secondary) - Gray        │
└─────────────────────────────────────┘
```

## Responsive Breakpoints

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Large Desktop (> 1024px)                                   │
│  • Sidebar: 380px width                                     │
│  • Toggle: Fixed to right edge                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tablet (768px - 1024px)                                    │
│  • Sidebar: Full height, same width                         │
│  • Toggle: Mobile button shown                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Mobile (< 768px)                                           │
│  • Sidebar: 100% width, full height                         │
│  • Toggle: Floating button (bottom-right)                   │
│  • Tabs: Horizontal, full width                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Animation Timing

```
Open Sidebar:
  Duration: 0.4s
  Timing: cubic-bezier(0.4, 0, 0.2, 1)
  
  0% ────────────────► 100%
  translateX(100%)     translateX(0)
  opacity: 0           opacity: 1

Close Sidebar:
  Duration: 0.4s
  Timing: cubic-bezier(0.4, 0, 0.2, 1)
  
  0% ────────────────► 100%
  translateX(0)        translateX(100%)
  opacity: 1           opacity: 0

Tab Switch:
  Duration: 0.3s
  Timing: ease
  
  Content fade out → fade in
```

## Touch Targets (Mobile)

```
Minimum touch target: 44x44px

┌─────────────────────────────────┐
│ Tab Button                      │
│ ┌──────────────┐               │
│ │              │ ← 44px min    │
│ │ Performance  │               │
│ │              │               │
│ └──────────────┘               │
│                                 │
│ Mobile Toggle Button            │
│ ┌────────┐                     │
│ │        │ ← 56x56px           │
│ │   ☰    │                     │
│ │        │                     │
│ └────────┘                     │
│                                 │
│ Close Button                    │
│ ┌────┐                         │
│ │ × │ ← 40x40px                │
│ └────┘                         │
└─────────────────────────────────┘
```

---

**Legend:**
- `┌─┐└─┘│─` Box drawing characters
- `☰` Hamburger menu icon
- `×` Close button
- `◉` Progress ring
- `🏆🎯📊⏱🖱⚠❓👥💬🚀📡` Emoji icons
- `→ ← ↑` Direction indicators
- `▼` Active tab indicator
