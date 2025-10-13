# 🧪 All Popups Testing Guide - Complete Checklist

## 📋 Quick Start

**Purpose:** Verify all 9 popups are responsive on mobile, tablet, and desktop  
**Time Required:** 30-45 minutes for complete testing  
**Tools Needed:** Chrome DevTools or real devices

---

## 🎯 Testing Procedure

### Step 1: Open Troubleshooting Page
```
URL: http://127.0.0.1:5001/troubleshooting/
```

### Step 2: Clear Browser Cache
```
Windows: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

### Step 3: Open Chrome DevTools
```
F12 or Right-click → Inspect
Toggle device toolbar: Ctrl + Shift + M (Windows)
                       Cmd + Shift + M (Mac)
```

---

## 📱 Device Profiles to Test

### Priority 1: Essential Devices
- ✅ **iPhone SE (375 × 667)** - Smallest common phone
- ✅ **iPhone 13 Pro (390 × 844)** - Modern iPhone
- ✅ **iPad (768 × 1024)** - Standard tablet
- ✅ **Desktop (1920 × 1080)** - Standard desktop

### Priority 2: Additional Coverage
- ✅ **Galaxy S20 (360 × 800)** - Very small phone
- ✅ **Pixel 5 (393 × 851)** - Android phone
- ✅ **iPad Pro (1024 × 1366)** - Large tablet
- ✅ **Desktop 4K (2560 × 1440)** - Large monitor

### Landscape Testing
- ✅ **iPhone 13 Landscape (844 × 390)** - Critical for Foundation modal
- ✅ **iPad Landscape (1024 × 768)** - Tablet horizontal
- ✅ **Mobile Landscape (640 × 360)** - Small phone horizontal

---

## 🎯 Popup-by-Popup Testing Checklist

### 1. Link Up Welcome Modal ✅

**How to Open:**
1. Navigate to troubleshooting page
2. Modal should auto-open on first visit
3. Or look for "Start Link Up" button

**Test Checklist:**

#### Mobile (375px)
- [ ] Modal width: calc(100vw - 24px) ✓
- [ ] No horizontal scrolling ✓
- [ ] 2 option cards stack vertically ✓
- [ ] Cards are full-width ✓
- [ ] Text is readable (≥14px) ✓
- [ ] Close button is 44px × 44px ✓
- [ ] Tap close button works ✓

#### Tablet (768px)
- [ ] Modal width: max 720px, centered ✓
- [ ] 2 option cards in grid ✓
- [ ] Proper spacing between cards ✓
- [ ] Close button is 48px × 48px ✓

#### Desktop (1920px)
- [ ] Modal width: 900px, centered ✓
- [ ] Cards side-by-side ✓
- [ ] Hover effects work ✓
- [ ] Visual polish maintained ✓

---

### 2. Scenario Selection Modal ✅

**How to Open:**
1. After Link Up modal, click an option
2. Or click "Scenarios" button on page

**Test Checklist:**

#### Mobile (375px)
- [ ] Modal width: calc(100vw - 24px) ✓
- [ ] 4 scenario cards stack vertically ✓
  - [ ] FOUNDATION card ✓
  - [ ] NOVICE card ✓
  - [ ] INTERMEDIATE card ✓
  - [ ] ADVANCED card ✓
- [ ] Each card full-width ✓
- [ ] Lock icons visible ✓
- [ ] Requirements text readable ✓
- [ ] Scroll works smoothly ✓
- [ ] Close button 44px × 44px ✓

#### Tablet (768px)
- [ ] Modal width: max 720px ✓
- [ ] Cards in 2×2 grid (if implemented) ✓
- [ ] Proper spacing ✓
- [ ] Close button 48px × 48px ✓

#### Desktop (1920px)
- [ ] Modal width: 900px, centered ✓
- [ ] Cards in grid layout ✓
- [ ] Hover effects work ✓
- [ ] Animations smooth ✓

---

### 3. Foundation Learning Modal (16 Modules) ✅

**How to Open:**
1. In Scenario Selection Modal, click "FOUNDATION"
2. Or click any Foundation scenario button

**Test Checklist:**

#### Mobile Portrait (375px)
- [ ] Modal width: calc(100vw - 24px) ✓
- [ ] Header "Foundation Learning" 20px font ✓
- [ ] Progress bar visible and styled ✓
- [ ] "4/16 modules completed" text readable ✓
- [ ] **Phase 1: Device Discovery** section ✓
  - [ ] Phase heading 18px font ✓
  - [ ] Description text readable (12px) ✓
  - [ ] 3 module buttons visible ✓
    - [ ] 💻 Meet the PC - 80px height ✓
    - [ ] 🔀 Meet the Switch - 80px height ✓
    - [ ] 📡 Meet the Router - 80px height ✓
  - [ ] Button icon 28px size ✓
  - [ ] Button title 15px font ✓
  - [ ] Button description 12px font ✓
  - [ ] Full-width buttons ✓
  - [ ] Buttons are tap-friendly ✓
- [ ] **Phase 2: Basic Connections** section ✓
  - [ ] 3 module buttons ✓
  - [ ] Same styling as Phase 1 ✓
- [ ] **Phase 3: Network Topologies** section ✓
  - [ ] 5 module buttons ✓
- [ ] **Phase 4: Basic Topologies** section ✓
  - [ ] 5 module buttons ✓
- [ ] Content scrolls smoothly ✓
- [ ] Max-height: calc(100vh - 160px) ✓
- [ ] Scrollbar styled (6px width) ✓
- [ ] "← Back" button full-width ✓
- [ ] Close button 44px × 44px ✓

#### Tablet (768px)
- [ ] Modal width: max 800px, centered ✓
- [ ] Module buttons 90px height ✓
- [ ] Icon 30px size ✓
- [ ] Title 16px font ✓
- [ ] Description 13px font ✓
- [ ] Proper spacing (20px content padding) ✓
- [ ] Close button 48px × 48px ✓

#### Desktop (1920px)
- [ ] Modal width: max 1000px, centered ✓
- [ ] Module buttons 100px height ✓
- [ ] Icon 36px size ✓
- [ ] Title 18px font ✓
- [ ] Description 15px font ✓
- [ ] Hover effects work ✓
- [ ] Button transforms on hover ✓

#### Mobile Landscape (844×390)
**CRITICAL TEST:** Most content-heavy modal
- [ ] Modal fits in viewport ✓
- [ ] Header 16px font ✓
- [ ] Module buttons 70px height (compact) ✓
- [ ] Icon 24px size ✓
- [ ] Title 13px font ✓
- [ ] Description 11px font ✓
- [ ] Content area scrollable ✓
- [ ] Max-height: calc(100vh - 100px) ✓
- [ ] All 16 modules accessible via scroll ✓
- [ ] No content cut off ✓

#### Touch Device Simulation
**In Chrome DevTools:**
1. Select device with touch (iPhone, iPad, etc.)
2. Click "Toggle device toolbar"
3. Ensure "Touch" is enabled in device settings

**Test:**
- [ ] Module buttons min-height 90px ✓
- [ ] Active state on tap: scale(0.98) ✓
- [ ] Background feedback on tap ✓
- [ ] No hover effects (touch devices) ✓
- [ ] Smooth scrolling with finger ✓

---

### 4. Easy/Novice Modal ✅

**How to Open:**
1. In Scenario Selection Modal, click "NOVICE"
2. Or click any Novice scenario button

**Test Checklist:**

#### Mobile (375px)
- [ ] Modal width: calc(100vw - 24px) ✓
- [ ] Header "Novice Scenarios" 20px font ✓
- [ ] Scenario list visible ✓
- [ ] Each scenario button full-width ✓
- [ ] Scenario descriptions readable ✓
- [ ] Close button 44px × 44px ✓

#### Tablet (768px)
- [ ] Modal width: max 720px, centered ✓
- [ ] Proper spacing ✓
- [ ] Close button 48px × 48px ✓

#### Desktop (1920px)
- [ ] Modal width: max 800px, centered ✓
- [ ] Hover effects work ✓

---

### 5. Medium/Intermediate Modal ✅

**How to Open:**
1. In Scenario Selection Modal, click "INTERMEDIATE"
2. Or click any Intermediate scenario button

**Test Checklist:**

#### Mobile (375px)
- [ ] Modal width: calc(100vw - 24px) ✓
- [ ] Header "Intermediate Scenarios" 20px font ✓
- [ ] Scenario list stacked vertically ✓
- [ ] Full-width scenario buttons ✓
- [ ] Readable text ✓
- [ ] Close button 44px × 44px ✓

#### Tablet (768px)
- [ ] Modal width: max 720px ✓
- [ ] Close button 48px × 48px ✓

#### Desktop (1920px)
- [ ] Modal width: max 800px ✓
- [ ] Hover effects work ✓

---

### 6. Hard/Advanced Modal ✅

**How to Open:**
1. In Scenario Selection Modal, click "ADVANCED"
2. Or click any Advanced scenario button

**Test Checklist:**

#### Mobile (375px)
- [ ] Modal width: calc(100vw - 24px) ✓
- [ ] Header "Advanced Scenarios" 20px font ✓
- [ ] Enterprise scenarios visible ✓
- [ ] Full-width buttons ✓
- [ ] Text readable ✓
- [ ] Close button 44px × 44px ✓

#### Tablet (768px)
- [ ] Modal width: max 720px ✓
- [ ] Proper layout ✓
- [ ] Close button 48px × 48px ✓

#### Desktop (1920px)
- [ ] Modal width: max 800px ✓
- [ ] Professional appearance ✓

---

### 7. Configuration CLI Modal ✅

**How to Open:**
1. Click on any device (Router, Switch, PC) in canvas
2. Or right-click device → "Configure"

**Test Checklist:**

#### Mobile Portrait (375px)
- [ ] Modal width: calc(100vw - 24px) ✓
- [ ] Header "Device Configuration CLI" 18px font ✓
- [ ] Device name visible (e.g., "Router-1") ✓
- [ ] **CLI Terminal Output Area** ✓
  - [ ] Height: calc(100vh - 200px) ✓
  - [ ] Min-height: 300px ✓
  - [ ] Monospace font maintained ✓
  - [ ] Font size: 12px ✓
  - [ ] Background: dark terminal style ✓
  - [ ] Text color: terminal green/white ✓
  - [ ] Scrollable vertically ✓
  - [ ] Commands visible (e.g., "show ip interface brief") ✓
  - [ ] Output formatted correctly ✓
  - [ ] Line numbers/prompts visible ✓
- [ ] **CLI Input Area** ✓
  - [ ] Height: 44px (touch-friendly) ✓
  - [ ] Font size: 13px ✓
  - [ ] Placeholder visible ("Enter command...") ✓
  - [ ] Tappable on mobile ✓
  - [ ] Keyboard appears when tapped ✓
  - [ ] Text input works ✓
  - [ ] Paste commands works ✓
- [ ] Close button 44px × 44px ✓
- [ ] Scrollbar styled (6px width) ✓

#### Tablet (768px)
- [ ] Modal width: max 900px ✓
- [ ] Terminal height: 60vh ✓
- [ ] Min-height: 400px ✓
- [ ] Font size: 13px output, 14px input ✓
- [ ] Input area: 48px height ✓
- [ ] Close button 48px × 48px ✓

#### Desktop (1920px)
- [ ] Modal width: max 1200px ✓
- [ ] Terminal height: 70vh ✓
- [ ] Min-height: 500px ✓
- [ ] Font size: 14px output, 15px input ✓
- [ ] Professional terminal appearance ✓
- [ ] Command history navigation (↑↓) ✓

#### Mobile Landscape (844×390)
**CRITICAL TEST:** CLI needs vertical space
- [ ] Modal fits in viewport ✓
- [ ] Header 16px font ✓
- [ ] Terminal height: calc(100vh - 160px) ✓
- [ ] Min-height: 200px ✓
- [ ] Font size: 11px output, 12px input ✓
- [ ] Input area: 40px height (compact) ✓
- [ ] Scrollable terminal ✓
- [ ] All CLI output accessible ✓

#### Touch Device (CLI Input)
- [ ] Input field min-height: 48px ✓
- [ ] Touch-action: manipulation ✓
- [ ] Tapping input focuses cursor ✓
- [ ] No zoom when focusing input ✓
- [ ] Virtual keyboard appears correctly ✓
- [ ] Copy/paste gestures work ✓

---

### 8. Problem Popup ✅

**How to Open:**
1. During active challenge/scenario
2. Click "View Problem" or similar button
3. Or triggered automatically on problem start

**Test Checklist:**

#### Mobile (375px)
- [ ] Modal width: calc(100vw - 24px) ✓
- [ ] Header readable ✓
- [ ] Problem description visible ✓
- [ ] Hints section visible ✓
- [ ] Text is readable ✓
- [ ] Close button 44px × 44px ✓

#### Tablet (768px)
- [ ] Modal width: max 720px ✓
- [ ] Proper layout ✓
- [ ] Close button 48px × 48px ✓

#### Desktop (1920px)
- [ ] Modal width: max 800px ✓
- [ ] Clear presentation ✓

---

### 9. Challenges Modal ✅

**How to Open:**
1. Click "Challenges" button on main page
2. Or access from navigation menu

**Test Checklist:**

#### Mobile (375px)
- [ ] Modal width: calc(100vw - 24px) ✓
- [ ] Header "Challenges" 20px font ✓
- [ ] Challenge cards stacked vertically ✓
- [ ] Each card full-width ✓
- [ ] Challenge icons/badges visible ✓
- [ ] Challenge titles readable ✓
- [ ] Difficulty indicators visible ✓
- [ ] "Start Challenge" buttons 44px height ✓
- [ ] Scrollable if many challenges ✓
- [ ] Close button 44px × 44px ✓

#### Tablet (768px)
- [ ] Modal width: max 720px ✓
- [ ] Challenge cards in grid (if applicable) ✓
- [ ] Proper spacing ✓
- [ ] Close button 48px × 48px ✓

#### Desktop (1920px)
- [ ] Modal width: max 1000px ✓
- [ ] Grid layout for challenges ✓
- [ ] Hover effects work ✓
- [ ] Visual polish maintained ✓

#### Touch Device
- [ ] Challenge items min-height: 80px ✓
- [ ] Active state feedback on tap ✓
- [ ] Easy tapping on challenge cards ✓

---

## 🧪 Comprehensive Test Scenarios

### Scenario 1: Mobile User Journey
**Device:** iPhone 13 (390×844)

1. **Start:** Open http://127.0.0.1:5001/troubleshooting/
2. **Link Up Modal:** Appears automatically
   - [ ] Modal fits screen ✓
   - [ ] Tap "Start Learning" ✓
3. **Scenario Modal:** Opens after closing Link Up
   - [ ] Tap "FOUNDATION" card ✓
4. **Foundation Modal:** Opens with 16 modules
   - [ ] Scroll through all 4 phases ✓
   - [ ] Tap "💻 Meet the PC" ✓
5. **Back to Scenario:** Tap "← Back"
   - [ ] Returns to Scenario Modal ✓
6. **Try CLI:** Place device on canvas
   - [ ] Tap device to open Config Modal ✓
   - [ ] Type command in CLI ✓
   - [ ] Scroll terminal output ✓
7. **Challenges:** Close modals, tap "Challenges"
   - [ ] Challenges Modal opens ✓
   - [ ] Tap challenge card ✓

**Pass Criteria:** All modals open, close, and function correctly without horizontal scrolling or layout issues.

---

### Scenario 2: Tablet User Journey
**Device:** iPad (768×1024)

1. **Start:** Open troubleshooting page
2. **Test all 9 popups** one by one
3. **Rotate to landscape** (1024×768)
4. **Test all 9 popups again** in landscape
5. **Verify:**
   - [ ] All modals centered ✓
   - [ ] Proper spacing maintained ✓
   - [ ] Touch targets ≥48px ✓
   - [ ] No content clipping ✓

**Pass Criteria:** Consistent experience in both orientations.

---

### Scenario 3: Desktop User Journey
**Device:** Desktop (1920×1080)

1. **Open all 9 popups** using mouse
2. **Test hover effects:**
   - [ ] Foundation module buttons ✓
   - [ ] Scenario cards ✓
   - [ ] Close buttons ✓
   - [ ] Challenge cards ✓
3. **Test keyboard navigation:**
   - [ ] Tab between buttons ✓
   - [ ] Enter to activate ✓
   - [ ] Escape to close modal ✓
4. **Resize browser window:**
   - [ ] 1024px width ✓
   - [ ] 768px width ✓
   - [ ] 480px width ✓
5. **Verify responsive adaption** at each size

**Pass Criteria:** Smooth transitions between breakpoints, no layout breaks.

---

### Scenario 4: Landscape Mobile Journey
**Device:** iPhone 13 Landscape (844×390)

**CRITICAL TEST:** Most challenging for content-heavy modals

1. **Foundation Modal in Landscape:**
   - [ ] Open Foundation modal ✓
   - [ ] Verify 16 modules visible via scroll ✓
   - [ ] Buttons 70px height (compact) ✓
   - [ ] Scroll smoothly through phases ✓
   - [ ] Close button accessible ✓

2. **CLI Modal in Landscape:**
   - [ ] Open Config modal ✓
   - [ ] Terminal height: calc(100vh - 160px) ✓
   - [ ] Min-height: 200px maintained ✓
   - [ ] Input field accessible ✓
   - [ ] Type commands ✓
   - [ ] Scroll terminal output ✓

3. **Other Modals:**
   - [ ] Link Up Modal fits ✓
   - [ ] Scenario Modal fits ✓
   - [ ] Challenges Modal fits ✓

**Pass Criteria:** All modals fit in viewport, content accessible, no overlapping elements.

---

## 🎯 Critical Visual Checks

### Check 1: Touch Target Sizes
**Tool:** Chrome DevTools Ruler Tool

**Measure these elements:**
- [ ] Close buttons: 44-48px × 44-48px ✓
- [ ] Foundation module buttons: 80-100px height ✓
- [ ] CLI input field: 44-48px height ✓
- [ ] Challenge cards: 80px height ✓
- [ ] Scenario cards: Adequate tappable area ✓

**WCAG 2.1 Standards:**
- Level AA: 44px × 44px (Minimum)
- Level AAA: 48px × 48px (Optimal) ← **Our target**

---

### Check 2: Typography Readability
**Tool:** DevTools Computed Styles

**Verify font sizes:**

| Element | Mobile | Tablet | Desktop |
|---------|--------|--------|---------|
| Modal headers | 18-20px | 22px | 24px |
| Foundation button title | 15px | 16px | 18px |
| Foundation button desc | 12px | 13px | 15px |
| CLI output | 12px | 13px | 14px |
| CLI input | 13px | 14px | 15px |
| Body text | 14px | 15px | 16px |

**Minimum Standards:**
- Body text: ≥14px
- Descriptions: ≥12px
- Headers: ≥18px

---

### Check 3: Scrolling Behavior
**Test in each modal:**

1. **Foundation Modal:**
   - [ ] Smooth scrolling ✓
   - [ ] Scrollbar styled (6px width) ✓
   - [ ] No momentum issues ✓
   - [ ] All 16 modules reachable ✓

2. **CLI Modal:**
   - [ ] Terminal scrolls smoothly ✓
   - [ ] Scrollbar styled ✓
   - [ ] Auto-scroll on new output ✓

3. **Challenges Modal:**
   - [ ] Smooth scrolling ✓
   - [ ] No lag ✓

**iOS Safari Specific:**
- [ ] -webkit-overflow-scrolling: touch works ✓
- [ ] No rubber-banding breaks layout ✓

---

### Check 4: Overlay & Z-Index
**Verify layering:**

1. Open multiple modals (if possible)
2. **Check z-index hierarchy:**
   - Canvas: z-index 10
   - Device palette: z-index 100
   - Modals: z-index 2001
   - Notifications: z-index 3000

3. **Verify:**
   - [ ] Modal overlays canvas ✓
   - [ ] Modal backgrounds darken page ✓
   - [ ] Close button visible above content ✓
   - [ ] No stacking context issues ✓

---

## 🚨 Common Issues to Watch For

### Issue 1: Horizontal Scrolling
**Symptoms:** Content wider than viewport, scrollbar appears

**Check:**
- [ ] No horizontal scrollbar on any device ✓
- [ ] Content fits within calc(100vw - 24px) ✓
- [ ] No fixed widths exceeding viewport ✓

**Fix if found:** Reduce padding or use max-width constraints

---

### Issue 2: Text Too Small
**Symptoms:** Squinting required, zooming necessary

**Check:**
- [ ] All text ≥12px on mobile ✓
- [ ] Headers ≥18px ✓
- [ ] Body text ≥14px ✓

**Fix if found:** Increase font-size in mobile breakpoint

---

### Issue 3: Touch Targets Too Small
**Symptoms:** Difficulty tapping buttons, mis-taps

**Check:**
- [ ] All interactive elements ≥44px ✓
- [ ] Optimal targets are 48px ✓
- [ ] Spacing between targets ≥8px ✓

**Fix if found:** Increase padding or min-height

---

### Issue 4: Content Clipping
**Symptoms:** Text cut off, buttons not visible

**Check:**
- [ ] All content visible without scroll ✓
- [ ] Scrollable areas have scrollbar ✓
- [ ] Max-height allows all content ✓

**Fix if found:** Adjust max-height or enable scrolling

---

### Issue 5: Landscape Layout Broken
**Symptoms:** Overlapping content, unusable interface

**Check:**
- [ ] Foundation modal fits in landscape ✓
- [ ] CLI modal fits in landscape ✓
- [ ] Buttons not overlapping ✓
- [ ] Content scrollable ✓

**Fix if found:** Apply landscape-specific styles

---

## 📊 Testing Completion Matrix

### Device × Popup Matrix

| Popup | iPhone SE | iPhone 13 | iPad | Desktop | Landscape |
|-------|-----------|-----------|------|---------|-----------|
| 1. Link Up | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2. Scenario | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3. Foundation | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4. Easy/Novice | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5. Medium/Inter | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6. Hard/Advanced | ☐ | ☐ | ☐ | ☐ | ☐ |
| 7. Config CLI | ☐ | ☐ | ☐ | ☐ | ☐ |
| 8. Problem | ☐ | ☐ | ☐ | ☐ | ☐ |
| 9. Challenges | ☐ | ☐ | ☐ | ☐ | ☐ |

**Completion Goal:** All 45 cells checked ✓

---

## ✅ Sign-Off Checklist

### Before Marking Complete

- [ ] All 9 popups tested on mobile (iPhone SE) ✓
- [ ] All 9 popups tested on tablet (iPad) ✓
- [ ] All 9 popups tested on desktop (1920×1080) ✓
- [ ] Foundation modal tested in landscape ✓
- [ ] CLI modal tested in landscape ✓
- [ ] Touch targets measured (≥44px) ✓
- [ ] Typography sizes verified ✓
- [ ] No horizontal scrolling anywhere ✓
- [ ] Scrolling smooth in all popups ✓
- [ ] Close buttons work on all devices ✓
- [ ] No console errors ✓
- [ ] Performance acceptable (<100ms modal open) ✓

### Documentation Review

- [ ] ALL_POPUPS_RESPONSIVE_COMPLETE.md reviewed ✓
- [ ] MODAL_RESPONSIVE_VISUAL_GUIDE.md referenced ✓
- [ ] MODAL_RESPONSIVE_QUICK_SUMMARY.md referenced ✓

### Stakeholder Approval

- [ ] QA team signed off ✓
- [ ] Design team reviewed visual consistency ✓
- [ ] Product owner approved UX ✓
- [ ] Dev team confirmed no regressions ✓

---

## 🎉 Testing Complete!

Once all checkboxes are marked:

1. **Document findings** in a testing report
2. **Create bug tickets** for any issues found
3. **Update documentation** with any discovered edge cases
4. **Mark as PRODUCTION READY** if all tests pass

---

## 📞 Need Help?

**Issue Found?**
1. Document the exact device/size
2. Take screenshot
3. Note specific popup affected
4. Describe expected vs. actual behavior
5. Check browser console for errors

**Quick Fixes:**
- Clear cache: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)
- Hard refresh: Shift+F5
- Restart browser
- Test in incognito mode

---

**Testing Guide Version:** 1.0  
**Last Updated:** 2025-10-13  
**Status:** Ready for QA  
**Priority:** HIGH - Critical UX Validation

---

## 🚀 Ready to Test!

Start with **Scenario 1: Mobile User Journey** (iPhone 13) for the most comprehensive test. Then proceed to landscape and tablet testing.

**Estimated Time:**
- Quick Test (Priority 1 devices): 15 minutes
- Thorough Test (All devices): 45 minutes
- Full QA (All scenarios): 2 hours

Good luck! 🎯
