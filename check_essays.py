from __init__ import create_app, db
from admin.models.class_model import class_students
from user.models.user import User
from admin.models.essay_response import EssayResponse

app = create_app()

with app.app_context():
    print('=== CLASS 9 STUDENTS ===')
    students_query = db.session.query(User.id, User.username).join(class_students, User.id == class_students.c.user_id).filter(class_students.c.class_id == 9)
    students = students_query.all()
    for student in students:
        print(f'Student: {student.username} (ID: {student.id})')
    
    if not students:
        print("No students found in class 9")
    
    print('\n=== ALL ESSAY RESPONSES ===')
    essays = EssayResponse.query.all()
    for essay in essays:
        print(f'Essay ID: {essay.id}, User ID: {essay.user_id}, Question: {essay.question_text[:50]}...')
    
    if not essays:
        print("No essay responses found")
    
    print('\n=== ALL USERS ===')
    users = User.query.all()
    for user in users:
        print(f'User: {user.username} (ID: {user.id})')
    
    print('\n=== CLASS_STUDENTS TABLE ===')
    class_student_records = db.session.execute(
        db.text("SELECT class_id, user_id FROM class_students")
    ).fetchall()
    for record in class_student_records:
        print(f'Class ID: {record[0]}, User ID: {record[1]}')