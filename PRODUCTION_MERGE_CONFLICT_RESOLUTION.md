# 🚨 Production Merge Conflict Resolution Guide

## Current Situation

Your production server has **local changes** that conflict with the incoming updates from GitHub.

### Files with Local Changes (will be overwritten):
1. `templates/user/dashboard.html`
2. `user/models/challenge_score.py`
3. `user/services/badge_service.py`
4. `user/views.py`

### Untracked Files (blocking merge):
1. `diagnose_dashboard_inconsistency.py`
2. `test_challenge_progress.py`

---

## ✅ SAFE Resolution Steps

### Step 1: Backup Current Production State

```bash
# Create a backup directory with timestamp
BACKUP_DIR=~/RiddleNet_backup_$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup modified files
cp templates/user/dashboard.html $BACKUP_DIR/
cp user/models/challenge_score.py $BACKUP_DIR/
cp user/services/badge_service.py $BACKUP_DIR/
cp user/views.py $BACKUP_DIR/

# Backup untracked files
cp diagnose_dashboard_inconsistency.py $BACKUP_DIR/
cp test_challenge_progress.py $BACKUP_DIR/

# Verify backups
ls -lh $BACKUP_DIR/
echo "✅ Backup created at: $BACKUP_DIR"
```

### Step 2: Review What's Changed Locally

```bash
# See what's different in production
git diff templates/user/dashboard.html
git diff user/models/challenge_score.py
git diff user/services/badge_service.py
git diff user/views.py

# Check status
git status
```

### Step 3: Choose Your Resolution Strategy

---

## 🎯 OPTION A: Keep Remote Changes (Recommended for MVP Fix)

**Use this if**: You want the MVP badge fix from GitHub to override production changes.

```bash
# Stash local changes (saves them, but doesn't apply)
git stash push -m "Production changes before MVP badge fix - $(date +%Y%m%d_%H%M%S)"

# Move untracked files to backup
mv diagnose_dashboard_inconsistency.py $BACKUP_DIR/
mv test_challenge_progress.py $BACKUP_DIR/

# Pull the MVP fix
git pull origin main

# Restart application
sudo systemctl restart riddlenet

# Monitor logs
sudo journalctl -u riddlenet -f
```

**Result**: Your production gets the MVP badge fix from GitHub. Local changes are saved in stash.

---

## 🎯 OPTION B: Keep Local Changes (Merge Manually)

**Use this if**: Production has important changes you need to preserve.

```bash
# Commit local changes first
git add templates/user/dashboard.html user/models/challenge_score.py user/services/badge_service.py user/views.py
git commit -m "Production changes before merge - $(date +%Y%m%d_%H%M%S)"

# Move untracked files
mv diagnose_dashboard_inconsistency.py $BACKUP_DIR/
mv test_challenge_progress.py $BACKUP_DIR/

# Pull and merge
git pull origin main

# Git will show merge conflicts - you'll need to resolve them manually
# Edit each conflicted file and choose which changes to keep
```

**Result**: You'll need to manually resolve conflicts in each file.

---

## 🎯 OPTION C: Review First, Then Decide (Safest)

**Use this if**: You're not sure what's in production.

```bash
# Create a comparison file
echo "=== PRODUCTION vs GITHUB COMPARISON ===" > $BACKUP_DIR/comparison.txt
echo "" >> $BACKUP_DIR/comparison.txt

# Show what's different
echo "--- user/views.py ---" >> $BACKUP_DIR/comparison.txt
git diff user/views.py >> $BACKUP_DIR/comparison.txt
echo "" >> $BACKUP_DIR/comparison.txt

echo "--- badge_service.py ---" >> $BACKUP_DIR/comparison.txt
git diff user/services/badge_service.py >> $BACKUP_DIR/comparison.txt
echo "" >> $BACKUP_DIR/comparison.txt

echo "--- challenge_score.py ---" >> $BACKUP_DIR/comparison.txt
git diff user/models/challenge_score.py >> $BACKUP_DIR/comparison.txt
echo "" >> $BACKUP_DIR/comparison.txt

echo "--- dashboard.html ---" >> $BACKUP_DIR/comparison.txt
git diff templates/user/dashboard.html >> $BACKUP_DIR/comparison.txt

# View the comparison
cat $BACKUP_DIR/comparison.txt | less
```

**Then choose** Option A or B based on what you see.

---

## 🚀 RECOMMENDED: Quick MVP Deployment

Since you want the MVP badge fix deployed, use **Option A**:

```bash
# 1. Backup everything
BACKUP_DIR=~/RiddleNet_backup_$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp templates/user/dashboard.html user/models/challenge_score.py user/services/badge_service.py user/views.py diagnose_dashboard_inconsistency.py test_challenge_progress.py $BACKUP_DIR/ 2>/dev/null
echo "✅ Backups at: $BACKUP_DIR"

# 2. Stash local changes
git stash push -m "Production state before MVP badge fix"

# 3. Remove untracked files
rm diagnose_dashboard_inconsistency.py test_challenge_progress.py

# 4. Pull MVP fix
git pull origin main

# 5. Restart
sudo systemctl restart riddlenet

# 6. Test immediately
curl -I http://localhost:5000/dashboard
```

---

## 🔍 After Deployment: Verify MVP Fix

```bash
# Check logs for debug messages
sudo journalctl -u riddlenet -f | grep "DASHBOARD DEBUG"

# Should see:
# [DASHBOARD DEBUG] Link Up! validation: X/12 sub-items
```

---

## 🔄 If You Need to Restore Local Changes Later

```bash
# List stashed changes
git stash list

# Apply the stash (keeps it in stash list)
git stash apply stash@{0}

# Or pop the stash (removes it from stash list)
git stash pop
```

---

## ⚠️ Troubleshooting

### If restart fails:
```bash
# Check status
sudo systemctl status riddlenet

# View recent errors
sudo journalctl -u riddlenet -n 50

# Try manual restart
cd ~/RiddleNet
source venv/bin/activate
python application.py
```

### If you want to completely reset to GitHub state:
```bash
# ⚠️ NUCLEAR OPTION - Loses all local changes
git fetch origin
git reset --hard origin/main
sudo systemctl restart riddlenet
```

---

## 📊 Summary

| Option | Speed | Safety | Use Case |
|--------|-------|--------|----------|
| **A** | Fast | Safe (stashed) | Deploy MVP fix now |
| **B** | Slow | Safest | Keep production changes |
| **C** | Medium | Safest | Review before deciding |

**For MVP badge fix deployment, use Option A!** 🚀

---

## 📝 Quick Command Sequence

```bash
BACKUP_DIR=~/RiddleNet_backup_$(date +%Y%m%d_%H%M%S) && \
mkdir -p $BACKUP_DIR && \
cp templates/user/dashboard.html user/models/challenge_score.py user/services/badge_service.py user/views.py $BACKUP_DIR/ 2>/dev/null && \
git stash push -m "Production state before MVP fix" && \
rm -f diagnose_dashboard_inconsistency.py test_challenge_progress.py && \
git pull origin main && \
sudo systemctl restart riddlenet && \
echo "✅ MVP fix deployed! Monitor logs with: sudo journalctl -u riddlenet -f"
```

Copy and paste the above single command for instant deployment! 🎉
