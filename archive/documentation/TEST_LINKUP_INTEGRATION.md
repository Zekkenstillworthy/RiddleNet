# Test Guide: Link Up to Performance Sidebar Integration

## Quick Test (Browser Console)

Open the troubleshooting page at `http://127.0.0.1:5001/troubleshooting/` and run these commands in the browser console:

### Test 1: Start a Challenge
```javascript
// Click "Link Up!" button and select "Basic Network Connectivity"
// OR run this in console:
if (window.networkLevelSystem) {
    window.networkLevelSystem.startChallenge('basic-connectivity');
    console.log('✅ Challenge started! Check the performance sidebar.');
} else {
    console.error('❌ Network Level System not loaded');
}
```

**Expected Result:**
- Active Challenge section appears in performance sidebar
- Shows "Basic Network Connectivity"
- Shows "Level 1 ⭐"
- Shows "0 / 4 Steps"
- Shows "50 XP"
- Progress bar at 0%

---

### Test 2: Update Progress (Step by Step)
```javascript
// Step 1
window.updateChallengeProgress('basic-connectivity', 1, 4, 'Place 2 PCs');
console.log('Step 1 complete');

// Wait a moment, then Step 2
setTimeout(() => {
    window.updateChallengeProgress('basic-connectivity', 2, 4, 'Place 1 Switch');
    console.log('Step 2 complete');
}, 2000);

// Wait a moment, then Step 3
setTimeout(() => {
    window.updateChallengeProgress('basic-connectivity', 3, 4, 'Connect devices');
    console.log('Step 3 complete');
}, 4000);

// Wait a moment, then Step 4
setTimeout(() => {
    window.updateChallengeProgress('basic-connectivity', 4, 4, 'Configure IPs');
    console.log('Step 4 complete');
}, 6000);
```

**Expected Result:**
- Progress bar animates from 0% → 25% → 50% → 75% → 100%
- Steps counter updates: 0/4 → 1/4 → 2/4 → 3/4 → 4/4
- Success hints appear at step 2 and 4

---

### Test 3: Complete Challenge
```javascript
// Run after all steps are done
window.completeLinkUpChallenge('basic-connectivity', 'Basic Network Connectivity');
console.log('Challenge completed!');
```

**Expected Result:**
- XP notification appears: "+50 XP"
- Challenge completion notification shows
- Active Challenge section hides after 5 seconds
- XP counter in Network Engineer Level section increases

---

### Test 4: Complete Test Sequence (All at Once)
```javascript
// Full test sequence
(async function testLinkUpIntegration() {
    console.log('🧪 Starting Link Up Integration Test...');
    
    // 1. Start challenge
    console.log('📝 Step 1: Starting challenge...');
    window.networkLevelSystem.startChallenge('basic-connectivity');
    await new Promise(r => setTimeout(r, 2000));
    
    // 2. Progress through steps
    console.log('📝 Step 2: Progressing through challenge steps...');
    for (let step = 1; step <= 4; step++) {
        const stepNames = ['Place 2 PCs', 'Place 1 Switch', 'Connect devices', 'Configure IPs'];
        window.updateChallengeProgress('basic-connectivity', step, 4, stepNames[step - 1]);
        console.log(`   ✓ Step ${step}/4: ${stepNames[step - 1]}`);
        await new Promise(r => setTimeout(r, 1500));
    }
    
    // 3. Complete challenge
    console.log('📝 Step 3: Completing challenge...');
    await new Promise(r => setTimeout(r, 1000));
    window.completeLinkUpChallenge('basic-connectivity', 'Basic Network Connectivity');
    
    console.log('✅ Test complete! Check the performance sidebar and XP counter.');
})();
```

**Expected Result:**
- Challenge starts and appears in sidebar
- Progress animates through all 4 steps over ~8 seconds
- Challenge completes with XP award
- Sidebar section hides after 5 seconds
- Total test time: ~13 seconds

---

## Manual Testing Checklist

### Part 1: UI Elements
- [ ] Performance sidebar is visible on page load
- [ ] "Link Up!" button is present in device palette
- [ ] Clicking "Link Up!" opens the challenges modal
- [ ] Challenge cards are displayed in the modal
- [ ] Active Challenge section is hidden by default

### Part 2: Challenge Start
- [ ] Click on "Basic Network Connectivity" challenge card
- [ ] Modal closes automatically
- [ ] Active Challenge section appears in sidebar
- [ ] Challenge name is displayed correctly
- [ ] Difficulty badge shows "Level 1 ⭐"
- [ ] Steps counter shows "0 / 4 Steps"
- [ ] XP reward shows "50 XP"
- [ ] Progress bar is at 0%

### Part 3: Progress Updates
- [ ] Run progress update commands in console
- [ ] Progress bar animates smoothly
- [ ] Steps counter updates correctly
- [ ] Success hints appear at milestones (step 2, 4)
- [ ] No console errors appear

### Part 4: Challenge Completion
- [ ] Run completion command in console
- [ ] XP notification appears
- [ ] Challenge completion notification shows
- [ ] Progress bar reaches 100%
- [ ] Active Challenge section hides after 5 seconds
- [ ] XP counter in Network Engineer Level increases by 50

### Part 5: WebSocket Integration
- [ ] Open DevTools → Network → WS tab
- [ ] Start a challenge
- [ ] Verify `troubleshooting_progress` event is sent with `challenge_started`
- [ ] Update progress
- [ ] Verify `troubleshooting_progress` event is sent with step data
- [ ] Complete challenge
- [ ] Verify `troubleshooting_progress` event is sent with `challenge_completed`

---

## Test Different Challenges

### Test Router Setup Challenge (5 steps)
```javascript
window.networkLevelSystem.startChallenge('router-setup');
for (let i = 1; i <= 5; i++) {
    setTimeout(() => {
        window.updateChallengeProgress('router-setup', i, 5, `Step ${i}`);
    }, i * 2000);
}
setTimeout(() => {
    window.completeLinkUpChallenge('router-setup', 'First Router Configuration');
}, 12000);
```

### Test Network Quiz (separate page)
```javascript
// This redirects to /quiz page
// Testing in browser: Click on "Network Knowledge Quiz" card
```

---

## Common Issues & Solutions

### Issue: "window.networkLevelSystem is undefined"
**Solution:** Wait 1 second after page load, or check that JavaScript loaded correctly:
```javascript
setTimeout(() => {
    if (window.networkLevelSystem) {
        console.log('✅ System ready');
    } else {
        console.error('❌ System not initialized');
    }
}, 1000);
```

### Issue: Active Challenge section doesn't appear
**Solution:** Check that challenge exists and is unlocked:
```javascript
const challenge = window.networkLevelSystem.challenges.find(c => c.id === 'basic-connectivity');
console.log('Challenge:', challenge);
console.log('Unlocked:', challenge.unlocked);
```

### Issue: Progress doesn't update
**Solution:** Verify active challenge is set:
```javascript
console.log('Active Challenge:', window.networkLevelSystem.activeChallenge);
// Should show: { id: 'basic-connectivity', challenge: {...}, stepsCompleted: 0, ... }
```

### Issue: WebSocket events not sending
**Solution:** Check WebSocket connection:
```javascript
if (window.socketClient && window.socketClient.socket) {
    console.log('Socket connected:', window.socketClient.socket.connected);
} else {
    console.error('Socket client not available');
}
```

---

## Performance Testing

### Memory Leak Check
```javascript
// Start and complete multiple challenges rapidly
for (let i = 0; i < 10; i++) {
    setTimeout(() => {
        window.networkLevelSystem.startChallenge('basic-connectivity');
        setTimeout(() => {
            window.completeLinkUpChallenge('basic-connectivity', 'Test');
        }, 500);
    }, i * 1000);
}
// Monitor memory in DevTools Performance tab
```

### Animation Performance
```javascript
// Test rapid progress updates
for (let i = 0; i <= 100; i += 5) {
    setTimeout(() => {
        const step = Math.floor((i / 100) * 4) + 1;
        window.updateChallengeProgress('basic-connectivity', step, 4, `Step ${step}`);
    }, i * 50);
}
// Should animate smoothly without lag
```

---

## Browser Compatibility Test

Test in multiple browsers:
- [ ] Chrome/Edge (Latest)
- [ ] Firefox (Latest)
- [ ] Safari (if on Mac)

Check for:
- CSS animations working
- WebSocket connections stable
- No console errors
- Progress bar smooth transitions

---

## Success Criteria

✅ All tests pass without errors  
✅ UI updates are smooth and responsive  
✅ WebSocket events are sent correctly  
✅ XP is awarded properly  
✅ No memory leaks detected  
✅ Works in all major browsers  

---

## Automated Test Script

Save this as a bookmarklet or run directly:

```javascript
javascript:(function(){
    const test = async () => {
        console.clear();
        console.log('%c🧪 RiddleNet Link Up Integration Test', 'font-size:20px;color:#00D9FF;font-weight:bold');
        
        const tests = [
            { name: 'System Loaded', fn: () => !!window.networkLevelSystem },
            { name: 'Socket Available', fn: () => !!window.socketClient },
            { name: 'Challenge Exists', fn: () => {
                const c = window.networkLevelSystem.challenges.find(x => x.id === 'basic-connectivity');
                return c && c.unlocked;
            }},
            { name: 'Start Challenge', fn: () => {
                window.networkLevelSystem.startChallenge('basic-connectivity');
                return !!window.networkLevelSystem.activeChallenge;
            }},
            { name: 'Update Progress', fn: async () => {
                for(let i=1; i<=4; i++) {
                    window.updateChallengeProgress('basic-connectivity', i, 4, `Step ${i}`);
                    await new Promise(r => setTimeout(r, 500));
                }
                return true;
            }},
            { name: 'Complete Challenge', fn: () => {
                window.completeLinkUpChallenge('basic-connectivity', 'Test');
                return true;
            }}
        ];
        
        for (const t of tests) {
            try {
                const result = await t.fn();
                console.log(result ? `✅ ${t.name}` : `❌ ${t.name} FAILED`);
            } catch (e) {
                console.error(`❌ ${t.name} ERROR:`, e.message);
            }
            await new Promise(r => setTimeout(r, 1000));
        }
        
        console.log('%c🎉 Test Complete!', 'font-size:16px;color:#00ff00;font-weight:bold');
    };
    test();
})();
```

Copy and paste this into your browser console on the troubleshooting page to run all tests automatically!
