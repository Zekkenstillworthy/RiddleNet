"""
Create challenge_progress table - CRITICAL FIX for 500 error
Run this script to create the missing table
"""
from __init__ import db, create_app
from user.models.challenge_progress import ChallengeProgress

print("🔧 Creating challenge_progress table...")
print("=" * 60)

# Create Flask app context
app = create_app()

with app.app_context():
    try:
        # Create the table
        db.create_all()
        
        print("✅ Database tables created successfully!")
        print("")
        print("📋 Verifying challenge_progress table...")
        
        # Verify table exists by running a simple query
        count = ChallengeProgress.query.count()
        print(f"✅ challenge_progress table exists with {count} records")
        
        print("")
        print("🎉 Database migration complete!")
        print("=" * 60)
        print("")
        print("📝 Next steps:")
        print("1. Restart your Flask application")
        print("2. Refresh your browser (Ctrl + Shift + R)")
        print("3. The 500 error should now be fixed!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
