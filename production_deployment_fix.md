# 🚨 Production Deployment - Git Conflict Resolution

## Issue
Git pull failed due to untracked files that would be overwritten by merge.

## 🔧 Solution Steps

### Option 1: Backup and Remove Conflicting Files (Recommended)

```bash
# 1. Create backup directory
mkdir -p ~/riddlenet_backup_$(date +%Y%m%d_%H%M%S)

# 2. Move conflicting files to backup
cd ~/RiddleNet
mv check_all_challenges.py ~/riddlenet_backup_*/
mv check_challenge_scores.py ~/riddlenet_backup_*/
mv check_legacy_scores.py ~/riddlenet_backup_*/
mv fix_osi_completion.py ~/riddlenet_backup_*/
mv quick_check.py ~/riddlenet_backup_*/

# 3. Pull latest changes
git pull origin main

# 4. Restart application
sudo systemctl restart riddlenet

# 5. Verify deployment
sudo systemctl status riddlenet
```

### Option 2: Stash Local Changes (Alternative)

```bash
cd ~/RiddleNet

# Stash untracked files
git stash --include-untracked

# Pull latest changes
git pull origin main

# Restart application
sudo systemctl restart riddlenet

# (Optional) Restore stashed files if needed
# git stash pop
```

### Option 3: Force Overwrite (Use with Caution)

```bash
cd ~/RiddleNet

# Remove conflicting files
rm -f check_all_challenges.py check_challenge_scores.py check_legacy_scores.py fix_osi_completion.py quick_check.py

# Pull latest changes
git pull origin main

# Restart application
sudo systemctl restart riddlenet
```

## ✅ Recommended Commands (Copy-Paste Ready)

```bash
# Full deployment sequence with backup
cd ~/RiddleNet
mkdir -p ~/riddlenet_backup_$(date +%Y%m%d_%H%M%S)
mv check_all_challenges.py check_challenge_scores.py check_legacy_scores.py fix_osi_completion.py quick_check.py ~/riddlenet_backup_*/ 2>/dev/null
git pull origin main
sudo systemctl restart riddlenet
sudo systemctl status riddlenet
echo "✅ Deployment complete! Check dashboard at http://54.66.229.118"
```

## 🧪 Post-Deployment Verification

```bash
# Check if badge fix is applied
grep -A 5 "MVP FIX: Only show badges for COMPLETED challenges" ~/RiddleNet/user/views.py

# View recent logs
sudo journalctl -u riddlenet -n 50 --no-pager

# Check application is running
curl -I http://localhost:5000 || curl -I http://localhost:8000
```

## 📊 Expected Output After Fix

Dashboard should now show:
- ✅ Only 1 badge (Network Detective - 100% complete)
- ✅ Badge count: 1
- ✅ Challenges complete: 1/4
- ❌ No badges for incomplete challenges (OSI 50%, Quiz 7%)

## 🔄 If Restart Needed After Pull

```bash
# Check what process is running
ps aux | grep -i riddlenet | grep -v grep

# If using gunicorn
sudo systemctl restart riddlenet

# If using custom service
sudo supervisorctl restart riddlenet

# Manual restart (if no service manager)
pkill -f 'gunicorn.*run:app'
cd ~/RiddleNet
source venv/bin/activate  # if using venv
gunicorn -c gunicorn.conf.py run:app --daemon
```
