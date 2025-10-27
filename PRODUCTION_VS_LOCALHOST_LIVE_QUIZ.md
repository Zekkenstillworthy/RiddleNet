# Production vs Localhost Live Quiz Comparison

**Date:** October 28, 2025  
**Issue:** Live Quiz answer submission failing on production with database schema error

---

## 🎯 Executive Summary

**Are they the same in terms of logic?**  
✅ **YES** - The application code, models, and logic are **IDENTICAL**.

**What's different?**  
❌ **NO** - The database schemas are **OUT OF SYNC**.

---

## 🔴 Critical Issue Identified

### Error on Production Server
```
[ERROR] column live_quiz_responses.answered_at does not exist
LINE 1: ...ses.is_correct AS live_quiz_responses_is_correct, live_quiz_...

sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn)
```

### Root Cause
The `live_quiz_responses` table on **production** is missing the `answered_at` column (and potentially other columns) that exist in the SQLAlchemy ORM model.

---

## 📊 Schema Comparison

### Expected Schema (From ORM Model)
**File:** `user/models/live_quiz.py` - `LiveQuizResponse` class

```python
class LiveQuizResponse(db.Model):
    __tablename__ = 'live_quiz_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, ...)
    session_id = db.Column(db.Integer, ...)
    question_id = db.Column(db.Integer, ...)
    selected_answer = db.Column(db.String(1000), ...)
    is_correct = db.Column(db.Boolean, ...)
    
    # ⚠️ MISSING ON PRODUCTION:
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)      # ❌
    response_time = db.Column(db.Float, ...)                           # ❌
    points_awarded = db.Column(db.Integer, default=0)                  # ❌
    question_text = db.Column(db.String(500), nullable=True)           # ❌
    correct_answer = db.Column(db.String(1000), nullable=True)         # ❌
    created_at = db.Column(db.DateTime, default=datetime.utcnow)       # ❌
```

### Localhost Database
✅ **Has all columns** - Table created/migrated correctly during development

### Production Database
❌ **Missing columns** - Table created with old schema, migrations not run

---

## 🔍 Migration Status

### Existing Migrations
| Migration | Target Table | Status |
|-----------|--------------|--------|
| `008_update_live_quiz_session_columns.py` | `live_quiz_sessions` | ✅ Run on localhost |
| `009_update_live_quiz_participants_columns.py` | `live_quiz_participants` | ✅ Run on localhost |
| `010_initialize_live_quiz_sessions.py` | `live_quiz_sessions` | ⚠️ Empty file |

### Missing Migration
| Migration | Target Table | Status |
|-----------|--------------|--------|
| `011_update_live_quiz_responses_columns.py` | `live_quiz_responses` | ✅ **CREATED** (needs to run on production) |

---

## 💡 Why This Happened

1. **Development Workflow:**
   - You created the `LiveQuizResponse` model with all fields
   - SQLAlchemy auto-created the table on localhost with all columns
   - You tested Live Quiz on localhost - **worked perfectly**

2. **Production Deployment:**
   - The model code was deployed to production ✅
   - BUT migrations were NOT run on production database ❌
   - Production database still has old schema (missing columns)
   - Code tries to query `answered_at` → **CRASH**

3. **Migration Gap:**
   - Migrations were created for `live_quiz_sessions` and `live_quiz_participants`
   - BUT no migration was created for `live_quiz_responses`
   - This table's schema was never updated on production

---

## 🛠️ Solution

### Step 1: Upload Migration to Production
```bash
# From your local machine
scp -i riddlenetv1.pem migrations/011_update_live_quiz_responses_columns.py ubuntu@54.66.229.118:~/RiddleNet/migrations/
scp -i riddlenetv1.pem deployment/fix_production_live_quiz_responses.sh ubuntu@54.66.229.118:~/RiddleNet/deployment/
```

### Step 2: SSH to Production
```bash
ssh -i riddlenetv1.pem ubuntu@54.66.229.118
```

### Step 3: Run the Fix Script
```bash
cd ~/RiddleNet
chmod +x deployment/fix_production_live_quiz_responses.sh
./deployment/fix_production_live_quiz_responses.sh
```

### Step 4: Verify
```bash
# Check application is running
sudo systemctl status riddlenet

# Check logs
sudo journalctl -u riddlenet -f
```

### Alternative: Manual Migration
If the script doesn't work, run migration manually:
```bash
cd ~/RiddleNet
python3 migrations/011_update_live_quiz_responses_columns.py upgrade
sudo systemctl restart riddlenet
```

---

## 🧪 Testing After Fix

### Test on Production:
1. **Join Live Quiz** as a student
2. **Answer a question** 
3. **Check for errors** in console/logs
4. **Verify leaderboard** updates correctly

### Expected Result:
- ✅ No `UndefinedColumn` errors
- ✅ Answers are saved to database
- ✅ Leaderboard shows scores
- ✅ Points calculated correctly

---

## 📝 What the Migration Does

The `011_update_live_quiz_responses_columns.py` migration:

1. **Adds missing columns:**
   - `answered_at` (TIMESTAMP) - When answer was submitted
   - `response_time` (FLOAT) - Seconds taken to answer
   - `points_awarded` (INTEGER) - Points given for answer
   - `question_text` (VARCHAR) - Historical question text
   - `correct_answer` (VARCHAR) - Historical correct answer
   - `created_at` (TIMESTAMP) - Record creation time

2. **Sets sensible defaults:**
   - Existing rows get `NOW()` for timestamps
   - `0` for numeric fields
   - `NULL` for optional text fields

3. **Applies NOT NULL constraints:**
   - Ensures data integrity for required fields

4. **Backfills data:**
   - Updates existing records to have valid values

---

## ✅ Verification Checklist

After running migration on production:

- [ ] Migration script completed without errors
- [ ] All columns exist in `live_quiz_responses` table
- [ ] Application restarted successfully
- [ ] Live Quiz session can be created
- [ ] Student can join Live Quiz
- [ ] Student can submit answers (NO errors)
- [ ] Leaderboard displays correctly
- [ ] Points are calculated and saved

---

## 🚨 Important Notes

### Database Consistency
- **Localhost:** Uses SQLite or local PostgreSQL (auto-creates schemas)
- **Production:** Uses RDS PostgreSQL (requires explicit migrations)
- Always run migrations on production after model changes

### Future Prevention
1. **Always create migrations** for model changes
2. **Test migrations** on staging environment
3. **Document migration order** in deployment guides
4. **Version control migrations** with the code
5. **Check production schema** after deployments

### Migration Best Practices
```bash
# After changing a model:
1. Create migration file
2. Test migration locally (upgrade + downgrade)
3. Commit migration with code changes
4. Deploy code to production
5. Run migration on production
6. Verify schema matches model
7. Restart application
```

---

## 🔄 Summary

| Aspect | Localhost | Production | Match? |
|--------|-----------|------------|--------|
| **Application Code** | Latest | Latest | ✅ SAME |
| **Python Models** | LiveQuizResponse with all fields | LiveQuizResponse with all fields | ✅ SAME |
| **Database Schema** | All columns present | Missing `answered_at`, etc. | ❌ DIFFERENT |
| **Live Quiz Logic** | Works perfectly | Crashes on answer submit | ❌ BROKEN |
| **Socket Events** | Working | Working | ✅ SAME |
| **Frontend Code** | Latest fixes | Latest fixes | ✅ SAME |

**Conclusion:** The logic is identical, but production database schema is outdated. Running the migration will sync them.

---

## 📞 Support

If issues persist after migration:
1. Check production logs: `sudo journalctl -u riddlenet -f`
2. Verify database connection: `psql -h <host> -U <user> -d <database>`
3. Inspect table schema: `\d live_quiz_responses`
4. Test query manually: `SELECT * FROM live_quiz_responses LIMIT 1;`

---

**Status:** 🟡 **AWAITING PRODUCTION MIGRATION**  
**Action Required:** Run migration on production server  
**ETA:** 5-10 minutes  
**Risk Level:** Low (migration adds columns, doesn't delete data)
