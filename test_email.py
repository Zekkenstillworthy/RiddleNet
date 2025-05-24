"""
Test script to verify Flask-Mail is configured correctly
"""
import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

# Load environment variables
load_dotenv()

# Create a test Flask app
app = Flask(__name__)

# Configure Flask-Mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

# Initialize Flask-Mail
mail = Mail(app)

def test_send_email():
    """Test sending an email"""
    with app.app_context():
        try:
            # Create a test message
            msg = Message(
                "RiddleNet Email OTP Test",
                recipients=[os.getenv("MAIL_USERNAME")]  # Send to self for testing
            )
            msg.body = "This is a test email to verify Flask-Mail is configured correctly."
            
            # Send the email
            mail.send(msg)
            print("✅ Test email sent successfully! Please check your inbox.")
            
        except Exception as e:
            print(f"❌ Error sending test email: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Make sure your .env file has valid MAIL_USERNAME and MAIL_PASSWORD values")
            print("2. If using Gmail, make sure you've created an App Password (see .env file instructions)")
            print("3. Check your internet connection")
            print("4. Make sure port 587 is not blocked by your firewall or network")

if __name__ == "__main__":
    # Print email configuration (with password masked)
    print("Email Configuration:")
    print(f"  MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"  MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"  MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"  MAIL_PASSWORD: {'*' * 12 if app.config['MAIL_PASSWORD'] else 'NOT SET'}")
    
    # Ask user to confirm before sending test email
    if app.config["MAIL_USERNAME"] and app.config["MAIL_PASSWORD"]:
        confirm = input("\nSend a test email? (y/n): ")
        if confirm.lower() == 'y':
            test_send_email()
        else:
            print("Test email sending cancelled")
    else:
        print("\n❌ Missing email credentials in .env file. Please set MAIL_USERNAME and MAIL_PASSWORD.")
