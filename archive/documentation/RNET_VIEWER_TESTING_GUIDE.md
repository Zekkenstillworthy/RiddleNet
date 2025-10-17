# RNet Viewer Testing Guide

## Quick Start

### Step 1: Open the RNet Viewer
1. Navigate to: `http://127.0.0.1:5001/rnet/viewer`
2. Open Browser DevTools (F12)
3. Go to Console tab

### Step 2: Check Initialization
Look for these logs in the console:
```
🚀 RNet Viewer initialized
📋 Loading modal element: Found
📁 File input element: Found
✅ File input change listener attached
```

If any show "NOT FOUND", there's an issue with the page template.

### Step 3: Upload a .rnet File
Click "Choose File" or drag/drop a .rnet file.

### Step 4: Monitor Both Consoles

#### Browser Console Should Show:
```
📂 File select event triggered
✅ File selected: {name: "file.rnet", size: X, ...}
✅ File validation passed
📦 FormData created
⏳ Showing loading modal
🌐 Sending POST request to: /rnet/api/parse
📨 Response received: {status: 200, ok: true}
📦 Response data received
✅ File parsed successfully
🎨 displayFileData called
✅ displayFileData completed
```

#### Backend Terminal Should Show:
```
================================================================================
🔍 RNET FILE PARSE REQUEST
================================================================================
📋 Request method: POST
✅ File object received
✅ File validation passed
✅ JSON parsed successfully
✅ RNet format validation passed
✅ Response data prepared successfully
✅ PARSE SUCCESSFUL - Returning response
================================================================================
```

## Common Problems & Solutions

### Problem 1: File Not Loading At All

**Symptoms:**
- No logs after file selection
- Nothing happens when clicking "Choose File"

**Check:**
```
📁 File input element: Found  ← Should see this
✅ File input change listener attached  ← Should see this
```

**Solution:**
- If "NOT FOUND", the HTML template has an issue
- Verify `<input type="file" id="rnet-file-input">` exists

---

### Problem 2: File Uploads But Nothing Displays

**Symptoms:**
- Upload completes
- Loading modal closes
- Page stays on upload screen

**Check Browser Console:**
```
📦 Response data received: {...}  ← Look at this object
```

**Common Causes:**
1. `data.success = false` - Backend parsing failed
2. Elements not found - Check for:
   ```
   📋 Upload section: NOT FOUND  ← BAD
   📋 Display section: NOT FOUND  ← BAD
   ```

**Solution:**
- If `success: false`, check backend logs for error details
- If elements not found, verify HTML IDs match:
  - `upload-section`
  - `display-section`
  - `file-info-content`
  - `simulation-info-content`

---

### Problem 3: Backend Error 400 (No File)

**Backend Shows:**
```
❌ No 'file' key in request.files
```

**Cause:**
- Form data not sent correctly
- File input name doesn't match

**Solution:**
- Verify `formData.append('file', file)` in JavaScript
- Check network tab for request payload

---

### Problem 4: Backend Error 400 (Invalid Format)

**Backend Shows:**
```
❌ Invalid file extension: something.txt
```
OR
```
❌ Invalid RNet file format: wrongformat
```

**Solution:**
- Ensure file ends with `.rnet`
- Ensure JSON contains `"format": "rnetfile"`

---

### Problem 5: JSON Parse Error

**Backend Shows:**
```
❌ JSON decode error: ...
   Line: X, Column: Y
```

**Cause:**
- Invalid JSON in .rnet file
- Missing commas, brackets, quotes

**Solution:**
- Validate JSON at https://jsonlint.com/
- Check the exact line/column mentioned in error

---

### Problem 6: QR Code Not Showing

**Browser Console:**
```
⚠️ No QR code found, hiding QR section
```

**Backend Shows:**
```
📋 QR code included: false
```

**Cause:**
- .rnet file doesn't have QR code data
- `verification.qr_code_included = false`
- Missing `qr_code_base64` field

**Solution:**
- Check .rnet file has:
  ```json
  "verification": {
      "qr_code_included": true,
      "qr_code_base64": "..."
  }
  ```

---

## Test .rnet File Template

Save this as `test.rnet`:

```json
{
    "format": "rnetfile",
    "version": "1.0",
    "exported_at": "2025-10-08T19:00:00Z",
    "exported_by": "Admin User",
    "simulation": {
        "id": 1,
        "title": "Network Troubleshooting Scenario",
        "description": "A comprehensive network troubleshooting exercise",
        "simulation_type": "Troubleshooting",
        "category": "Networking",
        "difficulty": "Intermediate",
        "estimated_duration": 45
    },
    "verification": {
        "qr_code_included": true,
        "qr_code_base64": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mNk+M9Qz0AEYBxVSF+FADhVAwM0AgzhAAAAAElFTkSuQmCC",
        "confirmation_url": "http://127.0.0.1:5001/verify",
        "instructions": "Scan this QR code to verify simulation ownership"
    },
    "export_metadata": {
        "exported_from": "RiddleNet Admin Panel",
        "platform_version": "1.0",
        "checksum": "abc123def456",
        "total_steps": 5,
        "requires_review": false
    }
}
```

This should work perfectly and show all features.

---

## Debug Checklist

Before reporting an issue, check:

- [ ] Browser console shows initialization logs
- [ ] File input element is found
- [ ] File selection triggers event
- [ ] File passes validation
- [ ] Network request is sent (check Network tab)
- [ ] Response status is 200
- [ ] Response contains `success: true`
- [ ] Backend shows successful parse logs
- [ ] Display section appears
- [ ] All content sections populated

---

## Network Tab Inspection

### Check the Request:
1. Open DevTools → Network tab
2. Upload a file
3. Look for `parse` request
4. Check:
   - **Method:** POST
   - **Status:** 200
   - **Type:** xhr or fetch

### View Request Details:
- **Headers tab:** Should show `Content-Type: multipart/form-data`
- **Payload tab:** Should show the uploaded file
- **Response tab:** Should show JSON with `success: true`

---

## Quick Diagnosis Table

| Symptom | Location | Check |
|---------|----------|-------|
| No upload button works | Browser Console | `File input element: Found` |
| File selected but nothing happens | Browser Console | Look for `handleFile called` |
| Request fails immediately | Browser Console | Check `Response received` status |
| 400 error | Backend Terminal | Look for specific error message |
| 500 error | Backend Terminal | Check full traceback |
| Data loads but page blank | Browser Console | Check element existence logs |
| QR code missing | Browser Console | Check `QR code found` message |

---

## Support Information

If issues persist after checking all logs:

1. **Copy full console output** (both browser and backend)
2. **Copy the .rnet file content**
3. **Note the exact error message**
4. **Include browser and OS version**

This will help diagnose the root cause quickly.

---

## Success Indicators

You know it's working when:
- ✅ File uploads without errors
- ✅ Upload section disappears
- ✅ Display section appears with data
- ✅ File information shows correctly
- ✅ Simulation details display
- ✅ QR code appears (if included)
- ✅ Export metadata shows
- ✅ No red ❌ logs in console

---

## Date
October 8, 2025

## Status
✅ Ready for testing
