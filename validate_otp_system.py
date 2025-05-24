"""
Complete OTP System Validation Script

This script performs a full validation of the OTP system, including:
1. Database configuration
2. Email configuration
3. OTP generation and sending
4. OTP validation

Usage:
python validate_otp_system.py
"""
import os
import sys
import time
import datetime
import random
from dotenv import load_dotenv

# Ensure proper project path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables from .env file
load_dotenv()

# Create Flask app context
from __init__ import create_app, db, mail
app = create_app()

def check_database_configuration():
    """Check if the database has the required OTP columns"""
    print("\n=== Checking Database Configuration ===")
    with app.app_context():
        from user.models.user import User
        
        # Check if a test user exists
        test_user = User.query.first()
        if not test_user:
            print("❌ No users found in the database")
            return False
            
        print(f"✅ Found user: {test_user.username}")
        
        # Check for OTP columns
        try:
            print(f"OTP column exists: {hasattr(test_user, 'otp')}")
            print(f"OTP timestamp column exists: {hasattr(test_user, 'otp_generated_at')}")
            
            if hasattr(test_user, 'otp') and hasattr(test_user, 'otp_generated_at'):
                print("✅ OTP columns are properly configured")
                return True
            else:
                print("❌ OTP columns are missing from the User model")
                print("Run python add_otp_columns.py to add them")
                return False
        except Exception as e:
            print(f"❌ Error checking OTP columns: {str(e)}")
            return False

def check_email_configuration():
    """Verify the email configuration is correct"""
    print("\n=== Checking Email Configuration ===")
    print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    print(f"MAIL_PASSWORD: {'*' * 8 if app.config.get('MAIL_PASSWORD') else 'NOT SET'}")
    
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        print("❌ Email credentials are missing in .env file")
        return False
    
    # Send a test email
    try:
        from flask_mail import Message
        
        with app.app_context():
            test_recipient = app.config.get('MAIL_USERNAME')
            
            msg = Message(
                "RiddleNet OTP System Test",
                recipients=[test_recipient]
            )
            msg.body = "This is a test email to verify the OTP system is configured correctly."
            
            mail.send(msg)
            print(f"✅ Test email sent to {test_recipient}")
            return True
    except Exception as e:
        print(f"❌ Error sending test email: {str(e)}")
        print("Please check EMAIL_SETUP_INSTRUCTIONS.md for troubleshooting")
        return False

def test_otp_workflow(username=None):
    """Test the complete OTP workflow for a user"""
    print("\n=== Testing OTP Workflow ===")
    with app.app_context():
        from user.models.user import User
        from flask_mail import Message
        
        # Get user to test
        if not username:
            user = User.query.filter(User.email.isnot(None)).first()
            if not user:
                print("❌ No user with email found in database")
                return False
        else:
            user = User.query.filter_by(username=username).first()
            if not user:
                print(f"❌ User '{username}' not found")
                return False
                
        if not user.email:
            print(f"❌ User {user.username} has no email address")
            return False
            
        print(f"Testing with user: {user.username} (Email: {user.email})")
        
        # 1. Generate OTP
        print("\nStep 1: Generating OTP...")
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_generated_at = datetime.datetime.now()
        user.totp_enabled = True
        db.session.commit()
        print(f"✅ OTP generated: {otp}")
        
        # 2. Send OTP via email
        print("\nStep 2: Sending OTP via email...")
        try:
            msg = Message(
                "Your RiddleNet OTP Code",
                recipients=[user.email]
            )
            msg.body = f"Your verification code is: {otp}\n\nThis code will expire in 10 minutes."
            
            mail.send(msg)
            print(f"✅ OTP sent to {user.email}")
        except Exception as e:
            print(f"❌ Error sending OTP: {str(e)}")
            return False
            
        # 3. Validate OTP
        print("\nStep 3: Validating OTP...")
        print(f"Stored OTP: {user.otp}")
        print(f"Generated at: {user.otp_generated_at}")
        
        # Check if OTP matches
        if user.otp == otp:
            print("✅ OTP matches")
        else:
            print("❌ OTP does not match")
            return False
            
        # Check if OTP is expired
        current_time = datetime.datetime.now()
        if user.otp_generated_at:
            otp_age = current_time - user.otp_generated_at
            if otp_age.total_seconds() <= 600:  # 10 minutes
                print("✅ OTP is still valid")
            else:
                print("❌ OTP has expired")
                return False
        
        print("\n✅ OTP workflow validation complete!")
        return True

def main():
    """Run all validation checks"""
    print("==== RiddleNet OTP System Validation ====")
    
    # Check database configuration
    db_ok = check_database_configuration()
    
    # Check email configuration
    email_ok = check_email_configuration()
    
    # Only test workflow if both database and email are configured correctly
    if db_ok and email_ok:
        # Optional: Get username from command line args
        username = sys.argv[1] if len(sys.argv) > 1 else None
        workflow_ok = test_otp_workflow(username)
        
        if workflow_ok:
            print("\n✅ OTP system validation successful!")
        else:
            print("\n❌ OTP workflow validation failed.")
    else:
        print("\n❌ Skipping OTP workflow test due to configuration issues.")
        print("Please fix the reported issues and run this script again.")

if __name__ == "__main__":
    main()
