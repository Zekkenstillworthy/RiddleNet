# Live Quiz Production Fix - Quick Reference

## 🚨 Problem
Live Quiz button not showing on production server

## ✅ Root Cause
Database has no active/waiting sessions (feature works by design)

## 🔧 Fix in 3 Commands

```bash
cd /path/to/RiddleNet
python scripts/seed_live_quiz_sessions.py --status active
sudo systemctl restart riddlenet
```

**Done!** Button appears in < 1 minute

---

## 📋 Common Commands

### Seed All Modules (Recommended)
```bash
python scripts/seed_live_quiz_sessions.py
```
Creates waiting sessions for all modules

### Create One Active Session (Testing)
```bash
python scripts/seed_live_quiz_sessions.py --active
```
Instant live quiz on first module

### Seed Specific Class/Module
```bash
# Only Networking 1
python scripts/seed_live_quiz_sessions.py --class 7

# Only Module 2
python scripts/seed_live_quiz_sessions.py --module 2

# Active session for Class 7, Module 2
python scripts/seed_live_quiz_sessions.py --class 7 --module 2 --status active
```

### Clean and Reseed
```bash
python scripts/seed_live_quiz_sessions.py --clean
python scripts/seed_live_quiz_sessions.py --status active
```

---

## 🔍 Diagnostic Commands

### Check Current State
```bash
python scripts/check_live_quiz_sessions.py
```

### Production Readiness
```bash
python scripts/production_deployment_check.py
```

---

## 🎯 Expected Results

### Before Fix
- ❌ Button hidden on all module pages
- ❌ Query returns 0 sessions

### After Fix (waiting)
```
┌────────────────────────────────────┐
│  Live Quiz Starting Soon  ⏳WAITING │
└────────────────────────────────────┘
```

### After Fix (active)
```
┌──────────────────────────────┐
│  ⚡ Join Live Quiz Now! 🔴LIVE │  ← Pulsing
└──────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Button Still Hidden After Seeding

1. **Restart app:**
   ```bash
   sudo systemctl restart riddlenet
   ```

2. **Check database:**
   ```bash
   python scripts/check_live_quiz_sessions.py
   ```

3. **Verify module match:**
   - Sessions exist for Module 1
   - But viewing Module 2 (create session for Module 2)

### Sessions Exist but Button Hidden

1. **Check status:**
   - Only `'active'` and `'waiting'` show button
   - `'completed'` hides button

2. **Clear cache:**
   ```
   Ctrl+Shift+R in browser
   ```

---

## 📞 Support

**Scripts Location:** `/scripts/`
- `seed_live_quiz_sessions.py` - Create sessions
- `check_live_quiz_sessions.py` - Check status
- `production_deployment_check.py` - Verify deployment

**Documentation:**
- `PRODUCTION_LIVE_QUIZ_SETUP.md` - Full guide
- `LIVE_QUIZ_FINAL_ANALYSIS.md` - Technical details

**Logs:**
- Application: `journalctl -u riddlenet -f`
- Route: Look for `Found X live quiz sessions for module Y`

---

## ⏱️ Quick Stats

- **Fix Time:** < 2 minutes
- **Commands Needed:** 3
- **Downtime:** ~30 seconds (restart only)
- **Complexity:** Low (automated script)

---

**Last Updated:** October 27, 2025  
**Status:** Production Ready ✅
