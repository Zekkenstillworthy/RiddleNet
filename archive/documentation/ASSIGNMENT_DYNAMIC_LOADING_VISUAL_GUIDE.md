# 🎨 Assignment Dynamic Loading - Visual Guide

## 📐 UI Layout Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HEADER / NAVIGATION                         │
└─────────────────────────────────────────────────────────────────────┘
┌──────────────────┬──────────────────────────────────────────────────┐
│                  │                                                  │
│   SIDEBAR        │          MAIN CONTENT AREA                       │
│                  │        (.lesson-content)                         │
│  ┌────────────┐  │                                                  │
│  │ Modules    │  │  ┌────────────────────────────────────────────┐ │
│  │  Module 1  │  │  │  ASSIGNMENT CONTENT                        │ │
│  │  Module 2  │  │  │  (Loaded Dynamically)                      │ │
│  └────────────┘  │  │                                            │ │
│                  │  │  📋 Title                                  │ │
│  ┌────────────┐  │  │  📅 Due Date                               │ │
│  │Assignments │  │  │  🎯 Points                                 │ │
│  │            │  │  │  📝 Description                            │ │
│  │[Assignment]│←─┼──┤  📖 Instructions                           │ │
│  │[Assignment]│  │  │  ✅ Submission Details                     │ │
│  │[ACTIVE]    │  │  │  📊 Requirements                           │ │
│  │[Assignment]│  │  │                                            │ │
│  └────────────┘  │  └────────────────────────────────────────────┘ │
│                  │                                                  │
└──────────────────┴──────────────────────────────────────────────────┘
```

---

## 🔄 Assignment Click Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER CLICKS ASSIGNMENT                           │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
                ┌────────────────────────────┐
                │ loadAssignment(id) called  │
                └────────────┬───────────────┘
                             ↓
        ┌────────────────────┴────────────────────┐
        │                                         │
        ↓                                         ↓
┌───────────────────┐                  ┌──────────────────┐
│ Update UI State   │                  │  Show Loading    │
│ - Remove active   │                  │  - Spinner       │
│   from lessons    │                  │  - Message       │
│ - Add active to   │                  │  - Blue glow     │
│   assignment      │                  └─────────┬────────┘
└─────────┬─────────┘                            │
          │                                      │
          └──────────────────┬───────────────────┘
                             ↓
                ┌────────────────────────────┐
                │  AJAX Request              │
                │  GET /api/assignments/{id} │
                └────────────┬───────────────┘
                             ↓
                    ┌────────┴────────┐
                    │                 │
                    ↓                 ↓
            ┌───────────┐      ┌──────────┐
            │  SUCCESS  │      │  ERROR   │
            └─────┬─────┘      └────┬─────┘
                  │                 │
                  ↓                 ↓
      ┌──────────────────┐   ┌─────────────────┐
      │ renderAssignment │   │  Show Error     │
      │ Content()        │   │  - Red warning  │
      │                  │   │  - Retry button │
      │ - Build HTML     │   └─────────────────┘
      │ - Insert content │
      │ - Scroll to top  │
      └──────────────────┘
```

---

## 🎯 Status Badge Colors

```
┌──────────────┬──────────────┬─────────────────────┐
│   Status     │    Color     │       Icon          │
├──────────────┼──────────────┼─────────────────────┤
│NOT_SUBMITTED │ Gray/Muted   │ ○ fa-circle         │
│SUBMITTED     │ Blue/Accent  │ ✓ fa-check-circle   │
│GRADED        │ Green/Neon   │ ★ fa-star           │
│OVERDUE       │ Red/Danger   │ ⚠ fa-exclamation    │
│RESUBMITTED   │ Orange/Warn  │ ↻ fa-redo           │
└──────────────┴──────────────┴─────────────────────┘
```

---

## 📊 Data Flow Diagram

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │ 1. User clicks assignment
       ↓
┌──────────────────────┐
│  JavaScript Function │
│  loadAssignment()    │
└──────┬───────────────┘
       │ 2. AJAX GET request
       ↓
┌────────────────────────────┐
│  Flask API Endpoint        │
│  /api/assignments/<id>     │
└──────┬─────────────────────┘
       │ 3. Query database
       ↓
┌─────────────────────────┐
│  Database Tables        │
│  - class_assignments    │
│  - assignment_submissions│
└──────┬──────────────────┘
       │ 4. Return JSON
       ↓
┌──────────────────────────┐
│  JavaScript Renderer     │
│  renderAssignmentContent()│
└──────┬───────────────────┘
       │ 5. Update DOM
       ↓
┌──────────────┐
│ Browser UI   │
│ (Updated)    │
└──────────────┘
```

---

## 🎨 Assignment Content Layout

```
╔═══════════════════════════════════════════════════════════╗
║                    ASSIGNMENT VIEW                        ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  📍 Breadcrumb: Dashboard > Class > Assignments > Title  ║
║                                                           ║
║  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ║
║  ┃  📋 Assignment Title                              ┃  ║
║  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ║
║                                                           ║
║  🏷️ Type    📅 Due Date    🎯 Points    📊 Status        ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ ℹ️  DESCRIPTION                                      │ ║
║  │                                                      │ ║
║  │ Assignment description text goes here...            │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ 📖 INSTRUCTIONS                                      │ ║
║  │                                                      │ ║
║  │ Step-by-step instructions...                        │ ║
║  │ 1. First step                                       │ ║
║  │ 2. Second step                                      │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ ✅ YOUR SUBMISSION (if submitted)                    │ ║
║  │                                                      │ ║
║  │ 📅 Submitted: Oct 11, 2025                          │ ║
║  │ ⭐ Grade: 95/100                                     │ ║
║  │ 💬 Feedback: Great work!                            │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
║  ┌───────────────┬──────────────┬────────────────────┐  ║
║  │ 📤 FILE       │ ⌨️  TEXT      │ ⏰ LATE           │  ║
║  │ UPLOADS       │ SUBMISSION   │ SUBMISSIONS       │  ║
║  │               │              │                   │  ║
║  │ Max 5 files   │ Type your    │ -10% per day      │  ║
║  │ 10MB each     │ response     │                   │  ║
║  └───────────────┴──────────────┴────────────────────┘  ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐ ║
║  │ ℹ️  Submission functionality coming soon!            │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🔲 Loading State Animation

```
Frame 1:        Frame 2:        Frame 3:        Frame 4:
   ⠋              ⠙              ⠹              ⠸
   ○              ◔              ◑              ◕
   
 Loading          Loading         Loading         Loading
Assignment...   Assignment...   Assignment...   Assignment...

(Cyan glow spinner rotates continuously)
```

---

## ❌ Error State Layout

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║                         ⚠️                                ║
║                    (Red Triangle)                        ║
║                                                           ║
║              Error Loading Assignment                    ║
║                                                           ║
║    Unable to load assignment details. Please try again.  ║
║                                                           ║
║              ┌─────────────────┐                         ║
║              │  🔄 Retry       │                         ║
║              └─────────────────┘                         ║
║                 (Blue button)                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🎭 Active State Visual

### Before Click
```
┌─────────────────┐
│ Assignment 1    │  ← Normal (dark background)
├─────────────────┤
│ Assignment 2    │  ← Normal
├─────────────────┤
│ Assignment 3    │  ← Normal
└─────────────────┘
```

### After Click (Assignment 2)
```
┌─────────────────┐
│ Assignment 1    │  ← Normal (dark background)
├═════════════════┤
║ Assignment 2    ║  ← ACTIVE (cyan glow, lighter bg)
├─────────────────┤
│ Assignment 3    │  ← Normal
└─────────────────┘
```

---

## 🌈 Color Scheme

```
┌────────────────┬──────────────┬─────────────────┐
│   Element      │  Color Name  │   Hex Value     │
├────────────────┼──────────────┼─────────────────┤
│ Cyber Glow     │ Cyan         │ #00D9FF         │
│ Neon Green     │ Green        │ #39FF14         │
│ Network Purple │ Purple       │ #8B5CF6         │
│ Accent Blue    │ Blue         │ #3B82F6         │
│ Success        │ Green        │ #10B981         │
│ Warning        │ Orange       │ #F59E0B         │
│ Danger         │ Red          │ #EF4444         │
│ Background     │ Dark Blue    │ #0F172A         │
│ Surface        │ Slate        │ #1E293B         │
│ Border Glow    │ Cyan Alpha   │ rgba(0,217,255,0.3) │
└────────────────┴──────────────┴─────────────────┘
```

---

## 📱 Responsive Behavior

### Desktop (> 1024px)
```
┌──────────┬─────────────────────────┐
│          │                         │
│ Sidebar  │   Assignment Content    │
│  300px   │      Flexible width     │
│          │                         │
└──────────┴─────────────────────────┘
```

### Tablet (768px - 1024px)
```
┌──────────┬──────────────────┐
│          │                  │
│ Sidebar  │   Assignment     │
│  250px   │   Flexible       │
│          │                  │
└──────────┴──────────────────┘
```

### Mobile (< 768px)
```
┌─────────────────────────┐
│    Assignment Content    │
│      Full Width          │
│  (Sidebar collapses)     │
└─────────────────────────┘
```

---

## 🔍 Browser DevTools Inspector

### HTML Structure
```html
<div class="lesson-content">
  <div class="assignment-view">
    <div class="assignment-view-header">
      <div class="lesson-breadcrumb">...</div>
      <h1 class="lesson-title">...</h1>
      <div class="lesson-meta">...</div>
    </div>
    <div class="content-section">...</div>
    <div class="content-section">...</div>
    <div class="requirements-grid">...</div>
  </div>
</div>
```

### Network Tab - API Call
```
Request URL: http://127.0.0.1:5001/api/assignments/1
Request Method: GET
Status Code: 200 OK
Response Headers:
  Content-Type: application/json
Response Body:
  {
    "id": 1,
    "title": "Assignment 1",
    ...
  }
```

---

## 🎬 Animation Timeline

```
Time    Action
────────────────────────────────────────────────────
0ms     User clicks assignment
10ms    Active state updates (instant)
20ms    Loading spinner appears
50ms    AJAX request sent
200ms   Server response received
220ms   Content rendering starts
250ms   HTML injected into DOM
270ms   Smooth scroll animation begins
500ms   Scroll animation completes
────────────────────────────────────────────────────
Total:  ~500ms for complete transition
```

---

## 📐 Spacing & Typography

```
┌─────────────────────────────────────────────────┐
│ H1 Title          | 1.5rem (24px)   | Bold     │
│ H3 Section Title  | 1.25rem (20px)  | Semibold│
│ H4 Subtitle       | 1.1rem (18px)   | Semibold│
│ Body Text         | 1rem (16px)     | Regular │
│ Small Text        | 0.9rem (14px)   | Regular │
│ Metadata          | 0.95rem (15px)  | Medium  │
├─────────────────────────────────────────────────┤
│ Padding (Cards)   | 20px            |          │
│ Margin (Sections) | 24px            |          │
│ Border Radius     | 12px            |          │
│ Box Shadow        | 0 4px 12px      |          │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Click Zones

```
Assignment Item Clickable Area:
┌───────────────────────────────────────┐
│ ← Full area is clickable              │
│                                       │
│   Assignment Title          [Status]  │
│   📅 Due Date | 🏷️ Type | ⭐ Points   │
│                                       │
│ ← Cursor changes to pointer on hover │
└───────────────────────────────────────┘
```

---

**Visual Guide Complete** ✅  
All UI elements, layouts, and interactions documented with ASCII diagrams.

