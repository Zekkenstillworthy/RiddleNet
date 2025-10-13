# Navigation Confirmation Modal - Responsive Breakpoints Visual Guide

## 📱 Device Size Comparison

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DESKTOP (>1024px)                                │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  ⚠️ Leave Challenge?                                       │     │
│  │  You're currently in an active challenge!                 │     │
│  │  [ Stay ]  [ Quit ]                                       │     │
│  └───────────────────────────────────────────────────────────┘     │
│  Modal Width: 90% (max 550px) | Buttons: Side-by-Side             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│              TABLET LANDSCAPE (769-1024px)                          │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │  ⚠️ Leave Challenge?                                     │       │
│  │  You're currently in an active challenge!               │       │
│  │  [ Stay ]  [ Quit ]                                     │       │
│  └─────────────────────────────────────────────────────────┘       │
│  Modal Width: 85% (max 600px) | Buttons: Side-by-Side             │
└─────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│   TABLET PORTRAIT (481-768px)              │
│  ┌──────────────────────────────────┐     │
│  │  ⚠️ Leave Challenge?              │     │
│  │  You're in an active challenge!  │     │
│  │  ┌────────────────────────────┐  │     │
│  │  │ Stay in Challenge          │  │     │
│  │  └────────────────────────────┘  │     │
│  │  ┌────────────────────────────┐  │     │
│  │  │ Quit Challenge             │  │     │
│  │  └────────────────────────────┘  │     │
│  └──────────────────────────────────┘     │
│  Width: 92% | Buttons: Vertical Stack     │
└────────────────────────────────────────────┘

┌──────────────────────────────┐
│   MOBILE (320-480px)         │
│ ┌──────────────────────────┐ │
│ │ ⚠️ Leave Challenge?      │ │
│ │ You're in challenge!     │ │
│ │ ┌──────────────────────┐ │ │
│ │ │ Stay in Challenge    │ │ │
│ │ └──────────────────────┘ │ │
│ │ ┌──────────────────────┐ │ │
│ │ │ Quit Challenge       │ │ │
│ │ └──────────────────────┘ │ │
│ └──────────────────────────┘ │
│ Width: 100% | Full Touch    │
└──────────────────────────────┘

┌─────────────────────┐
│  SMALL (≤360px)     │
│ ┌─────────────────┐ │
│ │ ⚠️ Leave?       │ │
│ │ Active chall.   │ │
│ │ ┌─────────────┐ │ │
│ │ │ Stay        │ │ │
│ │ └─────────────┘ │ │
│ │ ┌─────────────┐ │ │
│ │ │ Quit        │ │ │
│ │ └─────────────┘ │ │
│ └─────────────────┘ │
│ Compact Layout      │
└─────────────────────┘
```

---

## 🎨 Font Size Progression

```
DESKTOP (>1024px):
━━━━━━━━━━━━━━━━━━━━━━━━━
Heading:      28px ▓▓▓▓▓▓▓▓
Icon:         48px ▓▓▓▓▓▓▓▓▓▓
Warning:      20px ▓▓▓▓▓
Details:      16px ▓▓▓
Button:       16px ▓▓▓

TABLET (481-768px):
━━━━━━━━━━━━━━━━━━━━━━━━━
Heading:      24px ▓▓▓▓▓▓
Icon:         42px ▓▓▓▓▓▓▓▓
Warning:      18px ▓▓▓▓
Details:      15px ▓▓
Button:       15px ▓▓

MOBILE (320-480px):
━━━━━━━━━━━━━━━━━━━━━━━━━
Heading:      20px ▓▓▓▓
Icon:         36px ▓▓▓▓▓▓
Warning:      17px ▓▓▓
Details:      14px ▓▓
Button:       14px ▓▓

SMALL (≤360px):
━━━━━━━━━━━━━━━━━━━━━━━━━
Heading:      18px ▓▓▓
Icon:         32px ▓▓▓▓▓
Warning:      16px ▓▓
Details:      13px ▓
Button:       13px ▓
```

---

## 📐 Touch Target Sizes

```
iOS/Android Guidelines: 44-48px minimum

DESKTOP:
[  Button  ] → No minimum (mouse precision)

TABLET:
┌────────────────────┐
│      Button        │  48px height
└────────────────────┘

MOBILE:
┌────────────────────┐
│      Button        │  48px height (iOS/Android standard)
└────────────────────┘

SMALL MOBILE:
┌────────────────────┐
│      Button        │  44px height (iOS minimum)
└────────────────────┘
```

---

## 🔄 Layout Transformations

### Desktop/Tablet Landscape → Buttons Horizontal
```
┌──────────────────────────────────────┐
│          ⚠️ Leave Challenge?         │
│  ┌────────────┐    ┌──────────────┐ │
│  │   Stay     │    │    Quit      │ │
│  └────────────┘    └──────────────┘ │
└──────────────────────────────────────┘
```

### Tablet Portrait/Mobile → Buttons Vertical
```
┌──────────────────────────────────────┐
│          ⚠️ Leave Challenge?         │
│  ┌────────────────────────────────┐  │
│  │      Stay in Challenge         │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │      Quit Challenge            │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

### Mobile Landscape → Compact Horizontal
```
┌────────────────────────────────────────┐
│ ⚠️ Leave?  [Stay] [Quit]              │
└────────────────────────────────────────┘
         ↑ Compact layout saves vertical space
```

---

## 🌊 Animation Flow

### Desktop Entry Animation
```
Step 1:  ·  (scale: 0.8, translateY: -50px, opacity: 0)
         ↓
Step 2:  ○  (transition: 0.4s cubic-bezier)
         ↓
Step 3:  ● (scale: 1, translateY: 0, opacity: 1)
```

### Mobile Entry Animation
```
Step 1:  · (scale: 0.9, translateY: -30px, opacity: 0)
         ↓  ← Less distance, faster feel
Step 2:  ○ (transition: 0.4s cubic-bezier)
         ↓
Step 3:  ● (scale: 1, translateY: 0, opacity: 1)
```

### Touch Feedback
```
Normal:    [  Button  ]
           ↓ User taps
Active:    [ Button  ]  ← scale(0.97)
           ↓ 100ms
Normal:    [  Button  ]
```

---

## 📊 Spacing Hierarchy

### Padding Progression (Outside → Inside)

```
DESKTOP:
┌─ 30px ─────────────────────────┐
│ Header                          │  30px top/bottom
├─────────────────────────────────┤
│ Body                            │  35px top/bottom
├─────────────────────────────────┤
│ Actions                         │  25px top/bottom
└─────────────────────────────────┘

TABLET:
┌─ 26px ─────────────────────────┐
│ Header                          │  26px
├─────────────────────────────────┤
│ Body                            │  28px
├─────────────────────────────────┤
│ Actions                         │  22px
└─────────────────────────────────┘

MOBILE:
┌─ 24px ─────────────────────────┐
│ Header                          │  24px
├─────────────────────────────────┤
│ Body                            │  24px
├─────────────────────────────────┤
│ Actions                         │  20px
└─────────────────────────────────┘

SMALL:
┌─ 20px ─────────────────────────┐
│ Header                          │  20px
├─────────────────────────────────┤
│ Body                            │  20px
├─────────────────────────────────┤
│ Actions                         │  18px
└─────────────────────────────────┘
```

---

## 🎯 Button Width Comparison

```
DESKTOP/TABLET LANDSCAPE:
[←───── 180px min ─────→] [←───── 180px min ─────→]
    Stay Button                Quit Button

TABLET PORTRAIT/MOBILE:
[←──────────── 100% width ──────────────→]
              Stay Button

[←──────────── 100% width ──────────────→]
              Quit Button
```

---

## 🔍 Z-Index Stacking

```
Layer 6: Modal Content      (z-index: auto, inside 50000)
         ┌─────────────────┐
         │ Stay  │  Quit   │
         └─────────────────┘
              ↑
Layer 5: Modal Container    (z-index: 50000)
         ══════════════════
              ↑
Layer 4: Backdrop           (backdrop-filter + rgba)
         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
              ↑
Layer 3: Page Content       (z-index: auto)
         ░░░░░░░░░░░░░░░░░░
```

---

## 📱 Device Examples

### Desktop
- iMac, MacBook, Windows Desktop
- Chrome, Firefox, Edge, Safari
- Mouse + Keyboard interaction

### Tablet Landscape
- iPad Pro (12.9" landscape)
- Surface Pro (landscape)
- Galaxy Tab S8+ (landscape)
- Kindle Fire HD

### Tablet Portrait
- iPad Air (portrait)
- iPad Mini (portrait)
- Galaxy Tab A (portrait)
- Microsoft Surface Go

### Mobile
- iPhone 14 Pro (393×852)
- iPhone 13 (390×844)
- Galaxy S23 (360×800)
- Pixel 7 (412×915)

### Small Mobile
- iPhone SE (375×667)
- Galaxy S9 (360×740)
- Older budget phones

---

## ✅ Testing Matrix

| Device Type | Width Range | Button Layout | Touch Target | Test Status |
|-------------|-------------|---------------|--------------|-------------|
| Desktop | >1024px | Horizontal | - | ⬜ To Test |
| Tablet L | 769-1024px | Horizontal | 48px | ⬜ To Test |
| Tablet P | 481-768px | Vertical | 48px | ⬜ To Test |
| Mobile | 320-480px | Vertical | 48px | ⬜ To Test |
| Small | ≤360px | Vertical | 44px | ⬜ To Test |
| Landscape | h≤600px | Horizontal | 40px | ⬜ To Test |

---

**Legend**:
- ▓ = Filled/Active
- ░ = Background/Inactive
- ━ = Border/Separator
- ↑/↓ = Flow/Transition
- ┌┐└┘├┤ = Box corners
- [ ] = Button outline
- ⬜ = Checkbox unchecked
- ✅ = Checkbox checked
