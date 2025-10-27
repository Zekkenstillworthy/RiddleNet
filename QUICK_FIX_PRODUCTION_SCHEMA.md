# Quick Fix: Production Live Quiz Schema Error

## 🎯 Problem
```
[ERROR] column live_quiz_responses.answered_at does not exist
```

## ✅ Solution (5 steps)

### 1️⃣ Upload Migration to Production
```cmd
:: From Windows cmd (your local machine)
cd C:\Users\gilbe\OneDrive\Desktop\RiddleNet

scp -i riddlenetv1.pem migrations\011_update_live_quiz_responses_columns.py ubuntu@54.66.229.118:~/RiddleNet/migrations/

scp -i riddlenetv1.pem deployment\fix_production_live_quiz_responses.sh ubuntu@54.66.229.118:~/RiddleNet/deployment/
```

### 2️⃣ SSH to Production
```cmd
ssh -i riddlenetv1.pem ubuntu@54.66.229.118
```

### 3️⃣ Run the Automated Fix
```bash
cd ~/RiddleNet
chmod +x deployment/fix_production_live_quiz_responses.sh
./deployment/fix_production_live_quiz_responses.sh
```

### 4️⃣ Verify Application
```bash
# Check service is running
sudo systemctl status riddlenet

# Watch logs for errors
sudo journalctl -u riddlenet -f --lines=50
```

### 5️⃣ Test Live Quiz
1. Open browser: http://54.66.229.118
2. Login as student
3. Join a Live Quiz session
4. **Answer a question** ← This is the critical test
5. Check for errors in browser console (F12)
6. Verify answer is saved and leaderboard updates

---

## 🆘 If Automated Script Fails

### Manual Migration:
```bash
cd ~/RiddleNet
python3 migrations/011_update_live_quiz_responses_columns.py upgrade
sudo systemctl restart riddlenet
```

### Check Migration Success:
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/ubuntu/RiddleNet')
from __init__ import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    columns = {col['name'] for col in inspector.get_columns('live_quiz_responses')}
    
    if 'answered_at' in columns:
        print("✅ SUCCESS: answered_at column exists!")
    else:
        print("❌ FAILED: answered_at column still missing")
        
    print("\nAll columns:")
    for col in sorted(columns):
        print(f"  - {col}")
EOF
```

---

## 📋 Expected Output

### During Migration:
```
📝 Adding answered_at column
📝 Adding response_time column
📝 Adding points_awarded column
📝 Adding question_text column
📝 Adding correct_answer column
📝 Adding created_at column
[OK] live_quiz_responses table is aligned with ORM model.
```

### After Migration:
```
✅ All columns verified!
📊 Final schema:
  ✓ answered_at
  ✓ correct_answer
  ✓ created_at
  ✓ id
  ✓ is_correct
  ✓ participant_id
  ✓ points_awarded
  ✓ question_id
  ✓ question_text
  ✓ response_time
  ✓ selected_answer
  ✓ session_id
```

---

## ⏱️ Time Estimate
- Upload files: 30 seconds
- SSH + run script: 2 minutes
- Application restart: 30 seconds
- Testing: 2 minutes

**Total:** ~5 minutes

---

## 🚨 Troubleshooting

### Error: "Permission denied"
```bash
chmod +x deployment/fix_production_live_quiz_responses.sh
```

### Error: "Module not found"
```bash
# Ensure you're in the RiddleNet directory
cd ~/RiddleNet
pwd  # Should show /home/ubuntu/RiddleNet
```

### Error: "Application context" error
```bash
# Use the full Python path
/usr/bin/python3 migrations/011_update_live_quiz_responses_columns.py upgrade
```

### Application won't restart
```bash
# Check for errors
sudo journalctl -u riddlenet --no-pager -n 100

# Try manual restart
sudo systemctl stop riddlenet
sudo systemctl start riddlenet
sudo systemctl status riddlenet
```

---

## ✅ Success Indicators

- ✅ Migration script shows "[OK] live_quiz_responses table is aligned with ORM model."
- ✅ `systemctl status riddlenet` shows "active (running)"
- ✅ No errors in logs when student submits answer
- ✅ Leaderboard updates with scores
- ✅ Console shows no "UndefinedColumn" errors

---

## 📞 Need Help?

1. **Check logs:** `sudo journalctl -u riddlenet -f`
2. **Verify database:** Connect to PostgreSQL and run `\d live_quiz_responses`
3. **Test connection:** Ensure application can connect to database
4. **Rollback (if needed):** `python3 migrations/011_update_live_quiz_responses_columns.py downgrade`

---

**Remember:** This is a **safe migration** - it only ADDS columns, doesn't delete any data!
