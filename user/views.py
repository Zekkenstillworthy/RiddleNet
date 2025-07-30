from flask import render_template, session, Blueprint, request, redirect, url_for, flash, jsonify
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
def classes():
    if 'user_id' not in session:
        return redirect(url_for('user.index', message='You need to log in first!'))
    
    user = UserModel.query.get(session['user_id'])
    # No need to fetch classes here - we'll do it client-side with API
    return render_template('user/class.html', user=user)
    
@user_bp.route('/learning/networking-1')
def networking_1():
    # Redirect to class 7 instead of the old learning page
    return redirect('/class/7/')

@user_bp.route('/learning/networking-2')
def networking_2():
    # Redirect to class 9 instead of the old learning page
    return redirect('/class/9/')

# Temporarily disabled - using specific class routes instead
# @user_bp.route('/class/<int:class_id>')
# @user_login_required
def class_detail_disabled(class_id):
    """Class detail - Uses standardized template for all classes - DISABLED"""
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
    
    try:
        # DATABASE FIRST approach - get learning paths and simulations
        from admin.models.learning_path import LearningPath
        from admin.models.simulation import Simulation
        from services.progression_service import progression_service
        
        # Get DATABASE simulations assigned to this class
        database_simulations = Simulation.query.filter_by(
            is_published=True,
            is_active=True
        ).all()
        
        # Get assigned learning paths from DATABASE
        learning_paths = LearningPath.query.filter_by(
            class_id=class_id,
            is_published=True
        ).all()
        
        # If no database content, fallback to static modules
        static_modules = []
        if not database_simulations and not learning_paths:
            print(f"No database content for class {class_id}, using static fallback")
            if class_id == 7:  # Networking 1
                static_modules = [
                    {
                        'title': 'Network Components',
                        'description': 'Learn about basic network hardware and components',
                        'lessons': ['Hardware', 'Cables', 'Devices'],
                        'url': '/networking1-simulations'
                    },
                    {
                        'title': 'OSI Model',
                        'description': 'Understanding the 7-layer OSI model',
                        'lessons': ['Physical', 'Data Link', 'Network', 'Transport'],
                        'url': '/networking1-osi-simulation'
                    }
                ]
            elif class_id == 9:  # Networking 2
                static_modules = [
                    {
                        'title': 'Routing Fundamentals',
                        'description': 'Basic routing concepts and protocols',
                        'lessons': ['Static Routing', 'Dynamic Routing'],
                        'url': '/networking2-simulations'
                    },
                    {
                        'title': 'Network Security',
                        'description': 'Securing network infrastructure',
                        'lessons': ['Firewalls', 'VPNs', 'Access Control'],
                        'url': '/networking2-security-simulation'
                    }
                ]
        from services.progression_service import progression_service
        
        # Get static modules (hardcoded content)
        static_modules = []
        if class_id == 7:  # Networking 1
            static_modules = [
                {
                    'title': 'Network Components',
                    'description': 'Learn about basic network hardware and components',
                    'lessons': ['Hardware', 'Cables', 'Devices'],
                    'url': '/networking1-simulations'
                },
                {
                    'title': 'OSI Model',
                    'description': 'Understanding the 7-layer OSI model',
                    'lessons': ['Physical', 'Data Link', 'Network', 'Transport'],
                    'url': '/networking1-osi-simulation'
                }
            ]
        elif class_id == 9:  # Networking 2
            static_modules = [
                {
                    'title': 'Routing Fundamentals',
                    'description': 'Basic routing concepts and protocols',
                    'lessons': ['Static Routing', 'Dynamic Routing'],
                    'url': '/networking2-simulations'
                },
                {
                    'title': 'Network Security',
                    'description': 'Securing network infrastructure',
                    'lessons': ['Firewalls', 'VPNs', 'Access Control'],
                    'url': '/networking2-security-simulation'
                }
            ]
        
        # Get assigned learning paths
        learning_paths = []
        paths = LearningPath.query.filter_by(is_published=True).all()
        for path in paths:
            progress = progression_service.get_user_progress_in_path(user_id, path.id)
            path.progress_percentage = progress['percentage']
            learning_paths.append(path)
        
        # Calculate overall progress
        overall_progress = 0
        total_progress = 0
        count = 0
        
        # Include static module progress (placeholder)
        total_progress += 25  # Assume 25% for static modules
        count += 1
        
        # Include learning path progress
        for path in learning_paths:
            total_progress += path.progress_percentage
            count += 1
        
        overall_progress = total_progress / count if count > 0 else 0
        
        # Get recent activities
        recent_activities = []
        try:
            from admin.models.simulation import SimulationAttempt
            attempts = SimulationAttempt.query.filter_by(
                user_id=user_id
            ).order_by(SimulationAttempt.completed_at.desc()).limit(5).all()
            
            for attempt in attempts:
                if attempt.simulation:
                    recent_activities.append({
                        'title': f"Completed {attempt.simulation.title}",
                        'date': attempt.completed_at.strftime('%Y-%m-%d') if attempt.completed_at else 'Recent'
                    })
        except Exception as e:
            print(f"Error getting recent activities: {e}")
        
        # Get achievements
        achievements = []
        try:
            achievements = progression_service.get_user_achievements(user_id)
        except Exception as e:
            print(f"Error getting achievements: {e}")

        # USE STANDARDIZED CLASS TEMPLATE FOR ALL CLASSES
        print("DEBUG: Using new standardized class template")
        
        # Prepare class data for the standardized template
        class_data = {
            'id': class_obj.id,
            'name': class_obj.name,
            'description': class_obj.description,
            'code': class_obj.code,
            'section': class_obj.section or 'General'
        }
        
        # Get modules from database or use static fallback
        modules = []
        simulations = []
        question_groups = []
        lessons = []
        static_simulations = []
        
        # Add learning paths as modules
        for path in learning_paths:
            modules.append({
                'id': path.id,
                'name': path.title,
                'description': path.description,
                'type': 'learning_path'
            })
        
        # Add database simulations
        for sim in database_simulations:
            simulations.append({
                'id': sim.id,
                'name': sim.title,
                'description': sim.description,
                'route': f'/simulation/{sim.id}',
                'icon': 'fas fa-flask'
            })
        
        # Add static lessons and simulations based on class
        if class_id == 7:  # Networking 1
            lessons = [
                {
                    'title': 'Network Fundamentals',
                    'description': 'Introduction to networking concepts and principles',
                    'url': '/learning/networking-1'
                },
                {
                    'title': 'OSI Model Deep Dive',
                    'description': 'Comprehensive study of the 7-layer OSI model',
                    'url': '/networking1-osi-simulation'
                }
            ]
            static_simulations = [
                {
                    'title': 'Network Components',
                    'description': 'Interactive simulation of network hardware and components',
                    'url': '/networking1-components-simulation',
                    'icon': 'fas fa-microchip'
                },
                {
                    'title': 'OSI Model Simulation',
                    'description': 'Hands-on exploration of the OSI model layers',
                    'url': '/networking1-osi-simulation',
                    'icon': 'fas fa-layer-group'
                },
                {
                    'title': 'Ethernet Technology',
                    'description': 'Learn about Ethernet protocols and implementation',
                    'url': '/networking1-ethernet-simulation',
                    'icon': 'fas fa-ethernet'
                },
                {
                    'title': 'TCP/IP Protocol Suite',
                    'description': 'Explore the TCP/IP protocol stack',
                    'url': '/networking1-tcpip-simulation',
                    'icon': 'fas fa-network-wired'
                },
                {
                    'title': 'Application Layer Protocols',
                    'description': 'HTTP, FTP, SMTP and other application protocols',
                    'url': '/networking1-application-simulation',
                    'icon': 'fas fa-globe'
                },
                {
                    'title': 'Data Link Layer',
                    'description': 'Frame transmission and error detection mechanisms',
                    'url': '/networking1-datalink-simulation',
                    'icon': 'fas fa-link'
                }
            ]
        elif class_id == 9:  # Networking 2
            lessons = [
                {
                    'title': 'Advanced Routing',
                    'description': 'Advanced routing protocols and techniques',
                    'url': '/learning/networking-2'
                },
                {
                    'title': 'Network Security',
                    'description': 'Comprehensive network security principles',
                    'url': '/networking2-security-simulation'
                }
            ]
            static_simulations = [
                {
                    'title': 'Routing Fundamentals',
                    'description': 'Basic routing concepts and static routing',
                    'url': '/networking2-routing-fundamentals-simulation',
                    'icon': 'fas fa-route'
                },
                {
                    'title': 'RIP Protocol',
                    'description': 'Routing Information Protocol simulation',
                    'url': '/networking2-rip-simulation',
                    'icon': 'fas fa-share-alt'
                },
                {
                    'title': 'OSPF Protocol',
                    'description': 'Open Shortest Path First routing protocol',
                    'url': '/networking2-ospf-simulation',
                    'icon': 'fas fa-project-diagram'
                },
                {
                    'title': 'EIGRP Protocol',
                    'description': 'Enhanced Interior Gateway Routing Protocol',
                    'url': '/networking2-eigrp-simulation',
                    'icon': 'fas fa-sitemap'
                },
                {
                    'title': 'VLAN & Trunking',
                    'description': 'Virtual LANs and trunk configuration',
                    'url': '/networking2-vlan-simulation',
                    'icon': 'fas fa-code-branch'
                },
                {
                    'title': 'VPN Technologies',
                    'description': 'Virtual Private Network implementation',
                    'url': '/networking2-vpn-simulation',
                    'icon': 'fas fa-shield-alt'
                },
                {
                    'title': 'Network Security',
                    'description': 'Firewalls, IDS/IPS, and security protocols',
                    'url': '/networking2-security-simulation',
                    'icon': 'fas fa-lock'
                },
                {
                    'title': 'QoS & Performance',
                    'description': 'Quality of Service and network optimization',
                    'url': '/networking2-qos-simulation',
                    'icon': 'fas fa-tachometer-alt'
                },
                {
                    'title': 'Wireless Networks',
                    'description': '802.11 standards and wireless security',
                    'url': '/networking2-wireless-simulation',
                    'icon': 'fas fa-wifi'
                },
                {
                    'title': 'Network Management',
                    'description': 'SNMP, monitoring, and network troubleshooting',
                    'url': '/networking2-management-simulation',
                    'icon': 'fas fa-chart-line'
                },
                {
                    'title': 'Troubleshooting Labs',
                    'description': 'Hands-on network troubleshooting scenarios',
                    'url': '/networking2-troubleshooting-simulation',
                    'icon': 'fas fa-tools'
                }
            ]
        
        # Get question groups for assessments
        try:
            # Get question groups assigned to this specific class
            qgs = class_obj.question_groups.filter_by(is_active=True).all()
            for qg in qgs:
                question_groups.append({
                    'id': qg.id,
                    'name': qg.name,
                    'description': qg.description,
                    'questions': []  # Add question count if needed
                })
        except Exception as e:
            print(f"Error loading question groups: {e}")
            # Fallback: get all question groups if is_active column doesn't exist
            try:
                qgs = class_obj.question_groups.all()
                for qg in qgs:
                    question_groups.append({
                        'id': qg.id,
                        'name': qg.name,
                        'description': qg.description,
                        'questions': []
                    })
            except Exception as e2:
                print(f"Error loading question groups (fallback): {e2}")
        
        return render_template('user/user_class_standardized.html',
                             class_data=class_data,
                             modules=modules,
                             simulations=simulations,
                             question_groups=question_groups,
                             lessons=lessons,
                             static_simulations=static_simulations,
                             class_progress={
                                 'completion': round(overall_progress, 1),
                                 'modules': len(modules),
                                 'hours': len(modules) * 3,  # Estimate 3 hours per module
                                 'score': 85
                             },
                             overall_progress=round(overall_progress, 1),
                             recent_activities=recent_activities,
                             achievements=achievements,
                             user=user)
        
    except Exception as e:
        print(f"Error in class detail: {e}")
        
        # FALLBACK: Use standardized template with basic data
        print("DEBUG: Using standardized template with fallback data")
        
        class_data = {
            'id': class_obj.id,
            'name': class_obj.name,
            'description': class_obj.description or 'Interactive learning environment',
            'code': class_obj.code,
            'section': class_obj.section or 'General'
        }
        
        # Basic fallback data
        modules = []
        simulations = []
        question_groups = []
        lessons = []
        static_simulations = []
        
        return render_template('user/user_class_standardized.html',
                             class_data=class_data,
                             modules=modules,
                             simulations=simulations,
                             question_groups=question_groups,
                             lessons=lessons,
                             static_simulations=static_simulations,
                             class_progress={
                                 'completion': 0,
                                 'modules': 0,
                                 'hours': 0,
                                 'score': 0
                             },
                             overall_progress=0,
                             recent_activities=[],
                             achievements=[],
                             user=user)

# Alternative route for backward compatibility
@user_bp.route('/class/<int:class_id>/')
@user_login_required  
def class_detail_alternative(class_id):
    """Alternative route for class detail - redirects to main route"""
    return redirect(url_for('user.class_detail', class_id=class_id))

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
    
    user = UserModel.query.get(session['user_id'])
    
    try:
        print("DEBUG: Starting leaderboard query...")
        # Get each user's highest score across all categories with proper attribute names
        user_best_scores = []
          # Get all users with scores including profile image
        users_with_scores = (
            db.session.query(UserModel.id, UserModel.username, UserModel.profile_img)
            .join(UserScore)
            .distinct()
            .all()
        )
        print(f"DEBUG: Found {len(users_with_scores)} users with scores")
        
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
                    def __init__(self, username, score, category, date_attempted, profile_image):
                        self.username = username
                        self.score = score
                        self.category = category
                        self.date_attempted = date_attempted
                        self.profile_image = profile_image
                
                entry = LeaderboardEntry(
                    username=username,
                    score=highest_score_entry.score,
                    category=highest_score_entry.category,
                    date_attempted=highest_score_entry.date_attempted,
                    profile_image=profile_img
                )
                user_best_scores.append(entry)
                print(f"DEBUG: Created entry for {username}: score={entry.score}, category={entry.category}, profile_img={profile_img}")
        
        # Sort by score (highest first)
        leaderboard_data = sorted(user_best_scores, key=lambda x: x.score, reverse=True)
        print(f"DEBUG: Final leaderboard has {len(leaderboard_data)} entries")
        
        # Verify the data structure
        for i, item in enumerate(leaderboard_data[:3]):
            print(f"DEBUG: Entry {i+1}: {type(item)}, username={item.username}, score={item.score}")
        
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
                .group_by(UserModel.id, UserModel.username)
                .order_by(func.max(UserScore.score).desc())
                .all()
            )
    except Exception as e:
        print(f"ERROR in leaderboard: {e}")
        import traceback
        traceback.print_exc()
        leaderboard_data = []
        category_leaderboards = {}
    
    print(f"DEBUG: About to render template with {len(leaderboard_data)} leaderboard entries")
    if leaderboard_data:
        print(f"DEBUG: First entry type: {type(leaderboard_data[0])}, has score: {hasattr(leaderboard_data[0], 'score')}")
    
    return render_template('user/leaderboard.html', 
                         user=user,
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
                         score=user_scores,  # Use 'score' to match template expectation
                         scores=user_scores,  # Keep 'scores' for compatibility
                         total_attempts=total_attempts,
                         average_score=average_score,
                         highest_score=highest_score,
                         category_stats=category_stats)

@user_bp.route('/about_us')
def about_us():
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')
    
    user = UserModel.query.get(session['user_id'])
    return render_template('user/about_us.html', user=user)

@user_bp.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')

    user = UserModel.query.get(session['user_id'])
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

@user_bp.route('/save_crimping_score', methods=['POST'])
@user_login_required
def save_crimping_score():
    """Save crimping simulation score"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        score = data.get('score', 0)
        wiring_type = data.get('wiring_type', 'unknown')
        completion_time = data.get('completion_time', 0)
        
        # Create a new score entry - only use fields that exist in the Score model
        new_score = UserScore(
            user_id=user_id,
            score=score,
            category='crimping'  # Simple category name that matches the database
        )
        
        db.session.add(new_score)
        db.session.commit()
        
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
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        return jsonify({
            'status': 'success',
            'message': 'Crimping score saved successfully!',
            'score': score
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving crimping score: {e}")
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
    """Track user progress in networking lessons"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session['user_id']
    data = request.json
    
    if not data or 'lesson_id' not in data or 'module_id' not in data:
        return jsonify({"error": "Invalid data"}), 400
    
    lesson_id = data['lesson_id']
    module_id = data['module_id']
    completed = data.get('completed', False)
    progress_percent = data.get('progress_percent', 0)
    
    # Import NetworkingProgress model
    from user.models.networking_progress import NetworkingProgress
    
    # Check if progress record exists
    progress = NetworkingProgress.query.filter_by(
        user_id=user_id,
        module_id=module_id,
        lesson_id=lesson_id
    ).first()
    
    if progress:
        # Update existing record
        progress.completed = completed
        progress.progress_percent = progress_percent
        progress.last_accessed = datetime.utcnow()
    else:
        # Create new record
        progress = NetworkingProgress(
            user_id=user_id,
            module_id=module_id,
            lesson_id=lesson_id,
            completed=completed,
            progress_percent=progress_percent
        )
        db.session.add(progress)
    
    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Progress updated",
            "data": {
                "lesson_id": lesson_id,
                "completed": completed,
                "progress_percent": progress_percent
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_bp.route('/api/networking/lesson/<lesson_id>')
def get_networking_lesson(lesson_id):
    """Get content for a specific networking lesson"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Static content imports removed - returning database-driven message
    return jsonify({"error": "Networking content now managed through database. Please use dynamic class routes."}), 404
# ===================================================================
# DEPRECATED API ENDPOINTS - REPLACED BY DATABASE-DRIVEN CONTENT
# ===================================================================

@user_bp.route('/api/networking2/lessons')
def get_networking2_lessons():
    """DEPRECATED: Get all networking 2 lesson content"""
    return jsonify({"error": "This endpoint is deprecated. Use dynamic class routes for content."}), 404

@user_bp.route('/api/networking2/lesson/<lesson_id>')
def get_networking2_lesson(lesson_id):
    """DEPRECATED: Get content for a specific networking 2 lesson"""
    return jsonify({"error": "This endpoint is deprecated. Use dynamic class routes for content."}), 404

@user_bp.route('/api/networking2/progress', methods=['POST'])
def track_networking2_progress():
    """DEPRECATED: Track user progress in networking 2 lessons"""
    return jsonify({"error": "This endpoint is deprecated. Use progression API instead."}), 404

@user_bp.route('/api/networking1/structure')
def get_networking1_structure():
    """DEPRECATED: Get the complete structure of Networking 1 course"""
    return jsonify({"error": "This endpoint is deprecated. Use dynamic class routes for content."}), 404

# =============================================================================
# Helper function for simulation routes
# =============================================================================

def get_user_from_session():
    """Helper function to get user information from session"""
    user = None
    if 'user_id' in session:
        user = UserModel.query.get(session['user_id'])
    return user

def _render_individual_simulation(simulation_name, networking_type):
    """Helper function to render individual simulations - DATABASE FIRST"""
    try:
        # Direct database lookup first with improved search
        from admin.models.simulation import Simulation
        
        # Map route names to search terms that match database content
        search_mappings = {
            'components': ['component', 'hardware', 'network device'],
            'osi': ['osi', 'layer', '7 layer'],
            'tcpip': ['tcp', 'ip', 'protocol'],
            'ethernet': ['ethernet', 'frame', 'switching'],
            'application': ['application', 'http', 'dns'],
            'datalink': ['data', 'link', 'mac'],
            'routing_fundamentals': ['routing', 'static', 'route'],
            'dynamic_routing': ['dynamic', 'rip', 'eigrp'],
            'ospf': ['ospf'],
            'security': ['security', 'vpn']
        }
        
        # Get search terms
        terms = search_mappings.get(simulation_name, [simulation_name])
        
        # Try each search term
        for term in terms:
            sims = Simulation.query.filter(
                Simulation.title.ilike(f'%{term}%'),
                Simulation.is_published == True,
                Simulation.is_active == True
            ).all()
            
            if sims:
                # Found database simulation(s) - use the first one
                return redirect(url_for('dynamic_simulations.run_simulation', simulation_id=sims[0].id))
        
        # No database match - try static template
        try:
            template_name = f"user/networking{networking_type}-{simulation_name}-simulation.html"
            user = get_user_from_session()
            return render_template(template_name, user=user)
        except:
            # No template - redirect to dashboard
            return redirect(url_for('dynamic_simulations.simulations_dashboard'))
            
    except Exception as e:
        print(f"Error in simulation helper: {e}")
        return redirect(url_for('dynamic_simulations.simulations_dashboard'))

# NETWORKING 1 SIMULATION ROUTES
@user_bp.route('/networking1-simulations')
@user_login_required
def networking1_simulations():
    """Networking 1 simulations hub - DATABASE FIRST, static as fallback"""
    try:
        from services.hybrid_simulation_service import HybridSimulationService
        from admin.models.learning_path import LearningPath
        
        service = HybridSimulationService()
        all_simulations = service.get_combined_networking1_content()
        
        # Get learning paths for this category
        learning_paths = LearningPath.query.filter_by(
            course_level='Networking 1',
            is_published=True
        ).all()
        
        # Separate database and static simulations
        database_sims = [sim for sim in all_simulations if sim.get('type') == 'database']
        static_sims = [sim for sim in all_simulations if sim.get('type') == 'static']
        
        print(f"Networking1 simulations loaded: {len(all_simulations)} total, {len(database_sims)} from database, {len(static_sims)} static")
        
        # Get current user for template
        user = UserModel.query.get(session['user_id']) if 'user_id' in session else None
        
        # Structure data for enhanced template
        content = {
            'database': database_sims,
            'static': static_sims,
            'learning_paths': [{'id': lp.id, 'title': lp.title, 'description': lp.description, 'simulations': []} for lp in learning_paths]
        }
        
        return render_template('user/simulations.html', 
                             content=content,
                             course_title="Networking Fundamentals Simulations",
                             lesson_key="networking1",
                             using_database=len(database_sims) > 0,
                             user=user)
    except Exception as e:
        print(f"Error loading networking1 simulations: {e}")
        import traceback
        traceback.print_exc()
        # Last resort fallback to dynamic dashboard
        return redirect(url_for('dynamic_simulations.simulations_dashboard') + '?category=networking1')

@user_bp.route('/networking1-components-simulation')
@user_login_required
def networking1_components_simulation():
    """Network Components Builder Simulation - DATABASE FIRST"""
    return _render_individual_simulation('components', '1')

@user_bp.route('/networking1-osi-simulation')
@user_login_required
def networking1_osi_simulation():
    """OSI Model Interactive Simulation - DATABASE FIRST"""
    return _render_individual_simulation('osi', '1')

@user_bp.route('/networking1-tcpip-simulation')
@user_login_required
def networking1_tcpip_simulation():
    """TCP/IP Protocol Stack Simulation - DATABASE FIRST"""
    return _render_individual_simulation('tcpip', '1')

@user_bp.route('/networking1-ethernet-simulation')
@user_login_required
def networking1_ethernet_simulation():
    """Ethernet Technology Simulation - DATABASE FIRST"""
    return _render_individual_simulation('ethernet', '1')

@user_bp.route('/networking1-application-simulation')
@user_login_required  
def networking1_application_simulation():
    """Application Layer Protocols Simulation - DATABASE FIRST"""
    return _render_individual_simulation('application', '1')

@user_bp.route('/networking1-datalink-simulation')
@user_login_required
def networking1_datalink_simulation():
    """Data Link Layer Simulation - DATABASE FIRST"""
    return _render_individual_simulation('datalink', '1')

# NETWORKING 2 SIMULATION ROUTES
@user_bp.route('/networking2-simulations')
@user_login_required
def networking2_simulations():
    """Networking 2 simulations hub - DATABASE FIRST, static as fallback"""
    try:
        from services.hybrid_simulation_service import HybridSimulationService
        from admin.models.learning_path import LearningPath
        
        service = HybridSimulationService()
        all_simulations = service.get_combined_networking2_content()
        
        # Get learning paths for this category
        learning_paths = LearningPath.query.filter_by(
            category='networking2',
            is_published=True
        ).all()
        
        # Separate database and static simulations
        database_sims = [sim for sim in all_simulations if sim.get('type') == 'database']
        static_sims = [sim for sim in all_simulations if sim.get('type') == 'static']
        
        print(f"Networking2 simulations loaded: {len(all_simulations)} total, {len(database_sims)} from database, {len(static_sims)} static")
        
        # Get current user for template
        user = UserModel.query.get(session['user_id']) if 'user_id' in session else None
        
        # Structure data for enhanced template
        content = {
            'database': database_sims,
            'static': static_sims,
            'learning_paths': [{'id': lp.id, 'title': lp.title, 'description': lp.description, 'simulations': []} for lp in learning_paths]
        }
        
        return render_template('user/simulations.html', 
                             content=content,
                             course_title="Advanced Networking Simulations",
                             lesson_key="networking2",
                             using_database=len(database_sims) > 0,
                             user=user)
    except Exception as e:
        print(f"Error loading networking2 simulations: {e}")
        import traceback
        traceback.print_exc()
        # Last resort fallback to dynamic dashboard
        return redirect(url_for('dynamic_simulations.simulations_dashboard') + '?category=networking2')

# Core Module Simulations
@user_bp.route('/networking2-routing-fundamentals-simulation')
@user_login_required
def networking2_routing_fundamentals_simulation():
    """Module 1: Routing Fundamentals Simulation - DATABASE FIRST"""
    return _render_individual_simulation('routing_fundamentals', '2')

@user_bp.route('/networking2-dynamic-routing-simulation')
@user_login_required
def networking2_dynamic_routing_simulation():
    """Module 2: Dynamic Routing Protocols Simulation - redirects to dynamic dashboard"""
    return redirect(url_for('dynamic_simulations.simulations_dashboard', category='networking2'))

@user_bp.route('/networking2-rip-simulation')
@user_login_required
def networking2_rip_simulation():
    """Module 3: Routing Information Protocol (RIP) Simulation"""
    return _render_individual_simulation('networking2_rip_simulation', 'networking2')

@user_bp.route('/networking2-eigrp-simulation')
@user_login_required
def networking2_eigrp_simulation():
    """Module 4: Enhanced Interior Gateway Routing Protocol (EIGRP) Simulation"""
    return _render_individual_simulation('networking2_eigrp_simulation', 'networking2')

@user_bp.route('/networking2-ospf-simulation')
@user_login_required
def networking2_ospf_simulation():
    """Module 5: Open Shortest Path First (OSPF) Simulation"""
    return _render_individual_simulation('networking2_ospf_simulation', 'networking2')

@user_bp.route('/networking2-security-simulation')
@user_login_required
def networking2_security_simulation():
    """Module 6: Network Security and VPN Simulation"""
    return _render_individual_simulation('networking2_security_simulation', 'networking2')

@user_bp.route('/networking2-vlan-simulation')
@user_login_required
def networking2_vlan_simulation():
    """Module 7: VLAN Trunking Protocol Simulation"""
    return _render_individual_simulation('networking2_vlan_simulation', 'networking2')

# Additional Specialized Simulations
@user_bp.route('/networking2-routing-simulation')
@user_login_required
def networking2_routing_simulation():
    """Advanced Routing Simulation"""
    return _render_individual_simulation('networking2_routing_simulation', 'networking2')

@user_bp.route('/networking2-wireless-simulation')
@user_login_required
def networking2_wireless_simulation():
    """Wireless Networks Simulation"""
    return _render_individual_simulation('networking2_wireless_simulation', 'networking2')

@user_bp.route('/networking2-management-simulation')
@user_login_required
def networking2_management_simulation():
    """Network Management Simulation"""
    return _render_individual_simulation('networking2_management_simulation', 'networking2')

@user_bp.route('/networking2-vpn-simulation')
@user_login_required
def networking2_vpn_simulation():
    """VPN Technologies Simulation"""
    return _render_individual_simulation('networking2_vpn_simulation', 'networking2')

@user_bp.route('/networking2-troubleshooting-simulation')
@user_login_required
def networking2_troubleshooting_simulation():
    """Network Troubleshooting Simulation"""
    return _render_individual_simulation('networking2_troubleshooting_simulation', 'networking2')

@user_bp.route('/networking2-qos-simulation')
@user_login_required
def networking2_qos_simulation():
    """QoS & Network Performance Analysis Simulation"""
    return _render_individual_simulation('networking2_qos_simulation', 'networking2')


# DYNAMIC SYSTEM REDIRECTS
from flask import redirect, url_for

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
