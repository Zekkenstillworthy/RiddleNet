# Badge Sub-Item Completion Fix

## Problem Statement

**Current Issue**: Badges are awarded when completing a single challenge at any difficulty level, not after completing ALL sub-items.

**User Requirement**:
- Progress should be: `Progress = (CompletedItems / TotalItems) * 100`
- Badges should be earned ONLY when: `CompletedItems == TotalItems`

**Example**: Link Up! challenge has 9 sub-challenges:
- **Easy (Foundation)**: vlan-basics, default-gateway, dhcp-client
- **Medium (Intermediate)**: extended-ring-redundancy, hybrid-star-ring, partial-mesh-ospf
- **Hard (Advanced)**: mpls-vpn-complex, datacenter-fabric, sd-wan-overlay

Currently, badge is awarded after completing just ONE challenge. It should only be awarded after completing ALL 9.

---

## Current Challenge Structure

### 1. **Crimping Simulation**
- **Type**: `crimping`
- **Sub-items**: None (single challenge)
- **Badge**: `cable_master` (awarded at 100%)
- **Status**: ✅ Already correct

### 2. **OSI Model TCP/IP**
- **Type**: `osi`
- **Sub-items**: 
  - Level 1 (OSI Model)
  - Level 2 (TCP/IP)
- **Badge**: `osi_tcp_master` (awarded when BOTH levels at 100%)
- **Status**: ✅ Already correct (validates both levels)

### 3. **Link Up! (Troubleshooting)**
- **Type**: `troubleshooting` (stored as `linkup_easy`, `troubleshooting_medium`, `troubleshooting_hard`)
- **Sub-items**: 
  - **Easy**: vlan-basics, default-gateway, dhcp-client (3 challenges)
  - **Medium**: extended-ring-redundancy, hybrid-star-ring, partial-mesh-ospf (3 challenges)
  - **Hard**: mpls-vpn-complex, datacenter-fabric, sd-wan-overlay (3 challenges)
- **Badge**: `troubleshooting_pro` 
- **Current Logic**: ❌ Awarded after completing ANY single challenge at 100%
- **Required Logic**: ✅ Should be awarded after completing ALL 9 challenges

### 4. **Quiz Challenge**
- **Type**: `quiz`
- **Sub-items**: None (single challenge)
- **Badge**: `quiz_champion` (awarded at 100%)
- **Status**: ✅ Already correct

---

## Solution Design

### Phase 1: Track Sub-Item Completion

**Goal**: Track which specific sub-challenges have been completed for Link Up!

**Approach**: Use the `metadata` field in `ChallengeScore` to track completed sub-items.

**Database Schema (no migration needed)**:
```python
ChallengeScore:
  - challenge_type: 'troubleshooting' (normalized from linkup_easy, troubleshooting_medium, troubleshooting_hard)
  - metadata: {
      'completed_challenges': [
        'vlan-basics',
        'default-gateway',
        'dhcp-client',
        'extended-ring-redundancy',
        ...
      ],
      'challenge_counts': {
        'easy': 3,  # Number of easy challenges completed
        'medium': 2,  # Number of medium challenges completed  
        'hard': 1    # Number of hard challenges completed
      }
    }
```

### Phase 2: Update Badge Logic

**Current**: Badge awarded when ANY single challenge at 100%
```python
if score == 100:
    award_badge('troubleshooting_pro')
```

**New**: Badge awarded when ALL 9 challenges completed
```python
completed_challenges = metadata.get('completed_challenges', [])
TOTAL_REQUIRED = 9

if len(completed_challenges) == TOTAL_REQUIRED:
    award_badge('troubleshooting_pro')
```

### Phase 3: Update Progress Calculation

**Current**: Progress shows best score from single challenge (0-100%)

**New**: Progress shows completion ratio
```python
Progress = (CompletedItems / TotalItems) * 100
Progress = (len(completed_challenges) / 9) * 100

# Examples:
# 0 challenges complete → 0%
# 3 challenges complete → 33.3%
# 6 challenges complete → 66.7%
# 9 challenges complete → 100%
```

### Phase 4: Update Dashboard Display

**Current**: Shows best score percentage

**New**: Shows completion progress
```html
<div class="challenge-progress">
  <p>Link Up!: {{ troubleshooting_completed }}/{{ troubleshooting_total }} challenges</p>
  <p>Progress: {{ troubleshooting_progress }}%</p>
</div>
```

---

## Implementation Plan

### Step 1: Update `troubleshooting_controller.py`
**File**: `user/controllers/troubleshooting_controller.py`

**Modify**: `_submit_hardcoded_challenge()` method

**Changes**:
1. When saving score, track the scenario_id in metadata
2. Retrieve all previous challenge scores for this user
3. Build a list of completed challenges
4. Store in metadata: `completed_challenges` and `challenge_counts`

```python
# Get all previous troubleshooting scores for this user
all_troubleshooting_scores = ChallengeScore.query.filter_by(
    user_id=user_id
).filter(
    ChallengeScore.challenge_type.in_(['linkup_easy', 'troubleshooting_medium', 'troubleshooting_hard'])
).all()

# Extract completed scenarios (those with 100% score)
completed_scenarios = set()
for score_record in all_troubleshooting_scores:
    if score_record.score >= 100:
        scenario = score_record.metadata.get('scenario_id')
        if scenario:
            completed_scenarios.add(scenario)

# Add current scenario if 100%
if match_percentage >= 100:
    completed_scenarios.add(scenario_id)

# Count by difficulty
easy_count = sum(1 for s in completed_scenarios if s in ['vlan-basics', 'default-gateway', 'dhcp-client'])
medium_count = sum(1 for s in completed_scenarios if s in ['extended-ring-redundancy', 'hybrid-star-ring', 'partial-mesh-ospf'])
hard_count = sum(1 for s in completed_scenarios if s in ['mpls-vpn-complex', 'datacenter-fabric', 'sd-wan-overlay'])

# Store in metadata
metadata = {
    'scenario_id': scenario_id,
    'scenario_name': challenge_info['name'],
    'time_taken': time_taken,
    'difficulty': challenge_info['difficulty'],
    'completed_challenges': list(completed_scenarios),
    'challenge_counts': {
        'easy': easy_count,
        'medium': medium_count,
        'hard': hard_count,
        'total': len(completed_scenarios)
    }
}
```

### Step 2: Update `badge_service.py`
**File**: `user/services/badge_service.py`

**Modify**: `_check_troubleshooting_badges()` method

**Changes**:
1. Check metadata for completed_challenges list
2. Award badge ONLY if all 9 challenges completed

```python
@staticmethod
def _check_troubleshooting_badges(user_id, score, metadata):
    """Check and award troubleshooting-related badges - ONE badge per challenge"""
    badges = []
    
    # Get completed challenges from metadata
    completed_challenges = metadata.get('completed_challenges', []) if metadata else []
    TOTAL_REQUIRED = 9  # 3 easy + 3 medium + 3 hard
    
    print(f"[BADGE SERVICE] Troubleshooting Badge Check")
    print(f"  Completed challenges: {len(completed_challenges)}/{TOTAL_REQUIRED}")
    print(f"  List: {completed_challenges}")
    
    # Award badge ONLY when ALL 9 challenges are completed
    if len(completed_challenges) >= TOTAL_REQUIRED:
        print(f"[BADGE SERVICE] ✅ All {TOTAL_REQUIRED} challenges complete - awarding badge!")
        
        badge, is_new = UserBadge.award_badge(
            user_id=user_id,
            badge_id='troubleshooting_pro',
            badge_name='Troubleshooting Pro',
            badge_description='Completed all Link Up challenges!',
            challenge_type='troubleshooting',
            earned_score=100.0,  # Badge represents 100% completion
            badge_rarity='legendary',
            metadata={
                'completed_challenges': completed_challenges,
                'total_challenges': TOTAL_REQUIRED
            }
        )
        
        if is_new:
            print(f"[BADGE SERVICE] 🎉 NEW BADGE AWARDED: Troubleshooting Pro")
            badges.append(badge.to_dict())
        else:
            print(f"[BADGE SERVICE] ℹ️ Badge already exists: Troubleshooting Pro")
    else:
        print(f"[BADGE SERVICE] ❌ Only {len(completed_challenges)}/{TOTAL_REQUIRED} complete - No badge yet")
        print(f"[BADGE SERVICE] Still need: {TOTAL_REQUIRED - len(completed_challenges)} more challenges")
    
    return badges
```

### Step 3: Update `challenge_score.py`
**File**: `user/models/challenge_score.py`

**Add New Method**: `get_troubleshooting_progress()`

```python
@staticmethod
def get_troubleshooting_progress(user_id):
    """
    Get Link Up! challenge progress with sub-item tracking
    
    Returns:
        {
            'completed_challenges': [...],  # List of completed scenario IDs
            'challenge_counts': {
                'easy': 2,
                'medium': 1,
                'hard': 0,
                'total': 3
            },
            'progress_percentage': 33.3,  # (3/9) * 100
            'is_complete': False
        }
    """
    # Get the latest troubleshooting challenge score
    challenge = ChallengeScore.query.filter_by(
        user_id=user_id,
        challenge_type='troubleshooting'
    ).order_by(ChallengeScore.updated_at.desc()).first()
    
    if not challenge or not challenge.metadata:
        return {
            'completed_challenges': [],
            'challenge_counts': {'easy': 0, 'medium': 0, 'hard': 0, 'total': 0},
            'progress_percentage': 0.0,
            'is_complete': False
        }
    
    completed_challenges = challenge.metadata.get('completed_challenges', [])
    challenge_counts = challenge.metadata.get('challenge_counts', {})
    
    TOTAL_REQUIRED = 9
    total_completed = len(completed_challenges)
    progress_percentage = (total_completed / TOTAL_REQUIRED) * 100.0
    
    return {
        'completed_challenges': completed_challenges,
        'challenge_counts': challenge_counts,
        'progress_percentage': round(progress_percentage, 1),
        'is_complete': total_completed >= TOTAL_REQUIRED
    }
```

**Modify**: `effective_best_score()` for troubleshooting

```python
@staticmethod
def effective_best_score(challenge_score):
    """
    Calculate the effective best score for UI display
    
    For troubleshooting challenges, returns progress percentage (CompletedItems/TotalItems)*100
    For other challenges, returns the stored best_score
    """
    if not challenge_score:
        return 0.0
    
    # Special handling for troubleshooting (Link Up!)
    if challenge_score.challenge_type == 'troubleshooting':
        completed_challenges = challenge_score.metadata.get('completed_challenges', []) if challenge_score.metadata else []
        TOTAL_REQUIRED = 9
        progress_percentage = (len(completed_challenges) / TOTAL_REQUIRED) * 100.0
        return round(progress_percentage, 1)
    
    # Special handling for OSI challenge (two levels)
    elif challenge_score.challenge_type == 'osi':
        # ... existing OSI logic ...
    
    # For all other challenges (crimping, quiz)
    return float(challenge_score.best_score or 0.0)
```

### Step 4: Update `views.py` Dashboard
**File**: `user/views.py`

**Changes**:
1. Get troubleshooting progress with sub-item tracking
2. Pass to template

```python
# Get troubleshooting progress with sub-item tracking
troubleshooting_progress = ChallengeScore.get_troubleshooting_progress(user.id)

# Pass to template
return render_template(
    'user/dashboard.html',
    # ... existing variables ...
    troubleshooting_progress=troubleshooting_progress,
    troubleshooting_completed=troubleshooting_progress['challenge_counts']['total'],
    troubleshooting_total=9,
    # ... rest ...
)
```

### Step 5: Update Dashboard Template
**File**: `templates/user/dashboard.html`

**Find**: Link Up! challenge card
**Update**: Show sub-item progress

```html
<div class="card challenge-card">
  <h3>🔗 Link Up!</h3>
  <div class="challenge-progress">
    <p>Completed: {{ troubleshooting_completed }}/{{ troubleshooting_total }} challenges</p>
    <p>Progress: {{ troubleshooting_progress.progress_percentage }}%</p>
    
    <div class="difficulty-breakdown">
      <span class="easy">Easy: {{ troubleshooting_progress.challenge_counts.easy }}/3</span>
      <span class="medium">Medium: {{ troubleshooting_progress.challenge_counts.medium }}/3</span>
      <span class="hard">Hard: {{ troubleshooting_progress.challenge_counts.hard }}/3</span>
    </div>
  </div>
</div>
```

---

## Testing Plan

### Test Case 1: No Challenges Completed
- **Action**: New user, no challenges attempted
- **Expected**: Progress = 0%, No badge

### Test Case 2: Partial Completion (3/9)
- **Action**: Complete 3 easy challenges at 100%
- **Expected**: Progress = 33.3%, No badge

### Test Case 3: Partial Completion (6/9)
- **Action**: Complete 3 easy + 3 medium challenges at 100%
- **Expected**: Progress = 66.7%, No badge

### Test Case 4: All Challenges Complete (9/9)
- **Action**: Complete all 9 challenges at 100%
- **Expected**: Progress = 100%, Badge awarded

### Test Case 5: Badge Validation on Dashboard
- **Action**: User with partial completion should NOT see badge
- **Expected**: Badge filtered out in dashboard validation

---

## Database Migration

**Required**: ❌ None (using existing `metadata` JSONB field)

**Optional**: Cleanup script to recalculate progress for existing users

```python
# cleanup_troubleshooting_progress.py
from user.models.challenge_score import ChallengeScore
from __init__ import db, create_app

app = create_app()
with app.app_context():
    # Get all troubleshooting challenge scores
    all_scores = ChallengeScore.query.filter(
        ChallengeScore.challenge_type.in_(['linkup_easy', 'troubleshooting_medium', 'troubleshooting_hard'])
    ).all()
    
    # Group by user
    user_challenges = {}
    for score in all_scores:
        user_id = score.user_id
        if user_id not in user_challenges:
            user_challenges[user_id] = []
        user_challenges[user_id].append(score)
    
    # Recalculate for each user
    for user_id, scores in user_challenges.items():
        completed_scenarios = set()
        for score_record in scores:
            if score_record.score >= 100:
                scenario = score_record.metadata.get('scenario_id') if score_record.metadata else None
                if scenario:
                    completed_scenarios.add(scenario)
        
        # Update the latest score record for this user
        latest_score = scores[-1]  # Assuming sorted by date
        latest_score.metadata = latest_score.metadata or {}
        latest_score.metadata['completed_challenges'] = list(completed_scenarios)
        latest_score.metadata['challenge_counts'] = {
            'easy': sum(1 for s in completed_scenarios if s in ['vlan-basics', 'default-gateway', 'dhcp-client']),
            'medium': sum(1 for s in completed_scenarios if s in ['extended-ring-redundancy', 'hybrid-star-ring', 'partial-mesh-ospf']),
            'hard': sum(1 for s in completed_scenarios if s in ['mpls-vpn-complex', 'datacenter-fabric', 'sd-wan-overlay']),
            'total': len(completed_scenarios)
        }
        
        print(f"Updated user {user_id}: {len(completed_scenarios)} challenges completed")
    
    db.session.commit()
    print("✅ Progress recalculation complete!")
```

---

## Deployment Steps

1. **Backup Database**: `pg_dump riddlenet > backup_$(date +%Y%m%d).sql`

2. **Apply Code Changes**:
   - Update `troubleshooting_controller.py`
   - Update `badge_service.py`
   - Update `challenge_score.py`
   - Update `views.py`
   - Update `dashboard.html`

3. **Run Progress Recalculation**: `python cleanup_troubleshooting_progress.py`

4. **Restart Application**: `sudo systemctl restart riddlenet`

5. **Test**: 
   - Check dashboard shows correct progress
   - Complete a challenge and verify progress updates
   - Verify badge only awarded after 9/9 complete

---

## Summary

**Key Changes**:
1. ✅ Track completed sub-challenges in metadata
2. ✅ Award badges ONLY when all sub-items complete
3. ✅ Progress calculation: `(CompletedItems / TotalItems) * 100`
4. ✅ Dashboard shows accurate sub-item progress

**Affected Files**:
- `user/controllers/troubleshooting_controller.py`
- `user/services/badge_service.py`
- `user/models/challenge_score.py`
- `user/views.py`
- `templates/user/dashboard.html`
- New: `cleanup_troubleshooting_progress.py`

**Impact**:
- Crimping: No change (single challenge)
- OSI: No change (already validates both levels)
- Link Up!: **Major change** (now requires all 9 challenges)
- Quiz: No change (single challenge)
