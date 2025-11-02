# 🚀 MVP Production Quick Reference

## Connection

```bash
ssh -i riddlenetv1.pem ubuntu@54.66.229.118
cd /home/ubuntu/RiddleNet
```

---

## Validation Commands

### 1. Check Badge & Progress Accuracy

```bash
python3 production_mvp_badge_validation.py
```

**Purpose**: Validates all badges against challenge completion status

**Checks**:
- ✅ Link Up!: 12/12 sub-items required for badge
- ✅ OSI: Both levels must be 100%
- ✅ Crimping: Must be 100% score
- ✅ Quiz: Must be 100% score

---

### 2. Cleanup Invalid Badges

```bash
python3 cleanup_invalid_badges.py
```

**Purpose**: Removes badges where challenge is not 100% complete

**WARNING**: This will delete invalid badges. Confirm before proceeding.

---

### 3. Check Specific User

```bash
python3 << 'EOF'
from application import create_app
from user.models.challenge_score import ChallengeScore
from user.models.user_badge import UserBadge
from user.models import User as UserModel

app = create_app()
with app.app_context():
    user_id = 1  # Replace with actual user ID
    user = UserModel.query.get(user_id)
    print(f"\nUser: {user.username} (ID: {user_id})")
    
    # Get badges
    badges = UserBadge.query.filter_by(user_id=user_id).all()
    print(f"Total badges: {len(badges)}")
    
    # Get challenges
    challenges = ChallengeScore.query.filter_by(user_id=user_id).all()
    print(f"Total challenges: {len(challenges)}")
    
    # Link Up! progress
    linkup = ChallengeScore.query.filter_by(user_id=user_id, challenge_type='troubleshooting').first()
    if linkup and linkup.challenge_metadata:
        completed = len(linkup.challenge_metadata.get('completed_challenges', []))
        print(f"\nLink Up!: {completed}/12 sub-items")
        counts = linkup.challenge_metadata.get('challenge_counts', {})
        print(f"  Foundation: {counts.get('foundation', 0)}/3")
        print(f"  Easy: {counts.get('easy', 0)}/3")
        print(f"  Medium: {counts.get('medium', 0)}/3")
        print(f"  Hard: {counts.get('hard', 0)}/3")
EOF
```

---

## Application Management

### Restart Application

```bash
sudo systemctl restart riddlenet
```

### Check Application Status

```bash
sudo systemctl status riddlenet
```

### View Logs (Real-time)

```bash
sudo journalctl -u riddlenet -f
```

### View Recent Logs

```bash
sudo journalctl -u riddlenet -n 100
```

### Search Logs for Badge Activity

```bash
sudo journalctl -u riddlenet | grep "BADGE SERVICE"
```

### Search Logs for Dashboard Activity

```bash
sudo journalctl -u riddlenet | grep "DASHBOARD DEBUG"
```

---

## Database Queries

### Count Total Badges

```bash
python3 << 'EOF'
from application import create_app
from user.models.user_badge import UserBadge

app = create_app()
with app.app_context():
    total = UserBadge.query.count()
    print(f"Total badges: {total}")
    
    by_type = {}
    for badge in UserBadge.query.all():
        by_type[badge.challenge_type] = by_type.get(badge.challenge_type, 0) + 1
    
    print("\nBadges by challenge type:")
    for ctype, count in by_type.items():
        print(f"  {ctype}: {count}")
EOF
```

### Check User Progress

```bash
python3 << 'EOF'
from application import create_app
from user.models.challenge_score import ChallengeScore

app = create_app()
with app.app_context():
    user_id = 1  # Replace with actual user ID
    
    for ctype in ['crimping', 'osi', 'troubleshooting', 'quiz']:
        challenge = ChallengeScore.query.filter_by(
            user_id=user_id, 
            challenge_type=ctype
        ).first()
        
        if challenge:
            if ctype == 'troubleshooting' and challenge.challenge_metadata:
                completed = len(challenge.challenge_metadata.get('completed_challenges', []))
                print(f"{ctype}: {completed}/12 sub-items ({(completed/12)*100:.1f}%)")
            else:
                score = ChallengeScore.effective_best_score(challenge)
                print(f"{ctype}: {score:.1f}%")
        else:
            print(f"{ctype}: No data")
EOF
```

---

## Expected Progress Formulas

### Link Up! (Troubleshooting)
```
Progress = (Completed Sub-Items / 12) × 100%
Badge = Awarded when 12/12 complete
```

### Crimping Simulation
```
Progress = Score %
Badge = Awarded when 100%
```

### OSI Model & TCP/IP
```
Progress = Average of both levels (until both at 100%)
Badge = Awarded when both levels at 100%
```

### Quiz Challenge
```
Progress = Score %
Badge = Awarded when 100%
```

---

## Dashboard Consistency Rule

```
Challenges Complete = Badges Earned
```

If these numbers don't match → Run validation script!

---

## Common Issues & Fixes

### Issue: Badge showing but challenge not complete

**Fix**:
```bash
python3 production_mvp_badge_validation.py
python3 cleanup_invalid_badges.py
sudo systemctl restart riddlenet
```

### Issue: Progress percentage not accurate

**Check**:
```bash
# View logs for progress calculation
sudo journalctl -u riddlenet | grep "Progress"

# Verify metadata in database
python3 << 'EOF'
from application import create_app
from user.models.challenge_score import ChallengeScore

app = create_app()
with app.app_context():
    user_id = 1  # Replace
    challenge = ChallengeScore.query.filter_by(
        user_id=user_id, 
        challenge_type='troubleshooting'
    ).first()
    
    if challenge:
        print(challenge.challenge_metadata)
EOF
```

### Issue: Dashboard not updating

**Fix**:
```bash
# Clear cache
sudo systemctl restart riddlenet

# Check for errors
sudo journalctl -u riddlenet -n 50
```

---

## File Locations

### Application Root
```
/home/ubuntu/RiddleNet/
```

### Validation Scripts
```
/home/ubuntu/RiddleNet/production_mvp_badge_validation.py
/home/ubuntu/RiddleNet/cleanup_invalid_badges.py
```

### Key Source Files
```
/home/ubuntu/RiddleNet/user/views.py
/home/ubuntu/RiddleNet/user/models/challenge_score.py
/home/ubuntu/RiddleNet/user/services/badge_service.py
```

### Logs
```
/var/log/syslog
sudo journalctl -u riddlenet
```

---

## Emergency Rollback

If issues occur after validation:

1. **Stop application**:
   ```bash
   sudo systemctl stop riddlenet
   ```

2. **Restore database backup** (if created):
   ```bash
   # Restore from backup
   # (Backup command should be run BEFORE validation)
   ```

3. **Restart application**:
   ```bash
   sudo systemctl start riddlenet
   ```

---

## Testing Checklist

- [ ] Run validation script
- [ ] Review issues found
- [ ] Run cleanup script (if needed)
- [ ] Restart application
- [ ] Test as user in browser
- [ ] Verify dashboard counts match
- [ ] Check "Your Achievements" section
- [ ] Verify progress percentages
- [ ] Test all 4 challenge types

---

## Support

**View Application Logs**:
```bash
sudo journalctl -u riddlenet -f
```

**Check Application Status**:
```bash
sudo systemctl status riddlenet
```

**Application Port**: 8000 (default)

**Database**: PostgreSQL (riddlenet)

---

**Last Updated**: November 3, 2025  
**Version**: MVP 1.0
