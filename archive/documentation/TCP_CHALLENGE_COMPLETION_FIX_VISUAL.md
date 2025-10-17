# TCP/IP Challenge Completion Status - Visual Flow

## The Problem (Before Fix)

```
User completes Level 2 (TCP/IP) → Frontend saves score
     ↓
Frontend sends: { level: 2, level2_score: 100, both_levels_complete: false }
     ↓
Backend saves → Database: { level2_score: 100 }  ❌ MISSING level1_score!
     ↓
Page reloads → Backend checks: level2_score > 0? ✅ YES
     ↓
BUT... merged_challenge_data might not have level1_score preserved
     ↓
Result: Level 2 shows "Unlocked" instead of "Completed" 😢
```

## The Solution (After Fix)

```
User completes Level 2 (TCP/IP) → Frontend saves score
     ↓
Frontend sends: { level1_score: 100, level2_score: 100, both_levels_complete: false }
     ↓
Backend merges with existing data:
  - Fetches existing challenge_metadata
  - Merges: { level1_score: 100 } + { level2_score: 100 }
  - Result: { level1_score: 100, level2_score: 100 }
     ↓
Backend saves → Database: { level1_score: 100, level2_score: 100 } ✅
     ↓
Page reloads → Backend checks: level2_score (100) > 0? ✅ YES
     ↓
Result: Level 2 shows "Completed (100%)" 🎉
```

## Data Flow Comparison

### Before Fix
```
Save Level 1:
challenge_data: { level1_score: 100 }

Save Level 2:
challenge_data: { level2_score: 100 }  ❌ level1_score LOST!

Database state:
{ level2_score: 100 }  ❌ Incomplete
```

### After Fix
```
Save Level 1:
challenge_data: { level1_score: 100, level2_score: 0 }

Save Level 2:
challenge_data: { level1_score: 100, level2_score: 100 }  ✅ Both preserved!

Backend merges with existing:
existing: { level1_score: 100, level2_score: 0 }
+ new:    { level1_score: 100, level2_score: 100 }
= merged: { level1_score: 100, level2_score: 100 }  ✅

Database state:
{ level1_score: 100, level2_score: 100, both_levels_complete: true }  ✅
```

## UI State Machine

```
┌─────────────────┐
│  Initial Load   │
│ Level 1: Start  │
│ Level 2: Locked │
└────────┬────────┘
         │ Complete Level 1
         ↓
┌──────────────────────┐
│   After Level 1      │
│ Level 1: ✅ Complete │
│ Level 2: 🔓 Unlocked │
└──────────┬───────────┘
           │ Complete Level 2
           ↓
┌──────────────────────────┐
│    After Level 2         │
│ Level 1: ✅ Complete     │
│ Level 2: ✅ Complete ⭐  │ ← FIX: Now shows Completed!
│ Badge: 🏆 OSI & TCP/IP  │
└──────────────────────────┘
```

## Backend Logic

```python
# views.py - osi_simulation()
level_completion_data = {
    'level1_complete': challenge_data.get('level1_score', 0) > 0,
    'level2_complete': (level2_score_val > 0) or both_levels_complete,  # ← Key check
    'level1_score': challenge_data.get('level1_score', 0),
    'level2_score': level2_score_val,
    'combined_score': osi_challenge.best_score,
    'both_levels_complete': both_levels_complete
}
```

**The Fix**: Now `level2_score` is always included in saves, so `level2_score_val > 0` correctly evaluates to `True` after Level 2 completion!

## Frontend Logic

```javascript
// osi-simulation.html - saveLevelScoreAsync()
const challengeData = {
  level: level,
  level1_score: level === 1 ? levelScore : level1Score,  // ← Always include level1
  level2_score: level === 2 ? levelScore : 0,            // ← Set when level 2 done
  both_levels_complete: false
};
```

**The Fix**: Both scores are explicitly included in every save, preventing data loss during the Level 2 save operation.

## Success Criteria

✅ **Level 1 Complete**: Shows "Completed (100%)" + Unlocks Level 2
✅ **Level 2 Complete**: Shows "Completed (100%)" immediately after finish
✅ **Page Reload**: Both levels still show "Completed (100%)"
✅ **Database**: Contains both `level1_score` and `level2_score`
✅ **Badge Award**: "OSI & TCP/IP Master" badge is awarded
✅ **Persistence**: Completion status survives browser refresh
