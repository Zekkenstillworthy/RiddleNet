# Client-Side Encryption Compatibility Fix

## 🐛 Issue Fixed

**Error**: `File integrity check failed: Missing required encryption fields`

**Location**: RNet Viewer when trying to load student-exported files

**Root Cause**: The server-side encryption validation code expected HMAC signatures (`integrity_signature`) that client-side Base64 encryption doesn't provide.

## ✅ Fix Applied

Updated `utils/rnet_encryption.py` to handle **two encryption formats**:

### Format 1: Client-Side Base64 Encryption (Students)
```json
{
  "format": "rnetfile_encrypted",
  "version": "2.0",
  "encrypted_data": "base64_encoded_json",
  "metadata": {
    "encryption_method": "client_base64_obfuscation"
  }
}
```

### Format 2: Server-Side AES-256 Encryption (Instructors)
```json
{
  "format": "rnetfile_encrypted",
  "version": "2.0",
  "encrypted_data": "aes_encrypted_data",
  "iv": "initialization_vector",
  "integrity_signature": "hmac_signature",
  "encryption_metadata": {
    "algorithm": "AES-256-CBC"
  }
}
```

## 📝 Code Changes

### File: `utils/rnet_encryption.py`

#### 1. Updated `decrypt_rnet_data()` method (Line ~118)

**Added detection and handling for client-side encryption**:

```python
# Check if this is client-side Base64 encryption (from student exports)
encryption_metadata = encrypted_data.get('metadata', {})
encryption_method = encryption_metadata.get('encryption_method', '')

if encryption_method == 'client_base64_obfuscation':
    encrypted_b64 = encrypted_data.get('encrypted_data')
    if not encrypted_b64:
        raise ValueError('Missing encrypted_data field')
    
    try:
        # Decode Base64
        decoded_str = base64.b64decode(encrypted_b64).decode('utf-8')
        # Parse JSON
        decrypted_data = json.loads(decoded_str)
        return decrypted_data
    except Exception as e:
        raise ValueError(f'Client-side decryption failed: {str(e)}')

# Handle server-side AES-256 encryption (from instructor exports)
# ... existing AES decryption code ...
```

#### 2. Updated `validate_integrity()` method (Line ~252)

**Added validation for client-side encrypted files**:

```python
# Check if this is client-side Base64 encryption (from student exports)
encryption_metadata = data.get('metadata', {})
encryption_method = encryption_metadata.get('encryption_method', '')

if encryption_method == 'client_base64_obfuscation':
    # Client-side encryption doesn't have HMAC, so just verify the data exists
    encrypted_b64 = data.get('encrypted_data')
    if not encrypted_b64:
        return False, 'Missing encrypted_data field'
    # Client-side encryption is valid if it has encrypted_data
    return True, None

# Server-side AES encryption validation
# ... existing HMAC validation code ...
```

## 🔄 How It Works Now

### Student Export → Import Flow:

```
Student exports simulation
         ↓
Client-side Base64 encryption
         ↓
File saved: {format: "rnetfile_encrypted", metadata: {encryption_method: "client_base64_obfuscation"}}
         ↓
Instructor uploads to RNet Viewer
         ↓
validate_integrity() detects client-side encryption
         ↓
✅ Validation passes (no HMAC check needed)
         ↓
decrypt_rnet_data() detects client-side format
         ↓
Base64 decode → JSON parse
         ↓
✅ File displayed in viewer
```

### Instructor Export → Import Flow:

```
Instructor exports simulation
         ↓
Server-side AES-256-CBC encryption + HMAC
         ↓
File saved: {format: "rnetfile_encrypted", encrypted_data, iv, integrity_signature}
         ↓
Anyone uploads to RNet Viewer
         ↓
validate_integrity() detects server-side encryption
         ↓
✅ HMAC signature validated
         ↓
decrypt_rnet_data() uses AES decryption
         ↓
✅ File displayed in viewer (if signature valid)
❌ Rejected if tampered with
```

## 🧪 Testing

### Test 1: Student-Exported File

1. **Export from student portal**:
   - Go to simulation as student
   - Click Save button
   - File downloads with Base64 encryption

2. **Upload to RNet Viewer**:
   - Go to `/instructor/rnet/viewer`
   - Drag & drop the .rnet file
   - **Expected**: ✅ File loads successfully

3. **Console output should show**:
   ```
   [INFO] Encrypted RNet file detected
   [OK] Integrity check passed
   [OK] File decrypted successfully
   ✅ Simulation data displayed
   ```

### Test 2: Instructor-Exported File

1. **Export from instructor portal**:
   - Go to simulation editor
   - Export simulation
   - File downloads with AES-256 encryption

2. **Upload to RNet Viewer**:
   - Drag & drop the .rnet file
   - **Expected**: ✅ File loads successfully with HMAC validation

3. **Console output should show**:
   ```
   [INFO] Encrypted RNet file detected
   [OK] Integrity check passed (HMAC validated)
   [OK] File decrypted successfully
   ✅ Simulation data displayed
   ```

### Test 3: Legacy Unencrypted File

1. **Upload old .rnet file** (before encryption was added)
2. **Expected**: ✅ File loads successfully (backward compatible)
3. **Console output**:
   ```
   [INFO] Unencrypted RNet file (legacy format)
   ✅ Simulation data displayed
   ```

### Test 4: Tampered File

1. **Export file as instructor** (with AES encryption)
2. **Open in Notepad and modify `encrypted_data`**
3. **Upload to RNet Viewer**
4. **Expected**: ❌ Rejected with integrity error
5. **Console output**:
   ```
   [ERROR] Integrity check failed: file has been tampered with
   ❌ File rejected
   ```

## 📊 Encryption Method Detection Logic

```python
def detect_encryption_type(rnet_data):
    """Pseudocode showing detection logic"""
    
    # Not encrypted at all?
    if rnet_data.get('format') == 'rnetfile':
        return 'LEGACY_UNENCRYPTED'
    
    # Not in encrypted format?
    if rnet_data.get('format') != 'rnetfile_encrypted':
        return 'INVALID'
    
    # Check metadata for encryption method
    metadata = rnet_data.get('metadata', {})
    method = metadata.get('encryption_method', '')
    
    # Client-side Base64?
    if method == 'client_base64_obfuscation':
        return 'CLIENT_BASE64'
    
    # Has HMAC signature?
    if rnet_data.get('integrity_signature'):
        return 'SERVER_AES256'
    
    return 'UNKNOWN'
```

## 🎯 Supported Formats Summary

| Format | Encryption | Integrity Check | Source | Status |
|--------|-----------|-----------------|--------|---------|
| `rnetfile` (v1.0) | None | N/A | Legacy exports | ✅ Supported |
| `rnetfile_encrypted` (v2.0) with `client_base64_obfuscation` | Base64 | None | Student exports | ✅ Supported |
| `rnetfile_encrypted` (v2.0) with HMAC | AES-256-CBC | HMAC-SHA256 | Instructor exports | ✅ Supported |

## 🔐 Security Comparison

### Client-Side (Student):
- **Encryption**: Base64 encoding
- **Integrity**: None (file format validation only)
- **Tampering Detection**: ❌ No
- **Decryption**: Anyone can decode Base64
- **Use Case**: Basic obfuscation for student work

### Server-Side (Instructor):
- **Encryption**: AES-256-CBC with random IV
- **Integrity**: HMAC-SHA256 signature
- **Tampering Detection**: ✅ Yes (cryptographic)
- **Decryption**: Requires secret key (server-only)
- **Use Case**: Secure distribution of official content

## 📋 Summary

**What was broken**: 
- RNet Viewer rejected student-exported files
- Expected HMAC signatures that don't exist in Base64 encryption

**What was fixed**:
- ✅ `decrypt_rnet_data()` now detects and handles Base64 format
- ✅ `validate_integrity()` skips HMAC check for Base64 files
- ✅ Both encryption types now work in RNet Viewer
- ✅ Backward compatibility maintained for legacy files

**Impact**:
- Students can export and instructors can view their files
- Instructors get full AES-256 encryption with tamper detection
- No breaking changes to existing functionality

**Files Modified**:
- `utils/rnet_encryption.py` (~30 lines modified)

**Testing Status**:
- ✅ Ready to test with student-exported files
- ✅ Instructor files should continue working
- ✅ Legacy files should continue working

---

**Fix Applied**: October 29, 2025
**Status**: ✅ Ready for Testing
**Encryption Support**: Client Base64 + Server AES-256 + Legacy Unencrypted
