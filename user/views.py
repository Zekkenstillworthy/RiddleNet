from flask import render_template, session, Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func
import os
from datetime import datetime
import sys
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
# Static content imports removed - using database-driven content
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
@login_required
def classes():
    if not current_user.is_authenticated:
        return redirect(url_for('user.index', message='You need to log in first!'))
    
    user = current_user
    # No need to fetch classes here - we'll do it client-side with API
    return render_template('user/class.html', user=user)
    
@user_bp.route('/learning/networking-1')
def networking_1():
    # Redirect directly to first lesson of first module of class 7
    from admin.models.module import Module, Lesson
    try:
        first_module = Module.query.filter_by(class_id=7, is_active=True, is_published=True).order_by(Module.order_index.asc()).first()
        if first_module:
            first_lesson = Lesson.query.filter_by(module_id=first_module.id, is_active=True).order_by(Lesson.order_index.asc()).first()
            if first_lesson:
                return redirect(url_for('universal_class.module_detail', class_id=7, module_id=first_module.id) + f'?lesson_id={first_lesson.id}')
        # Fallback to universal class page (which itself will redirect)
        return redirect(url_for('universal_class.dynamic_class_detail', class_id=7))
    except Exception as e:
        print(f"Error redirecting networking_1: {e}")
        return redirect(url_for('universal_class.dynamic_class_detail', class_id=7))

@user_bp.route('/learning/networking-2')
def networking_2():
    # Redirect to class 9 instead of the old learning page
    return redirect('/class/9/')

# Use universal dynamic class route
# UNIVERSAL CLASS ROUTE - Using direct import since blueprint registration has issues
@user_bp.route('/class/<int:class_id>')
@user_bp.route('/class/<int:class_id>/')  # Handle trailing slash
def class_detail_universal(class_id):
    """Universal class route - imports the dynamic class detail function directly"""
    try:
        # Import the universal class detail function
        from user.routes.universal_class_routes import dynamic_class_detail
        # Call it directly with the same parameters it expects
        return dynamic_class_detail(class_id)
    except Exception as e:
        # Provide helpful error information for debugging
        flash(f'Error loading class {class_id}: {str(e)}', 'error')
        return redirect(url_for('user.classes'))

# CLASS ROUTING NOW HANDLED BY UNIVERSAL TEMPLATE SYSTEM
# All class details are handled by the dynamic universal template system in universal_class_routes.py

@user_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_authenticated:
        return render_template('user/index.html', message='You need to log in first!')

    user = current_user
    user_score = UserScore.query.filter_by(user_id=user.id).all()

    # Get user's best scores for each category
    topology_score = db.session.query(func.max(UserScore.score)).filter(
        UserScore.user_id == user.id,
        UserScore.category == 'topology'
    ).scalar() or 0
    
    crimping_score = db.session.query(func.max(UserScore.score)).filter(
        UserScore.user_id == user.id,
        UserScore.category == 'crimping'
    ).scalar() or 0
    
    osi_score = db.session.query(func.max(UserScore.score)).filter(
        UserScore.user_id == user.id,
        UserScore.category == 'osi'
    ).scalar() or 0

    try:
        # Enhanced leaderboard data with user details and profile images (migrated from leaderboard route)
        user_best_scores = []
        # Get all users with scores including profile image
        users_with_scores = (
            db.session.query(UserModel.id, UserModel.username, UserModel.profile_img)
            .join(UserScore)
            .distinct()
            .all()
        )
        
        # For each user, get their highest score entry
        for user_id, username, profile_img in users_with_scores:
            highest_score_entry = (
                db.session.query(UserScore)
                .filter(UserScore.user_id == user_id)
                .order_by(UserScore.score.desc(), UserScore.date_attempted.desc())
                .first()
            )
            
            if highest_score_entry:
                # Create a simple object-like structure for the template
                class LeaderboardEntry:
                    def __init__(self, user_id, username, score, category, date_attempted, profile_img):
                        self.user_id = user_id
                        self.username = username
                        self.score = score
                        self.category = category
                        self.date_attempted = date_attempted
                        self.profile_img = profile_img
                
                entry = LeaderboardEntry(
                    user_id=user_id,
                    username=username,
                    score=highest_score_entry.score,
                    category=highest_score_entry.category,
                    date_attempted=highest_score_entry.date_attempted,
                    profile_img=profile_img
                )
                user_best_scores.append(entry)
        
        # Sort by score (highest first)
        leaderboard_data = sorted(user_best_scores, key=lambda x: x.score, reverse=True)
        
        # Category-specific leaderboards with enhanced data
        categories = ['topology', 'crimping', 'troubleshoot', 'riddle']
        category_leaderboards = {}
        for category in categories:
            category_leaderboards[f"{category}_leaderboard"] = (
                db.session.query(
                    UserModel.username, 
                    UserModel.profile_img,
                    func.max(UserScore.score).label('highest_score'), 
                    func.max(UserScore.date_attempted).label('latest_attempt')
                )
                .join(UserScore)
                .filter(UserScore.category == category)
                .group_by(UserModel.id, UserModel.username, UserModel.profile_img)
                .order_by(func.max(UserScore.score).desc())
                .all()
            )
    except Exception as e:
        print(f"ERROR in dashboard leaderboard: {e}")
        import traceback
        traceback.print_exc()
        leaderboard_data = []
        category_leaderboards = {}

    return render_template(
        'user/dashboard.html', 
        user=user, 
        score=user_score, 
        leaderboard=leaderboard_data,
        category_leaderboards=category_leaderboards,
        topology_score=topology_score,
        crimping_score=crimping_score,
        osi_score=osi_score,
        **category_leaderboards
    )

@user_bp.route('/profile')
@login_required
def profile():
    from flask import session
    
    if not current_user.is_authenticated:
        return render_template('user/index.html', message='You need to log in first!')
    
    # CRITICAL FIX: Enforce user namespace isolation
    auth_namespace = session.get('auth_namespace', 'unknown')
    if auth_namespace != 'user':
        flash('Access denied. User credentials required.', 'error')
        return redirect(url_for('user.login'))
    
    # Verify current_user is actually a User instance (not Admin)
    if not isinstance(current_user, UserModel):
        flash('Access denied. User credentials required.', 'error')
        session.clear()  # Clear potentially poisoned session
        return redirect(url_for('user.login'))
    
    user = current_user
    return render_template('user/profile.html', user=user)

@user_bp.route('/scores')
@login_required
def scores():
    if not current_user.is_authenticated:
        return render_template('user/index.html', message='You need to log in first!')
    
    user = current_user
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
                         score=user_scores,  # Use 'score' to match template expectation
                         scores=user_scores,  # Keep 'scores' for compatibility
                         total_attempts=total_attempts,
                         average_score=average_score,
                         highest_score=highest_score,
                         category_stats=category_stats)

@user_bp.route('/about_us')
@login_required
def about_us():
    if not current_user.is_authenticated:
        return render_template('user/index.html', message='You need to log in first!')
    
    user = current_user
    return render_template('user/about_us.html', user=user)

@user_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    from flask import session
    
    if not current_user.is_authenticated:
        return render_template('user/index.html', message='You need to log in first!')
    
    # CRITICAL FIX: Enforce user namespace isolation
    auth_namespace = session.get('auth_namespace', 'unknown')
    if auth_namespace != 'user':
        flash('Access denied. User credentials required.', 'error')
        session.clear()  # Clear potentially poisoned session
        return redirect(url_for('user.login'))
    
    # Verify current_user is actually a User instance (not Admin)
    if not isinstance(current_user, UserModel):
        flash('Access denied. User credentials required.', 'error')
        session.clear()  # Clear potentially poisoned session
        return redirect(url_for('user.login'))

    user = current_user
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('user.index'))

    # Get form data
    username = request.form.get('username', '').strip()
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    profile_img = request.files.get('profile_img')

    try:
        # Validate username
        if not username:
            flash('Username is required', 'error')
            return redirect(url_for('user.profile'))

        # Check if username is already taken by another user
        existing_user = UserModel.query.filter(UserModel.username == username, UserModel.id != user.id).first()
        if existing_user:
            flash('Username is already taken', 'error')
            return redirect(url_for('user.profile'))

        # Handle password update
        if new_password:
            # Validate current password if changing password
            if not current_password:
                flash('Current password is required to change password', 'error')
                return redirect(url_for('user.profile'))
            
            if not user.check_password(current_password):
                flash('Current password is incorrect', 'error')
                return redirect(url_for('user.profile'))
            
            # Check if new passwords match
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('user.profile'))
            
            # Validate password strength (optional)
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return redirect(url_for('user.profile'))
            
            user.set_password(new_password)

        # Handle profile image upload
        if profile_img and profile_img.filename:
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            file_extension = profile_img.filename.rsplit('.', 1)[1].lower() if '.' in profile_img.filename else ''
            
            if file_extension not in allowed_extensions:
                flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'error')
                return redirect(url_for('user.profile'))
              # Create filename with user ID to avoid conflicts
            img_filename = f"user_{user.id}_{secure_filename(profile_img.filename)}"
            
            # Ensure the static/img/profiles directory exists
            profiles_dir = os.path.join('static', 'img', 'profiles')
            if not os.path.exists(profiles_dir):
                os.makedirs(profiles_dir)
            
            # Save the file
            img_path = os.path.join(profiles_dir, img_filename)
            profile_img.save(img_path)
            
            # Update user profile image (store just the filename, not the full path)
            user.profile_img = img_filename

        # Update username
        user.username = username

        # Commit changes
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
        # Send WebSocket notification if available
        try:
            socketio = get_socketio()
            if socketio:
                socketio.emit('profile_updated', {
                    'user_id': user.id,
                    'username': user.username,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=f'user_{user.id}')
        except Exception as e:
            print(f"WebSocket notification failed: {e}")

    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while updating your profile: {str(e)}', 'error')
        print(f"Profile update error: {e}")
        traceback.print_exc()

    return redirect(url_for('user.profile'))

@user_bp.route('/delete_score/<int:score_id>', methods=['POST'])
@login_required
def delete_score(score_id):
    if not current_user.is_authenticated:
        return render_template('user/index.html', message='You need to log in first!')
        
    score = UserScore.query.get(score_id)
    if score and score.user_id == current_user.id:
        db.session.delete(score)
        db.session.commit()
    return redirect(url_for('user.dashboard'))

@user_bp.route('/troubleshoot')
def troubleshoot():
    # Pass user context if available
    user = None
    if 'user_id' in session:
        user = UserModel.query.get(session['user_id'])
    
    # Check if a scenario ID is provided
    scenario_id = request.args.get('scenario')
    scenario_data = None
    
    if scenario_id:
        # If scenario ID is provided, load the scenario for the troubleshooting interface
        try:
            from admin.models.troubleshooting import Troubleshooting
            scenario = Troubleshooting.query.get(scenario_id)
            if scenario and scenario.is_active:
                scenario_data = scenario.to_dict()
                # Don't expose sensitive data in the initial load
                if 'solution' in scenario_data:
                    del scenario_data['solution']
                if 'expected_topology' in scenario_data:
                    del scenario_data['expected_topology']
        except Exception as e:
            print(f"Error loading scenario {scenario_id}: {e}")
    
    return render_template('user/troubleshoot.html', title="troubleshoot", user=user, scenario=scenario_data)

@user_bp.route('/crimp')
@user_bp.route('/crimping-simulation')
@user_login_required
def crimping_simulation():
    """UTP Cable Crimping Simulation - Interactive learning tool for cable crimping"""
    user = UserModel.query.get(session['user_id'])
    return render_template('user/crimping-simulation.html', 
                         title="UTP Cable Crimping Simulation", 
                         user=user)

@user_bp.route('/osi-simulation')
@user_login_required
def osi_simulation():
    """OSI Model Simulation - Interactive learning tool for understanding the 7-layer OSI model"""
    user = UserModel.query.get(session['user_id'])
    return render_template('user/osi-simulation.html', 
                         title="OSI Model Simulation", 
                         user=user)

@user_bp.route('/save_crimping_score', methods=['POST'])
@user_login_required
def save_crimping_score():
    """Save crimping simulation score (MVP Presenter Layer)"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        score = data.get('score', 0)
        wiring_type = data.get('wiring_type', 'unknown')
        completion_time = data.get('completion_time', 0)
        
        print(f"[MVP Backend] Received score submission:")
        print(f"  - User ID: {user_id}")
        print(f"  - Score: {score}")
        print(f"  - Wiring Type: {wiring_type}")
        print(f"  - Completion Time: {completion_time}s")
        
        # Create a new score entry - only use fields that exist in the Score model
        new_score = UserScore(
            user_id=user_id,
            score=score,
            category='crimping'  # Simple category name that matches the database
        )
        
        db.session.add(new_score)
        db.session.commit()
        
        print(f"[MVP Backend] ✅ Score saved to database (ID: {new_score.id})")
        
        # Send WebSocket notification if available
        try:
            from utils.socket_monitor import get_socketio
            socketio = get_socketio()
            if socketio:
                user = UserModel.query.get(user_id)
                socketio.emit('crimping_score_saved', {
                    'user_id': user_id,
                    'username': user.username if user else 'Unknown',
                    'score': score,
                    'wiring_type': wiring_type,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=f'user_{user_id}')
                print(f"[MVP Backend] WebSocket notification sent")
        except Exception as e:
            print(f"[MVP Backend] WebSocket notification failed: {e}")
        
        return jsonify({
            'status': 'success',
            'message': 'Crimping score saved successfully!',
            'score': score,
            'saved_id': new_score.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"[MVP Backend] ❌ Error saving crimping score: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Failed to save score: {str(e)}'
        }), 500

@user_bp.route('/save_osi_score', methods=['POST'])
@user_login_required
def save_osi_score():
    """Save OSI simulation score"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        score = data.get('score', 0)
        layer_accuracy = data.get('layer_accuracy', {})
        completion_time = data.get('completion_time', 0)
        
        # Create a new score entry for OSI simulation
        new_score = UserScore(
            user_id=user_id,
            score=score,
            category='osi'  # New category for OSI simulation
        )
        
        db.session.add(new_score)
        db.session.commit()
        
        # WebSocket notification for real-time updates (optional)
        try:
            from socket_events import socketio
            socketio.emit('score_updated', {
                'user_id': user_id,
                'category': 'osi',
                'new_score': score,
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'user_{user_id}')
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        return jsonify({
            'status': 'success',
            'message': 'OSI simulation score saved successfully!',
            'score': score
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving OSI score: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to save score'
        }), 500

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
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
            }, room='admin_room')
            
            # Send logout notification to user's personal room
            socketio.emit('logout_complete', {
                'status': 'success',
                'message': f'Goodbye, {username}!',
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'user_{user_id}')
            
            print(f"WebSocket logout notifications sent for user: {username}")
    except Exception as ws_error:
        print(f"WebSocket logout notification failed: {str(ws_error)}")
    
    # Use Flask-Login logout
    from flask_login import logout_user
    logout_user()
    
    # CRITICAL FIX: Clear the user's session and namespace
    session.clear()  # This will clear auth_namespace too
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
                'timestamp': datetime.utcnow().isoformat(),
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
                    'timestamp': datetime.utcnow().isoformat(),
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
                    'timestamp': datetime.utcnow().isoformat(),
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
                        'timestamp': datetime.utcnow().isoformat(),
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
                            'timestamp': datetime.utcnow().isoformat(),
                            'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                        }, room='admin_room')
                except Exception as ws_error:
                    print(f"WebSocket invalid OTP notification failed: {str(ws_error)}")
                
                return render_template('user/index.html', message='Invalid OTP code. Please try again or request a new code.')
                
            # Check if OTP is expired (10 minutes)
            current_time = datetime.now()
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
                                'timestamp': datetime.utcnow().isoformat(),
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
                            'timestamp': datetime.utcnow().isoformat(),
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
                        'timestamp': datetime.utcnow().isoformat(),
                        'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                    }, room='admin_room')
            except Exception as ws_error:
                print(f"WebSocket OTP validation error notification failed: {str(ws_error)}")
            
            return render_template('user/index.html', message=f'Error validating OTP: {str(e)}. Please try again.')
    
    # Set user in session (FIXED INDENTATION)
    session['user_id'] = user.id
    session['auth_namespace'] = 'user'  # CRITICAL FIX: Set user namespace
    print(f"Login successful for user: {username}, user_id: {user.id}, namespace: {session.get('auth_namespace')}")
    
    # Use Flask-Login for proper login and authentication
    # Remember=True ensures the user stays logged in for the session
    login_user(user, remember=True)
    print(f"Flask-Login current_user: {current_user.is_authenticated}")
    
    # Send WebSocket notification for successful login
    try:
        socketio = get_socketio()
        if socketio:
            # Send enhanced notification using new service
            try:
                from services.notification_service import get_notification_service, NotificationType, NotificationPriority
                notification_service = get_notification_service(socketio)
                
                # Send welcome notification to user
                notification_service.send_user_notification(
                    user_id=user.id,
                    notification_type=NotificationType.LOGIN_ACTIVITY,
                    title="Welcome Back!",
                    message=f"Successfully logged in to RiddleNet at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                    priority=NotificationPriority.LOW
                )
                
                # Send admin notification for high-value accounts or security alerts
                if hasattr(user, 'is_admin') and user.is_admin:
                    notification_service.send_admin_notification(
                        notification_type=NotificationType.SECURITY_ALERT,
                        title="Admin Login Detected",
                        message=f"Admin user {username} logged in from {request.environ.get('REMOTE_ADDR', 'unknown')}",
                        priority=NotificationPriority.HIGH
                    )
            except Exception as enhanced_error:
                print(f"Enhanced notification failed, using legacy: {enhanced_error}")
                
                # Fallback to legacy notifications
                # Notify admin of successful login
                socketio.emit('user_login_activity', {
                    'user_id': user.id,
                    'username': username,
                    'action': 'login_successful',
                    'email': user.email,
                    'timestamp': datetime.utcnow().isoformat(),
                    'ip_address': request.environ.get('REMOTE_ADDR', 'unknown'),
                    'user_agent': request.headers.get('User-Agent', 'unknown')
                }, room='admin_room')
                
                # Send welcome notification to user's personal room
                socketio.emit('login_success', {
                    'status': 'success',
                    'message': f'Welcome back, {username}!',
                'timestamp': datetime.utcnow().isoformat()
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
            user.otp_generated_at = datetime.now()
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
                        'timestamp': datetime.utcnow().isoformat(),
                        'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                    }, room='admin_room')
                    
                    # Send real-time notification to user's personal room
                    socketio.emit('otp_request_received', {
                        'status': 'processing',
                        'message': 'OTP request received, sending email...',
                        'timestamp': datetime.utcnow().isoformat()
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
                            'timestamp': datetime.utcnow().isoformat()
                        }, room='admin_room')
                        
                        # Notify user of successful email delivery
                        socketio.emit('otp_email_sent', {
                            'status': 'success',
                            'message': 'OTP sent to your email successfully',
                            'timestamp': datetime.utcnow().isoformat()
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
                            'timestamp': datetime.utcnow().isoformat()
                        }, room='admin_room')
                        
                        # Notify user of failed email delivery
                        socketio.emit('otp_email_failed', {
                            'status': 'error',
                            'message': 'Failed to send OTP email',
                            'timestamp': datetime.utcnow().isoformat()
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
                        'timestamp': datetime.utcnow().isoformat()
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

@user_bp.route('/topology/gamified')
@user_login_required
def gamified_topology():
    """Render the gamified topology simulation page."""
    from services.gamified_topology_service import GamifiedTopologyService
    
    try:
        service = GamifiedTopologyService()
        
        # Get user progress and scenarios
        user_progress = service.get_user_progress(current_user.id)
        scenarios = service.get_available_scenarios(current_user.id)
        
        # Format data for the frontend
        gamified_data = {
            'userProgress': {
                'total_completed': user_progress.get('total_completed', 0),
                'total_scenarios': user_progress.get('total_scenarios', 0),
                'total_score': user_progress.get('total_score', 0),
                'completion_percentage': user_progress.get('completion_percentage', 0),
                'current_level': user_progress.get('current_level', 1),
                'achievements': user_progress.get('achievements', [])
            },
            'scenarios': scenarios
        }
        
        return render_template(
            'user/gamified_topology.html',
            gamified_data=gamified_data
        )
        
    except Exception as e:
        print(f"Error in gamified topology route: {e}")
        flash('Error loading gamified topology. Please try again.', 'error')
        return redirect(url_for('user.topology'))

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
            
            progress.last_attempt = datetime.utcnow()
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
                    'timestamp': datetime.utcnow().isoformat()
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
                'timestamp': datetime.utcnow().isoformat()
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
                'timestamp': datetime.utcnow().isoformat()
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
                    topology_progress.last_attempt = datetime.utcnow()
                else:
                    topology_progress = TopologyProgress(
                        user_id=current_user.id,
                        topology_type=topology_type,
                        highest_score=score,
                        completion_count=1 if completed else 0,
                        last_attempt=datetime.utcnow()
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
                'timestamp': datetime.utcnow().isoformat()
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
                    'timestamp': datetime.utcnow().isoformat()
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
                'timestamp': datetime.utcnow().isoformat()
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
                'timestamp': datetime.utcnow().isoformat(),
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

@user_bp.route('/api/networking/track-progress', methods=['POST'])
def track_networking_progress():
    """DEPRECATED: Track user progress in networking lessons - use progression API instead"""
    return jsonify({"error": "This endpoint is deprecated. Use progression API instead."}), 404

@user_bp.route('/api/networking/lesson/<lesson_id>')
def get_networking_lesson(lesson_id):
    """DEPRECATED: Get content for a specific networking lesson - use dynamic class routes"""
    return jsonify({"error": "Networking content now managed through database. Please use dynamic class routes."}), 404
# =============================================================================
# DYNAMIC SYSTEM REDIRECTS - All networking simulations now use database content
# =============================================================================

@user_bp.route('/networking1-simulations')
def networking1_simulations_redirect():
    """Redirect to dynamic simulations dashboard"""
    return redirect(url_for('dynamic_simulations.simulations_dashboard') + '?filter=networking1')

@user_bp.route('/networking2-simulations') 
def networking2_simulations_redirect():
    """Redirect to dynamic simulations dashboard"""
    return redirect(url_for('dynamic_simulations.simulations_dashboard') + '?filter=networking2')

@user_bp.route('/networking1-<simulation_name>-simulation')
def networking1_simulation_redirect(simulation_name):
    """Redirect networking1 simulations to dynamic system"""
    # Find simulation by name
    from admin.models.simulation import Simulation
    sim = Simulation.query.filter(
        Simulation.title.contains(simulation_name.replace('-', ' ').title()),
        Simulation.simulation_type == 'Networking 1'
    ).first()
    
    if sim:
        return redirect(url_for('dynamic_simulations.run_simulation', simulation_id=sim.id))
    else:
        return redirect(url_for('dynamic_simulations.simulations_dashboard'))

@user_bp.route('/networking2-<simulation_name>-simulation')
def networking2_simulation_redirect(simulation_name):
    """Redirect networking2 simulations to dynamic system"""
    # Find simulation by name
    from admin.models.simulation import Simulation
    sim = Simulation.query.filter(
        Simulation.title.contains(simulation_name.replace('-', ' ').title()),
        Simulation.simulation_type == 'Networking 2'
    ).first()
    
    if sim:
        return redirect(url_for('dynamic_simulations.run_simulation', simulation_id=sim.id))
    else:
        return redirect(url_for('dynamic_simulations.simulations_dashboard'))


@user_bp.route('/debug-auth')
def debug_auth():
    """Temporary debug route to test authentication"""
    from utils.auth_utils import get_current_user_context
    
    # Manually set Gilbert in session for testing
    user = UserModel.query.filter_by(username='Gilbert').first()
    if user:
        session['user_id'] = user.id
        login_user(user)
        print(f"[DEBUG] Manually logged in Gilbert (ID: {user.id})")
    
    # Test our debug function
    context = get_current_user_context()
    return f"<h2>Debug Authentication Results:</h2><pre>{context}</pre>"

@user_bp.route('/landscape-test')
@user_login_required
def landscape_test():
    """Test page for mobile landscape optimizations"""
    return render_template('landscape-test.html')

# Register the gamified topology routes blueprint
try:
    from user.routes.gamified_topology_routes import gamified_topology_bp
    user_bp.register_blueprint(gamified_topology_bp, url_prefix='/topology')
    print("Successfully registered gamified topology routes")
except ImportError as e:
    print(f"Warning: Could not import gamified topology routes: {e}")
except Exception as e:
    print(f"Error registering gamified topology routes: {e}")
