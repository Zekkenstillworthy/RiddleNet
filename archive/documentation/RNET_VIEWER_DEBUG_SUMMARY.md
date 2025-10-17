# RNet Viewer Debug Logging Summary

## Overview
Comprehensive debug logging has been added to the RNet file viewer to help diagnose why .rnet files are not loading properly.

## Changes Made

### Frontend Debug Logging (`templates/admin/rnet_file_viewer.html`)

#### 1. **Initialization Logging**
- ✅ Page load detection
- ✅ Modal element verification
- ✅ File input element verification
- ✅ Event listener attachment confirmation
- ✅ Current page URL and API endpoint logging

#### 2. **File Selection Debug Logs**
- ✅ File select event detection
- ✅ File object details (name, size, type, lastModified)
- ✅ Files count validation
- ✅ Extension validation feedback

#### 3. **File Upload Debug Logs**
- ✅ File validation step confirmation
- ✅ FormData creation logging
- ✅ API request URL and method
- ✅ Request details (file size, name, content type)

#### 4. **Network Request/Response Logs**
- ✅ Response status and headers
- ✅ Response OK status check
- ✅ Parsed JSON data structure
- ✅ Success/failure determination
- ✅ Error details with stack trace

#### 5. **Data Display Logging**
- ✅ Section toggle verification (upload/display)
- ✅ Element existence checks for all content containers
- ✅ Data population confirmation for each section
- ✅ QR code data validation
- ✅ HTML content setting confirmation

#### 6. **Drag & Drop Logging**
- ✅ Drag events (over, leave, drop)
- ✅ Files count in drop event
- ✅ File details from drag/drop

### Backend Debug Logging (`admin/routes/rnet_viewer_routes.py`)

#### 1. **Request Reception Logs**
- ✅ Request method and content type
- ✅ Available request.files keys
- ✅ Available request.form keys
- ✅ File object details

#### 2. **File Validation Logs**
- ✅ Filename validation
- ✅ Extension validation
- ✅ File empty check

#### 3. **File Parsing Logs**
- ✅ File content reading (length, preview)
- ✅ JSON parsing status
- ✅ Top-level keys in parsed data
- ✅ Format validation
- ✅ Data structure keys (simulation, verification, export_metadata)

#### 4. **Error Handling Logs**
- ✅ Unicode decode errors with details
- ✅ JSON parse errors with position
- ✅ Format validation failures
- ✅ Critical errors with full traceback

#### 5. **Response Preparation Logs**
- ✅ Response data structure keys
- ✅ QR code inclusion status
- ✅ Success confirmation

## Debug Console Output Format

### Console Log Emoji Guide
- 🚀 Initialization
- 📋 Configuration/State
- 📁 File operations
- 📂 File selection
- 📥 File drop
- 🎯 Drag events
- 🔍 Inspection/Debugging
- ✅ Success
- ⚠️ Warning
- ❌ Error
- 📦 Data packages
- 📨 Network responses
- 🌐 API calls
- ⏳ Loading states
- 🎨 UI updates
- 📝 Data display
- 🔲 QR code operations
- 📄 File details

### Backend Log Format
```
================================================================================
🔍 RNET FILE PARSE REQUEST
================================================================================
📋 Request method: POST
📋 Request content type: multipart/form-data
...
✅ PARSE SUCCESSFUL - Returning response
================================================================================
```

## How to Use Debug Logs

### 1. **Open Browser DevTools**
   - Press F12 or right-click → Inspect
   - Go to Console tab

### 2. **Try Uploading a .rnet File**
   - Click "Choose File" or drag/drop a .rnet file
   - Watch the console for debug output

### 3. **Check Backend Logs**
   - Look at the terminal/console where Flask is running
   - Search for the colorful emoji-prefixed logs

## Common Issues to Diagnose

### Issue: No response after file selection
**Check for:**
- ❌ File input not found
- ❌ Event listener not attached
- ❌ Fetch request not sent

### Issue: File uploads but nothing displays
**Check for:**
- ❌ Response data.success = false
- ❌ Display section elements not found
- ❌ HTML not being set in content containers

### Issue: Backend error
**Check for:**
- ❌ Invalid JSON format
- ❌ Missing 'format' field
- ❌ Unicode decode errors
- ❌ File not found in request.files

### Issue: QR code not showing
**Check for:**
- ❌ qr_code_included = false
- ❌ qr_code_base64 empty or null
- ❌ QR section hidden

## Debug Checklist

When testing, verify each step logs successfully:

### Frontend Flow
1. ✅ Page loads → "🚀 RNet Viewer initialized"
2. ✅ File selected → "📂 File select event triggered"
3. ✅ File validated → "✅ File validation passed"
4. ✅ Request sent → "🌐 Sending POST request to: /rnet/api/parse"
5. ✅ Response received → "📨 Response received"
6. ✅ Data parsed → "📦 Response data received"
7. ✅ UI updated → "✅ displayFileData completed"

### Backend Flow
1. ✅ Request received → "🔍 RNET FILE PARSE REQUEST"
2. ✅ File extracted → "✅ File object received"
3. ✅ File validated → "✅ File validation passed"
4. ✅ JSON parsed → "✅ JSON parsed successfully"
5. ✅ Format validated → "✅ RNet format validation passed"
6. ✅ Response prepared → "✅ Response data prepared successfully"
7. ✅ Response sent → "✅ PARSE SUCCESSFUL - Returning response"

## Next Steps

After implementing these logs:

1. **Test with a sample .rnet file**
2. **Copy the console output** (both browser and backend)
3. **Identify where the flow breaks**
4. **Look for the last successful ✅ log before an error**
5. **Check the specific error message**

## Testing Guide

### Create a Test .rnet File
```json
{
    "format": "rnetfile",
    "version": "1.0",
    "exported_at": "2025-10-08T19:00:00Z",
    "exported_by": "Test User",
    "simulation": {
        "id": 1,
        "title": "Test Simulation",
        "description": "A test simulation",
        "simulation_type": "Troubleshooting",
        "category": "Networking",
        "difficulty": "Beginner",
        "estimated_duration": 30
    },
    "verification": {
        "qr_code_included": true,
        "qr_code_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "confirmation_url": "http://127.0.0.1:5001/verify",
        "instructions": "Scan to verify"
    },
    "export_metadata": {
        "test_mode": true,
        "platform": "RiddleNet"
    }
}
```

Save as `test.rnet` and upload to verify all logging works.

## Expected Output Example

### Browser Console
```javascript
🚀 RNet Viewer initialized
📋 Loading modal element: Found
📁 File input element: Found
✅ File input change listener attached
📂 File select event triggered
✅ File selected: {name: "test.rnet", size: 567, ...}
✅ File validation passed
📦 FormData created with file: test.rnet
⏳ Showing loading modal
🌐 Sending POST request to: /rnet/api/parse
📨 Response received: {status: 200, ok: true, ...}
📦 Response data received: {success: true, ...}
✅ File parsed successfully
🎨 displayFileData called
✅ Sections toggled - upload hidden, display shown
📝 Displaying file info...
✅ File info HTML set
...
✅ displayFileData completed
```

### Backend Terminal
```
================================================================================
🔍 RNET FILE PARSE REQUEST
================================================================================
📋 Request method: POST
📋 Request content type: multipart/form-data; ...
✅ File object received: <FileStorage: 'test.rnet' ...>
📄 Filename: test.rnet
✅ File validation passed
📖 Reading file content...
✅ File read successfully, length: 567 characters
🔧 Parsing JSON...
✅ JSON parsed successfully
✅ RNet format validation passed
✅ Response data prepared successfully
================================================================================
✅ PARSE SUCCESSFUL - Returning response
================================================================================
```

## Troubleshooting Tips

1. **If no logs appear at all:**
   - Check if JavaScript is enabled
   - Check browser console for syntax errors
   - Verify the page loaded correctly

2. **If logs stop at a certain point:**
   - That's where the issue occurs
   - Read the last error message carefully
   - Check for missing elements or network issues

3. **If backend shows errors:**
   - Look at the error type (JSONDecodeError, etc.)
   - Check the file format matches expected structure
   - Verify all required fields are present

## File Modified
- ✅ `templates/admin/rnet_file_viewer.html` - Added comprehensive frontend logging
- ✅ `admin/routes/rnet_viewer_routes.py` - Added detailed backend logging

## Date
October 8, 2025

## Status
✅ Debug logging fully implemented and ready for testing
