# 🔐 RNet File Encryption - What You Need to Know

## What Changed?

**Before**: You could open `.rnet` files in Notepad and edit them
**After**: `.rnet` files are encrypted and tamper-proof

## Why This Matters

✅ **Prevents Cheating**: Students can't edit simulation files to change scores
✅ **Data Integrity**: Files are verified for tampering automatically  
✅ **Security**: Simulation content is protected from unauthorized modifications

## What This Means for You

### As a User (Student/Instructor)

**Nothing changes!** The encryption is completely transparent:

- 📥 **Export** works exactly the same
- 📤 **Import** works exactly the same
- 👁️ **View** works exactly the same
- 💾 **Save** works exactly the same

You won't even notice the difference!

### What You'll See

When you open a `.rnet` file in Notepad now, instead of seeing:

```json
{
  "format": "rnetfile",
  "simulation": {
    "title": "My Simulation",
    ...
  }
}
```

You'll see:

```json
{
  "format": "rnetfile_encrypted",
  "version": "2.0",
  "encrypted_data": "U2FsdGVkX1...",
  "iv": "Bm9yIHlvdXI...",
  ...
}
```

**This is normal and expected!** The file is encrypted for security.

## What You CAN'T Do Anymore

❌ Edit `.rnet` files in Notepad
❌ Modify simulation scores manually
❌ Change simulation content
❌ Tamper with validation rules

## What You CAN Still Do

✅ Export simulations
✅ Import simulations  
✅ Share `.rnet` files
✅ View file information
✅ Use all existing features

## If You Get an Error

### "Integrity check failed"

**What it means**: The file was modified or corrupted

**What to do**: 
1. Re-download the original file
2. Don't try to edit it in Notepad
3. Contact your instructor if the error persists

### "Decryption failed"

**What it means**: The file is corrupted or invalid

**What to do**:
1. Check you're using the correct file
2. Try re-downloading it
3. Contact support if the issue continues

## For Instructors

### Everything Works Automatically

- Export → Encrypted automatically
- Import → Decrypted automatically
- Share files → Students can use them normally

### Old Files Still Work

- Files from before encryption work fine
- They'll be encrypted when exported again
- No need to re-create anything

## Technical Details (Optional)

- **Encryption**: AES-256-CBC (military-grade)
- **Integrity**: HMAC-SHA256 verification
- **Format**: JSON with base64 encoding
- **Performance**: < 2ms per file (imperceptible)

## Need Help?

1. Check if the file was modified in Notepad (don't do this!)
2. Try re-downloading the original file
3. Contact your system administrator
4. Report persistent issues

## Bottom Line

🔒 **Files are now secure and tamper-proof**
🚀 **Everything works exactly the same for you**
✨ **No action required on your part**

---

**Questions?** This is a security enhancement that protects simulation integrity while maintaining full functionality.
