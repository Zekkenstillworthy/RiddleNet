# Link Up Popup to Live Performance Sidebar Integration

## Overview
This document describes how the Link Up Popup (Network Challenges) is connected to the Live Performance sidebar (`id="performance-sidebar"`) on the troubleshooting page.

## Implementation Summary

### 1. New UI Component - Active Challenge Section
Added a new section to the performance sidebar that displays:
- **Challenge Name**: The title of the currently active challenge
- **Difficulty Badge**: Visual indicator showing the challenge level and difficulty stars
- **Progress Bar**: Animated progress bar showing completion percentage
- **Steps Counter**: Shows current step vs. total steps (e.g., "3 / 5 Steps")
- **XP Reward**: Displays the XP that will be earned upon completion

**Location**: `templates/user/troubleshoot.html`
- Positioned between the "Network Engineer Level" section and the "Progress" section
- Hidden by default (`display: none`) until a challenge is started

### 2. Challenge Tracking System

#### When a Challenge Starts:
1. User clicks on a challenge card in the Link Up modal
2. `NetworkLevelSystem.startChallenge(challengeId)` is called
3. The sidebar's active challenge section is shown and populated with:
   - Challenge name and difficulty
   - Total steps from challenge definition
   - XP reward information
4. Progress bar is reset to 0%
5. WebSocket event is emitted: `troubleshooting_progress` with event type `challenge_started`

#### During Challenge Progress:
Progress can be updated in two ways:

**Method 1: WebSocket Events (Real-time)**
```javascript
// Backend emits troubleshooting_progress event
{
    challenge_id: 'basic-connectivity',
    current_step: 2,
    total_steps: 4,
    progress_percentage: 50,
    step_completed: true,
    step_name: 'Connect devices'
}
```
The frontend listens and automatically updates the sidebar.

**Method 2: Manual JavaScript API**
```javascript
// Call from anywhere in your code
window.updateChallengeProgress(
    'basic-connectivity',  // challengeId
    2,                      // currentStep
    4,                      // totalSteps
    'Connect devices'       // stepName (optional)
);
```

#### When a Challenge Completes:
1. Progress reaches 100% or `completeActiveChallenge()` is called
2. XP is awarded to the user
3. Achievement notifications are shown
4. The active challenge section is hidden after 5 seconds
5. WebSocket event is emitted with event type `challenge_completed`

### 3. Challenge Definitions
Each challenge now includes a `steps` property that defines the total number of steps:

```javascript
{
    id: "basic-connectivity",
    title: "Basic Network Connectivity",
    level: 1,
    difficulty: 1,
    xp: 50,
    steps: 4,  // NEW: Total number of steps in this challenge
    description: "...",
    requirements: [...],
    unlocked: true,
    badge: "🌐"
}
```

Current challenge steps:
- **basic-connectivity**: 4 steps
- **router-setup**: 5 steps
- **rip-protocol**: 6 steps
- **vlan-basics**: 7 steps
- **ospf-config**: 8 steps
- **network-troubleshooting**: 10 steps

### 4. Integration Points

#### From Link Up Popup to Sidebar:
When user clicks a challenge card:
```javascript
NetworkLevelSystem.startChallenge(challengeId)
  └─> updateActiveChallengeInSidebar(challenge)
      └─> Shows sidebar section
      └─> Populates challenge info
      └─> Resets progress to 0%
```

#### From WebSocket to Sidebar:
Server sends progress updates:
```javascript
socket.on('troubleshooting_progress', function(data) {
    NetworkLevelSystem.updateChallengeProgress(
        data.current_step,
        data.total_steps,
        data.progress_percentage
    );
});
```

#### From Your Code to Sidebar:
Manual progress updates:
```javascript
// Simple API for updating progress
window.updateChallengeProgress(challengeId, step, total, stepName);

// Complete the challenge
window.completeLinkUpChallenge(challengeId, challengeName);
```

### 5. CSS Styling
New styles added for the active challenge section:
- `.active-challenge-container`: Main container with cyber-themed styling
- `.challenge-header-info`: Header with challenge name and difficulty
- `.challenge-difficulty-badge`: Animated badge showing level
- `.challenge-progress-bar`: Animated progress bar with gradient fill
- `.challenge-stats`: Statistics display (steps and XP)

Colors match the existing cyber theme:
- Primary: `#00D9FF` (cyber glow)
- Background: `rgba(0, 217, 255, 0.05)`
- Border: `rgba(0, 217, 255, 0.2)`

### 6. WebSocket Events

#### Client → Server Events:
```javascript
// Challenge started
{
    event: 'troubleshooting_progress',
    data: {
        challenge_id: 'basic-connectivity',
        challenge_name: 'Basic Network Connectivity',
        current_step: 0,
        total_steps: 4,
        progress_percentage: 0,
        event: 'challenge_started'
    }
}

// Progress update
{
    event: 'troubleshooting_progress',
    data: {
        challenge_id: 'basic-connectivity',
        current_step: 2,
        total_steps: 4,
        progress_percentage: 50,
        step_completed: true,
        step_number: 2,
        step_name: 'Connect devices',
        event: 'progress_update'
    }
}

// Challenge completed
{
    event: 'troubleshooting_progress',
    data: {
        challenge_id: 'basic-connectivity',
        challenge_name: 'Basic Network Connectivity',
        progress_percentage: 100,
        time_taken: 245,  // seconds
        event: 'challenge_completed'
    }
}
```

#### Server → Client Events:
The server should handle `troubleshooting_progress` socket events in `socket_events.py`:
```python
@socketio.on('troubleshooting_progress')
@authenticated_only
def handle_troubleshooting_progress(data):
    # Process the progress data
    # Broadcast to other participants if needed
    emit('user_troubleshooting_progress', {
        'user_id': current_user.id,
        'username': current_user.username,
        **data
    }, room=f"troubleshooting_{data['challenge_id']}")
```

## Usage Examples

### Example 1: Start a Challenge
```javascript
// User clicks on "Basic Network Connectivity" in Link Up popup
// This is automatically handled when clicking challenge cards
```

### Example 2: Update Progress Manually
```javascript
// When user completes a step in your challenge logic
function onDeviceConnected() {
    window.updateChallengeProgress(
        'basic-connectivity',  // challenge ID
        2,                      // completed 2 steps
        4,                      // out of 4 total
        'Connect devices'       // step name
    );
}
```

### Example 3: Complete a Challenge
```javascript
// When user finishes all requirements
function onChallengeSuccess() {
    window.completeLinkUpChallenge(
        'basic-connectivity',
        'Basic Network Connectivity'
    );
}
```

### Example 4: Listen for Progress Events
```javascript
// The system automatically listens, but you can add custom handlers
if (window.socketClient) {
    window.socketClient.on('troubleshooting_progress', function(data) {
        console.log('Challenge progress:', data);
        // Your custom logic here
    });
}
```

## Testing Instructions

1. **Open the troubleshooting page**: Navigate to `http://127.0.0.1:5001/troubleshooting/`

2. **Open the Link Up popup**: Click the "Link Up!" button in the device palette

3. **Start a challenge**: Click on "Basic Network Connectivity" card

4. **Verify sidebar update**:
   - Active Challenge section should appear in the performance sidebar
   - Should show: "Basic Network Connectivity", Level 1, 0/4 Steps, 50 XP

5. **Test manual progress update** (in browser console):
   ```javascript
   window.updateChallengeProgress('basic-connectivity', 1, 4, 'Place 2 PCs');
   // Should update to 1/4 steps, 25% progress bar
   
   window.updateChallengeProgress('basic-connectivity', 2, 4, 'Place Switch');
   // Should update to 2/4 steps, 50% progress bar
   
   window.updateChallengeProgress('basic-connectivity', 3, 4, 'Connect devices');
   // Should update to 3/4 steps, 75% progress bar
   
   window.updateChallengeProgress('basic-connectivity', 4, 4, 'Configure IPs');
   // Should update to 4/4 steps, 100% progress bar
   ```

6. **Test challenge completion** (in browser console):
   ```javascript
   window.completeLinkUpChallenge('basic-connectivity', 'Basic Network Connectivity');
   // Should award 50 XP, show completion notification, hide section after 5 seconds
   ```

7. **Check WebSocket integration**:
   - Open browser DevTools → Network → WS
   - Watch for `troubleshooting_progress` events being sent
   - Verify events include challenge_id, steps, and progress data

## Files Modified

1. **templates/user/troubleshoot.html**:
   - Added HTML for active challenge section (~30 lines)
   - Added CSS styles for challenge tracking (~70 lines)
   - Modified `NetworkLevelSystem.startChallenge()` method
   - Added `updateActiveChallengeInSidebar()` method
   - Added `updateChallengeProgress()` method
   - Added `completeActiveChallenge()` method
   - Modified WebSocket event handler for `troubleshooting_progress`
   - Added global helper functions: `window.updateChallengeProgress()`, `window.completeLinkUpChallenge()`
   - Updated challenge definitions to include `steps` property

2. **socket_events.py** (already configured):
   - Handler for `troubleshooting_progress` event exists at line 472
   - Broadcasts progress to troubleshooting room

## Future Enhancements

1. **Auto-detection**: Automatically detect when challenge requirements are met
2. **Step validation**: Server-side validation of step completion
3. **Multiplayer progress**: Show other users' progress on same challenge
4. **Challenge hints**: Display hints in sidebar based on current step
5. **Time tracking**: Show elapsed time for current challenge
6. **Leaderboard**: Display fastest completion times
7. **Challenge replay**: Allow users to retry completed challenges
8. **Achievement badges**: Visual badges for challenge milestones

## Troubleshooting

### Challenge section not showing:
- Check that `window.networkLevelSystem` is initialized
- Verify challenge ID exists in the challenges array
- Check browser console for errors

### Progress not updating:
- Verify WebSocket connection is active
- Check that `window.socketClient` exists
- Ensure challenge was started before updating progress

### XP not awarded on completion:
- Verify `completeActiveChallenge()` is being called
- Check that challenge hasn't already been completed
- Look for errors in `NetworkLevelSystem.completeChallenge()`

## Support
For issues or questions, check:
- Browser console for errors
- WebSocket tab in DevTools
- Server logs for socket event handling
