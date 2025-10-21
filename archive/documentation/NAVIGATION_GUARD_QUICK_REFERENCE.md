# Navigation Guard - Quick Reference Guide

## 🚀 Quick Start

### Add to New Challenge Page (3 Steps)

**1. Include Modal Component**
```html
{% include 'components/navigation_confirmation_modal.html' %}
```

**2. Activate Guard**
```javascript
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    if (typeof window.challengeNavigationGuard !== 'undefined') {
      window.challengeNavigationGuard.activate();
      window.challengeNavigationGuard.setProgress('Challenge Name: In progress');
    }
  }, 1000);
});
```

**3. Deactivate on Completion**
```javascript
function deactivateNavigationGuard() {
  if (typeof window.challengeNavigationGuard !== 'undefined') {
    window.challengeNavigationGuard.deactivate();
  }
}
// Call this when challenge is completed
```

---

## 📋 API Reference

### Global Object: `window.challengeNavigationGuard`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `activate()` | none | void | Start protecting navigation |
| `deactivate()` | none | void | Stop protecting navigation |
| `setProgress(info)` | info: string | void | Update progress display |
| `getElapsedTime()` | none | string | Get formatted time (MM:SS) |
| `showConfirmation(url)` | url: string | void | Show confirmation modal |

### Global Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `interceptNavigation(event, url)` | event: Event, url: string | boolean | Intercept nav clicks |
| `stayInChallenge()` | none | void | Close modal, stay |
| `confirmQuitChallenge()` | none | void | Deactivate & navigate |

---

## 💡 Common Patterns

### Pattern 1: Basic Integration
```javascript
// Activate on load
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(() => window.challengeNavigationGuard.activate(), 1000);
});

// Deactivate on success
function onChallengeComplete() {
  deactivateNavigationGuard();
  showSuccessModal();
}
```

### Pattern 2: Progress Updates
```javascript
// Update as user progresses
function updateProgress(current, total) {
  const percent = Math.round((current / total) * 100);
  window.challengeNavigationGuard.setProgress(`Progress: ${percent}% (${current}/${total})`);
}
```

### Pattern 3: Conditional Deactivation
```javascript
function submitChallenge() {
  const score = calculateScore();
  
  if (score >= passingScore) {
    deactivateNavigationGuard(); // Pass - allow navigation
  } else {
    // Fail - keep guard active for retry
  }
}
```

---

## 🎨 Modal Elements

### HTML Structure
```html
<div id="navigationConfirmationModal">
  <div class="navigation-confirmation-content">
    <div class="navigation-confirmation-header">
      <i class="fas fa-exclamation-triangle"></i>
      <h2>Leave Challenge?</h2>
    </div>
    <div class="navigation-confirmation-body">
      <p class="warning-message">You're in an active challenge!</p>
      <p class="warning-details">Progress will be saved...</p>
      <div class="progress-info">
        <span id="navConfirmTime">Time spent: 0:00</span>
        <span id="navConfirmProgress">Progress: In progress</span>
      </div>
    </div>
    <div class="navigation-confirmation-actions">
      <button class="stay-btn" onclick="stayInChallenge()">Stay</button>
      <button class="quit-btn" onclick="confirmQuitChallenge()">Quit</button>
    </div>
  </div>
</div>
```

### Key CSS Classes
| Class | Purpose |
|-------|---------|
| `.navigation-confirmation-modal` | Modal overlay (z-index: 50000) |
| `.navigation-confirmation-content` | Main modal container |
| `.navigation-confirmation-header` | Red gradient header with warning |
| `.navigation-confirmation-body` | Content area with progress info |
| `.navigation-confirmation-actions` | Button container |
| `.stay-btn` | Green "Stay" button |
| `.quit-btn` | Gray "Quit" button |
| `.progress-info` | Progress display area |

---

## 🔍 Debugging

### Check Guard Status
```javascript
// Is guard active?
console.log(window.challengeNavigationGuard.isActive);

// When did challenge start?
console.log(window.challengeNavigationGuard.startTime);

// What's the current progress?
console.log(window.challengeNavigationGuard.progressInfo);

// What URL is pending?
console.log(window.challengeNavigationGuard.pendingNavigation);
```

### Force Actions
```javascript
// Manually activate
window.challengeNavigationGuard.activate();

// Manually deactivate
window.challengeNavigationGuard.deactivate();

// Show modal manually
window.challengeNavigationGuard.showConfirmation('/user/dashboard');

// Update progress manually
window.challengeNavigationGuard.setProgress('Custom progress message');
```

### Console Log Messages
```
[NavigationGuard] Challenge navigation guard activated
[NavigationGuard] User chose to stay in challenge
[NavigationGuard] User confirmed quit challenge
[NavigationGuard] Challenge navigation guard deactivated
[CrimpingChallenge] Navigation guard activated
[CrimpingChallenge] Navigation guard deactivated - challenge completed
```

---

## ⚠️ Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Modal doesn't show | Guard not active | Call `activate()` after page load |
| Buttons don't work | JS error | Check browser console for errors |
| Always shows "0:00" | startTime not set | Guard must be activated first |
| Can't navigate after completion | Guard still active | Call `deactivate()` on completion |
| Modal shows on non-challenge pages | Guard not deactivated | Ensure deactivation on completion |

---

## 📱 Mobile Considerations

### Touch Events
- Buttons are minimum 48px height for easy tapping
- Full-width buttons on screens < 480px
- No hover effects on touch devices (use :active instead)

### Viewport
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### Responsive Breakpoints
- **Desktop**: 550px max width, side-by-side buttons
- **Tablet** (< 768px): 95% width, column buttons
- **Mobile** (< 480px): Full width, smaller text

---

## 🎯 Integration Checklist

- [ ] Include modal component in template
- [ ] Add activation script with DOMContentLoaded
- [ ] Set challenge-specific progress message
- [ ] Add deactivation function
- [ ] Call deactivation on challenge completion
- [ ] Test all sidebar navigation links
- [ ] Test Stay button functionality
- [ ] Test Quit button functionality
- [ ] Test on mobile device
- [ ] Verify console log messages

---

## 📊 Challenge Status Examples

### Good Progress Messages ✅
```javascript
'Crimping Challenge: In progress'
'OSI Model: Layer 3 of 7'
'Quiz: Question 5/10'
'Troubleshooting: Diagnostic phase'
'Network Setup: 70% complete'
```

### Bad Progress Messages ❌
```javascript
'In progress'              // Too generic
'Challenge'                // No context
''                         // Empty string
'Please wait'              // Not informative
```

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| `templates/components/navigation_confirmation_modal.html` | Modal component |
| `templates/user/base.html` | Navigation links with interceptors |
| `templates/user/crimping-simulation.html` | Crimping integration |
| `templates/user/osi-simulation.html` | OSI integration |
| `templates/user/troubleshoot.html` | Troubleshooting integration |
| `templates/user/quiz_challenge.html` | Quiz integration |
| `NAVIGATION_GUARD_IMPLEMENTATION.md` | Complete guide |

---

## 🎨 Color Reference

| Element | Color | Hex |
|---------|-------|-----|
| Header Background | Red Gradient | #ff4757 → #dc2626 |
| Stay Button | Green Gradient | #10b981 → #059669 |
| Quit Button | Gray Gradient | #6b7280 → #4b5563 |
| Progress Accent | Cyan | #00d4ff |
| Body Background | Dark Gradient | #1a1a2e → #16213e |
| Warning Text | Red | #ff4757 |
| Body Text | Light Gray | #e2e8f0 |

---

## 💻 Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully Supported |
| Firefox | 88+ | ✅ Fully Supported |
| Safari | 14+ | ✅ Fully Supported |
| Edge | 90+ | ✅ Fully Supported |
| Opera | 76+ | ✅ Fully Supported |
| Mobile Safari | iOS 14+ | ✅ Fully Supported |
| Chrome Mobile | Android 90+ | ✅ Fully Supported |

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Dec 2025 | Initial release |

---

**Quick Tip**: Always call `deactivateNavigationGuard()` when the challenge is successfully completed to allow free navigation!
