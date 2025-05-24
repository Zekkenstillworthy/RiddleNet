"""
Test OTP delivery functionality
"""
import os
import sys
from dotenv import load_dotenv
import datetime
import random

# Ensure proper project path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables from .env file
load_dotenv()

# Create Flask app context
from __init__ import create_app, db
app = create_app()

def test_otp_delivery():
    """Test the OTP delivery functionality by generating and sending an OTP to a specific user"""
    with app.app_context():
        from user.models.user import User
        from flask_mail import Message
        
        # Get username from command line or use default
        username = sys.argv[1] if len(sys.argv) > 1 else None
        
        if not username:
            print("Usage: python test_otp.py <username>")
            print("\nAvailable users:")
            users = User.query.all()
            for user in users:
                email_status = "✅" if user.email else "❌"
                print(f"  {user.username} {email_status} {user.email or 'No email set'}")
            return
            
        # Find the user
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User '{username}' not found in the database.")
            return
            
        # Check if user has an email
        if not user.email:
            print(f"Error: User '{username}' does not have an email address set.")
            return
            
        # Generate a random 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Update the user's OTP in the database
        user.otp = otp
        user.otp_generated_at = datetime.datetime.now()
        db.session.commit()
        
        print(f"Generated OTP for {username}: {otp}")
        
        # Attempt to send OTP via email
        try:
            print(f"Sending OTP to {user.email}...")
            
            # Create message
            msg = Message(
                "Your RiddleNet OTP Code",
                recipients=[user.email]
            )
            msg.body = f"Your verification code is: {otp}\n\nThis code will expire in 10 minutes."
            
            # Get mail extension and send
            mail = app.extensions['mail']
            mail.send(msg)
            
            print(f"✅ OTP sent successfully to {user.email}")
            print(f"OTP Code: {otp}")
            
            # Display configured mail settings
            print("\nEmail Configuration:")
            print(f"  MAIL_SERVER: {app.config['MAIL_SERVER']}")
            print(f"  MAIL_PORT: {app.config['MAIL_PORT']}")
            print(f"  MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
            print(f"  MAIL_PASSWORD: {'*' * 12 if app.config['MAIL_PASSWORD'] else 'NOT SET'}")
            
        except Exception as e:
            print(f"❌ Error sending OTP: {str(e)}")
            
            # Print troubleshooting guide
            print("\nTroubleshooting:")
            print("1. Check your .env file for proper email credentials")
            print("2. Make sure you have created an App Password if using Gmail")
            print("3. Run test_email.py to test basic email functionality")
            print("4. See EMAIL_SETUP_INSTRUCTIONS.md for detailed setup steps")

if __name__ == "__main__":
    test_otp_delivery()
