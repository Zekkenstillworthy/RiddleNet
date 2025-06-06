# Email Network Troubleshooting Guide

## Current Issue
The OTP functionality is experiencing DNS lookup timeouts when trying to connect to Gmail's SMTP server (`smtp.gmail.com`). The error indicates your network cannot resolve Gmail's SMTP server address.

## Quick Fix (Development Mode)
✅ **The system now includes a fallback mechanism:**
- When email sending fails due to network issues, the OTP is displayed directly in the browser
- This allows you to continue testing the login functionality
- Look for messages like: "OTP generated but email sending failed due to network issues. Your OTP is: XXXXXX (Development Mode)"

## Permanent Solutions

### Option 1: Fix Network DNS Issues
```bash
# Try flushing DNS cache (Windows)
ipconfig /flushdns
ipconfig /release
ipconfig /renew

# Test DNS resolution
nslookup smtp.gmail.com
ping smtp.gmail.com
```

### Option 2: Use Alternative DNS Servers
1. Change your DNS settings to use Google DNS:
   - Primary: 8.8.8.8
   - Secondary: 8.8.4.4

2. Or use Cloudflare DNS:
   - Primary: 1.1.1.1
   - Secondary: 1.0.0.1

### Option 3: Use Different Email Provider
Update your `.env` file to use a different SMTP provider:

**For Outlook/Hotmail:**
```env
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-app-password
```

Update `__init__.py`:
```python
app.config["MAIL_SERVER"] = "smtp-mail.outlook.com"
app.config["MAIL_PORT"] = 587
```

**For Yahoo:**
```env
MAIL_USERNAME=your-email@yahoo.com
MAIL_PASSWORD=your-app-password
```

Update `__init__.py`:
```python
app.config["MAIL_SERVER"] = "smtp.mail.yahoo.com"
app.config["MAIL_PORT"] = 587
```

### Option 4: Use Local SMTP for Development
Install and configure a local SMTP server like MailHog or smtp4dev for development:

```bash
# Using MailHog (requires Go)
go install github.com/mailhog/MailHog@latest
./MailHog

# Using smtp4dev (requires .NET)
dotnet tool install -g Rnwood.Smtp4dev
smtp4dev
```

Then update your configuration:
```python
app.config["MAIL_SERVER"] = "localhost"
app.config["MAIL_PORT"] = 1025  # MailHog default
app.config["MAIL_USE_TLS"] = False
```

## Testing Network Connectivity

### 1. Test SMTP Connection
```python
import smtplib
import socket

try:
    # Test DNS resolution
    socket.gethostbyname('smtp.gmail.com')
    print("✅ DNS resolution works")
    
    # Test SMTP connection
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print("✅ SMTP connection successful")
    server.quit()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### 2. Check Firewall/Antivirus
- Temporarily disable firewall/antivirus
- Check if corporate network blocks SMTP ports (587, 465)
- Try using a mobile hotspot to test if it's a network restriction

## Current Implementation Status

✅ **Working Features:**
- OTP generation and database storage
- User authentication flow
- Fallback mechanism for network issues
- Enhanced error handling

⚠️ **Development Mode:**
- OTP is displayed in browser when email fails
- Allows testing without working email

🔧 **Still Needs Configuration:**
- Reliable email delivery for production
- Network/DNS resolution for Gmail SMTP

## Next Steps

1. **For immediate testing:** Use the current fallback mechanism - OTP will be shown in the browser
2. **For production:** Choose one of the permanent solutions above
3. **Test the complete login flow:** Enter the displayed OTP to verify the authentication works

## Error Logs to Monitor

Check the Flask console for these error patterns:
- `socket.gaierror: [Errno 11002] Lookup timed out` - DNS issue
- `smtplib.SMTPAuthenticationError` - Credential issue
- `smtplib.SMTPException` - SMTP server issue
- `ConnectionRefusedError` - Network/firewall issue

The system now provides specific error messages for each type of failure to help with debugging.
