# Navigation Guard System - Architecture & Flow Diagrams

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RiddleNet Platform                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
        ┌───────────▼──────────┐    ┌──────────▼─────────┐
        │   User Navigation    │    │  Challenge Pages   │
        │   (Base Template)    │    │                    │
        └───────────┬──────────┘    └──────────┬─────────┘
                    │                           │
        ┌───────────▼───────────────────────────▼─────────┐
        │     Navigation Confirmation Modal Component     │
        │    (navigation_confirmation_modal.html)         │
        └───────────┬───────────────────────────┬─────────┘
                    │                           │
        ┌───────────▼──────────┐    ┌──────────▼─────────┐
        │  JavaScript Guard    │    │   Modal UI         │
        │  System (Global)     │    │   (HTML/CSS)       │
        └──────────────────────┘    └────────────────────┘
```

---

## 🔄 Component Interaction Flow

```
┌───────────────────┐
│   User Action     │
│  (Click Nav Link) │
└─────────┬─────────┘
          │
          ▼
┌─────────────────────────────────┐
│  interceptNavigation(event, url)│
│         (Global Function)        │
└─────────┬───────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│  Check: Guard Active?           │
│  (challengeNavigationGuard      │
│   .isActive)                    │
└─────────┬───────────────────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌───────┐   ┌───────────────────┐
│  NO   │   │       YES         │
│       │   │                   │
│Allow  │   │Prevent Navigation │
│Nav    │   │                   │
└───────┘   └─────────┬─────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │ showConfirmation(url)│
            │  Display Modal       │
            └──────────┬───────────┘
                      │
            ┌─────────┴─────────┐
            │                   │
            ▼                   ▼
    ┌────────────┐      ┌────────────┐
    │   "Stay"   │      │   "Quit"   │
    │   Button   │      │   Button   │
    └──────┬─────┘      └──────┬─────┘
           │                   │
           ▼                   ▼
    ┌──────────────┐   ┌──────────────────┐
    │ Close Modal  │   │ Deactivate Guard │
    │ Stay on Page │   │ Navigate to URL  │
    └──────────────┘   └──────────────────┘
```

---

## 🎮 Challenge Lifecycle Flow

```
┌────────────────────────┐
│  User Enters Challenge │
└──────────┬─────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Page Loads (DOMContentLoaded)│
└──────────┬───────────────────┘
           │
           ▼ (Wait 1 second)
┌──────────────────────────────┐
│  Activate Navigation Guard   │
│  challengeNavigationGuard    │
│  .activate()                 │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  isActive = true             │
│  startTime = Date.now()      │
│  progressInfo = "Challenge..." │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  User Interacts with         │
│  Challenge                   │
│  (Optional Progress Updates) │
└──────────┬───────────────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐   ┌────────────────┐
│Continue │   │   Complete     │
│Playing  │   │   Challenge    │
└────┬────┘   └───────┬────────┘
     │                │
     │                ▼
     │     ┌──────────────────────┐
     │     │ deactivateNavigation │
     │     │ Guard()              │
     │     └──────────┬───────────┘
     │                │
     │                ▼
     │     ┌──────────────────────┐
     │     │  isActive = false    │
     │     │  Navigation Free     │
     │     └──────────────────────┘
     │
     ▼
┌──────────────────────────┐
│  Try to Navigate Away?   │
│  (Click Sidebar Link)    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Show Confirmation Modal │
│  (Guard Active)          │
└──────────────────────────┘
```

---

## 📊 State Diagram

```
                    ┌──────────────┐
                    │   Initial    │
                    │  (No Guard)  │
                    └──────┬───────┘
                           │
                           │ activate()
                           ▼
                    ┌──────────────┐
                    │    Active    │
          ┌─────────│   (Guarded)  │◄─────────┐
          │         └──────┬───────┘          │
          │                │                  │
          │                │ Try Navigation   │
          │                ▼                  │
          │         ┌──────────────┐          │
          │         │   Pending    │          │
          │         │ (Modal Open) │          │
          │         └──────┬───────┘          │
          │                │                  │
          │         ┌──────┴──────┐           │
          │         │             │           │
          │         ▼             ▼           │
          │   ┌──────────┐  ┌──────────┐     │
          │   │  "Stay"  │  │  "Quit"  │     │
          │   └────┬─────┘  └────┬─────┘     │
          │        │             │            │
          │        │             ▼            │
          └────────┘      ┌──────────────┐   │
                          │  deactivate()│   │
                          └──────┬───────┘   │
                                 │            │
                                 ▼            │
                          ┌──────────────┐   │
                          │   Inactive   │   │
                          │  (Free Nav)  │   │
                          └──────┬───────┘   │
                                 │            │
                                 └────────────┘
                                  (Optional: 
                                   Reactivate)
```

---

## 🗂️ File Structure & Dependencies

```
RiddleNet Project
│
├── templates/
│   │
│   ├── components/
│   │   └── navigation_confirmation_modal.html
│   │       ├── HTML Structure (Modal)
│   │       ├── CSS Styles (Glassmorphism)
│   │       └── JavaScript (Guard Logic)
│   │
│   └── user/
│       │
│       ├── base.html
│       │   ├── Extends: None (Base Template)
│       │   ├── Includes: Navigation Sidebar
│       │   └── Modified: All nav links → onclick interceptor
│       │
│       ├── crimping-simulation.html
│       │   ├── Extends: base.html
│       │   ├── Includes: navigation_confirmation_modal.html
│       │   └── Activates: Guard on DOMContentLoaded
│       │
│       ├── osi-simulation.html
│       │   ├── Extends: base.html
│       │   ├── Includes: navigation_confirmation_modal.html
│       │   └── Activates: Guard on DOMContentLoaded
│       │
│       ├── troubleshoot.html
│       │   ├── Extends: base.html
│       │   ├── Includes: navigation_confirmation_modal.html
│       │   └── Activates: Guard on DOMContentLoaded
│       │
│       └── quiz_challenge.html
│           ├── Extends: base.html
│           ├── Includes: navigation_confirmation_modal.html
│           └── Activates: Guard on DOMContentLoaded
│
└── Documentation/
    ├── NAVIGATION_GUARD_IMPLEMENTATION.md (Complete Guide)
    ├── NAVIGATION_GUARD_QUICK_REFERENCE.md (Developer Ref)
    └── NAVIGATION_GUARD_TESTING_GUIDE.md (Testing Protocol)
```

---

## 🔐 Security Flow

```
┌──────────────────────┐
│   User Interaction   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────┐
│  Client-Side Validation      │
│  (JavaScript Guard Check)    │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  User Confirms Action        │
│  (Modal Interaction)         │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Navigation Request          │
│  (window.location.href)      │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Flask Route Handler         │
│  (Server-Side Logic)         │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Session Validation          │
│  (Flask Session Check)       │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Render Target Page          │
└──────────────────────────────┘

Note: Navigation guard is CLIENT-SIDE ONLY
      Server-side validation still required
```

---

## 🎯 Event Flow Timeline

```
Time →
│
├─ 0ms: Page Load Starts
│
├─ 500ms: DOM Parsed
│      └─ DOMContentLoaded Event Fires
│
├─ 1000ms: Guard Activation Script Runs
│      ├─ challengeNavigationGuard.activate()
│      ├─ isActive = true
│      ├─ startTime = Date.now()
│      └─ Console: "[Challenge] Guard activated"
│
├─ 1500ms: Page Fully Interactive
│      └─ User can interact with challenge
│
├─ 30000ms: User Clicks Sidebar Link
│      ├─ onclick="interceptNavigation()" called
│      ├─ event.preventDefault()
│      └─ showConfirmation() called
│
├─ 30050ms: Modal Displays
│      ├─ Fade-in animation (300ms)
│      ├─ Slide-in animation (400ms)
│      └─ Modal fully visible
│
├─ 32000ms: User Clicks "Stay" Button
│      ├─ stayInChallenge() called
│      ├─ Modal closes
│      └─ pendingNavigation = null
│
├─ 45000ms: User Completes Challenge
│      ├─ Success modal shown
│      ├─ deactivateNavigationGuard() called
│      ├─ isActive = false
│      └─ Console: "[Challenge] Guard deactivated"
│
├─ 46000ms: User Clicks Navigation Link
│      ├─ interceptNavigation() called
│      ├─ isActive = false
│      └─ Navigation proceeds immediately
│
└─ End
```

---

## 💾 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Memory (JavaScript)               │
│                                                              │
│  window.challengeNavigationGuard = {                        │
│    isActive: boolean          ─┐                            │
│    startTime: timestamp        │  ← Read by modal display   │
│    progressInfo: string        │                            │
│    pendingNavigation: url     ─┘                            │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
                             │
                             │ (No Server Communication)
                             │
                             ▼
                    ┌─────────────────┐
                    │  Modal Display  │
                    │  (DOM Update)   │
                    └─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  User Decision  │
                    │  (Stay / Quit)  │
                    └─────────────────┘
                             │
                ┌────────────┴───────────┐
                │                        │
                ▼                        ▼
        ┌──────────────┐        ┌──────────────┐
        │   No Data    │        │  Navigation  │
        │   Transfer   │        │   Request    │
        └──────────────┘        └──────┬───────┘
                                       │
                                       ▼
                               ┌───────────────┐
                               │  Flask Server │
                               │  (New Page)   │
                               └───────────────┘
```

---

## 🎨 CSS Architecture

```
Navigation Confirmation Modal
│
├── Overlay Layer (z-index: 50000)
│   ├── Background: rgba(0,0,0,0.95)
│   ├── Backdrop-filter: blur(25px)
│   └── Display: flex (centering)
│
└── Content Container
    │
    ├── Header Section
    │   ├── Background: Red Gradient
    │   ├── Warning Icon (Pulsing)
    │   └── Title Text
    │
    ├── Body Section
    │   ├── Background: Dark Gradient
    │   ├── Warning Message (Red)
    │   ├── Details Text (Gray)
    │   └── Progress Info Box
    │       ├── Border: Cyan
    │       ├── Time Display
    │       └── Progress Display
    │
    └── Actions Section
        ├── Background: Transparent Dark
        ├── Stay Button (Green Gradient)
        │   ├── Hover: Lift Effect
        │   └── Icon + Text
        └── Quit Button (Gray Gradient)
            ├── Hover: Lift Effect
            └── Icon + Text
```

---

## 📱 Responsive Behavior Flow

```
Device Detection
│
├─ Desktop (> 768px)
│   ├── Modal width: 550px max
│   ├── Buttons: Side-by-side
│   ├── Font sizes: Standard
│   └── Hover effects: Enabled
│
├─ Tablet (480px - 768px)
│   ├── Modal width: 95%
│   ├── Buttons: Column layout
│   ├── Font sizes: Slightly reduced
│   └── Touch targets: 48px minimum
│
└─ Mobile (< 480px)
    ├── Modal width: 95%
    ├── Buttons: Full width, stacked
    ├── Font sizes: Mobile optimized
    ├── Padding: Reduced
    └── Touch targets: 48px minimum
```

---

## 🔄 Update Propagation

```
Challenge Progress Changes
│
├─ User Action in Challenge
│   └─ (e.g., answers quiz question)
│
├─ Challenge Logic Updates State
│   └─ (e.g., currentQuestion++)
│
├─ Optional: Update Guard Progress
│   ├─ updateChallengeProgress() called
│   └─ challengeNavigationGuard.setProgress("Question 5/10")
│
└─ Progress Available for Modal
    └─ If user tries to navigate, modal shows updated progress
```

---

## 🎭 Modal Animation Sequence

```
Trigger Point (Navigation Click)
│
├─ Step 1: Modal Element Created/Shown
│   └─ display: none → display: flex
│
├─ Step 2: Overlay Fade-In (300ms)
│   └─ opacity: 0 → 1
│
├─ Step 3: Content Scale + Slide (400ms)
│   ├─ transform: scale(0.8) translateY(-50px)
│   └─ transform: scale(1) translateY(0)
│
├─ Step 4: Warning Icon Pulse Starts (2s loop)
│   └─ scale(1) → scale(1.1) → scale(1)
│
└─ Step 5: Modal Fully Interactive
    └─ User can click buttons
```

---

## 🧩 Integration Points

```
Base Template (base.html)
│
├─ Provides: Sidebar Navigation Structure
├─ Includes: All navigation links
└─ Modified: onclick interceptors added
    │
    └─ Calls: window.interceptNavigation()
             │
             └─ Defined in: navigation_confirmation_modal.html

Challenge Pages (e.g., crimping-simulation.html)
│
├─ Extends: base.html (gets sidebar)
├─ Includes: navigation_confirmation_modal.html
│            │
│            └─ Provides: Modal UI + JavaScript Guard
│
└─ Activates: Guard on page load
             │
             └─ challengeNavigationGuard.activate()
```

---

## 🌐 Browser Environment

```
Window Object
│
├── challengeNavigationGuard
│   ├── activate()
│   ├── deactivate()
│   ├── setProgress()
│   ├── getElapsedTime()
│   └── showConfirmation()
│
├── interceptNavigation()
├── stayInChallenge()
└── confirmQuitChallenge()

DOM Elements
│
├── #navigationConfirmationModal (container)
├── #navConfirmTime (time display)
└── #navConfirmProgress (progress display)
```

---

## 🎯 Summary Diagram

```
┌────────────────────────────────────────────────────────────┐
│                    Navigation Guard System                  │
│                                                             │
│  Purpose: Prevent accidental navigation from challenges    │
│                                                             │
│  Components:                                               │
│  ✓ Reusable Modal Component                               │
│  ✓ Global JavaScript Guard API                            │
│  ✓ Navigation Interceptors (Base Template)                │
│  ✓ Challenge-Specific Integrations                        │
│                                                             │
│  Features:                                                 │
│  ✓ Automatic Detection                                    │
│  ✓ Beautiful Confirmation Modal                           │
│  ✓ Time & Progress Tracking                               │
│  ✓ Responsive Design                                      │
│  ✓ Smooth Animations                                      │
│                                                             │
│  Status: Production Ready ✅                               │
└────────────────────────────────────────────────────────────┘
```

---

**Document Version**: 1.0.0  
**Created**: December 2025  
**Purpose**: Visual Architecture Reference
