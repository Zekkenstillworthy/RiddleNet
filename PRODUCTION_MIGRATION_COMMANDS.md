# Production Migration Commands

## Quick Manual Fix (Copy-Paste on Production)

Since you're already SSH'd into the production server, just run these commands:

```bash
# Navigate to RiddleNet directory
cd ~/RiddleNet

# Activate virtual environment
source venv/bin/activate

# Run the migration
python migrations/011_update_live_quiz_responses_columns.py upgrade

# Restart the application
sudo systemctl restart riddlenet

# Check status
sudo systemctl status riddlenet

# Watch logs for any errors
sudo journalctl -u riddlenet -f --lines=50
```

## Verify Migration Success

```bash
# Still in venv (source venv/bin/activate if needed)
python << 'EOF'
import sys
sys.path.insert(0, '/home/ubuntu/RiddleNet')
from __init__ import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    columns = {col['name'] for col in inspector.get_columns('live_quiz_responses')}
    
    expected = ['answered_at', 'response_time', 'points_awarded', 'question_text', 'correct_answer', 'created_at']
    missing = [col for col in expected if col not in columns]
    
    if missing:
        print(f"\n❌ Still missing: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("\n✅ All columns verified!")
        print("\n📊 Final schema:")
        for col in sorted(columns):
            print(f"  ✓ {col}")
EOF
```

## Exit venv

```bash
deactivate
```

---

## Expected Output

### From Migration:
```
📝 Adding answered_at column
📝 Adding response_time column
📝 Adding points_awarded column
📝 Adding question_text column
📝 Adding correct_answer column
📝 Adding created_at column
[OK] live_quiz_responses table is aligned with ORM model.
```

### From systemctl status:
```
● riddlenet.service - RiddleNet Application
     Loaded: loaded
     Active: active (running)
```

---

## If You Get Errors

### "ModuleNotFoundError: No module named 'flask'"
**Solution:** Make sure you activated the venv first:
```bash
source venv/bin/activate
```

### "Application context" error
**Solution:** The migration script should handle this, but if not:
```bash
cd ~/RiddleNet
source venv/bin/activate
python migrations/011_update_live_quiz_responses_columns.py upgrade
```

### Service won't restart
```bash
# Check what's wrong
sudo journalctl -u riddlenet --no-pager -n 50

# Try stopping and starting separately
sudo systemctl stop riddlenet
sleep 2
sudo systemctl start riddlenet
sudo systemctl status riddlenet
```

---

## Quick Test After Migration

1. Open browser to your production site
2. Login as student
3. Join a Live Quiz
4. **Answer a question** ← Critical test
5. Should see score update, no errors

✅ If the answer is saved and leaderboard updates = **SUCCESS!**
