from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from datetime import datetime
import pyotp
import qrcode
import os
from flask_login import login_required, current_user
from __init__ import db  # Import db from main app
from ..models.user import InstructorUser, Instructor  # Import the correct models
from ..models.score import InstructorScore  # Use renamed model
from ..models.essay_response import EssayResponse
from utils.password_validator import validate_password

user_bp = Blueprint('admin_user', __name__)

class UserController:
    @staticmethod
    @user_bp.route('/session-check')
    @login_required
    def session_check():
        """Debug endpoint to check session status"""
        from flask import session
        return jsonify({
            'authenticated': current_user.is_authenticated,
            'user_id': current_user.id if current_user.is_authenticated else None,
            'username': current_user.username if current_user.is_authenticated else None,
            'auth_namespace': session.get('auth_namespace'),
            'session_user_id': session.get('_user_id'),
            'is_instructor_instance': str(type(current_user))
        })
    
    @staticmethod
    @user_bp.route('/routes', methods=['GET'])
    @login_required
    def list_admin_routes():
        """Diagnostic endpoint: list instructor routes to verify delete endpoint is registered"""
        from flask import current_app
        routes = []
        for rule in current_app.url_map.iter_rules():
            rule_str = str(rule)
            if rule_str.startswith('/instructor'):
                routes.append({
                    'rule': rule_str,
                    'endpoint': rule.endpoint,
                    'methods': sorted(list(rule.methods)) if rule.methods else []
                })
        # Sort for readability
        routes = sorted(routes, key=lambda r: r['rule'])
        return jsonify({ 'routes': routes })

    # Changed from '/' to '/users' to prevent conflict with dashboard.index at /admin/
    @staticmethod
    @user_bp.route('/users')
    @login_required
    def index():
        # MVP FIX: Only show students enrolled in THIS admin's classes
        # Get classes created by current admin
        from instructor.models.class_model import Class, class_students
        
        admin_classes = Class.query.filter_by(created_by=current_user.id).all()
        admin_class_ids = [cls.id for cls in admin_classes]
        
        # Get student IDs enrolled in this admin's classes
        student_ids = []
        if admin_class_ids:
            student_ids = db.session.query(class_students.c.user_id).filter(
                class_students.c.class_id.in_(admin_class_ids)
            ).distinct().all()
            student_ids = [sid[0] for sid in student_ids]
        
        # Only get users (students) that are in THIS admin's classes
        if student_ids:
            users = InstructorUser.query.filter(InstructorUser.id.in_(student_ids)).order_by(InstructorUser.created_at.desc()).all()
        else:
            users = []  # New admin with no classes/students yet
        
        user_stats = []
        for user in users:
            scores_count = InstructorScore.query.filter_by(user_id=user.id).count()
            highest_score = db.session.query(func.max(InstructorScore.score)).filter_by(user_id=user.id).scalar() or 0
            
            # Ensure user has required fields - set defaults if missing
            if not user.created_at:
                user.created_at = datetime.utcnow()
            if not hasattr(user, 'status') or not user.status:
                user.status = 'active'
            
            user_stats.append({
                'user': user,
                'scores_count': scores_count,
                'highest_score': highest_score
            })
        
        # MVP FIX: Only show admin accounts (admins table is shared, but that's intentional)
        # Admins can see other admin accounts for collaboration purposes
        admins = Instructor.query.order_by(Instructor.created_at.desc()).all()
        
        # Ensure admins have required fields
        for admin in admins:
            if not admin.created_at:
                admin.created_at = datetime.utcnow()
        
        return render_template('instructor/user_management.html', 
                            user_stats=user_stats, 
                            admins=admins,
                            active_page='users')

    @staticmethod
    @user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    def edit_user(user_id):
        user = InstructorUser.query.get_or_404(user_id)
        
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email', '')
            password = request.form.get('password')
            status = request.form.get('status', 'active')
            is_instructor = request.form.get('is_instructor') == 'true'
            
            # Update user fields
            user.username = username
            user.email = email
            user.status = status
            user.is_instructor = is_instructor
            
            # Only update password if a new one is provided
            if password:
                user.set_password(password)
            
            try:
                db.session.commit()
                flash('User updated successfully', 'success')
                return redirect(url_for('user.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating user: {str(e)}', 'error')
        
        return render_template('instructor/edit_user.html', user=user, active_page='users')

    @user_bp.route('/delete/<int:user_id>', methods=['POST'])
    @login_required
    def delete_user(user_id):
        """Delete a regular user - FIXED with proper session debugging"""
        from flask import session
        import logging
        from user.models.user import User
        
        # Debug session information
        logging.info(f"🗑️ DELETE REQUEST - User ID: {user_id}")
        logging.info(f"🔐 Session data: auth_namespace={session.get('auth_namespace')}, user_id={session.get('_user_id')}")
        logging.info(f"👤 Current user: {current_user.username if current_user.is_authenticated else 'Not authenticated'}")
        
        # Check authentication explicitly
        if not current_user.is_authenticated:
            logging.error("❌ User not authenticated for delete operation")
            return jsonify({
                'success': False,
                'message': 'Authentication required. Please log in again.'
            }), 401
        
        user = User.query.get_or_404(user_id)
        
        # Regular users don't have the is_instructor check (that's for InstructorUser)
        # User model doesn't have is_instructor attribute
        
        try:
            # Delete related records from various tables
            # Import necessary models with error handling
            from user.models.score import Score
            
            # Delete related scores
            Score.query.filter_by(user_id=user.id).delete()
            
            # For tables with potential schema issues, use direct SQL deletion
            # This avoids SQLAlchemy trying to load model definitions that may not match the DB
            tables_to_clean = [
                'topology_progress',
                'networking_progress',
                'networking2_progress',
                'user_notification',
                'notification_preferences',
                'performance_feedback',
                'feedback_session',
                'points_balance',
                'quiz_attempt',
                'lesson_progress',
                'module_progress',
                'simulation_progress'
            ]
            
            for table in tables_to_clean:
                try:
                    # Use raw SQL to avoid model schema issues
                    result = db.session.execute(
                        db.text(f"DELETE FROM {table} WHERE user_id = :user_id"),
                        {"user_id": user.id}
                    )
                    # Commit immediately to avoid transaction failures affecting other tables
                    db.session.commit()
                    if result.rowcount > 0:
                        logging.info(f"✅ Deleted {result.rowcount} record(s) from {table} for user {user.id}")
                except Exception as e:
                    # Rollback this transaction and continue with next table
                    db.session.rollback()
                    # Log warning but continue - table might not exist or have different schema
                    logging.warning(f"⚠️ Could not clean {table}: {str(e)[:100]}")
            
            # Handle essay responses - either delete them or handle differently
            try:
                essay_responses = EssayResponse.query.filter_by(user_id=user.id).all()
                for essay in essay_responses:
                    db.session.delete(essay)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logging.warning(f"⚠️ Could not delete essay responses: {str(e)[:100]}")
            
            # Option 2 (alternative): Set essay user_id to null if NOT NULL constraint is removed
            # EssayResponse.query.filter_by(user_id=user.id).update({EssayResponse.user_id: None})
            
            # Delete any remaining foreign key references in other tables
            additional_tables = [
                'class_students',  # Many-to-many relationship table
                'user_classes',    # Alternative name for class enrollment
                'assignment_submission',
                'quiz_score',
                'simulation_attempt'
            ]
            
            for table in additional_tables:
                try:
                    result = db.session.execute(
                        db.text(f"DELETE FROM {table} WHERE user_id = :user_id"),
                        {"user_id": user.id}
                    )
                    db.session.commit()
                    if result.rowcount > 0:
                        logging.info(f"✅ Deleted {result.rowcount} record(s) from {table}")
                except Exception as e:
                    db.session.rollback()
                    logging.debug(f"Table {table} may not exist or have user_id column: {str(e)[:50]}")
            
            # Store username for logging before deletion
            username = user.username
            
            # Now delete the user using raw SQL to bypass SQLAlchemy cascade issues
            db.session.execute(
                db.text("DELETE FROM \"user\" WHERE id = :user_id"),
                {"user_id": user.id}
            )
            db.session.commit()
            
            logging.info(f"✅ Successfully deleted user {username} (ID: {user_id})")
            return jsonify({
                'success': True,
                'message': ''
            }), 200
        except Exception as e:
            db.session.rollback()
            logging.error(f"❌ Error deleting user: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error deleting user: {str(e)}'
            }), 500

    @staticmethod
    @user_bp.route('/admins/edit/<int:instructor_id>', methods=['GET', 'POST'])
    @login_required
    def edit_admin(instructor_id):
        admin = Instructor.query.get_or_404(instructor_id)
        
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email', '')
            password = request.form.get('password')
            role = request.form.get('role', 'admin')
            
            admin.username = username
            admin.email = email
            admin.role = role
            if password:
                admin.password_hash = generate_password_hash(password)
            
            try:
                db.session.commit()
                flash('Admin updated successfully', 'success')
                return redirect(url_for('user.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating admin: {str(e)}', 'error')
        
        return render_template('instructor/edit_admin.html', admin=admin, active_page='users')

    @user_bp.route('/admins/delete/<int:instructor_id>', methods=['POST'])
    @login_required
    def delete_admin(instructor_id):
        admin = Instructor.query.get_or_404(instructor_id)
        
        # Prevent deleting the last admin
        if Instructor.query.count() <= 1:
            return jsonify({
                'success': False,
                'message': 'Cannot delete the last admin account'
            }), 400
        
        try:
            db.session.delete(admin)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Admin deleted successfully'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error deleting admin: {str(e)}'
            }), 500

    @staticmethod
    @user_bp.route('/admins/add', methods=['GET', 'POST'])
    @login_required
    def add_admin():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            email = request.form.get('email', '')
            role = request.form.get('role', 'admin')
            
            # Validate inputs
            if not username or not password:
                flash('Username and password are required', 'error')
                return redirect(url_for('user.index'))
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('user.index'))
            
            # Validate password strength
            is_valid, errors = validate_password(password)
            if not is_valid:
                flash(errors[0], 'error')
                return redirect(url_for('user.index'))
            
            # Check if username already exists
            existing_admin = Instructor.query.filter_by(username=username).first()
            if existing_admin:
                flash('Username already exists', 'error')
                return redirect(url_for('user.index'))
            
            # Create new instructor user
            new_admin = Admin(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
                role=role,
                created_at=datetime.utcnow()
            )
            
            try:
                db.session.add(new_admin)
                db.session.commit()
                flash(f'Instructor user "{username}" created successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating admin: {str(e)}', 'error')
            
            return redirect(url_for('user.index'))
        
        # For GET requests, redirect to user management page
        # No need for a separate add_admin.html page anymore
        return redirect(url_for('user.index'))

    @staticmethod
    @user_bp.route('/reset-user-password/<int:user_id>', methods=['POST'])
    @login_required
    def reset_user_password(user_id):
        user = InstructorUser.query.get_or_404(user_id)
        # Logic to reset password - this would generate a random password or trigger a reset email
        flash(f'Password reset for {user.username}', 'success')
        return redirect(url_for('dashboard.index'))

    @staticmethod
    @user_bp.route('/add', methods=['POST'])
    @login_required
    def add_user():
        """Add a regular user"""
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            status = request.form.get('status', 'active')
            
            # Validate input
            if not username or not password:
                flash('Username and password are required', 'error')
                return redirect(url_for('user.index'))
            
            # Validate password strength
            is_valid, errors = validate_password(password)
            if not is_valid:
                flash(errors[0], 'error')
                return redirect(url_for('user.index'))
            
            # Check if username already exists
            existing_user = InstructorUser.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists', 'error')
                return redirect(url_for('user.index'))
            
            # Create new user
            try:
                new_user = InstructorUser(
                    username=username,
                    email=email,
                    status=status,
                    created_at=datetime.utcnow()
                )
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash(f'User {username} has been created successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating user: {str(e)}', 'error')
            
            return redirect(url_for('user.index'))
        
        # For GET requests, just redirect to the user management page
        return redirect(url_for('user.index'))

    @staticmethod
    @user_bp.route('/generate_totp/<int:user_id>', methods=['POST'])
    @login_required
    def generate_totp(user_id):
        """Generate a new TOTP key for a user"""
        user = InstructorUser.query.get_or_404(user_id)
        
        # Generate a new random TOTP key
        key = pyotp.random_base32()
        totp = pyotp.TOTP(key)
        uri = totp.provisioning_uri(name=f"{user.id}_{user.username}", issuer_name="RiddleNet")
        
        # Ensure directory exists
        qr_dir = os.path.join('static', 'img', 'img_qr')
        if not os.path.exists(qr_dir):
            os.makedirs(qr_dir)
            
        # Generate QR code
        qr_code_path = f"static/img/img_qr/{user.id}_totp.png"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(os.path.join('static', 'img', 'img_qr', f"{user.id}_totp.png"))
        
        # Save the key to the user
        user.totp_key = key
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": "TOTP enabled successfully",
            "totp_key": key,
            "qr_code_path": qr_code_path
        })
    
    @staticmethod
    @user_bp.route('/disable_totp/<int:user_id>', methods=['POST'])
    @login_required
    def disable_totp(user_id):
        """Disable TOTP for a user"""
        user = InstructorUser.query.get_or_404(user_id)
        
        # Remove TOTP key
        user.totp_key = None
        db.session.commit()
        
        # Delete QR code image if it exists
        qr_path = os.path.join('static', 'img', 'img_qr', f"{user.id}_totp.png")
        if os.path.exists(qr_path):
            os.remove(qr_path)
            
        return jsonify({
            "status": "success",
            "message": "TOTP disabled successfully"
        })
        
    @staticmethod
    @user_bp.route('/get_totp_info/<int:user_id>')
    @login_required
    def get_totp_info(user_id):
        """Get TOTP information for a user"""
        user = InstructorUser.query.get_or_404(user_id)
        
        totp_data = {
            "has_totp": user.totp_key is not None,
            "totp_key": user.totp_key if user.totp_key else None,
        }
        
        # Add QR code path if TOTP is enabled
        if user.totp_key:
            qr_path = f"/static/img/img_qr/{user.id}_totp.png"
            totp_data["qr_code_path"] = qr_path
            
        return jsonify(totp_data)

    @staticmethod
    @user_bp.route('/essay-responses')
    @login_required
    def user_essays():
        """Display users with option to view their essay responses"""
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get all users with pagination
        users = InstructorUser.query.paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('instructor/user_responses.html', 
                            users=users,
                            active_page='users')
    
    @staticmethod
    @user_bp.route('/api/<int:user_id>/essays')
    @login_required
    def get_user_essays(user_id):
        """API endpoint to get all essays for a specific user"""
        user = InstructorUser.query.get_or_404(user_id)
        essays = EssayResponse.query.filter_by(user_id=user_id).order_by(EssayResponse.submission_date.desc()).all()
        
        # Format essay data for JSON response
        essays_data = []
        for essay in essays:
            essays_data.append({
                'id': essay.id,
                'question': essay.question,
                'answer': essay.answer,
                'category': essay.category,
                'submission_date': essay.submission_date.strftime('%Y-%m-%d %H:%M') if essay.submission_date else 'N/A',
                'is_graded': essay.is_graded,
                'graded_score': essay.graded_score
            })
        
        return jsonify({
            'user_id': user_id,
            'username': user.username,
            'essays': essays_data
        })

    @staticmethod
    @user_bp.route('/create-new-user')
    @login_required
    def create_new_user_form():
        """Display the new dynamic user creation form"""
        return render_template('instructor/create_new_user.html', active_page='users')

    @staticmethod
    @user_bp.route('/create-new-user', methods=['POST'])
    @login_required
    def create_new_user():
        """Handle the new dynamic user creation form submission"""
        try:
            # Get form data
            user_type = request.form.get('user_type')
            username = request.form.get('username')
            email = request.form.get('email')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            status = request.form.get('status', 'active')
            enable_2fa = request.form.get('enable_2fa') == 'on'
            send_welcome_email = request.form.get('send_welcome_email') == 'on'
            force_password_change = request.form.get('force_password_change') == 'on'
            assigned_classes = request.form.getlist('assigned_classes')
            notes = request.form.get('notes', '')

            # Validate required fields
            if not all([user_type, username, email, first_name, last_name, password]):
                flash('All required fields must be filled', 'error')
                return redirect(url_for('admin_user.create_new_user_form'))

            # Validate password confirmation
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('admin_user.create_new_user_form'))
            
            # Validate password strength
            is_valid, errors = validate_password(password)
            if not is_valid:
                flash(errors[0], 'error')
                return redirect(url_for('admin_user.create_new_user_form'))

            # Check if username already exists
            existing_user = InstructorUser.query.filter_by(username=username).first()
            existing_admin = Instructor.query.filter_by(username=username).first()
            if existing_user or existing_admin:
                flash('Username already exists', 'error')
                return redirect(url_for('admin_user.create_new_user_form'))

            # Check if email already exists
            existing_email_user = InstructorUser.query.filter_by(email=email).first()
            existing_email_admin = Instructor.query.filter_by(email=email).first()
            if existing_email_user or existing_email_admin:
                flash('Email address already exists', 'error')
                return redirect(url_for('admin_user.create_new_user_form'))

            # Create user based on type
            if user_type == 'admin':
                # Create instructor user
                new_user = Admin(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password_hash=generate_password_hash(password),
                    role='admin',
                    created_at=datetime.utcnow(),
                    notes=notes
                )
                
                # Add 2FA if enabled
                if enable_2fa:
                    import pyotp
                    new_user.totp_key = pyotp.random_base32()

                db.session.add(new_user)
                db.session.commit()
                
                flash(f'Administrator "{username}" created successfully', 'success')
                
            elif user_type in ['student', 'instructor']:
                # Create regular user
                new_user = InstructorUser(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    status=status,
                    created_at=datetime.utcnow(),
                    force_password_change=force_password_change,
                    notes=notes
                )
                
                # Set user type (you may need to add a user_type field to your model)
                if hasattr(new_user, 'user_type'):
                    new_user.user_type = user_type
                
                # Set instructor privileges if needed
                if user_type == 'instructor':
                    new_user.is_instructor = True
                
                new_user.set_password(password)
                
                # Add 2FA if enabled
                if enable_2fa:
                    import pyotp
                    new_user.totp_key = pyotp.random_base32()

                db.session.add(new_user)
                db.session.commit()
                
                # Handle class assignments for instructors
                if user_type == 'instructor' and assigned_classes:
                    # You'll need to implement class assignment logic here
                    # This would typically involve a many-to-many relationship
                    pass
                
                flash(f'{user_type.title()} user "{username}" created successfully', 'success')
            
            # Send welcome email if requested
            if send_welcome_email:
                try:
                    # Import and use your email service
                    from flask_mail import Message
                    from __init__ import mail
                    
                    msg = Message(
                        'Welcome to RiddleNet',
                        recipients=[email],
                        html=f'''
                        <h2>Welcome to RiddleNet, {first_name}!</h2>
                        <p>Your account has been created successfully.</p>
                        <p><strong>Username:</strong> {username}</p>
                        <p><strong>Account Type:</strong> {user_type.title()}</p>
                        <p>Please log in to get started.</p>
                        '''
                    )
                    mail.send(msg)
                    flash('Welcome email sent successfully', 'success')
                except Exception as e:
                    flash(f'User created but welcome email failed to send: {str(e)}', 'warning')

            return jsonify({
                'status': 'success',
                'message': f'User "{username}" created successfully',
                'redirect': url_for('admin_user.index')
            })

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'error')
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    @user_bp.route('/check-username', methods=['POST'])
    @login_required
    def check_username_availability():
        """Check if username is available"""
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            
            if not username:
                return jsonify({'available': False, 'message': 'Username is required'})
            
            # Check in both user tables
            existing_user = InstructorUser.query.filter_by(username=username).first()
            existing_admin = Instructor.query.filter_by(username=username).first()
            
            available = not (existing_user or existing_admin)
            
            return jsonify({
                'available': available,
                'message': 'Username is available' if available else 'Username already exists'
            })
            
        except Exception as e:
            return jsonify({'available': False, 'message': str(e)}), 500

    @staticmethod
    @user_bp.route('/check-email', methods=['POST'])
    @login_required
    def check_email_availability():
        """Check if email is available"""
        try:
            data = request.get_json()
            email = data.get('email', '').strip()
            
            if not email:
                return jsonify({'available': False, 'message': 'Email is required'})
            
            # Check in both user tables
            existing_user = InstructorUser.query.filter_by(email=email).first()
            existing_admin = Instructor.query.filter_by(email=email).first()
            
            available = not (existing_user or existing_admin)
            
            return jsonify({
                'available': available,
                'message': 'Email is available' if available else 'Email already exists'
            })
            
        except Exception as e:
            return jsonify({'available': False, 'message': str(e)}), 500

    @staticmethod
    @user_bp.route('/generate-totp-secret', methods=['POST'])
    @login_required
    def generate_totp_secret():
        """Generate TOTP secret and QR code for new user"""
        try:
            import pyotp
            import qrcode
            import io
            import base64
            
            # Generate random secret
            secret = pyotp.random_base32()
            
            # Create TOTP URL for QR code
            totp_url = pyotp.totp.TOTP(secret).provisioning_uri(
                name="New User",
                issuer_name="RiddleNet"
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
            qr.add_data(totp_url)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 for web display
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            return jsonify({
                'success': True,
                'secret': secret,
                'qr_code_url': f'data:image/png;base64,{img_base64}'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @staticmethod
    @user_bp.route('/profile')
    @login_required
    def admin_profile():
        """Instructor profile page"""
        from flask import session
        
        print("🔍 INSTRUCTOR PROFILE: Route accessed")
        print(f"🔍 INSTRUCTOR PROFILE: Current user = {current_user.username if current_user.is_authenticated else 'Not authenticated'}")
        print(f"🔍 INSTRUCTOR PROFILE: User type = {type(current_user)}")
        
        # CRITICAL FIX: Auto-fix namespace if user is authenticated as Instructor
        auth_namespace = session.get('auth_namespace', 'unknown')
        print(f"🔍 INSTRUCTOR PROFILE: Auth namespace = {auth_namespace}")
        
        # If user is authenticated as Instructor but namespace is wrong, fix it
        if isinstance(current_user, (Instructor, InstructorUser)):
            if auth_namespace != 'instructor':
                print(f"🔧 INSTRUCTOR PROFILE: Auto-fixing namespace from '{auth_namespace}' to 'instructor'")
                session['auth_namespace'] = 'instructor'
                session.modified = True
                auth_namespace = 'instructor'
        
        if auth_namespace != 'instructor':
            print(f"❌ INSTRUCTOR PROFILE: Namespace check failed - expected 'instructor', got '{auth_namespace}'")
            flash('Access denied. Instructor credentials required.', 'error')
            return redirect(url_for('auth.login'))
        
        # Accept both legacy Instructor accounts and InstructorUser teacher accounts
        if not isinstance(current_user, (Instructor, InstructorUser)):
            print(f"❌ INSTRUCTOR PROFILE: User type check failed - user is {type(current_user)}")
            flash('Access denied. Instructor credentials required.', 'error')
            session.clear()  # Clear potentially poisoned session
            return redirect(url_for('auth.login'))
        
        print("✅ INSTRUCTOR PROFILE: All checks passed, rendering template")
        
        try:
            from utils.render_utils import render_safe_template
            return render_safe_template('instructor/profile.html', 
                                      admin=current_user,
                                      instructor=current_user,  # Add instructor variable for template
                                      title="Admin Profile",
                                      active_page='profile')
        except Exception as e:
            print(f"❌ INSTRUCTOR PROFILE: Template rendering error: {str(e)}")
            import logging
            import traceback
            logging.error(f"Error rendering admin profile: {str(e)}")
            traceback.print_exc()
            flash('Error loading profile page', 'error')
            return redirect(url_for('dashboard.index'))  # Fixed endpoint name
    
    @staticmethod
    @user_bp.route('/update_profile', methods=['POST'])
    @login_required
    def update_admin_profile():
        """Update admin profile"""
        from werkzeug.utils import secure_filename
        from flask import session
        
        # CRITICAL FIX: Enforce admin namespace isolation
        auth_namespace = session.get('auth_namespace', 'unknown')
        if auth_namespace != 'admin':
            flash('Access denied. Admin credentials required.', 'error')
            session.clear()  # Clear potentially poisoned session
            return redirect(url_for('auth.login'))
        
        if not isinstance(current_user, Instructor):
            flash('Access denied', 'error')
            session.clear()  # Clear potentially poisoned session
            return redirect(url_for('auth.login'))
        
        admin = current_user
        
        # Get form data
        username = request.form.get('username', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        email = request.form.get('email', '').strip()
        profile_img = request.files.get('profile_img')
        
        try:
            # Validate username
            if not username:
                flash('Username is required', 'error')
                return redirect(url_for('admin_user.admin_profile'))
            
            # Check if username is already taken by another admin
            existing_admin = Instructor.query.filter(Admin.username == username, Admin.id != admin.id).first()
            if existing_admin:
                flash('Username is already taken', 'error')
                return redirect(url_for('admin_user.admin_profile'))
            
            # Handle password update
            if new_password:
                # Validate current password if changing password
                if not current_password:
                    flash('Current password is required to change password', 'error')
                    return redirect(url_for('admin_user.admin_profile'))
                
                if not admin.check_password(current_password):
                    flash('Current password is incorrect', 'error')
                    return redirect(url_for('admin_user.admin_profile'))
                
                # Check if new passwords match
                if new_password != confirm_password:
                    flash('New passwords do not match', 'error')
                    return redirect(url_for('admin_user.admin_profile'))
                
                # Validate password strength using the new validator
                is_valid, errors = validate_password(new_password)
                if not is_valid:
                    flash(errors[0], 'error')
                    return redirect(url_for('admin_user.admin_profile'))
                
                admin.set_password(new_password)
            
            # Handle profile image upload
            if profile_img and profile_img.filename:
                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                file_extension = profile_img.filename.rsplit('.', 1)[1].lower() if '.' in profile_img.filename else ''
                
                if file_extension not in allowed_extensions:
                    flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'error')
                    return redirect(url_for('admin_user.admin_profile'))
                
                # Create filename with admin ID to avoid conflicts
                img_filename = f"admin_{admin.id}_{secure_filename(profile_img.filename)}"
                
                # Ensure the static/img/profiles directory exists
                profiles_dir = os.path.join('static', 'img', 'profiles')
                if not os.path.exists(profiles_dir):
                    os.makedirs(profiles_dir)
                
                # Save the file
                img_path = os.path.join(profiles_dir, img_filename)
                profile_img.save(img_path)
                
                # Update admin profile image (store just the filename, not the full path)
                admin.profile_img = img_filename
            
            # Update admin fields
            admin.username = username
            admin.email = email
            
            # Save changes
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
        
        return redirect(url_for('admin_user.admin_profile'))

    @staticmethod
    @user_bp.route('/available-classes')
    @login_required
    def get_available_classes():
        """Get list of available classes for instructor assignment"""
        try:
            # Import your class model here
            # from instructor.models.class import Class
            # classes = Class.query.filter_by(active=True).all()
            
            # For now, return sample data
            sample_classes = [
                {'id': 1, 'name': 'Networking Fundamentals', 'code': 'NET101'},
                {'id': 2, 'name': 'Advanced Routing', 'code': 'NET201'},
                {'id': 3, 'name': 'Network Security', 'code': 'SEC101'},
                {'id': 4, 'name': 'Wireless Technologies', 'code': 'WIR101'},
                {'id': 5, 'name': 'Network Management', 'code': 'NET301'}
            ]
            
            return jsonify({
                'success': True,
                'classes': sample_classes
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
