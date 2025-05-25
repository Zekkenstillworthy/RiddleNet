import sys
sys.path.append('.')
print("Starting import test...")

try:
    print("Importing db...")
    from __init__ import db
    print("✅ db import successful")

    print("Importing AdminUser...")
    from admin.models.user import AdminUser
    print("✅ AdminUser import successful")

    print("Importing Question...")
    from admin.models.question import Question
    print("✅ Question import successful")

    print("Importing class_students...")
    from admin.models.class_model import class_students
    print("✅ class_students import successful")

    print("Importing User...")
    from user.models.user import User
    print("✅ User import successful")

    print("Importing Score...")
    from user.models.score import Score
    print("✅ Score import successful")
    
    print("Importing EssayResponse...")
    from admin.models.essay_response import EssayResponse
    print("✅ EssayResponse import successful")

except Exception as e:
    print(f"❌ Error during import: {e}")
    import traceback
    traceback.print_exc()

print("Import test complete.")
