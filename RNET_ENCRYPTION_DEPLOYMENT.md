# 🚀 RNet Encryption - Production Deployment Guide

## ✅ Pre-Deployment Checklist

Before deploying to production, complete these steps:

### 1. Generate Unique Encryption Keys

**CRITICAL**: Change the default keys!

Run this Python script to generate secure keys:

```python
import os
import base64

# Generate 32-byte random keys
encryption_key = base64.b64encode(os.urandom(32)).decode()
hmac_key = base64.b64encode(os.urandom(32)).decode()

print("="*70)
print("🔑 Production Encryption Keys")
print("="*70)
print(f"\nRNET_ENCRYPTION_KEY={encryption_key}")
print(f"RNET_HMAC_KEY={hmac_key}")
print("\n⚠️ SAVE THESE KEYS SECURELY!")
print("⚠️ DO NOT COMMIT TO GIT!")
print("⚠️ DO NOT SHARE PUBLICLY!")
print("="*70)
```

### 2. Set Environment Variables

#### Windows (PowerShell)
```powershell
$env:RNET_ENCRYPTION_KEY="your-generated-key-here"
$env:RNET_HMAC_KEY="your-generated-hmac-key-here"
```

#### Windows (CMD)
```cmd
set RNET_ENCRYPTION_KEY=your-generated-key-here
set RNET_HMAC_KEY=your-generated-hmac-key-here
```

#### Linux/Mac
```bash
export RNET_ENCRYPTION_KEY="your-generated-key-here"
export RNET_HMAC_KEY="your-generated-hmac-key-here"
```

#### Permanent Setup (Windows)

1. Open System Properties → Advanced → Environment Variables
2. Add User Variables:
   - `RNET_ENCRYPTION_KEY` = your key
   - `RNET_HMAC_KEY` = your key
3. Restart application

### 3. Test the System

Run the test suite:

```bash
python test_rnet_encryption.py
```

Expected output:
```
🎉 ALL TESTS PASSED!
✅ Performance is excellent! (< 100ms)
```

### 4. Backup Keys Securely

**Store keys in:**
- Secure password manager
- Encrypted backup file
- Secure key management system (AWS KMS, Azure Key Vault, etc.)

**DO NOT store in:**
- Git repository
- Code files
- Unencrypted files
- Shared documents

## 📋 Deployment Steps

### Step 1: Update Code

Files already updated:
- ✅ `utils/rnet_encryption.py` - Encryption module
- ✅ `instructor/routes/simulation_routes.py` - Export/Import
- ✅ `user/dynamic_simulation_routes.py` - Student export
- ✅ `instructor/routes/rnet_viewer_routes.py` - File viewer

### Step 2: Set Environment Variables

Set production keys as shown above.

### Step 3: Restart Application

```bash
# Stop the application
# (Use your stop command, e.g., Ctrl+C, systemctl stop, etc.)

# Start with new environment variables
python run.py
```

### Step 4: Verify Deployment

1. **Test Export**:
   - Go to instructor panel
   - Export a simulation
   - Check the `.rnet` file is encrypted
   - Verify metadata is visible

2. **Test Import**:
   - Import the exported file
   - Verify it loads correctly
   - Check no errors in logs

3. **Test Tampering Detection**:
   - Edit the `.rnet` file in Notepad
   - Try to import it
   - Should see "Integrity check failed" error

4. **Test Backward Compatibility**:
   - Import an old unencrypted `.rnet` file
   - Should work without errors
   - Export it again
   - New export should be encrypted

## 🔍 Verification Commands

### Check Environment Variables
```bash
# Windows CMD
echo %RNET_ENCRYPTION_KEY%
echo %RNET_HMAC_KEY%

# PowerShell
$env:RNET_ENCRYPTION_KEY
$env:RNET_HMAC_KEY

# Linux/Mac
echo $RNET_ENCRYPTION_KEY
echo $RNET_HMAC_KEY
```

### Test Encryption Manually

```python
from utils.rnet_encryption import encrypt_rnet_file, decrypt_rnet_file

# Create test data
test_data = {
    'format': 'rnetfile',
    'version': '1.0',
    'simulation': {'title': 'Test'}
}

# Encrypt
encrypted = encrypt_rnet_file(test_data)
print("Encrypted format:", encrypted['format'])
print("Has signature:", bool(encrypted.get('integrity_signature')))

# Decrypt
decrypted = decrypt_rnet_file(encrypted)
print("Decryption successful:", decrypted == test_data)
```

## 📊 Monitoring

### Log Files to Monitor

Check `server_log.txt` for:

```
[INFO] RNet file for simulation X encrypted successfully
[INFO] Encrypted RNet file decrypted successfully
[ERROR] Encryption failed for simulation X: [error]
[ERROR] RNet file integrity check failed: [error]
```

### Success Indicators

✅ No decryption errors in logs
✅ Exported files have `"format": "rnetfile_encrypted"`
✅ Import works for both new and old files
✅ Tampering is detected and rejected

### Error Indicators

❌ "Decryption failed" errors
❌ "Integrity check failed" for valid files
❌ Environment variables not set
❌ Import errors for new files

## 🛠️ Troubleshooting

### Issue: "Decryption failed" for valid files

**Cause**: Environment variables not set or wrong keys

**Fix**:
1. Check environment variables are set
2. Verify keys match the ones used for encryption
3. Restart application after setting variables

### Issue: Old files don't work

**Cause**: Backward compatibility not working

**Fix**:
1. Check error logs for specific error
2. Verify file format is `"rnetfile"` (v1.0)
3. Check if file is corrupted

### Issue: Performance is slow

**Cause**: Encryption overhead (unlikely)

**Fix**:
1. Run performance test: `python test_rnet_encryption.py`
2. Should be < 100ms total
3. Check server resources

### Issue: All exports fail

**Cause**: Encryption module error

**Fix**:
1. Check `cryptography` package is installed
2. Verify Python version (3.8+)
3. Check for import errors in logs
4. Fallback should create unencrypted files

## 🔄 Rollback Plan

If you need to rollback:

### Option 1: Disable Encryption (Emergency)

Comment out encryption in code:

```python
# In simulation_routes.py (line ~1581)
# Comment out:
# encrypted_data = encrypt_rnet_file(rnetfile_data)
# Use instead:
final_data = rnetfile_data
```

### Option 2: Use Unencrypted Mode

The system automatically falls back to unencrypted on errors.

### Option 3: Restore Previous Version

Use Git to restore:
```bash
git checkout <previous-commit>
```

## 📝 Post-Deployment

### Week 1: Monitor Closely

- Check logs daily
- Verify all exports work
- Test imports regularly
- Monitor user reports

### Week 2: Review

- Check error rates
- Verify performance
- Review user feedback
- Document any issues

### Month 1: Optimize

- Review encryption logs
- Check for patterns
- Optimize if needed
- Update documentation

## 🎯 Success Metrics

After deployment, you should see:

- ✅ 0 decryption errors for valid files
- ✅ 100% tampering detection rate
- ✅ < 2ms encryption/decryption time
- ✅ Backward compatibility maintained
- ✅ No user complaints

## 🔐 Security Best Practices

1. **Change Default Keys**: Use unique production keys
2. **Secure Storage**: Store keys in secure key management
3. **Regular Rotation**: Consider rotating keys annually
4. **Access Control**: Limit who can access keys
5. **Audit Logs**: Monitor encryption/decryption events
6. **Backup**: Keep secure backup of keys

## 📞 Support Contacts

**For Issues**:
1. Check this deployment guide
2. Review `RNET_ENCRYPTION_GUIDE.md`
3. Check `server_log.txt`
4. Run test suite
5. Contact system administrator

## ✅ Final Checklist

Before going live:

- [ ] Generated unique production keys
- [ ] Set environment variables
- [ ] Tested encryption/decryption
- [ ] Tested tampering detection
- [ ] Tested backward compatibility
- [ ] Backed up keys securely
- [ ] Restarted application
- [ ] Verified in production
- [ ] Documented keys location
- [ ] Briefed support team

## 🎉 You're Ready!

Once all checklist items are complete:

```
🚀 Production deployment is COMPLETE!
✅ RNet files are now encrypted and secure
✅ System is fully functional
✅ Monitoring is in place
```

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Keys Backed Up**: _______________
**Verified By**: _______________

**Status**: ⏳ READY FOR PRODUCTION DEPLOYMENT
