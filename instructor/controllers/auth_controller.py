from flask import Blueprint, request, redirect, url_for, flash, session, current_app
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from __init__ import db, mail  # Use the main app's db instance and mail
from instructor.models.user import Instructor, InstructorPasswordReset
from utils.render_utils import render_safe_template
from utils.password_validator import validate_password
import os

auth_bp = Blueprint('auth', __name__)

class AuthController:
    @staticmethod
    @auth_bp.route('/')
    def landing():
        """Instructor landing page - shows features and tools for educators"""
        print("=" * 80)
        print("🏠 INSTRUCTOR LANDING: Route accessed at /instructor/")
        print(f"🔍 Current user authenticated: {current_user.is_authenticated}")
        if current_user.is_authenticated:
            print(f"🔍 Current user: {current_user.username}")
            print(f"🔍 Current user type: {type(current_user)}")
        print("=" * 80)
        
        # If already authenticated as instructor, redirect to dashboard
        if current_user.is_authenticated and isinstance(current_user, Instructor):
            print("✅ Already authenticated as Instructor, redirecting to dashboard")
            return redirect(url_for('dashboard.index'))
        
        # Show instructor landing page
        return render_safe_template('instructor/landing.html')

    @staticmethod
    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        print("=" * 80)
        print("🔍 AUTH LOGIN: Route accessed at /instructor/login")
        print(f"🔍 Request method: {request.method}")
        print(f"🔍 Current user authenticated: {current_user.is_authenticated}")
        if current_user.is_authenticated:
            print(f"🔍 Current user: {current_user.username}")
            print(f"🔍 Current user type: {type(current_user)}")
        print("=" * 80)
        
        # If someone is already authenticated, ensure it's an Admin; otherwise logout to prevent redirect loops
        if current_user.is_authenticated:
            if isinstance(current_user, Instructor):
                print("✅ Already authenticated as Instructor, redirecting to dashboard")
                return redirect(url_for('dashboard.index'))
            else:  # Different user namespace -> force logout & show admin login
                print("⚠️ Authenticated as different user type, logging out")
                logout_user()
                session.pop('auth_namespace', None)
                flash('You were logged out of the student session. Please log in with admin credentials.', 'info')
            
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Debug logging
            print(f"Login attempt for email: {email}")
            # IMPORTANT BUGFIX EXPLANATION:
            # Previously this function had an inner "from instructor.models.user import Instructor" inside
            # the authenticated branch above. Because of that import statement, Python treated
            # "Admin" as a local variable for the entire function body. When an unauthenticated
            # request hit this POST route, that branch (and thus the import) was skipped, and
            # the later reference to Admin below raised:
            #   UnboundLocalError: cannot access local variable 'Admin' where it is not associated with a value
            # Removing the function-scoped import (we already have a module-level import) resolves this.
            # Try to find the user in the Admin table by email
            admin = Instructor.query.filter_by(email=email).first()
            
            if admin and admin.check_password(password):
                # CRITICAL FIX: Set admin namespace BEFORE login_user
                session['auth_namespace'] = 'instructor'
                session.permanent = True  # Make session permanent to persist across requests
                session.modified = True  # Force Flask to save the session
                
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
                if next_url and next_url.startswith('/instructor'):
                    # Only redirect to admin URLs to prevent open redirects
                    return redirect(next_url)
                # Redirect to the canonical admin dashboard
                return redirect(url_for('dashboard.index'))
            else:
                flash('Invalid admin credentials', 'error')
        
        # Use the custom render_template function with debugging
        return render_safe_template('instructor/login.html')

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
            if not username or not password or not email:
                flash('Username, email, and password are required', 'error')
                print("❌ Validation failed: Missing required fields")
                return render_safe_template('instructor/signup.html')
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                print("❌ Validation failed: Passwords do not match")
                return render_safe_template('instructor/signup.html')
            
            # Validate password strength using the new validator
            is_valid, errors = validate_password(password)
            if not is_valid:
                # Show the first error message
                flash(errors[0], 'error')
                print(f"❌ Password validation failed: {errors[0]}")
                return render_safe_template('instructor/signup.html')
            
            # Check if username already exists
            existing_admin = Instructor.query.filter_by(username=username).first()
            if existing_admin:
                flash('Username already exists. Please choose another one.', 'error')
                print(f"❌ Username already exists: {username}")
                return render_safe_template('instructor/signup.html')
            
            # Check if email already exists (if provided)
            if email:
                existing_email = Instructor.query.filter_by(email=email).first()
                if existing_email:
                    flash('Email address is already registered. Please use a different email.', 'error')
                    print(f"❌ Email already exists: {email}")
                    return render_safe_template('instructor/signup.html')
            
            # Create new instructor user
            try:
                print(f"🔨 Creating new instructor user: {username}")
                new_admin = Instructor(
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
                created_admin = Instructor.query.filter_by(username=username).first()
                if created_admin:
                    print(f"✅ Admin created successfully: {created_admin.username}, ID: {created_admin.id}")
                else:
                    print("❌ Admin creation failed - not found in database after commit")
                
                flash('Admin account created successfully! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating admin account: {str(e)}")
                import traceback
                traceback.print_exc()
                flash('Error creating admin account. Please try again.', 'error')
                return render_safe_template('instructor/signup.html')
        
        # For GET requests, render the signup page
        print("📄 Rendering signup page (GET request)")
        return render_safe_template('instructor/signup.html')
        
    @staticmethod
    @auth_bp.route('/logout')
    @login_required
    def logout():
        # CRITICAL FIX: Clear admin-specific session data and namespace
        session.pop('instructor_id', None)
        session.pop('auth_namespace', None)  # Clear the namespace
        
        logout_user()  # Use Flask-Login's logout_user
        flash('Logged out successfully', 'success')
        
        # Ensure we redirect to admin login, not user login
        return redirect(url_for('auth.login'))

    @staticmethod
    @auth_bp.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        """Handle forgot password requests"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
            
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            
            if not email:
                flash('Email address is required', 'error')
                return render_safe_template('instructor/forgot_password.html')
            
            # Find admin by email
            admin = Instructor.query.filter_by(email=email).first()
            
            if admin:
                try:
                    # Create password reset token
                    reset_token = InstructorPasswordReset.create_token(admin.id, expiry_hours=1)
                    
                    # Send email with reset link
                    reset_url = url_for('auth.reset_password', token=reset_token.token, _external=True)
                    
                    msg = Message(
                        subject='RiddleNet Admin - Password Reset Request',
                        recipients=[email],
                        body=f'''Hello {admin.username},

You have requested a password reset for your RiddleNet admin account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
RiddleNet Team'''
                    )
                    
                    mail.send(msg)
                    flash('If an admin account with that email exists, you will receive password reset instructions.', 'success')
                    
                except Exception as e:
                    print(f"Error sending password reset email: {str(e)}")
                    flash('An error occurred while sending the password reset email. Please try again later.', 'error')
            else:
                # Don't reveal whether the email exists or not for security
                flash('If an admin account with that email exists, you will receive password reset instructions.', 'success')
            
            return redirect(url_for('auth.login'))
        
        return render_safe_template('instructor/forgot_password.html')

    @staticmethod
    @auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        """Handle password reset with token"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        
        # Validate the token
        reset_token = InstructorPasswordReset.get_valid_token(token)
        if not reset_token:
            flash('Invalid or expired password reset token.', 'error')
            return redirect(url_for('auth.login'))
        
        if request.method == 'POST':
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            # Validation
            if not password:
                flash('Password is required', 'error')
                return render_safe_template('instructor/reset_password.html', token=token)
            
            # Validate password strength using the new validator
            is_valid, errors = validate_password(password)
            if not is_valid:
                flash(errors[0], 'error')
                return render_safe_template('instructor/reset_password.html', token=token)
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_safe_template('instructor/reset_password.html', token=token)
            
            try:
                # Update the admin's password
                admin = reset_token.admin
                admin.set_password(password)
                
                # Mark the token as used
                reset_token.mark_as_used()
                
                db.session.commit()
                
                flash('Your password has been reset successfully. You can now log in with your new password.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                db.session.rollback()
                print(f"Error resetting password: {str(e)}")
                flash('An error occurred while resetting your password. Please try again.', 'error')
                return render_safe_template('instructor/reset_password.html', token=token)
        
        return render_safe_template('instructor/reset_password.html', token=token)

# Add a context processor to help with URL generation
@auth_bp.context_processor
def inject_url_prefix():
    """
    This function helps the templates determine whether to use 'instructor.' prefix
    for URLs depending on whether we're using the standalone admin app or the
    integrated blueprint.
    """
    def get_url_prefix():
        return ''  # No prefix for standalone app
        
    return dict(url_prefix=get_url_prefix)
