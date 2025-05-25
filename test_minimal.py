print("Starting minimal import test...")

try:
    print("Importing sys...")
    import sys
    print("✅ sys import successful")
    
    print("Adding current directory to path...")
    sys.path.append('.')
    print("✅ Path updated")
    
    print("Importing db...")
    from __init__ import db
    print("✅ db import successful")
    
    print("Import test complete.")
except Exception as e:
    print(f"❌ Error during import: {e}")
    import traceback
    traceback.print_exc()
