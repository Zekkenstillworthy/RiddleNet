"""
Update user email address
"""
import os
import sys
from dotenv import load_dotenv

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables from .env file
load_dotenv()

# Create app context
from __init__ import create_app, db
app = create_app()

def update_user_email(username, email):
    """Update a user's email address"""
    with app.app_context():
        from user.models import User as UserModel
        
        # Find the user
        user = UserModel.query.filter_by(username=username).first()
        if not user:
            print(f"User '{username}' not found")
            return False
        
        # Update the email
        user.email = email
        db.session.commit()
        
        print(f"✅ Updated email for {username} to {email}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_email.py <username> <email>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    
    update_user_email(username, email)
