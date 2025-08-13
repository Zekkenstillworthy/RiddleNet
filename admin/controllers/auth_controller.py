from flask import Blueprint, request, redirect, url_for, flash, session, current_app
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from __init__ import db  # Use the main app's db instance
from admin.models.user import Admin
from utils.render_utils import render_safe_template
import os

auth_bp = Blueprint('auth', __name__)

class AuthController:
    @staticmethod
    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        # Check if admin is already logged in
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Debug logging
            print(f"Login attempt for username: {username}")
                  # Try to find the user in the Admin table
            admin = Admin.query.filter_by(username=username).first()
            
            if admin and admin.check_password(password):
                # CRITICAL FIX: Set admin namespace BEFORE login_user
                session['auth_namespace'] = 'admin'
                
                # Use Flask-Login to log in the user with remember=True
                login_user(admin, remember=True)
                
                # Update last login
                admin.last_login = datetime.utcnow()
                db.session.commit()
                
                # Debug logging
                print(f"Login successful: {admin.username}, ID: {admin.id}, namespace: {session.get('auth_namespace')}")
                
                flash('Welcome to Admin Dashboard', 'success')
                
                # Check if there's a next parameter in the query string or form data
                next_url = request.args.get('next') or request.form.get('next')
                if next_url:
                    # Only redirect to URLs within the same site
                    return redirect(next_url)
                return redirect(url_for('dashboard.index'))
            else:
                flash('Invalid admin credentials', 'error')
        
        # Use the custom render_template function with debugging
        return render_safe_template('admin/login.html')

    @staticmethod
    @auth_bp.route('/signup', methods=['GET', 'POST'])
    def signup():
        print(f"🚀 SIGNUP ROUTE HIT! Method: {request.method}")
        print(f"🔐 current_user.is_authenticated: {current_user.is_authenticated}")
        
        # Check if admin is already logged in
        if current_user.is_authenticated:
            print("🔄 User is authenticated, redirecting to dashboard")
            return redirect(url_for('dashboard.index'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            email = request.form.get('email', '')
            
            # Debug logging
            print(f"Admin signup attempt for username: {username}")
            print(f"Email: {email}")
            
            # Validation
            if not username or not password:
                flash('Username and password are required', 'error')
                print("❌ Validation failed: Missing username or password")
                return render_safe_template('admin/signup.html')
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                print("❌ Validation failed: Passwords do not match")
                return render_safe_template('admin/signup.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                print("❌ Validation failed: Password too short")
                return render_safe_template('admin/signup.html')
            
            # Check if username already exists
            existing_admin = Admin.query.filter_by(username=username).first()
            if existing_admin:
                flash('Username already exists. Please choose another one.', 'error')
                print(f"❌ Username already exists: {username}")
                return render_safe_template('admin/signup.html')
            
            # Check if email already exists (if provided)
            if email:
                existing_email = Admin.query.filter_by(email=email).first()
                if existing_email:
                    flash('Email address is already registered. Please use a different email.', 'error')
                    print(f"❌ Email already exists: {email}")
                    return render_safe_template('admin/signup.html')
            
            # Create new admin user
            try:
                print(f"🔨 Creating new admin user: {username}")
                new_admin = Admin(
                    username=username,
                    email=email,
                    role='admin',
                    created_at=datetime.utcnow()
                )
                new_admin.set_password(password)
                
                print(f"✅ Admin object created, adding to database...")
                db.session.add(new_admin)
                db.session.commit()
                
                # Verify the admin was created
                created_admin = Admin.query.filter_by(username=username).first()
                if created_admin:
                    print(f"✅ Admin created successfully: {created_admin.username}, ID: {created_admin.id}")
                else:
                    print("❌ Admin creation failed - not found in database after commit")
                
                flash('Admin account created successfully! You can now log in.', 'success')
                return redirect('/admin/login')
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating admin account: {str(e)}")
                import traceback
                traceback.print_exc()
                flash('Error creating admin account. Please try again.', 'error')
                return render_safe_template('admin/signup.html')
        
        # For GET requests, render the signup page
        print("📄 Rendering signup page (GET request)")
        return render_safe_template('admin/signup.html')
        
    @staticmethod
    @auth_bp.route('/logout')
    @login_required
    def logout():
        # CRITICAL FIX: Clear admin-specific session data and namespace
        session.pop('admin_id', None)
        session.pop('auth_namespace', None)  # Clear the namespace
        
        logout_user()  # Use Flask-Login's logout_user
        flash('Logged out successfully', 'success')
        
        # Ensure we redirect to admin login, not user login
        return redirect(url_for('auth.login'))

# Add a context processor to help with URL generation
@auth_bp.context_processor
def inject_url_prefix():
    """
    This function helps the templates determine whether to use 'admin.' prefix
    for URLs depending on whether we're using the standalone admin app or the
    integrated blueprint.
    """
    def get_url_prefix():
        return ''  # No prefix for standalone app
        
    return dict(url_prefix=get_url_prefix)
