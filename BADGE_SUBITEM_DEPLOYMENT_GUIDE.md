# Badge Sub-Item Completion Fix - Deployment Guide

## Overview

This deployment fixes the badge awarding logic to require completion of ALL sub-challenges before awarding badges, implementing the requirement:

> **Progress = (CompletedItems / TotalItems) * 100**  
> **Badges = Earned only when CompletedItems == TotalItems**

## What Changed?

### Before (OLD System)
- ❌ Badge awarded after completing **ANY single** challenge at 100%
- ❌ User could get "Troubleshooting Pro" badge by completing just one easy challenge
- ❌ Progress didn't track individual sub-challenges

### After (NEW System)
- ✅ Badge awarded only after completing **ALL 9** challenges at 100%
- ✅ User must complete 3 easy + 3 medium + 3 hard challenges
- ✅ Progress tracked as: (CompletedItems / TotalItems) * 100
- ✅ Sub-item progress visible: "Easy: 2/3, Medium: 1/3, Hard: 0/3"

## Sub-Challenge Structure

### Link Up! Challenge (Troubleshooting)

**Easy (Foundation - 3 challenges)**:
1. VLAN Setup Basics
2. Default Gateway Configuration
3. DHCP Client Configuration

**Medium (Intermediate - 3 challenges)**:
4. Extended Ring with Redundancy
5. Hybrid Star-Ring Topology
6. Partial Mesh OSPF Network

**Hard (Advanced - 3 challenges)**:
7. MPLS VPN Route Leaking
8. Data Center Spine-Leaf VXLAN
9. SD-WAN Overlay Issues

**Badge Requirement**: Complete ALL 9 challenges at 100% to earn "Troubleshooting Pro" badge

## Files Modified

### 1. `user/controllers/troubleshooting_controller.py`
**Changes**: Added sub-item completion tracking in `_submit_hardcoded_challenge()`

**What it does**:
- Queries all previous troubleshooting challenges for the user
- Identifies which challenges have been completed at 100%
- Stores list of completed challenges in metadata
- Calculates progress by difficulty (easy/medium/hard)

### 2. `user/services/badge_service.py`
**Changes**: Updated `_check_troubleshooting_badges()` to require all 9 challenges

**What it does**:
- Reads completed_challenges from metadata
- Awards badge ONLY if all 9 challenges completed
- Shows detailed progress in console logs

### 3. `user/models/challenge_score.py`
**Changes**: Added `get_troubleshooting_progress()` method

**What it does**:
- Returns progress summary: completed challenges, counts by difficulty, progress percentage
- Used by dashboard to display accurate progress

### 4. New Files Created

**`cleanup_troubleshooting_progress.py`**:
- Recalculates progress for existing users
- Updates metadata with completed challenge tracking

**`cleanup_invalid_troubleshooting_badges.py`**:
- Removes badges from users who haven't completed all 9 challenges
- Supports `--dry-run` mode for testing

**`BADGE_SUB_ITEM_COMPLETION_FIX.md`**:
- Complete design documentation
- Testing plan
- Implementation details

---

## Pre-Deployment Checklist

### 1. Backup Database
```bash
# SSH into production server
ssh -i riddlenetv1.pem ubuntu@54.66.229.118

# Create backup
pg_dump riddlenet > backup_badge_fix_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backup_*.sql
```

### 2. Verify Code Changes
```bash
# Check that files have been modified
cd /home/ubuntu/RiddleNet
git status
git diff HEAD user/controllers/troubleshooting_controller.py
git diff HEAD user/services/badge_service.py
git diff HEAD user/models/challenge_score.py
```

### 3. Review Current Badge Status
```bash
# Count troubleshooting badges in database
psql riddlenet -c "SELECT COUNT(*) FROM user_badges WHERE challenge_type = 'troubleshooting';"

# See which users have badges
psql riddlenet -c "SELECT u.username, ub.badge_id, ub.badge_name, ub.earned_at FROM user_badges ub JOIN \"user\" u ON ub.user_id = u.id WHERE ub.challenge_type = 'troubleshooting' ORDER BY ub.earned_at DESC;"
```

---

## Deployment Steps

### Step 1: Stop Application
```bash
sudo systemctl stop riddlenet
```

### Step 2: Pull Latest Code
```bash
cd /home/ubuntu/RiddleNet
git pull origin main  # or your branch name
```

### Step 3: Verify Files
```bash
# Check that new files exist
ls -la cleanup_troubleshooting_progress.py
ls -la cleanup_invalid_troubleshooting_badges.py
ls -la BADGE_SUB_ITEM_COMPLETION_FIX.md

# Verify code changes
grep -A 20 "Track sub-item completion" user/controllers/troubleshooting_controller.py
grep -A 20 "CompletedItems == TotalItems" user/services/badge_service.py
```

### Step 4: Recalculate Progress for Existing Users
```bash
# Run progress recalculation script
source .venv/bin/activate  # Activate virtual environment
python cleanup_troubleshooting_progress.py
```

**Expected Output**:
```
================================================================================
Troubleshooting Progress Recalculation Script
================================================================================

✅ Found 15 troubleshooting challenge records

📊 Processing 5 users...

────────────────────────────────────────────────────────────────────────────────
👤 User ID: 1
────────────────────────────────────────────────────────────────────────────────
  Challenge: linkup_easy | Score: 100.0%
    ✅ Completed: vlan-basics (normalized: vlan-basics)
  Challenge: linkup_easy | Score: 100.0%
    ✅ Completed: default-gateway (normalized: default-gateway)
  Challenge: troubleshooting_medium | Score: 100.0%
    ✅ Completed: extended-ring-redundancy (normalized: extended-ring-redundancy)

  📈 Progress Summary:
    Easy: 2/3 - ['vlan-basics', 'default-gateway']
    Medium: 1/3 - ['extended-ring-redundancy']
    Hard: 0/3 - []
    Total: 3/9 (33.3%)

  ✅ Updated metadata for latest score record (ID: 42)
...

📊 RECALCULATION STATISTICS
  Users processed: 5
  Users with progress: 5
  Users at 100% (9/9): 0
  Total challenges completed: 12
  Users with invalid badges: 2

⚠️  WARNING: Some users have troubleshooting badges but haven't completed all 9 challenges.
```

### Step 5: Remove Invalid Badges (Optional)

**First, run in dry-run mode to see what would be removed:**
```bash
python cleanup_invalid_troubleshooting_badges.py --dry-run
```

**Expected Output**:
```
================================================================================
Invalid Troubleshooting Badge Cleanup Script
🔍 DRY RUN MODE - No changes will be made
================================================================================

📊 Found 2 troubleshooting badge(s)

────────────────────────────────────────────────────────────────────────────────
👤 User ID: 1 | Badge: troubleshooting_pro
────────────────────────────────────────────────────────────────────────────────
  Progress: 3/9 challenges complete
    Easy: 2/3
    Medium: 1/3
    Hard: 0/3
  Completed challenges: ['vlan-basics', 'default-gateway', 'extended-ring-redundancy']
  ❌ INVALID BADGE - User has only completed 3/9 challenges

================================================================================
⚠️  Found 1 invalid badge(s) to remove:

  - User ID: 1 | Badge: troubleshooting_pro (Troubleshooting Pro)

🔍 DRY RUN MODE - Badges would be removed, but no changes were made
```

**If you want to remove invalid badges, run without --dry-run:**
```bash
python cleanup_invalid_troubleshooting_badges.py
```

**You'll be prompted for confirmation:**
```
❓ Do you want to remove these invalid badges? (yes/no): yes

✅ Removed 1 invalid badge(s)
```

### Step 6: Restart Application
```bash
sudo systemctl start riddlenet
sudo systemctl status riddlenet
```

### Step 7: Verify Application is Running
```bash
# Check logs
sudo journalctl -u riddlenet -f

# Test the website
curl -I http://localhost:5000
```

---

## Post-Deployment Verification

### Test Case 1: New User Completes One Challenge
1. **Action**: New user completes `vlan-basics` challenge at 100%
2. **Expected**:
   - Progress: 1/9 (11.1%)
   - Badge: NOT awarded
   - Console log: "Only 1/9 complete - No badge yet"

### Test Case 2: Existing User Views Dashboard
1. **Action**: User with 3/9 challenges views dashboard
2. **Expected**:
   - No "Troubleshooting Pro" badge visible
   - Progress shows: "Easy: 2/3, Medium: 1/3, Hard: 0/3"

### Test Case 3: User Completes All 9 Challenges
1. **Action**: User completes final (9th) challenge at 100%
2. **Expected**:
   - Progress: 9/9 (100%)
   - Badge: "Troubleshooting Pro" awarded
   - Console log: "All 9 challenges complete - awarding badge!"

### Verification Commands

```bash
# Check application logs for badge awards
sudo journalctl -u riddlenet -n 100 | grep "BADGE SERVICE"

# Check database for troubleshooting progress
psql riddlenet -c "SELECT user_id, challenge_type, best_score, challenge_metadata->'challenge_counts' as progress FROM challenge_scores WHERE challenge_type IN ('linkup_easy', 'troubleshooting_medium', 'troubleshooting_hard', 'troubleshooting');"

# Verify badge counts
psql riddlenet -c "SELECT COUNT(*) FROM user_badges WHERE challenge_type = 'troubleshooting';"
```

---

## Rollback Plan

If issues occur, you can rollback:

### 1. Stop Application
```bash
sudo systemctl stop riddlenet
```

### 2. Restore Database Backup
```bash
psql riddlenet < backup_badge_fix_YYYYMMDD_HHMMSS.sql
```

### 3. Revert Code Changes
```bash
cd /home/ubuntu/RiddleNet
git log --oneline  # Find commit before changes
git revert <commit-hash>
```

### 4. Restart Application
```bash
sudo systemctl start riddlenet
```

---

## Troubleshooting

### Issue: Progress not updating
**Symptoms**: User completes challenge but progress stays at 0%

**Solution**:
```bash
# Check if metadata is being saved
psql riddlenet -c "SELECT id, user_id, challenge_type, challenge_metadata FROM challenge_scores WHERE user_id = <user_id>;"

# Re-run progress recalculation
python cleanup_troubleshooting_progress.py
```

### Issue: Badge still showing for user with < 9 challenges
**Symptoms**: User sees badge but hasn't completed all challenges

**Solution**:
```bash
# Check dashboard validation logic
sudo journalctl -u riddlenet -n 200 | grep "DASHBOARD DEBUG"

# Remove invalid badge
python cleanup_invalid_troubleshooting_badges.py
```

### Issue: Application won't start after deployment
**Symptoms**: `sudo systemctl status riddlenet` shows "failed"

**Solution**:
```bash
# Check error logs
sudo journalctl -u riddlenet -n 50

# Common issues:
# 1. Syntax error - check with: python -m py_compile user/controllers/troubleshooting_controller.py
# 2. Import error - check with: python -c "from user.models.challenge_score import ChallengeScore"
# 3. Database connection - check with: psql riddlenet -c "SELECT 1;"
```

---

## Monitoring

### Key Metrics to Watch

1. **Badge Awards**:
   ```bash
   # Count of troubleshooting badges over time
   psql riddlenet -c "SELECT DATE(earned_at), COUNT(*) FROM user_badges WHERE challenge_type = 'troubleshooting' AND earned_at > NOW() - INTERVAL '7 days' GROUP BY DATE(earned_at) ORDER BY DATE(earned_at);"
   ```

2. **Challenge Completion Rates**:
   ```bash
   # Average progress across all users
   psql riddlenet -c "SELECT AVG((challenge_metadata->'challenge_counts'->>'total')::int) as avg_completed FROM challenge_scores WHERE challenge_type IN ('troubleshooting');"
   ```

3. **Application Logs**:
   ```bash
   # Watch for badge service activity
   sudo journalctl -u riddlenet -f | grep "BADGE SERVICE"
   ```

---

## Summary

### What This Fix Does
✅ Requires ALL 9 sub-challenges complete before awarding badge  
✅ Tracks progress as (CompletedItems / TotalItems) * 100  
✅ Shows detailed progress breakdown by difficulty  
✅ Prevents premature badge awards  

### What This Fix Does NOT Do
❌ Change other challenge badges (Crimping, OSI, Quiz remain unchanged)  
❌ Modify database schema (uses existing metadata JSONB field)  
❌ Affect leaderboard scores  
❌ Change challenge completion criteria (still 100% required per challenge)  

### Impact
- **Users with < 9 challenges**: Will NOT see badge (correct)
- **Users with 9 challenges**: Will see badge (correct)
- **New users**: Must complete all 9 challenges to earn badge
- **Existing invalid badges**: Can be removed with cleanup script

---

## Contact

If you encounter issues during deployment:
1. Check the logs: `sudo journalctl -u riddlenet -f`
2. Verify database state: `psql riddlenet`
3. Review this guide's Troubleshooting section
4. Rollback if necessary (see Rollback Plan)

**Deployment Date**: {{ DATE }}  
**Deployed By**: {{ NAME }}  
**Version**: Badge Sub-Item Completion Fix v1.0
