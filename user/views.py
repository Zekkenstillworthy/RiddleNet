from flask import render_template, session, Blueprint, request, redirect, url_for, flash, jsonify
from flask import render_template, session, Blueprint, request, redirect, url_for, flash, jsonify
from sqlalchemy import func
import os
import time
import datetime
import traceback
import threading
import concurrent.futures
import subprocess
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
    return render_template('user/index.html')

@user_bp.route('/overview')
def overview():
    return render_template('user/overview.html')

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
    try:
        leaderboard_data = (
            db.session.query(UserModel.username, func.max(UserScore.score).label('highest_score'), func.max(UserScore.date_attempted).label('latest_attempt'))
            .join(UserScore)
            .group_by(UserModel.id)
            .order_by(func.max(UserScore.score).desc())
            .all()
        )
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        leaderboard_data = []

    return render_template('user/dashboard.html', leaderboard=leaderboard_data)

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
    return render_template('user/troubleshoot.html', title="troubleshoot")

@user_bp.route('/crimp')
def crimp():
    return render_template('user/crimping-simulation.html', title="crimp")

@user_bp.route('/logout')
def logout():
    # Log the logout event if user is in session - audit logging removed
    
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
    
    # Find the user by username
    user = UserModel.query.filter_by(username=username).first()
    
    if not user:
        print(f"User not found: {username}")
        return render_template('user/index.html', message='Invalid username.')
    
    # Debug info
    print(f"User found: {user.username}, TOTP enabled: {user.totp_enabled}, TOTP secret exists: {'Yes' if user.totp_secret else 'No'}")
      # Validate password
    if not user.check_password(password):
        print(f"Invalid password for user: {username}")
        return render_template('user/index.html', message='Invalid password.')
      # Validate OTP if TOTP is enabled for this user
    if user.totp_enabled:
        if not otp:
            print(f"OTP required but not provided for user: {username}")
            return render_template('user/index.html', message='OTP is required for this account. Please click "Request OTP" to receive a code via email.')
        
        try:
            # Check if OTP matches and hasn't expired (10 minute validity)
            if user.otp != otp:
                print(f"Invalid OTP code for user: {username}")
                return render_template('user/index.html', message='Invalid OTP code. Please try again or request a new code.')
                
            # Check if OTP is expired (10 minutes)
            current_time = datetime.datetime.now()
            if user.otp_generated_at:
                otp_age = current_time - user.otp_generated_at
                if otp_age.total_seconds() > 600:  # 10 minutes in seconds
                    print(f"Expired OTP code for user: {username}")
                    return render_template('user/index.html', message='OTP code has expired. Please click "Request OTP" for a new code.')
            else:
                print(f"OTP generation timestamp missing for user: {username}")
                return render_template('user/index.html', message='Invalid OTP. Please click "Request OTP" for a new code.')
                
            # Clear the OTP after successful validation
            user.otp = None
            user.otp_generated_at = None
            db.session.commit()
            
        except Exception as e:
            print(f"Error validating OTP for user {username}: {str(e)}")
            return render_template('user/index.html', message=f'Error validating OTP: {str(e)}. Please try again.')
    
    # Set user in session
    session['user_id'] = user.id
    print(f"Login successful for user: {username}, user_id: {user.id}")
    
    # Use Flask-Login for proper login and authentication
    # Remember=True ensures the user stays logged in for the session
    login_user(user, remember=True)
    print(f"Flask-Login current_user: {current_user.is_authenticated}")
    
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
            
            # Send OTP via email using direct SMTP to bypass Eventlet DNS issues
            success = send_otp_email_direct(user.email, user.username, otp)
            if success:
                return jsonify({'status': 'success', 'message': 'OTP sent to your email'}), 200
            else:
                # Fallback: show OTP in development mode
                return jsonify({
                    'status': 'warning', 
                    'message': f'OTP generated but email sending failed. Your OTP is: {otp} (Development Mode)',
                    'otp': otp
                }), 200
        except Exception as e:
            print(f"Error in send_otp: {str(e)}")
            import traceback
            print(traceback.format_exc())
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
    try:
        # Query all active topologies and get their types
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

def send_otp_email_direct(recipient_email, username, otp):
    """
    Send OTP email using direct SMTP connection to bypass Eventlet DNS issues.
    This function properly handles WebSocket/Eventlet environments by using IP addresses.
    Returns True if successful, False otherwise.
    """
    import smtplib
    import ssl
    import socket
    import os
    import threading
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import traceback
    import subprocess
    import sys
    
    def _resolve_smtp_server():
        """Resolve Gmail SMTP server IP to bypass DNS issues"""
        # Known Gmail SMTP IPs (these can change, but are relatively stable)
        gmail_ips = [
            '142.250.153.109',  # smtp.gmail.com
            '142.250.153.108',
            '142.251.167.109',
            '172.253.115.109',
            '64.233.184.109'
        ]
        
        # Try to resolve using system DNS first
        for attempt in range(3):
            try:
                # Use subprocess to bypass eventlet DNS resolution
                result = subprocess.run(['nslookup', 'smtp.gmail.com'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Address:' in line and not '::' in line:  # IPv4 only
                            ip = line.split('Address:')[-1].strip()
                            if ip and ip != '127.0.0.1':
                                print(f"Resolved smtp.gmail.com to {ip}")
                                return ip
            except:
                pass
        
        # Fallback to known IPs and test connectivity
        for ip in gmail_ips:
            try:
                # Test if we can connect to this IP
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(5)
                test_sock.connect((ip, 587))
                test_sock.close()
                print(f"Using fallback Gmail IP: {ip}")
                return ip
            except:
                continue
                
        print("Could not resolve smtp.gmail.com to any working IP")
        return None
    
    def _send_email_threaded():
        """Send email in a separate thread to avoid Eventlet interference"""
        try:
            # Get email configuration from environment
            smtp_server_ip = _resolve_smtp_server()
            if not smtp_server_ip:
                print("Failed to resolve Gmail SMTP server")
                return False
                
            smtp_port = 587
            sender_email = os.getenv('MAIL_USERNAME')
            sender_password = os.getenv('MAIL_PASSWORD')
            
            if not sender_email or not sender_password:
                print("Email configuration missing from environment variables")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Your RiddleNet OTP Code"
            message["From"] = sender_email
            message["To"] = recipient_email
            
            # Create the plain-text part
            text = f"""Hi {username},

Your verification code is: {otp}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
RiddleNet Team"""
            
            # Turn these into plain MIMEText objects
            part = MIMEText(text, "plain")
            message.attach(part)
            
            success = False
            
            # Method 1: Try standard SMTP with IP address
            try:
                print(f"Attempting SMTP connection to {smtp_server_ip}:587")
                server = smtplib.SMTP(smtp_server_ip, smtp_port, timeout=30)
                
                # Use the actual hostname for TLS verification
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.as_string())
                server.quit()
                
                print(f"OTP email sent successfully to {recipient_email} via IP {smtp_server_ip}")
                success = True
                
            except Exception as smtp_error:
                print(f"Method 1 SMTP error: {str(smtp_error)}")
                
                # Method 2: Try raw socket implementation
                try:
                    print(f"Attempting raw socket connection to {smtp_server_ip}:587")
                    
                    # Create raw socket connection
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(30)
                    sock.connect((smtp_server_ip, smtp_port))
                    
                    # Read initial response
                    response = sock.recv(1024).decode()
                    print(f"Initial response: {response.strip()}")
                    if not response.startswith('220'):
                        raise Exception(f"SMTP connection failed: {response}")
                    
                    # Send EHLO
                    sock.send(b'EHLO localhost\r\n')
                    response = sock.recv(1024).decode()
                    print(f"EHLO response: {response.strip()}")
                    
                    # Start TLS
                    sock.send(b'STARTTLS\r\n')
                    response = sock.recv(1024).decode()
                    print(f"STARTTLS response: {response.strip()}")
                    
                    # Wrap socket with SSL (use gmail hostname for cert verification)
                    context = ssl.create_default_context()
                    ssl_sock = context.wrap_socket(sock, server_hostname='smtp.gmail.com')
                    
                    # Send EHLO again
                    ssl_sock.send(b'EHLO localhost\r\n')
                    response = ssl_sock.recv(1024).decode()
                    print(f"SSL EHLO response: {response.strip()}")
                    
                    # Login
                    import base64
                    auth_string = f'\x00{sender_email}\x00{sender_password}'
                    auth_b64 = base64.b64encode(auth_string.encode()).decode()
                    ssl_sock.send(f'AUTH PLAIN {auth_b64}\r\n'.encode())
                    response = ssl_sock.recv(1024).decode()
                    print(f"AUTH response: {response.strip()}")
                    
                    if not response.startswith('235'):
                        raise Exception(f"SMTP authentication failed: {response}")
                    
                    # Send email commands
                    ssl_sock.send(f'MAIL FROM:<{sender_email}>\r\n'.encode())
                    response = ssl_sock.recv(1024).decode()
                    print(f"MAIL FROM response: {response.strip()}")
                    
                    ssl_sock.send(f'RCPT TO:<{recipient_email}>\r\n'.encode())
                    response = ssl_sock.recv(1024).decode()
                    print(f"RCPT TO response: {response.strip()}")
                    
                    ssl_sock.send(b'DATA\r\n')
                    response = ssl_sock.recv(1024).decode()
                    print(f"DATA response: {response.strip()}")
                    
                    # Send message
                    ssl_sock.send(message.as_bytes())
                    ssl_sock.send(b'\r\n.\r\n')
                    response = ssl_sock.recv(1024).decode()
                    print(f"Message response: {response.strip()}")
                    
                    ssl_sock.send(b'QUIT\r\n')
                    ssl_sock.close()
                    
                    print(f"OTP email sent successfully via raw socket to {recipient_email}")
                    success = True
                    
                except Exception as raw_error:
                    print(f"Method 2 raw socket error: {str(raw_error)}")
                    success = False
                    
            return success
            
        except Exception as e:
            print(f"Error in _send_email_threaded: {str(e)}")
            traceback.print_exc()
            return False
    
    try:
        # Use threading to completely escape eventlet context
        import concurrent.futures
        
        print(f"Starting email send to {recipient_email} for user {username}")
        
        # Execute in thread pool to avoid eventlet blocking
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_send_email_threaded)
            result = future.result(timeout=90)  # 90 second timeout
            return result
            
    except Exception as e:
        print(f"Error in send_otp_email_direct: {str(e)}")
        traceback.print_exc()
        
        # Final fallback: Try synchronous sending
        try:
            print("Attempting final fallback synchronous email send")
            return _send_email_threaded()
        except Exception as fallback_error:
            print(f"All email sending methods failed: {str(fallback_error)}")
            return False

# Create blueprint as expected by main __init__.py
