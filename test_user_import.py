import sys
sys.path.append('.')
print("Starting import test...")

try:
    print("Importing db...")
    from __init__ import db
    print("✅ db import successful")
    
    print("Importing User from user.models...")
    from user.models import User
    print(f"✅ User import successful - {User.__name__}")
    
    print("Import test complete.")
except Exception as e:
    print(f"❌ Error during import: {e}")
    import traceback
    traceback.print_exc()
