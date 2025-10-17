# Advanced Level Unlock Fix

## Problem
After completing all 3 Intermediate scenarios, the Advanced level remained locked. The system showed "Progress: 3/3 Intermediate scenarios completed" but didn't unlock the next difficulty level.

## Root Cause
The code had an unlock sync function for Intermediate level (`syncIntermediateUnlockFromNovice()`) that runs when Novice scenarios are completed, but there was **NO equivalent function** for Advanced level unlock when Intermediate scenarios are completed.

### Missing Implementation
1. No `syncAdvancedUnlockFromIntermediate()` function existed
2. No automatic unlock check when medium/intermediate difficulty scenarios were completed
3. The `difficulty_unlocks.hard` flag was never being set in localStorage
4. The Advanced level unlock logic didn't check for the persisted unlock flag

## Solution Implemented

### 1. Added `syncAdvancedUnlockFromIntermediate()` Function
Created a new function that mirrors the Intermediate unlock logic:
- Counts completed Intermediate (medium) scenarios
- Checks if ALL Intermediate scenarios are completed
- Sets `difficulty_unlocks.hard = true` in localStorage when unlocked
- Returns a snapshot with completion status

```javascript
function syncAdvancedUnlockFromIntermediate() {
    // Get all completed challenges
    const completedLinkup = JSON.parse(localStorage.getItem('completed_linkup_challenges') || '[]');
    
    // Count completed medium (intermediate) scenarios
    const mediumScenarios = scenarios.filter(s => s.difficulty === 'medium');
    const completedMedium = mediumScenarios.filter(s => completedLinkup.includes(s.id)).length;
    const totalMedium = mediumScenarios.length;
    
    // Check if all intermediate scenarios are completed
    const shouldUnlock = totalMedium > 0 && completedMedium >= totalMedium;
    
    // Update difficulty_unlocks.hard flag
    if (totalMedium > 0) {
        const unlocks = JSON.parse(localStorage.getItem('difficulty_unlocks') || '{}');
        if (!!unlocks.hard !== !!shouldUnlock) {
            unlocks.hard = shouldUnlock;
            localStorage.setItem('difficulty_unlocks', JSON.stringify(unlocks));
        }
    }
    
    return snapshot;
}
```

### 2. Call Sync Function After Intermediate Completion
Updated the `showResultsPopup()` function to call the new sync function:

```javascript
// ✅ MVP: Sync Advanced unlock immediately after Intermediate completion
if (scenario.difficulty === 'medium') {
    try {
        const snap = syncAdvancedUnlockFromIntermediate();
        console.log('🔄 Post-completion Advanced unlock sync:', snap);
        if (snap.shouldUnlock) {
            console.log('🎉 Advanced unlocked after completing Intermediate scenario!');
            updateDifficultyAccess();
        }
    } catch (e) {
        console.warn('Post-completion Advanced sync failed:', e);
    }
}
```

### 3. Call Sync on Page Load
Updated the `DOMContentLoaded` event listener to sync both levels:

```javascript
document.addEventListener('DOMContentLoaded', () => {
    try { 
        syncIntermediateUnlockFromNovice();
        syncAdvancedUnlockFromIntermediate(); // NEW
        
        setTimeout(() => {
            const snapIntermediate = syncIntermediateUnlockFromNovice();
            const snapAdvanced = syncAdvancedUnlockFromIntermediate(); // NEW
            if (snapIntermediate.total > 0 || snapAdvanced.total > 0) {
                updateDifficultyAccess();
            }
        }, 500);
    } catch {}
});
```

### 4. Updated Advanced Level Access Check
Modified the Advanced card unlock logic to respect the `difficulty_unlocks.hard` flag:

```javascript
const unlocks = JSON.parse(localStorage.getItem('difficulty_unlocks') || '{}');
const canAccessHard = !!unlocks.hard || (finalHasCompletedFoundation && 
                     completedEasy >= easyScenarios.length && 
                     completedMedium >= mediumScenarios.length);
```

## Testing Steps

### Option 1: Clear Cache and Replay (Recommended for Clean State)
1. **Clear browser cache**: Ctrl+Shift+Delete → Clear cached images and files
2. **Clear localStorage**: Press F12 → Console → Run:
   ```javascript
   localStorage.clear();
   location.reload();
   ```
3. Complete all 3 Intermediate scenarios again
4. Advanced level should unlock automatically

### Option 2: Manual Unlock (Quick Fix for Current User)
1. Press F12 to open browser console
2. Run this command:
   ```javascript
   let unlocks = JSON.parse(localStorage.getItem('difficulty_unlocks') || '{}');
   unlocks.hard = true;
   localStorage.setItem('difficulty_unlocks', JSON.stringify(unlocks));
   location.reload();
   ```
3. Advanced level should now be unlocked

## Expected Behavior After Fix
✅ When completing the last Intermediate scenario:
- Console logs: "🎉 Advanced unlocked after completing Intermediate scenario!"
- `difficulty_unlocks.hard` is set to `true` in localStorage
- `updateDifficultyAccess()` runs and removes lock overlay
- Advanced difficulty card becomes clickable

✅ On page load:
- `syncAdvancedUnlockFromIntermediate()` runs automatically
- Checks completed Intermediate scenarios
- Sets unlock flag if all are completed
- UI reflects correct unlock state

## Files Modified
- `templates/user/troubleshoot.html`
  - Added `syncAdvancedUnlockFromIntermediate()` function (line ~11327)
  - Updated completion flow in `showResultsPopup()` (line ~16599)
  - Updated `DOMContentLoaded` event (line ~11380)
  - Updated Advanced card unlock check (line ~12690)

## Console Logging
The fix includes comprehensive logging:
- `🔄 ===== SYNC ADVANCED UNLOCK START =====`
- `📂 Completed challenges: [...]`
- `📊 Intermediate Progress: X/3`
- `🔄 Advanced unlock state change? prev: false → next: true`
- `✅ Advanced unlock state UPDATED`
- `🎉 Advanced unlocked after completing Intermediate scenario!`

## Verification
Check the browser console for these logs after completing the 3rd Intermediate scenario to verify the fix is working.
