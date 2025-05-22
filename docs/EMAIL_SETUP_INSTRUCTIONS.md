# Email Setup Instructions

To fix the "Failed to send OTP" issue, follow these steps to set up a Gmail App Password:

1. **Enable 2-Step Verification on your Gmail account**:
   - Go to [Google Account Security Settings](https://myaccount.google.com/security)
   - Click on "2-Step Verification" and follow the steps to enable it if not already enabled

2. **Generate an App Password**:
   - Go to [App Passwords](https://myaccount.google.com/apppasswords) (you'll need to be signed in)
   - Under "Select app", choose "Mail"
   - Under "Select device", choose "Other (Custom name)" and enter "RiddleNet"
   - Click "Generate"
   - Google will display a 16-character app password (spaces are for readability, you don't need to include them)

3. **Update .env file**:
   - Open the `.env` file in your project directory
   - Replace `your_app_password_here` with the app password generated in the previous step
   - Make sure your Gmail address is correctly set in `MAIL_USERNAME`

4. **Test Email Configuration**:
   - Run `python test_email.py` and type 'y' when prompted to send a test email
   - Check your inbox to confirm the email was sent successfully

5. **If still not working**:
   - Ensure your Gmail account doesn't have security restrictions that prevent less secure apps
   - Check if your firewall or antivirus is blocking outgoing connections on port 587
   - If you're working in a corporate environment, make sure email services aren't restricted

## Common Gmail Issues and Solutions

1. **Gmail Account Locked**: If Google detects unusual activity, it might lock your account temporarily. Check for any security notifications from Google.

2. **Incorrect App Password**: Make sure you're copying the entire 16-character app password correctly (without spaces).

3. **Rate Limiting**: Gmail has sending limits. If you're sending too many emails too quickly, Google may temporarily block sending.
