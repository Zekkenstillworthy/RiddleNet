from flask import Blueprint, request, redirect, url_for, flash, session, current_app
from datetime import datetime
from werkzeug.security import check_password_hash
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
                # Use Flask-Login to log in the user with remember=True
                login_user(admin, remember=True)
                # Update last login
                admin.last_login = datetime.utcnow()
                db.session.commit()
                
                # Debug logging
                print(f"Login successful: {admin.username}, ID: {admin.id}, is_authenticated: {current_user.is_authenticated}")
                
                flash('Welcome to Admin Dashboard', 'success')
                
                # Check if there's a next parameter in the query string or form data
                next_url = request.args.get('next') or request.form.get('next')
                if next_url:
                    # Only redirect to URLs within the same site
                    return redirect(next_url)
                return redirect(url_for('dashboard.index'))
            else:
                flash('Invalid admin credentials', 'error')        # Debug template discovery
        from utils.template_utils import debug_template_paths
        debug_template_paths('admin/login.html')
        
        # Check if the login template exists
        template_exists = False
        for path in current_app.jinja_loader.searchpath:
            template_path = os.path.join(path, 'admin', 'login.html')
            if os.path.exists(template_path):
                print(f"Login template found at: {template_path}")
                template_exists = True
            # Also check for direct path
            direct_path = os.path.join(path, 'admin/login.html')
            if os.path.exists(direct_path):
                print(f"Login template found at direct path: {direct_path}")
                template_exists = True
        
        if not template_exists:
            print("WARNING: Login template not found in any template path!")
        
        # Use the custom render_template function with debugging
        return render_safe_template('admin/login.html')
        
    @staticmethod
    @auth_bp.route('/logout')
    @login_required
    def logout():
        logout_user()  # Use Flask-Login's logout_user
        flash('Logged out successfully', 'success')
        # Since the auth blueprint is registered with a prefix, we need to use the direct path
        return redirect('/admin/login')

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
