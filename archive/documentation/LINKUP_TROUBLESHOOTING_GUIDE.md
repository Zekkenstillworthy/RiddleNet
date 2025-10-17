# 🔍 Link Up Challenge MVP - Troubleshooting Guide

## Quick Diagnostics

### ✅ Everything Working?

Run this quick check:

```
1. Open Console (F12)
2. Complete ANY Link Up challenge
3. See these messages? ──→ ✅ WORKING!
   - 📊 Displaying challenge results
   - 💾 Saving Link Up challenge results to database
   - ✅ Topology score saved to backend
   - ✅ Challenge progress saved for Link Up
   - ✅ Link Up challenge results saved to database successfully

4. Sidebar shows results? ──→ ✅ WORKING!
5. Refresh browser (F5)
6. Results still visible? ──→ ✅ WORKING!

ALL 6 CHECKS PASSED = PERFECT! 🎊
```

---

## 🐛 Common Issues & Solutions

### Issue 1: No Console Messages

**Symptom:**
```
Complete challenge → Nothing in console
```

**Solution:**
```
1. Press F12 to open DevTools
2. Click "Console" tab
3. Try completing another challenge
4. If still nothing:
   - Check browser cache (clear it)
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Check if JavaScript errors exist (red messages)
```

---

### Issue 2: Results Not Showing in Sidebar

**Symptom:**
```
Complete challenge → Console shows success → But sidebar empty
```

**Solution:**
```
1. Is sidebar visible?
   - Look for "Performance Feedback" panel on right side
   - If hidden, look for button to open it

2. Scroll in sidebar
   - Results might be below current view
   - Look for "Challenge Results" section

3. Check for placeholder text
   - If says "Complete a Link Up challenge to see results"
   - Then results aren't updating

4. Debug:
   const container = document.getElementById('results-container');
   console.log(container);
   console.log(container.innerHTML);
```

---

### Issue 3: Console Shows Errors

**Symptom:**
```
❌ Error messages in red
```

**Common Errors & Fixes:**

#### Error: "Results container or sidebar not found"
```javascript
// Fix: Check if elements exist
const sidebar = document.getElementById('performance-sidebar');
const container = document.getElementById('results-container');
console.log('Sidebar:', sidebar);
console.log('Container:', container);

// If null, page structure changed - need to update IDs
```

#### Error: "fetch failed" or "Network error"
```javascript
// Fix 1: Check backend server is running
// Fix 2: Check endpoint URLs are correct
// Fix 3: Check authentication (logged in?)
// Fix 4: Check CORS settings
```

#### Error: "JSON parse error"
```javascript
// Fix: Backend returning invalid JSON
// Check backend response format
// Verify Content-Type: application/json
```

---

### Issue 4: Saves to One Table But Not Other

**Symptom:**
```
✅ Topology score saved to backend: 85
❌ Challenge progress save failed: [error]
```

**Solution:**
```
1. Check which endpoint failed:
   - /save_topology_score → challenge_score table
   - /api/challenge/save-progress → challenge_progress table

2. Test endpoint directly:
   fetch('/api/challenge/save-progress', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({
           challenge_type: 'linkup',
           state_data: {test: true},
           is_completed: true
       })
   }).then(r => r.json()).then(console.log);

3. Check backend logs for errors

4. Verify database table exists:
   SELECT * FROM challenge_progress LIMIT 1;
```

---

### Issue 5: Results Disappear on Refresh

**Symptom:**
```
Complete challenge → See results → Refresh → Results gone
```

**Solution:**
```
1. Check if data saved to database:
   - Console should show "✅ saved to database"
   - If shows ❌ error, database save failed

2. Check sessionStorage:
   console.log(sessionStorage.getItem('lastLinkUpResult'));
   // Should show challenge data

3. Backend might not be returning saved data on page load
   - Check if sidebar loads saved results on init
   - May need to implement results loading function

4. Database verification:
   SELECT * FROM challenge_progress 
   WHERE challenge_type = 'linkup' 
   ORDER BY updated_at DESC;
```

---

### Issue 6: Wrong Difficulty/Category Saved

**Symptom:**
```
Complete "Foundation" → Database shows "easy" or wrong category
```

**Solution:**
```
1. Check difficulty mapping:
   const difficultyMap = {
       1: 'foundation',
       2: 'easy',
       3: 'intermediate',
       4: 'hard'
   };

2. Verify scenario.difficulty value:
   console.log('Scenario:', scenario);
   console.log('Difficulty:', scenario.difficulty);

3. Check which completion path triggered:
   - showResultsPopup() → Uses scenario.difficulty
   - completeActiveChallenge() → Uses challenge.level

4. Fix: Ensure scenario object has correct difficulty property
```

---

### Issue 7: Badges Not Awarded

**Symptom:**
```
Complete challenge → No badge notification
```

**Solution:**
```
1. Check if badge criteria met:
   - First Link Up: Complete first challenge
   - Score-based: Achieve required score
   - Check badge requirements

2. Verify BadgeService loaded:
   console.log(window.badgeService);

3. Check backend response:
   // Should include badges_earned array
   {
     status: "success",
     badges_earned: ["first_linkup"]
   }

4. Check badge notification display:
   // Look for badge popup/notification element
```

---

### Issue 8: Multiple Completions Not Tracked

**Symptom:**
```
Complete challenge twice → total_attempts still shows 1
```

**Solution:**
```
1. Check if backend increments attempts:
   SELECT total_attempts FROM challenge_score 
   WHERE user_id = YOUR_ID 
   AND challenge_type = 'troubleshooting';

2. Verify each completion triggers save:
   - Each save should increment attempts
   - Check console for multiple save messages

3. Backend logic verification:
   - Should UPSERT (update or insert)
   - Should increment total_attempts
   - Should update best_score if higher
```

---

### Issue 9: Time Not Tracked

**Symptom:**
```
Sidebar shows "Time Taken: N/A"
```

**Solution:**
```
1. Check if time_taken passed in data:
   console.log('Challenge data:', data);
   console.log('Time taken:', data.time_taken);

2. Verify timer running during challenge:
   // Should track start time and end time

3. Fix: Ensure data object includes time_taken:
   const timeTaken = Date.now() - startTime;
   data.time_taken = Math.floor(timeTaken / 1000);
```

---

### Issue 10: WebSocket Errors

**Symptom:**
```
❌ WebSocket connection failed
```

**Solution:**
```
1. WebSocket is optional:
   // Challenge save should work without it

2. Check if WebSocket needed:
   if (window.socketClient) {
       // Only sends if available
   }

3. Ignore WebSocket errors for MVP:
   // Core functionality doesn't require it
```

---

## 🔬 Advanced Debugging

### Enable Verbose Logging

Add to console:
```javascript
// Log all fetch requests
const originalFetch = window.fetch;
window.fetch = function(...args) {
    console.log('🌐 Fetch:', args[0], args[1]);
    return originalFetch.apply(this, args)
        .then(response => {
            console.log('✅ Response:', response.status);
            return response;
        })
        .catch(error => {
            console.error('❌ Fetch error:', error);
            throw error;
        });
};
```

### Check Database State

```javascript
// If you have database access console:
SELECT 
    cp.challenge_type,
    cp.state_data,
    cp.is_completed,
    cp.updated_at,
    cs.best_score,
    cs.total_attempts
FROM challenge_progress cp
LEFT JOIN challenge_score cs 
    ON cp.user_id = cs.user_id 
    AND cs.challenge_type = 'troubleshooting'
WHERE cp.challenge_type = 'linkup'
ORDER BY cp.updated_at DESC;
```

### Monitor Network Tab

```
1. Open DevTools (F12)
2. Click "Network" tab
3. Filter: XHR
4. Complete challenge
5. Look for:
   - POST /save_topology_score (Status: 200)
   - POST /api/challenge/save-progress (Status: 200)
6. Click request → Preview → Check response
```

---

## 🆘 Emergency Reset

If everything is broken:

```javascript
// 1. Clear all local/session storage
localStorage.clear();
sessionStorage.clear();

// 2. Hard refresh
// Windows: Ctrl+Shift+R
// Mac: Cmd+Shift+R

// 3. Clear browser cache
// Chrome: Settings → Privacy → Clear browsing data

// 4. Try incognito/private window
// To rule out cache issues

// 5. Check backend server
// Restart Flask server if needed
```

---

## 📞 Getting Help

### Information to Provide

When reporting issues, include:

```
1. Browser & Version:
   - Chrome 118, Firefox 119, etc.

2. Console Output:
   - Copy all messages (success and errors)

3. Network Tab:
   - Screenshot of failed requests (if any)

4. Steps to Reproduce:
   - Exactly what you did
   - Which challenge completed
   - What happened vs. what expected

5. Database State:
   - Row count in challenge_progress
   - Row count in challenge_score

6. Environment:
   - Local dev or production?
   - Database type (SQLite, PostgreSQL)?
```

---

## ✅ Health Check Script

Run this in console to verify system health:

```javascript
// Link Up Challenge Health Check
console.log('🔍 Running Link Up Challenge Health Check...\n');

// Check 1: Functions exist
console.log('1. Function Check:');
console.log('   showResultsPopup:', typeof showResultsPopup);
console.log('   saveTopologyScoreToBackend:', typeof saveTopologyScoreToBackend);

// Check 2: DOM elements exist
console.log('\n2. DOM Elements:');
const sidebar = document.getElementById('performance-sidebar');
const container = document.getElementById('results-container');
console.log('   Sidebar:', sidebar ? '✅' : '❌');
console.log('   Container:', container ? '✅' : '❌');

// Check 3: Session storage
console.log('\n3. Session Storage:');
const lastResult = sessionStorage.getItem('lastLinkUpResult');
console.log('   Last Result:', lastResult ? '✅ Exists' : '⚠️ Empty');

// Check 4: Network Level System
console.log('\n4. Network Level System:');
console.log('   Instance:', window.networkLevelSystem ? '✅' : '❌');

// Check 5: Badge Service
console.log('\n5. Badge Service:');
console.log('   Instance:', window.badgeService ? '✅' : '❌');

console.log('\n✅ Health Check Complete!');
console.log('If all show ✅, system is healthy.');
console.log('If any show ❌, that component needs attention.');
```

---

## 🎯 Final Checklist

Before reporting as "not working":

```
□ Browser console open (F12)
□ Completed a challenge
□ Checked for console messages
□ Checked sidebar for results
□ Tried refreshing browser
□ Cleared cache and retried
□ Checked in incognito mode
□ Verified backend server running
□ Checked database tables exist
□ Ran health check script
```

**All checked and still broken? → Time to debug deeper!**

---

**Most issues are simple fixes - don't panic! 🚀**
