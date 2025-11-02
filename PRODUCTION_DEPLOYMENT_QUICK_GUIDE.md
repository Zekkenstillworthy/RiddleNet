# 🚀 Production Deployment - Quick Guide

## 🎯 What This Fix Does

**Problem**: Link Up! badge awarded at 12/26 items (46% completion shown as 100%)
**Solution**: Update tracking from 12 items → **26 items** (Foundation 17 + Easy 3 + Intermediate 3 + Hard 3)

---

## ⚡ Quick Deployment (5 Minutes)

### **Step 1: Connect & Backup**
```bash
ssh -i riddlenetv1.pem ubuntu@54.66.229.118
cd /var/www/riddlenet

# Backup files
sudo cp user/views.py user/views.py.backup_$(date +%Y%m%d_%H%M%S)
sudo cp user/services/badge_service.py user/services/badge_service.py.backup_$(date +%Y%m%d_%H%M%S)
sudo cp user/models/challenge_score.py user/models/challenge_score.py.backup_$(date +%Y%m%d_%H%M%S)
```

### **Step 2: Upload Files**

**Option A: Direct Edit on Server**
```bash
# Edit each file manually:
sudo nano /var/www/riddlenet/user/services/badge_service.py
sudo nano /var/www/riddlenet/user/models/challenge_score.py
sudo nano /var/www/riddlenet/user/views.py
```

**Option B: Upload from Local (Recommended)**
```bash
# From your Windows machine (Git Bash or PowerShell)
scp -i riddlenetv1.pem c:/Users/gilbe/OneDrive/Desktop/RiddleNet/user/views.py ubuntu@54.66.229.118:/tmp/
scp -i riddlenetv1.pem c:/Users/gilbe/OneDrive/Desktop/RiddleNet/user/services/badge_service.py ubuntu@54.66.229.118:/tmp/
scp -i riddlenetv1.pem c:/Users/gilbe/OneDrive/Desktop/RiddleNet/user/models/challenge_score.py ubuntu@54.66.229.118:/tmp/

# Then on server, move files:
sudo mv /tmp/views.py /var/www/riddlenet/user/views.py
sudo mv /tmp/badge_service.py /var/www/riddlenet/user/services/badge_service.py
sudo mv /tmp/challenge_score.py /var/www/riddlenet/user/models/challenge_score.py
```

### **Step 3: Set Permissions**
```bash
sudo chown www-data:www-data /var/www/riddlenet/user/views.py
sudo chown www-data:www-data /var/www/riddlenet/user/services/badge_service.py
sudo chown www-data:www-data /var/www/riddlenet/user/models/challenge_score.py
```

### **Step 4: Restart & Verify**
```bash
# Restart application
sudo systemctl restart riddlenet

# Check status
sudo systemctl status riddlenet

# Monitor logs
sudo journalctl -u riddlenet -f
```

---

## 🧪 Quick Test

```bash
python3 << 'EOF'
from application import create_app
from user.models.challenge_score import ChallengeScore

app = create_app()
with app.app_context():
    progress = ChallengeScore.get_troubleshooting_progress(1)
    print(f"\n✅ Link Up! Progress: {len(progress['completed_challenges'])}/26")
    print(f"✅ Percentage: {progress['progress_percentage']}%\n")
EOF
```

**Expected Output**:
```
✅ Link Up! Progress: X/26
✅ Percentage: Y.Y%
```

---

## 📝 Changes Made

### File 1: `user/services/badge_service.py`
```python
# Line 162-242: Updated TOTAL_REQUIRED
TOTAL_REQUIRED = 12  # ❌ OLD
TOTAL_REQUIRED = 26  # ✅ NEW

# Updated badge requirement
'Completed all 12 Link Up! challenges'  # ❌ OLD
'Completed all 26 Link Up! challenges'  # ✅ NEW
```

### File 2: `user/models/challenge_score.py`
```python
# Line 293-353: Updated TOTAL_REQUIRED
TOTAL_REQUIRED = 12  # ❌ OLD
TOTAL_REQUIRED = 26  # ✅ NEW
```

### File 3: `user/views.py`
```python
# Line 716-733: Updated TOTAL_LINK_UP_ITEMS
TOTAL_LINK_UP_ITEMS = 12  # ❌ OLD
TOTAL_LINK_UP_ITEMS = 26  # ✅ NEW

# Line 224-236: Updated badge validation
TOTAL_LINK_UP_ITEMS = 12  # ❌ OLD
TOTAL_LINK_UP_ITEMS = 26  # ✅ NEW
```

---

## ⚠️ Important Notes

### User Impact
- **Existing badges NOT deleted** (only hidden until 26/26 complete)
- **Progress recalculated** on next page load
- **No database changes** required

### What Users Will See

**Before Fix**:
- User with 12/26 items → Badge shows ❌ (incorrect)
- Progress: 100% ❌ (should be 46%)

**After Fix**:
- User with 12/26 items → No badge ✅ (correct)
- Progress: 46% ✅ (accurate)

---

## 🔄 Rollback (If Needed)

```bash
# Restore backups
TIMESTAMP="20250103_120000"  # Replace with your backup timestamp
sudo cp user/views.py.backup_$TIMESTAMP user/views.py
sudo cp user/services/badge_service.py.backup_$TIMESTAMP user/services/badge_service.py
sudo cp user/models/challenge_score.py.backup_$TIMESTAMP user/models/challenge_score.py

# Restart
sudo systemctl restart riddlenet
```

---

## ✅ Success Checklist

- [ ] Files backed up
- [ ] New files uploaded
- [ ] Permissions set correctly
- [ ] Application restarted successfully
- [ ] Test script shows 26-item tracking
- [ ] Dashboard loads without errors
- [ ] Challenges page shows correct progress
- [ ] Logs show no errors

---

## 📞 Quick Troubleshooting

### Issue: Application won't start
```bash
# Check logs
sudo journalctl -u riddlenet -n 50

# Check syntax errors
python3 -m py_compile /var/www/riddlenet/user/views.py
python3 -m py_compile /var/www/riddlenet/user/services/badge_service.py
python3 -m py_compile /var/www/riddlenet/user/models/challenge_score.py
```

### Issue: Progress still shows 12 items
```bash
# Clear application cache
sudo systemctl restart riddlenet

# Check file contents
grep "TOTAL_REQUIRED = 26" /var/www/riddlenet/user/services/badge_service.py
grep "TOTAL_LINK_UP_ITEMS = 26" /var/www/riddlenet/user/views.py
```

---

## 🎉 Done!

After deployment:
1. Test dashboard → Check "Your Achievements"
2. Test challenges page → Verify Link Up! progress
3. Monitor logs for 5-10 minutes
4. Verify user experience is improved

**Estimated Downtime**: < 10 seconds (during restart)
**Risk Level**: ⚠️ Low (only calculation changes, no database migrations)

---

**For detailed documentation, see**: `MVP_BADGE_PROGRESS_FIX_26_ITEMS.md`
