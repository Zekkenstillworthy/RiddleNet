from app_factory import create_app
from admin.models.class_model import Class
import json

app = create_app()

with app.app_context():
    try:
        # Try to get class with ID 4
        test_class = Class.query.get(4)
        if test_class:
            # Test the students property
            print(f"Class {test_class.name} has {len(test_class.students)} students")
            # Test the to_dict method
            print(json.dumps(test_class.to_dict(), indent=2))
        else:
            print("Class with ID 4 not found")
    except Exception as e:
        print(f"Error: {str(e)}")
