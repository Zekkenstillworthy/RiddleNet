# RiddleNet Email OTP Authentication

This application uses email-based One-Time Passwords (OTP) for two-factor authentication. When a user attempts to log in, they can request an OTP code which will be sent to their email address.

## Setup Instructions

1. Make sure you have installed all required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up your email credentials in the `.env` file:
   ```
   MAIL_USERNAME=your_gmail_address@gmail.com
   MAIL_PASSWORD=your_app_password
   ```

3. If using Gmail, you'll need to create an App Password:
   - Go to your Google Account settings: https://myaccount.google.com/security
   - Enable 2-Step Verification if not already enabled
   - Navigate to App Passwords (under "Signing in to Google")
   - Select "Mail" as the app and "Other" as device (name it "RiddleNet")
   - Copy the generated app password and use it as MAIL_PASSWORD in your .env file

4. Check for detailed setup instructions in `EMAIL_SETUP_INSTRUCTIONS.md`

5. Test your email configuration:
   ```
   python test_email.py
   ```

<<<<<<< HEAD
6. Validate the complete OTP system:
   ```
   python validate_otp_system.py
   ```

7. Start the application:
=======
6. Start the application:
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26
   ```
   python run.py
   ```

## OTP Authentication Flow

1. User enters their username and password on the login form
2. User clicks "Request OTP" button
3. An OTP code is generated and sent to the user's email address
4. User enters the OTP code in the login form
5. If the OTP code is valid, the user is logged in

## Security Features

- OTP codes expire after 10 minutes
- OTP codes are single-use (cleared after successful validation)
- OTP codes are 6 digits, providing adequate security while being easy to type

## Troubleshooting

### "Failed to send OTP" Error

If you're getting a "Failed to send OTP" error, try the following steps:

1. **Check Email Configuration**:
   - Make sure your `.env` file has the correct email credentials
   - If using Gmail, verify you're using an App Password and not your regular password
   - Run `python test_email.py` to test the email configuration

2. **Validate System Setup**:
<<<<<<< HEAD
   - Run `python validate_otp_system.py` to check all components
   - Check if your OTP columns are properly added to the database with `python add_otp_columns.py`
=======
   - Ensure that your database has the OTP columns (otp and otp_generated_at)
   - You can verify this by checking your user table schema in the database
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26

3. **Common Email Issues**:
   - Gmail security might block the app - check your Gmail security settings
   - Some networks block port 587 (TLS) - try using a different network
   - Rate limiting - Gmail limits how many emails you can send in a day

4. **Debug Process**:
   - Check the Flask application logs for detailed error messages
   - Use the test scripts provided to isolate which part of the system is failing

See `EMAIL_SETUP_INSTRUCTIONS.md` and `OTP_TESTING_GUIDE.md` for more detailed troubleshooting steps.

## Resources

- [Flask-Mail Documentation](https://pythonhosted.org/Flask-Mail/)
- [Google App Passwords](https://support.google.com/accounts/answer/185833)
- [SMTP Port Configuration](https://support.google.com/mail/answer/7126229)

- If you're not receiving OTP emails, check your spam folder
- Make sure your Gmail App Password is correctly configured
- Make sure the email address associated with your account is correct
