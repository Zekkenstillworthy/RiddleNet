# TCP/IP Challenge Completion Status Fix

## Problem
The TCP/IP challenge (Level 2) remained showing as "Unlocked" even after completion at 100%. The challenge completion status was not updating correctly to show "Completed" after finishing Level 2.

## Root Cause
1. **Frontend Issue**: When saving Level 2 score, the frontend was only sending `level2_score` in the challenge_data, without preserving the `level1_score` from the previous save.
2. **Backend Issue**: The backend wasn't merging the existing challenge_data properly before the fix, potentially losing Level 1 data when Level 2 was saved.

## Changes Made

### 1. Backend: `user/views.py` - `save_osi_score()` function
**File**: `c:\Users\gilbe\OneDrive\Desktop\RiddleNet\user\views.py`

#### Change A: Added Metadata Merging
```python
# Get existing challenge score to merge metadata
from user.models.challenge_score import ChallengeScore
existing_challenge = ChallengeScore.query.filter_by(
    user_id=user_id, 
    challenge_type='osi'
).first()

# Merge existing challenge_data with new data
merged_challenge_data = {}
if existing_challenge and existing_challenge.challenge_metadata:
    merged_challenge_data = existing_challenge.challenge_metadata.get('challenge_data', {}).copy()

# Update with new challenge data
if challenge_data:
    merged_challenge_data.update(challenge_data)
```

**Purpose**: Ensures that when Level 2 is saved, the Level 1 score is preserved in the merged data.

#### Change B: Added Debug Logging
```python
# Debug: Log saved challenge data
print(f"[OSI Score Save] User {user_id}:")
print(f"  Score: {score}")
print(f"  Challenge Data: {merged_challenge_data}")
print(f"  Skip Badge Check: {skip_badge_check}")
```

**Purpose**: Provides visibility into what data is being saved, helping with troubleshooting.

### 2. Frontend: `templates/user/osi-simulation.html` - `saveLevelScoreAsync()` function
**File**: `c:\Users\gilbe\OneDrive\Desktop\RiddleNet\templates\user\osi-simulation.html`

#### Change: Always Include Both Level Scores
```javascript
// Before (BROKEN):
const challengeData = {
  level: level,
  [`level${level}_score`]: levelScore,
  both_levels_complete: false
};

// After (FIXED):
const challengeData = {
  level: level,
  level1_score: level === 1 ? levelScore : level1Score, // Include both scores
  level2_score: level === 2 ? levelScore : 0, // Set level2_score when completing level 2
  both_levels_complete: false // MVP: Prevents badge award until final save
};
```

**Purpose**: Ensures both level1_score and level2_score are always present in the challenge_data when saving, preventing data loss.

#### Added Debug Logging
```javascript
console.log(`📊 Challenge Data: level1=${challengeData.level1_score}, level2=${challengeData.level2_score}`);
```

**Purpose**: Helps verify that both scores are being sent to the backend.

## How It Works Now

### Level 1 (OSI Model) Completion Flow:
1. User completes all 7 layers
2. Frontend calls `saveLevelScoreAsync(1, 100)`
3. Sends: `{ level1_score: 100, level2_score: 0, both_levels_complete: false }`
4. Backend saves with `skip_badge_check: true` (no badge yet)
5. Level 2 unlocks (shows "Unlocked!")

### Level 2 (TCP/IP Model) Completion Flow:
1. User completes all 4 layers
2. Frontend calls `saveLevelScoreAsync(2, 100)`
3. Sends: `{ level1_score: 100, level2_score: 100, both_levels_complete: false }`
4. Backend merges with existing data, saves both scores
5. UI immediately updates to show "Completed (100%)"
6. Frontend then calls `saveFinalChallengeScore(100)` with `both_levels_complete: true`
7. Backend awards badge (OSI & TCP/IP Master)

### Backend Completion Check (on page load):
```python
level2_complete = (level2_score > 0) or both_levels_complete
```

Now when the page reloads:
- If `level2_score > 0` in the database → Shows "Completed"
- If `both_levels_complete == true` → Shows "Completed"

## Testing Steps

1. **Start Fresh**: Clear any existing OSI challenge data for a test user
2. **Complete Level 1**: 
   - Arrange all 7 OSI layers correctly
   - Verify Level 1 shows "Completed (100%)"
   - Verify Level 2 shows "Unlocked!"
3. **Complete Level 2**:
   - Arrange all 4 TCP/IP layers correctly
   - Verify Level 2 immediately shows "Completed (100%)"
   - Verify badge is awarded
4. **Refresh Page**:
   - Navigate away and return to `/osi-simulation`
   - Verify Level 1 still shows "Completed (100%)"
   - Verify Level 2 still shows "Completed (100%)" ✅ **THIS IS THE FIX**
5. **Check Database**:
   - Verify `challenge_scores` table has entry with:
     - `challenge_type = 'osi'`
     - `best_score = 100`
     - `challenge_metadata.challenge_data.level1_score = 100`
     - `challenge_metadata.challenge_data.level2_score = 100`
     - `challenge_metadata.challenge_data.both_levels_complete = true`

## Console Log Verification

After completing Level 2, you should see:
```
💾 Saving Level 2 score first...
✅ Level 2 score saved: {status: 'success', ...}
📊 Challenge Data: level1=100, level2=100
🔄 Updating Level 2 UI status to Completed
✅ Level 2 UI updated to show completion
✅ Level 2 saved, now saving final combined score...
[OSI Score Save] User 1:
  Score: 100
  Challenge Data: {'level1_score': 100, 'level2_score': 100, 'both_levels_complete': False}
  Skip Badge Check: False
[OSI Score Save] User 1:
  Score: 100
  Challenge Data: {'level1_score': 100, 'level2_score': 100, 'combined_score': 100, 'both_levels_complete': True}
  Skip Badge Check: False
🎉 Challenge complete! Badge earned: OSI & TCP/IP Master
```

## Files Modified
1. `c:\Users\gilbe\OneDrive\Desktop\RiddleNet\user\views.py` (Backend)
2. `c:\Users\gilbe\OneDrive\Desktop\RiddleNet\templates\user\osi-simulation.html` (Frontend)

## Related Code
- `user/models/challenge_score.py` - Already had deep merge logic in `record_attempt()`
- `user/services/badge_service.py` - Badge awarding logic (unchanged)

## Result
✅ TCP/IP challenge now correctly shows "Completed (100%)" status after completion
✅ Status persists after page reload
✅ Both level scores are preserved in the database
✅ Badge is correctly awarded after both levels complete
