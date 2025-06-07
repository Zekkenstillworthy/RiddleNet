from user.models.user import User
from __init__ import db, create_app

try:
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f'User ID: {user.id}, Username: {user.username}, Profile Image: {user.profile_img}')
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
