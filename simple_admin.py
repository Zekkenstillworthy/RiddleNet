"""Simple admin creation script"""
from admin.app import AdminApp
from admin.models.user import Admin
from admin import db

# Initialize app
admin_app = AdminApp()

with admin_app.app.app_context():
    try:
        # Create tables
        db.create_all()
        
        # Check if admin exists
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin', email='admin@test.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")
            
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
