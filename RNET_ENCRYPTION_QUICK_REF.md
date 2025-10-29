# RNet Encryption Quick Reference

## 🔐 What Changed?

**Before**: `.rnet` files were plain JSON - anyone could edit them in Notepad
**After**: `.rnet` files are encrypted and tamper-proof

## ✅ Key Features

- **AES-256 Encryption** - Military-grade security
- **Tamper Detection** - HMAC integrity checks
- **Backward Compatible** - Old files still work
- **Automatic** - Transparent to users
- **Safe** - Graceful fallback on errors

## 🚀 Quick Start

### For Developers

No code changes needed! Everything is automatic:

```python
# Export (automatically encrypted)
GET /instructor/simulations/api/<id>/export

# Import (automatically decrypted)  
POST /instructor/simulations/api/<id>/import

# View (automatically decrypted)
POST /instructor/rnet/api/parse
```

### For Administrators

**Production Setup** (IMPORTANT):

```bash
# Set unique encryption keys
set RNET_ENCRYPTION_KEY=your-secure-key-minimum-32-characters-long
set RNET_HMAC_KEY=your-secure-hmac-key-minimum-32-characters
```

**Generate Secure Keys**:

```python
import os, base64
print(f"ENCRYPTION: {base64.b64encode(os.urandom(32)).decode()}")
print(f"HMAC: {base64.b64encode(os.urandom(32)).decode()}")
```

## 📦 File Format

### Encrypted File
```json
{
  "format": "rnetfile_encrypted",
  "version": "2.0",
  "encrypted_data": "...",
  "iv": "...",
  "integrity_signature": "...",
  "visible_metadata": {
    "simulation_title": "Network Lab"
  }
}
```

### Legacy File (Still Supported)
```json
{
  "format": "rnetfile",
  "version": "1.0",
  "simulation": {...}
}
```

## 🛠️ Common Tasks

### Check if File is Encrypted
```python
from utils.rnet_encryption import is_encrypted_rnet
if is_encrypted_rnet(data):
    print("Encrypted!")
```

### Validate File Integrity
```python
from utils.rnet_encryption import validate_rnet_integrity
is_valid, error = validate_rnet_integrity(data)
if not is_valid:
    print(f"Tampered! {error}")
```

### Manual Encryption
```python
from utils.rnet_encryption import encrypt_rnet_file
encrypted = encrypt_rnet_file(rnet_data)
```

### Manual Decryption
```python
from utils.rnet_encryption import decrypt_rnet_file
original = decrypt_rnet_file(encrypted_data)
```

## ⚠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| "Integrity check failed" | File was tampered - get original |
| "Decryption failed" | Check encryption keys |
| Old files not working | Should work automatically - check logs |
| Performance slow | Encryption adds <50ms - negligible |

## 🔍 Testing

```python
# Quick test
from utils.rnet_encryption import *

data = {'format': 'rnetfile', 'simulation': {}}
encrypted = encrypt_rnet_file(data)
decrypted = decrypt_rnet_file(encrypted)
assert data == decrypted
print("✅ Works!")
```

## 📋 Production Checklist

- [ ] Set `RNET_ENCRYPTION_KEY` environment variable
- [ ] Set `RNET_HMAC_KEY` environment variable
- [ ] Test export → import cycle
- [ ] Verify tampering detection
- [ ] Check old files still work
- [ ] Monitor logs for errors

## 💡 Key Points

1. **Automatic** - No user action required
2. **Secure** - Can't edit files in Notepad anymore
3. **Compatible** - Old files work fine
4. **Safe** - Falls back gracefully on errors
5. **Fast** - No noticeable performance impact

## 🎯 What Users See

**Nothing different!** 
- Export works the same
- Import works the same
- Files look slightly different in text editor (encrypted)
- But users don't need to care

## 📚 More Info

See full documentation: `RNET_ENCRYPTION_GUIDE.md`

---

**TL;DR**: Files are now encrypted and tamper-proof. Set encryption keys in production. Everything else is automatic.
