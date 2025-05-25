import sys
sys.path.append('.')
print("Starting import test...")

try:
    from user.models import User
    print("✅ User import successful")
except Exception as e:
    print(f"❌ Error importing User: {e}")
    import traceback
    traceback.print_exc()

print("Import test complete.")
