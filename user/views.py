from flask import render_template, session, Blueprint, request, redirect, url_for, flash, jsonify
from sqlalchemy import func
import os
import datetime
import traceback
import random
from werkzeug.utils import secure_filename
# Use specific imports with module paths to avoid conflicts
from .models import db
from .models import User as UserModel  # Rename to avoid conflicts
from .models import Score as UserScore  # Rename to avoid conflicts
from admin.models.topology import Topology
from user.models.topology_progress import TopologyProgress
from admin.models.class_model import Class
from flask_login import login_user, logout_user, current_user
from .utils import user_login_required
# Import media utilities
from utils.media_utils import serve_optimized_video, serve_optimized_audio

# Create blueprint as expected by main __init__.py
user_bp = Blueprint('user', __name__)

# Add optimized media routes
@user_bp.route('/media/video/<path:filename>')
def serve_video(filename):
    """Serve video files with optimized settings for WebSocket compatibility"""
    response = serve_optimized_video(filename)
    if response is None:
        return "Video not found", 404
    return response

@user_bp.route('/media/audio/<path:filename>')
def serve_audio(filename):
    """Serve audio files with optimized settings for WebSocket compatibility"""
    response = serve_optimized_audio(filename)
    if response is None:
        return "Audio not found", 404
    return response

@user_bp.route('/')
def index():
    # For login page, check if user is already logged in
    user = None
    if 'user_id' in session:
        user = UserModel.query.get(session['user_id'])
        # If user is already logged in, redirect to dashboard
        if user:
            return redirect(url_for('user.dashboard'))
    
    return render_template('user/index.html', user=user)

@user_bp.route('/overview')
def overview():
    # Overview can be accessed without login, but pass user if available
    user = None
    if 'user_id' in session:
        user = UserModel.query.get(session['user_id'])
    
    return render_template('user/overview.html', user=user)

@user_bp.route('/classes')
def classes():
    if 'user_id' not in session:
        return redirect(url_for('user.index', message='You need to log in first!'))
    
    # No need to fetch classes here - we'll do it client-side with API
    return render_template('user/classes.html')

@user_bp.route('/class/<int:class_id>')
def class_detail(class_id):
    if 'user_id' not in session:
        return redirect(url_for('user.index', message='You need to log in first!'))
    
    user_id = session['user_id']
    user = UserModel.query.get(user_id)
    
    # Find the class
    class_obj = Class.query.get_or_404(class_id)
    
    # Check if user is enrolled in this class using direct query
    from user.models import class_students
    enrollment = db.session.query(class_students).filter(
        class_students.c.class_id == class_id,
        class_students.c.user_id == user_id
    ).first()
    
    if not enrollment:
        flash('You are not enrolled in this class', 'error')
        return redirect(url_for('user.classes'))
    
    # Format student data for template - use direct query
    # We already imported class_students above
    from sqlalchemy import select
    
    # Get student IDs enrolled in this class
    student_ids = db.session.query(class_students.c.user_id).filter(
        class_students.c.class_id == class_id
    ).all()
    
    # Get student details
    student_ids = [student_id[0] for student_id in student_ids]  # Extract IDs from result tuples
    students = UserModel.query.filter(UserModel.id.in_(student_ids)).all()
    
    # Format for template
    students_data = []
    for student in students:
        students_data.append({
            'id': student.id,
            'name': student.username,
            'email': student.email if hasattr(student, 'email') else None
        })
    
    return render_template(
        'user/class_detail.html', 
        class_data=class_obj.to_dict_with_question_groups(),
        students=students_data
    )

@user_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')

    user = UserModel.query.get(session['user_id'])
    user_score = UserScore.query.filter_by(user_id=user.id).all()

    # Overall leaderboard data
    leaderboard_data = (
        db.session.query(
            UserModel.username, 
            func.max(UserScore.score).label('highest_score'), 
            func.max(UserScore.date_attempted).label('latest_attempt')
        )
        .join(UserScore)
        .group_by(UserModel.id)
        .order_by(func.max(UserScore.score).desc())
        .all()
    )

    # Category-specific leaderboards
    categories = ['topology', 'crimping', 'troubleshoot', 'riddle']
    category_leaderboards = {}
    
    for category in categories:
        category_leaderboards[f"{category}_leaderboard"] = (
            db.session.query(
                UserModel.username, 
                func.max(UserScore.score).label('highest_score'), 
                func.max(UserScore.date_attempted).label('latest_attempt')
            )
            .join(UserScore)
            .filter(UserScore.category == category)
            .group_by(UserModel.id)
            .order_by(func.max(UserScore.score).desc())
            .all()
        )

    return render_template(
        'user/dashboard.html', 
        user=user, 
        score=user_score, 
        leaderboard=leaderboard_data,
        **category_leaderboards
    )

@user_bp.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')
    
    try:
        # Overall leaderboard data
        leaderboard_data = (
            db.session.query(
                UserModel.username, 
                func.max(UserScore.score).label('highest_score'), 
                func.max(UserScore.date_attempted).label('latest_attempt')
            )
            .join(UserScore)
            .group_by(UserModel.id)
            .order_by(func.max(UserScore.score).desc())
            .all()
        )
        
        # Category-specific leaderboards
        categories = ['topology', 'crimping', 'troubleshoot', 'riddle']
        category_leaderboards = {}
        
        for category in categories:
            category_leaderboards[f"{category}_leaderboard"] = (
                db.session.query(
                    UserModel.username, 
                    func.max(UserScore.score).label('highest_score'), 
                    func.max(UserScore.date_attempted).label('latest_attempt')
                )
                .join(UserScore)
                .filter(UserScore.category == category)
                .group_by(UserModel.id)
                .order_by(func.max(UserScore.score).desc())
                .all()
            )
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        leaderboard_data = []
        category_leaderboards = {}

    return render_template('user/leaderboard.html', 
                         leaderboard=leaderboard_data, 
                         **category_leaderboards)

@user_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')
    
    user = UserModel.query.get(session['user_id'])
    return render_template('user/profile.html', user=user)

@user_bp.route('/scores')
def scores():
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')
    
    user = UserModel.query.get(session['user_id'])
    user_scores = UserScore.query.filter_by(user_id=user.id).order_by(UserScore.date_attempted.desc()).all()
    
    # Calculate statistics
    total_attempts = len(user_scores)
    total_score = sum(score.score for score in user_scores)
    average_score = total_score / total_attempts if total_attempts > 0 else 0
    highest_score = max(score.score for score in user_scores) if user_scores else 0
    
    # Category statistics
    categories = ['topology', 'crimping', 'troubleshoot', 'riddle']
    category_stats = {}
    for category in categories:
        category_scores = [score for score in user_scores if score.category == category]
        category_stats[category] = {
            'attempts': len(category_scores),
            'best_score': max(score.score for score in category_scores) if category_scores else 0,
            'average': sum(score.score for score in category_scores) / len(category_scores) if category_scores else 0
        }
    
    return render_template('user/scores.html', 
                         user=user, 
                         scores=user_scores,
                         total_attempts=total_attempts,
                         average_score=average_score,
                         highest_score=highest_score,
                         category_stats=category_stats)

@user_bp.route('/about_us')
def about_us():
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')
    
    return render_template('user/about_us.html')

@user_bp.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')

    user = UserModel.query.get(session['user_id'])
    username = request.form['username']
    password = request.form['password']
    profile_img = request.files.get('profile_img')

    user.username = username
    if password:
        user.set_password(password)
    if profile_img and profile_img.filename:
        img_filename = secure_filename(profile_img.filename)
        profile_img.save(os.path.join('static/img', img_filename))
        user.profile_img = f'img/{img_filename}'

    db.session.commit()
    return redirect(url_for('user.dashboard'))

@user_bp.route('/delete_score/<int:score_id>', methods=['POST'])
def delete_score(score_id):
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')
        
    score = UserScore.query.get(score_id)
    if score and score.user_id == session['user_id']:
        db.session.delete(score)
        db.session.commit()
    return redirect(url_for('user.dashboard'))

@user_bp.route('/troubleshoot')
def troubleshoot():
    # Pass user context if available
    user = None
    if 'user_id' in session:
        user = UserModel.query.get(session['user_id'])
    
    return render_template('user/troubleshoot.html', title="troubleshoot", user=user)

@user_bp.route('/crimp')
def crimp():
    # Pass user context if available
    user = None
    if 'user_id' in session:
        user = UserModel.query.get(session['user_id'])
    
    return render_template('user/crimping-simulation.html', title="crimp", user=user)

@user_bp.route('/logout')
def logout():
    # Get user info before clearing session for WebSocket notification
    user_id = session.get('user_id')
    username = None
    
    if user_id:
        user = UserModel.query.get(user_id)
        username = user.username if user else 'unknown'
    
    # Send WebSocket notification for logout attempt
    try:
        socketio = get_socketio()
        if socketio and user_id:
            # Notify admin of user logout
            socketio.emit('user_login_activity', {
                'user_id': user_id,
                'username': username,
                'action': 'logout',
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
            }, room='admin_room')
            
            # Send logout notification to user's personal room
            socketio.emit('logout_complete', {
                'status': 'success',
                'message': f'Goodbye, {username}!',
                'timestamp': datetime.datetime.utcnow().isoformat()
            }, room=f'user_{user_id}')
            
            print(f"WebSocket logout notifications sent for user: {username}")
    except Exception as ws_error:
        print(f"WebSocket logout notification failed: {str(ws_error)}")
    
    # Use Flask-Login logout
    from flask_login import logout_user
    logout_user()
    
    # Clear the user's session
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('user.index'))

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If it's a GET request, render the login page
    if request.method == 'GET':
        next_url = request.args.get('next', '')
        return render_template('user/index.html', next=next_url)
    
    # Otherwise, handle the login POST request
    username = request.form.get('username')
    password = request.form.get('password')
    otp = request.form.get('otp')
    
    # Debug info
    print(f"Login attempt for: {username}")
    print(f"OTP provided: {'Yes' if otp else 'No'}")
    
    # Send WebSocket notification for login attempt start
    try:
        socketio = get_socketio()
        if socketio:
            socketio.emit('user_login_activity', {
                'username': username,
                'action': 'login_attempt_started',
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'ip_address': request.environ.get('REMOTE_ADDR', 'unknown'),
                'user_agent': request.headers.get('User-Agent', 'unknown')
            }, room='admin_room')
    except Exception as ws_error:
        print(f"WebSocket login attempt notification failed: {str(ws_error)}")
    
    # Find the user by username
    user = UserModel.query.filter_by(username=username).first()
    
    if not user:
        print(f"User not found: {username}")
        
        # Send WebSocket notification for failed login (user not found)
        try:
            socketio = get_socketio()
            if socketio:
                socketio.emit('user_login_activity', {
                    'username': username,
                    'action': 'login_failed',
                    'reason': 'user_not_found',
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                }, room='admin_room')
        except Exception as ws_error:
            print(f"WebSocket login failure notification failed: {str(ws_error)}")
        
        return render_template('user/index.html', message='Invalid username.')
    
    # Debug info
    print(f"User found: {user.username}, TOTP enabled: {user.totp_enabled}, TOTP secret exists: {'Yes' if user.totp_secret else 'No'}")
      # Validate password
    if not user.check_password(password):
        print(f"Invalid password for user: {username}")
        
        # Send WebSocket notification for failed login (invalid password)
        try:
            socketio = get_socketio()
            if socketio:
                socketio.emit('user_login_activity', {
                    'user_id': user.id,
                    'username': username,
                    'action': 'login_failed',
                    'reason': 'invalid_password',
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                }, room='admin_room')
        except Exception as ws_error:
            print(f"WebSocket login failure notification failed: {str(ws_error)}")
        
        return render_template('user/index.html', message='Invalid password.')      # Validate OTP if TOTP is enabled for this user
    if user.totp_enabled:
        if not otp:
            print(f"OTP required but not provided for user: {username}")
            
            # Send WebSocket notification for missing OTP
            try:
                socketio = get_socketio()
                if socketio:
                    socketio.emit('user_login_activity', {
                        'user_id': user.id,
                        'username': username,
                        'action': 'login_failed',
                        'reason': 'otp_required_but_not_provided',
                        'timestamp': datetime.datetime.utcnow().isoformat(),
                        'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                    }, room='admin_room')
            except Exception as ws_error:
                print(f"WebSocket OTP missing notification failed: {str(ws_error)}")
            
            return render_template('user/index.html', message='OTP is required for this account. Please click "Request OTP" to receive a code via email.')
        
        try:
            # Check if OTP matches and hasn't expired (10 minute validity)
            if user.otp != otp:
                print(f"Invalid OTP code for user: {username}")
                
                # Send WebSocket notification for invalid OTP
                try:
                    socketio = get_socketio()
                    if socketio:
                        socketio.emit('user_login_activity', {
                            'user_id': user.id,
                            'username': username,
                            'action': 'login_failed',
                            'reason': 'invalid_otp',
                            'timestamp': datetime.datetime.utcnow().isoformat(),
                            'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                        }, room='admin_room')
                except Exception as ws_error:
                    print(f"WebSocket invalid OTP notification failed: {str(ws_error)}")
                
                return render_template('user/index.html', message='Invalid OTP code. Please try again or request a new code.')
                
            # Check if OTP is expired (10 minutes)
            current_time = datetime.datetime.now()
            if user.otp_generated_at:
                otp_age = current_time - user.otp_generated_at
                if otp_age.total_seconds() > 600:  # 10 minutes in seconds
                    print(f"Expired OTP code for user: {username}")
                    
                    # Send WebSocket notification for expired OTP
                    try:
                        socketio = get_socketio()
                        if socketio:
                            socketio.emit('user_login_activity', {
                                'user_id': user.id,
                                'username': username,
                                'action': 'login_failed',
                                'reason': 'otp_expired',
                                'otp_age_minutes': round(otp_age.total_seconds() / 60, 2),
                                'timestamp': datetime.datetime.utcnow().isoformat(),
                                'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                            }, room='admin_room')
                    except Exception as ws_error:
                        print(f"WebSocket expired OTP notification failed: {str(ws_error)}")
                    
                    return render_template('user/index.html', message='OTP code has expired. Please click "Request OTP" for a new code.')
            else:
                print(f"OTP generation timestamp missing for user: {username}")
                
                # Send WebSocket notification for missing OTP timestamp
                try:
                    socketio = get_socketio()
                    if socketio:
                        socketio.emit('user_login_activity', {
                            'user_id': user.id,
                            'username': username,
                            'action': 'login_failed',
                            'reason': 'otp_timestamp_missing',
                            'timestamp': datetime.datetime.utcnow().isoformat(),
                            'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                        }, room='admin_room')
                except Exception as ws_error:
                    print(f"WebSocket OTP timestamp missing notification failed: {str(ws_error)}")
                
                return render_template('user/index.html', message='Invalid OTP. Please click "Request OTP" for a new code.')
                
            # Clear the OTP after successful validation
            user.otp = None
            user.otp_generated_at = None
            db.session.commit()
            
        except Exception as e:
            print(f"Error validating OTP for user {username}: {str(e)}")
            
            # Send WebSocket notification for OTP validation error
            try:
                socketio = get_socketio()
                if socketio:
                    socketio.emit('user_login_activity', {
                        'user_id': user.id,
                        'username': username,
                        'action': 'login_failed',
                        'reason': 'otp_validation_error',
                        'error': str(e),
                        'timestamp': datetime.datetime.utcnow().isoformat(),
                        'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                    }, room='admin_room')
            except Exception as ws_error:
                print(f"WebSocket OTP validation error notification failed: {str(ws_error)}")
            
            return render_template('user/index.html', message=f'Error validating OTP: {str(e)}. Please try again.')
      # Set user in session
    session['user_id'] = user.id
    print(f"Login successful for user: {username}, user_id: {user.id}")
    
    # Use Flask-Login for proper login and authentication
    # Remember=True ensures the user stays logged in for the session
    login_user(user, remember=True)
    print(f"Flask-Login current_user: {current_user.is_authenticated}")
    
    # Send WebSocket notification for successful login
    try:
        socketio = get_socketio()
        if socketio:
            # Notify admin of successful login
            socketio.emit('user_login_activity', {
                'user_id': user.id,
                'username': username,
                'action': 'login_successful',
                'email': user.email,
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'ip_address': request.environ.get('REMOTE_ADDR', 'unknown'),
                'user_agent': request.headers.get('User-Agent', 'unknown')
            }, room='admin_room')
            
            # Send welcome notification to user's personal room
            socketio.emit('login_success', {
                'status': 'success',
                'message': f'Welcome back, {username}!',
                'timestamp': datetime.datetime.utcnow().isoformat()
            }, room=f'user_{user.id}')
            
            print(f"WebSocket login success notifications sent for user: {username}")
    except Exception as ws_error:
        print(f"WebSocket login success notification failed: {str(ws_error)}")
    
    # Check if there's a next parameter in the query string or form
    next_url = request.args.get('next') or request.form.get('next')
    if next_url:
        # Make sure the next URL is safe (belongs to the same site)
        if next_url.startswith('/'):
            print(f"Redirecting to: {next_url}")
            return redirect(next_url)
    
    # Redirect to dashboard on successful login if no next URL
    print("Redirecting to dashboard")
    return redirect(url_for('user.dashboard'))

@user_bp.route('/signup', methods=['POST'])
def signup():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle AJAX request
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')  # Add email field
        
        # Check if username exists
        existing_user = UserModel.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'status': 'error', 'message': 'Username already exists. Please choose another one.'}), 400
        
        # Check if email exists
        existing_email = UserModel.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'status': 'error', 'message': 'Email address already in use. Please use a different email.'}), 400
        
        # Create new user
        new_user = UserModel(username=username, email=email)  # Include email
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Account created successfully! You can now log in.'}), 201
    else:
        # Handle regular form submission
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')  # Add email field
          # Check if username exists
        existing_user = UserModel.query.filter_by(username=username).first()
        if existing_user:
            return render_template('user/index.html', message='Username already exists. Please choose another one.')
        
        # Check if email exists
        existing_email = UserModel.query.filter_by(email=email).first()
        if existing_email:
            return render_template('user/index.html', message='Email address already in use. Please use a different email.')
        
        # Create new user
        new_user = UserModel(username=username, email=email)  # Include email
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('user.index', message='Account created successfully! Please log in.'))

@user_bp.route('/send_otp', methods=['POST'])
def send_otp():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = request.get_json()
            username = data.get('username')
            
            if not username:
                return jsonify({'status': 'error', 'message': 'Username is required'}), 400
            
            # Find the user in the database
            user = UserModel.query.filter_by(username=username).first()
            if not user:
                return jsonify({'status': 'error', 'message': 'User not found'}), 404
            
            # Check if user has an email
            if not user.email:
                return jsonify({'status': 'error', 'message': 'Email not found for this user. Please update your profile with an email address.'}), 400
            
            # Generate a random 6-digit OTP
            import random
            otp = str(random.randint(100000, 999999))
            
            # Update the user's OTP in the database
            user.otp = otp
            user.otp_generated_at = datetime.datetime.now()
            user.totp_enabled = True  # Keep this flag for consistency
            db.session.commit()
            
            # Send WebSocket notification to admin for real-time monitoring
            try:
                socketio = get_socketio()
                if socketio:
                    # Notify admin room about OTP request
                    socketio.emit('user_otp_activity', {
                        'user_id': user.id,
                        'username': username,
                        'action': 'otp_requested',
                        'email': user.email,
                        'timestamp': datetime.datetime.utcnow().isoformat(),
                        'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                    }, room='admin_room')
                    
                    # Send real-time notification to user's personal room
                    socketio.emit('otp_request_received', {
                        'status': 'processing',
                        'message': 'OTP request received, sending email...',
                        'timestamp': datetime.datetime.utcnow().isoformat()
                    }, room=f'user_{user.id}')
                    
                    print(f"WebSocket notifications sent for OTP request: {username}")
            except Exception as ws_error:
                print(f"WebSocket notification failed: {str(ws_error)}")
            
            # Send OTP via email using optimized direct SMTP connection
            success = send_otp_email_direct(user.email, user.username, otp)
            
            if success:
                # Send WebSocket success notification
                try:
                    socketio = get_socketio()
                    if socketio:
                        # Notify admin of successful OTP delivery
                        socketio.emit('user_otp_activity', {
                            'user_id': user.id,
                            'username': username,
                            'action': 'otp_sent_successfully',
                            'email': user.email,
                            'timestamp': datetime.datetime.utcnow().isoformat()
                        }, room='admin_room')
                        
                        # Notify user of successful email delivery
                        socketio.emit('otp_email_sent', {
                            'status': 'success',
                            'message': 'OTP sent to your email successfully',
                            'timestamp': datetime.datetime.utcnow().isoformat()
                        }, room=f'user_{user.id}')
                except Exception as ws_error:
                    print(f"WebSocket success notification failed: {str(ws_error)}")
                
                return jsonify({'status': 'success', 'message': 'OTP sent to your email'}), 200
            else:
                # Send WebSocket failure notification
                try:
                    socketio = get_socketio()
                    if socketio:
                        # Notify admin of failed OTP delivery
                        socketio.emit('user_otp_activity', {
                            'user_id': user.id,
                            'username': username,
                            'action': 'otp_failed',
                            'email': user.email,
                            'error': 'SMTP delivery failed',
                            'timestamp': datetime.datetime.utcnow().isoformat()
                        }, room='admin_room')
                        
                        # Notify user of failed email delivery
                        socketio.emit('otp_email_failed', {
                            'status': 'error',
                            'message': 'Failed to send OTP email',
                            'timestamp': datetime.datetime.utcnow().isoformat()
                        }, room=f'user_{user.id}')
                except Exception as ws_error:
                    print(f"WebSocket failure notification failed: {str(ws_error)}")
                
                # Fast fallback for production: Return failure without development mode OTP display
                return jsonify({
                    'status': 'error', 
                    'message': 'Failed to send OTP email. Please check your email configuration and try again.'
                }), 500
        except Exception as e:
            print(f"Error in send_otp: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
            # Send WebSocket error notification
            try:
                socketio = get_socketio()
                if socketio:
                    socketio.emit('user_otp_activity', {
                        'username': username if 'username' in locals() else 'unknown',
                        'action': 'otp_error',
                        'error': str(e),
                        'timestamp': datetime.datetime.utcnow().isoformat()
                    }, room='admin_room')
            except Exception as ws_error:
                print(f"WebSocket error notification failed: {str(ws_error)}")
            
            return jsonify({'status': 'error', 'message': 'Internal server error. Please try again.'}), 500
    else:
        return jsonify({'status': 'error', 'message': 'This endpoint only accepts AJAX requests'}), 400

@user_bp.route('/topology')
@user_login_required
def topology():
    """Render the topology page with database-driven topology configurations."""
    print(f"In topology route. User authenticated: {current_user.is_authenticated}")
    print(f"Session user_id: {session.get('user_id')}")
    
    # Get all active topology types and data from the database
    topologies = Topology.query.filter_by(is_active=True).all()
    
    # Format the topology data for the frontend
    topology_data = {}
    topology_types = []
    
    for topology in topologies:
        topology_types.append(topology.topology_type)
        topology_data[topology.topology_type] = {
            'title': topology.title,
            'description': topology.description,
            'device_requirements': topology.device_requirements,
            'base_score': topology.base_score,
            'scoring_metrics': topology.scoring_metrics,
            'validation_rules': {
                'expected_config': topology.expected_config,
                'rules': []  # Add validation rules if needed
            }
        }
    
    # Get user's completed topologies
    completed_topologies = []
    if current_user.is_authenticated:
        user_progress = TopologyProgress.query.filter_by(user_id=current_user.id).all()
        for progress in user_progress:
            if progress.completion_count > 0:
                completed_topologies.append(progress.topology_type)
    
    # Render the template with the data
    return render_template(
        'user/topology.html',
        topology_data=topology_data,
        topology_types=topology_types,
        completed_topologies=completed_topologies
    )

@user_bp.route('/topology/challenges')
@user_login_required
def get_topology_challenges():
    """Get all active topology challenges"""
    topologies = Topology.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': topology.id,
        'title': topology.title,
        'description': topology.description,
        'difficulty': topology.difficulty,
        'topology_type': topology.topology_type,
        'base_score': topology.base_score
    } for topology in topologies]), 200

@user_bp.route('/topology/challenge/<int:topology_id>')
@user_login_required
def get_topology_challenge(topology_id):
    """Get a specific topology challenge by ID"""
    topology = Topology.query.get_or_404(topology_id)
    
    return jsonify({
        'id': topology.id,
        'title': topology.title,
        'description': topology.description,
        'difficulty': topology.difficulty,
        'topology_type': topology.topology_type,
        'initial_config': topology.get_initial_config(),
        'base_score': topology.base_score,
        'time_bonus': topology.time_bonus,
        'perfect_match_bonus': topology.perfect_match_bonus
    }), 200

@user_bp.route('/topology/completed')
@user_login_required
def get_completed_topologies():
    """Get IDs of topology challenges completed by the current user"""
    user_id = current_user.id
    
    # Query the Score table for completed topology challenges
    completed_score = UserScore.query.filter_by(
        user_id=user_id,
        category='topology'
    ).all()
    
    # Since topic_id doesn't exist, we'll return empty list for now
    # This can be updated later if you add a way to track completed topologies
    completed_ids = []
    
    return jsonify({'completed': completed_ids}), 200

@user_bp.route('/save_topology_score', methods=['POST'])
@user_login_required
def save_topology_score():
    """Save a topology score for the current user"""
    data = request.json
    user_id = current_user.id
    
    if not data or 'score' not in data or 'category' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    # Create a new score record
    new_score = UserScore(
        user_id=user_id,
        score=data['score'],
        category=data['category']
        # topic_id field removed as it doesn't exist in the database
    )
    
    db.session.add(new_score)
    db.session.commit()
    
    # Score logging removed
    
    return jsonify({'status': 'success', 'message': 'Score saved successfully'}), 200

@user_bp.route('/topology/progress', methods=['POST'])
@user_login_required
def save_topology_progress():
    """Save user's topology progress to the database"""
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Invalid request format'}), 400
    
    data = request.json
    topology_type = data.get('topology_type')
    completed = data.get('completed', False)
    score = data.get('score', 0)
    
    if not topology_type:
        return jsonify({'status': 'error', 'message': 'Topology type is required'}), 400
    
    try:
        # Check if progress record exists for this user and topology type
        progress = TopologyProgress.query.filter_by(
            user_id=current_user.id,
            topology_type=topology_type
        ).first()
        
        if progress:
            # Update existing record
            if score > progress.highest_score:
                progress.highest_score = score
            
            if completed:
                progress.completion_count += 1
            
            progress.last_attempt = datetime.datetime.utcnow()
        else:
            # Create new record
            progress = TopologyProgress(
                user_id=current_user.id,
                topology_type=topology_type,
                highest_score=score,
                completion_count=1 if completed else 0,
            )
            db.session.add(progress)
        
        db.session.commit()
        return jsonify({
            'status': 'success', 
            'message': 'Progress saved',
            'progress': {
                'topology_type': topology_type,
                'highest_score': progress.highest_score,
                'completion_count': progress.completion_count
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error saving topology progress: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@user_bp.route('/api/topology/config/<topology_type>', methods=['GET'])
@user_login_required
def get_topology_config(topology_type):
    """Get configuration for a specific topology type"""
    try:
        # Find the topology in the database
        topology = Topology.query.filter_by(
            topology_type=topology_type,
            is_active=True
        ).first()
        
        if not topology:
            return jsonify({
                'status': 'error',
                'message': f'No active topology found with type: {topology_type}'
            }), 404
        
        # Return the configuration data
        return jsonify({
            'status': 'success',
            'config': {
                'title': topology.title,
                'description': topology.description,
                'device_requirements': topology.device_requirements,
                'base_score': topology.base_score,
                'scoring_metrics': topology.scoring_metrics,
                'validation_rules': {
                    'expected_config': topology.expected_config,
                    'rules': []  # Add validation rules if needed
                }
            }
        })
    
    except Exception as e:
        print(f"Error retrieving topology config: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve topology configuration: {str(e)}'
        }), 500

@user_bp.route('/api/topology/types', methods=['GET'])
@user_login_required
def get_topology_types():
    """Get all available topology types"""
    try:        # Query all active topologies and get their types
        topologies = Topology.query.filter_by(is_active=True).all()
        topology_types = [topology.topology_type for topology in topologies]
        
        # If no topologies are found, use default types
        if not topology_types:
            topology_types = ['point-to-point', 'mesh', 'star', 'bus', 'ring', 'tree', 'hybrid']
            
        return jsonify({
            'status': 'success',
            'topology_types': topology_types
        })
        
    except Exception as e:
        print(f"Error retrieving topology types: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve topology types: {str(e)}'
        }), 500

# =============================================================================
# WebSocket Event Handlers for User Module
# =============================================================================

# Import WebSocket dependencies lazily to avoid circular imports
def get_socketio():
    """Get socketio instance lazily to avoid import issues"""
    try:
        from socket_manager import socketio
        return socketio
    except ImportError:
        return None

def get_socketio_decorators():
    """Get socketio decorators lazily"""
    try:
        from flask_socketio import emit, join_room, leave_room
        from socket_manager import authenticated_only
        return emit, join_room, leave_room, authenticated_only
    except ImportError:
        return None, None, None, None

# Register WebSocket events for user functionality
def register_user_websocket_events():
    """Register user-specific WebSocket events"""
    socketio = get_socketio()
    if not socketio:
        print("WebSocket not available - running without real-time features")
        return
    
    emit, join_room, leave_room, authenticated_only = get_socketio_decorators()
    if not all([emit, join_room, leave_room, authenticated_only]):
        print("WebSocket decorators not available")
        return

    @socketio.on('user_join_general')
    @authenticated_only
    def handle_user_join_general():
        """Handle user joining general room for notifications"""
        try:
            if current_user.is_authenticated:
                join_room('user_general')
                emit('user_joined', {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'timestamp': datetime.datetime.utcnow().isoformat()
                })
                print(f"User {current_user.username} joined general room")
        except Exception as e:
            print(f"Error in user_join_general: {str(e)}")

    @socketio.on('user_activity_update')
    @authenticated_only
    def handle_user_activity_update(data):
        """Handle user activity updates (page visits, interactions)"""
        try:
            activity_type = data.get('activity_type', 'unknown')
            page = data.get('page', 'unknown')
            details = data.get('details', {})
            
            # Emit to admin room for monitoring
            socketio.emit('user_activity', {
                'user_id': current_user.id,
                'username': current_user.username,
                'activity_type': activity_type,
                'page': page,
                'details': details,
                'timestamp': datetime.datetime.utcnow().isoformat()
            }, room='admin_room')
            
            print(f"User {current_user.username} activity: {activity_type} on {page}")
        except Exception as e:
            print(f"Error in user_activity_update: {str(e)}")

    @socketio.on('user_topology_join')
    @authenticated_only
    def handle_user_topology_join(data):
        """Handle user joining a topology challenge room"""
        try:
            topology_type = data.get('topology_type')
            if not topology_type:
                return
            
            room_name = f"topology_{topology_type}"
            join_room(room_name)
            
            # Notify admin of user joining topology
            socketio.emit('user_topology_activity', {
                'user_id': current_user.id,
                'username': current_user.username,
                'action': 'joined',
                'topology_type': topology_type,
                'timestamp': datetime.datetime.utcnow().isoformat()
            }, room='admin_room')
            
            emit('topology_joined', {'topology_type': topology_type})
            print(f"User {current_user.username} joined topology {topology_type}")
        except Exception as e:
            print(f"Error in user_topology_join: {str(e)}")

    @socketio.on('user_topology_progress')
    @authenticated_only
    def handle_user_topology_progress(data):
        """Handle real-time topology progress updates"""
        try:
            topology_type = data.get('topology_type')
            progress = data.get('progress', 0)
            score = data.get('score', 0)
            completed = data.get('completed', False)
            
            if not topology_type:
                return
            
            # Update progress in database
            try:
                topology_progress = TopologyProgress.query.filter_by(
                    user_id=current_user.id,
                    topology_type=topology_type
                ).first()
                
                if topology_progress:
                    if score > topology_progress.highest_score:
                        topology_progress.highest_score = score
                    if completed:
                        topology_progress.completion_count += 1
                    topology_progress.last_attempt = datetime.datetime.utcnow()
                else:
                    topology_progress = TopologyProgress(
                        user_id=current_user.id,
                        topology_type=topology_type,
                        highest_score=score,
                        completion_count=1 if completed else 0,
                        last_attempt=datetime.datetime.utcnow()
                    )
                    db.session.add(topology_progress)
                
                db.session.commit()
            except Exception as db_error:
                print(f"Database error in topology progress: {str(db_error)}")
                db.session.rollback()
            
            # Emit progress to admin room for monitoring
            socketio.emit('user_topology_progress', {
                'user_id': current_user.id,
                'username': current_user.username,
                'topology_type': topology_type,
                'progress': progress,
                'score': score,
                'completed': completed,
                'timestamp': datetime.datetime.utcnow().isoformat()
            }, room='admin_room')
            
            # Emit to topology room
            room_name = f"topology_{topology_type}"
            socketio.emit('topology_progress_updated', {
                'user_id': current_user.id,
                'progress': progress,
                'score': score
            }, room=room_name)
            
            print(f"User {current_user.username} topology progress: {topology_type} - {progress}%")
        except Exception as e:
            print(f"Error in user_topology_progress: {str(e)}")

    @socketio.on('user_score_update')
    @authenticated_only
    def handle_user_score_update(data):
        """Handle user score updates with real-time notifications"""
        try:
            category = data.get('category', 'general')
            score = data.get('score', 0)
            topic_id = data.get('topic_id')
            
            # Save score to database
            try:
                new_score = UserScore(
                    user_id=current_user.id,
                    score=score,
                    category=category
                )
                db.session.add(new_score)
                db.session.commit()
                
                # Emit to admin room for monitoring
                socketio.emit('user_score_achieved', {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'category': category,
                    'score': score,
                    'timestamp': datetime.datetime.utcnow().isoformat()
                }, room='admin_room')
                
                emit('score_saved', {
                    'status': 'success',
                    'score': score,
                    'category': category
                })
                
                print(f"User {current_user.username} scored {score} in {category}")
            except Exception as db_error:
                print(f"Database error saving score: {str(db_error)}")
                db.session.rollback()
                emit('score_error', {'message': 'Failed to save score'})
                
        except Exception as e:
            print(f"Error in user_score_update: {str(e)}")

    @socketio.on('user_otp_requested')
    @authenticated_only
    def handle_user_otp_requested(data):
        """Handle OTP request notifications for admin monitoring"""
        try:
            username = data.get('username', current_user.username)
            
            # Notify admin of OTP request
            socketio.emit('user_otp_activity', {
                'user_id': current_user.id,
                'username': username,
                'action': 'otp_requested',
                'timestamp': datetime.datetime.utcnow().isoformat()
            }, room='admin_room')
            
            print(f"OTP requested for user: {username}")
        except Exception as e:
            print(f"Error in user_otp_requested: {str(e)}")

    @socketio.on('user_login_attempt')
    def handle_user_login_attempt(data):
        """Handle login attempt notifications (no auth required)"""
        try:
            username = data.get('username', 'unknown')
            success = data.get('success', False)
            method = data.get('method', 'password')  # 'password', 'otp'
            
            # Notify admin of login attempt
            socketio.emit('user_login_activity', {
                'username': username,
                'success': success,
                'method': method,
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
            }, room='admin_room')
            
            print(f"Login attempt: {username} - {'Success' if success else 'Failed'} ({method})")
        except Exception as e:
            print(f"Error in user_login_attempt: {str(e)}")

    print("User WebSocket events registered successfully")

# Call the registration function when module is loaded
try:
    register_user_websocket_events()
except Exception as e:
    print(f"Could not register WebSocket events: {str(e)}")
    print("Continuing without real-time features...")

# =============================================================================
# OTP Email Function (Enhanced with WebSocket Support)
# =============================================================================
def send_otp_email_direct(recipient_email, username, otp):
    """
    Send OTP email using standard SMTP configuration.
    Simple and reliable email delivery for OTP authentication.
    """
    import smtplib
    import ssl
    import os
    import socket
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        # Use hostname but override DNS to use direct IP to bypass Eventlet DNS issues
        smtp_server = 'smtp.gmail.com'  # Use hostname for SSL certificate validation
        smtp_server_ip = '142.250.153.109'  # Gmail SMTP server IP
        smtp_port = 587
        sender_email = os.getenv('MAIL_USERNAME')
        sender_password = os.getenv('MAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            print("Email configuration missing")
            return False
        
        print(f"Connecting to Gmail SMTP at {smtp_server_ip}:{smtp_port} (hostname: {smtp_server})")
        
        # Create message with proper hostname for SMTP HELO command
        message = MIMEMultipart('alternative')
        message['Subject'] = 'RiddleNet OTP Verification'
        message['From'] = sender_email
        message['To'] = recipient_email
        
        # Create the email content
        text = f"""
        Hello {username},
        
        Your OTP verification code is: {otp}
        
        This code will expire in 10 minutes.
        
        If you did not request this code, please ignore this email.
        
        Best regards,
        RiddleNet Team
        """
        
        html = f"""
        <html>
        <body>
            <h2>RiddleNet OTP Verification</h2>
            <p>Hello <strong>{username}</strong>,</p>
            <p>Your OTP verification code is:</p>
            <h1 style="color: #007bff; font-size: 32px; text-align: center; background-color: #f8f9fa; padding: 20px; border-radius: 5px;">{otp}</h1>
            <p>This code will expire in <strong>10 minutes</strong>.</p>
            <p>If you did not request this code, please ignore this email.</p>
            <br>
            <p>Best regards,<br>RiddleNet Team</p>
        </body>
        </html>
        """
        
        # Convert to MIMEText objects
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        # Add parts to message
        message.attach(part1)
        message.attach(part2)
        
        # Create secure connection and send email - disable SSL verification for IP connection
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Create connection using IP address
        with smtplib.SMTP(smtp_server_ip, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        
        print(f"OTP email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Create blueprint as expected by main __init__.py
