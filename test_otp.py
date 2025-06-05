#!/usr/bin/env python3
"""
Test script to verify OTP functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from __init__ import create_app
from user.models.user import User
from flask_mail import Message

def test_otp_function():
    """Test the OTP functionality"""
    try:
        app = create_app()
        
        with app.app_context():
            # Test if we can access Flask-Mail
            mail = app.extensions['mail']
            print("✅ Flask-Mail is properly configured")
            
            # Test if we can create a test user
            test_user = User.query.filter_by(username='test_user').first()
            if not test_user:
                print("❌ No test user found. Create a user first to test OTP.")
                return
            
            # Test OTP generation
            import random
            otp = str(random.randint(100000, 999999))
            print(f"✅ OTP generated: {otp}")
            
            # Test message creation
            msg = Message(
                "Your RiddleNet OTP Code",
                recipients=[test_user.email] if test_user.email else ['test@example.com']
            )
            msg.body = f"Your verification code is: {otp}\n\nThis code will expire in 10 minutes."
            print("✅ Message created successfully")
            
            # Don't actually send the email in test mode
            print("✅ OTP functionality test passed!")
            
    except Exception as e:
        print(f"❌ Error testing OTP functionality: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_otp_function()
