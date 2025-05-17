from __init__ import create_app
from admin.models.class_model import Class

app = create_app()

with app.app_context():
    try:
        class_obj = Class.query.get(4)
        if class_obj:
            print(f"Found class: {class_obj.name}")
            print(f"Trying to access students property...")
            students = class_obj.students
            print(f"Number of students in class: {len(students.all() if students else [])}")
            print(f"Trying to_dict()...")
            class_dict = class_obj.to_dict()
            print(f"Class dict: {class_dict}")
        else:
            print(f"Class with ID 4 not found")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
