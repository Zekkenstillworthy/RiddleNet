from flask import render_template, session, Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func
import os
from datetime import datetime
import sys
from utils.password_validator import validate_password
import traceback
import random
from werkzeug.utils import secure_filename
# Use specific imports with module paths to avoid conflicts
from .models import db
from .models import User as UserModel  # Rename to avoid conflicts
from .models import Score as UserScore  # Rename to avoid conflicts
from user.models.challenge_score import ChallengeScore
from instructor.models.topology import Topology
from user.models.topology_progress import TopologyProgress
from instructor.models.class_model import Class
from flask_login import login_user, logout_user, current_user
from .utils import user_login_required
# Import media utilities
from utils.media_utils import serve_optimized_video, serve_optimized_audio
from utils.security import safe_next_or_fallback
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
    # Landing page - check if user is already logged in
    user = None
    if 'user_id' in session:
        user = UserModel.query.get(session['user_id'])
        # If user is already logged in, redirect to dashboard
        if user:
            return redirect(url_for('user.dashboard'))
    
    # Show gamified landing page
    return render_template('user/landing.html', user=user)

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
    from instructor.models.module import Module, Lesson
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

    # Get user's best scores from new ChallengeScore model (MVP)
    from user.models.challenge_score import ChallengeScore
    from user.models.user_badge import UserBadge
    
    # [OK] FIX: Get all 4 challenge types (troubleshooting = Link Up!)
    crimping_challenge = ChallengeScore.query.filter_by(user_id=user.id, challenge_type='crimping').first()
    osi_challenge = ChallengeScore.query.filter_by(user_id=user.id, challenge_type='osi').first()
    troubleshooting_challenge = ChallengeScore.query.filter_by(user_id=user.id, challenge_type='troubleshooting').first()
    quiz_challenge = ChallengeScore.query.filter_by(user_id=user.id, challenge_type='quiz').first()
    
    # Extract best scores (for backward compatibility and template)
    crimping_score_value = ChallengeScore.effective_best_score(crimping_challenge)
    osi_score_value = ChallengeScore.effective_best_score(osi_challenge)
    topology_score_value = ChallengeScore.effective_best_score(troubleshooting_challenge)  # Keep legacy name
    linkup_score_value = topology_score_value  # Same as topology (Link Up!)
    quiz_score_value = ChallengeScore.effective_best_score(quiz_challenge)
    
    # Calculate dashboard stats (MVP)
    challenge_stats = ChallengeScore.get_user_stats(user.id)
    
    # Get user badges (MVP)
    user_badges = UserBadge.get_user_badges(user.id)

    # Deduplicate badges by badge_id while keeping most recent award first
    deduped_badges = []
    seen_badge_ids = set()
    for badge in user_badges:
        normalized_badge_id = (badge.badge_id or '').strip().lower()
        if not normalized_badge_id or normalized_badge_id in seen_badge_ids:
            continue
        deduped_badges.append(badge)
        seen_badge_ids.add(normalized_badge_id)

    # Pick the highest value badge per challenge type (legendary > rare > common)
    rarity_rank = {'legendary': 3, 'rare': 2, 'common': 1}
    challenge_badge_map = {}
    for badge in deduped_badges:
        challenge_key = (badge.challenge_type or '').strip().lower()
        if not challenge_key:
            continue
        current_choice = challenge_badge_map.get(challenge_key)
        current_rank = rarity_rank.get((current_choice.badge_rarity or '').lower(), 0) if current_choice else -1
        new_rank = rarity_rank.get((badge.badge_rarity or '').lower(), 0)

        should_replace = False
        if not current_choice:
            should_replace = True
        elif new_rank > current_rank:
            should_replace = True
        elif new_rank == current_rank:
            existing_time = current_choice.earned_at or datetime.min
            new_time = badge.earned_at or datetime.min
            should_replace = new_time > existing_time

        if should_replace:
            challenge_badge_map[challenge_key] = badge
        else:
            print(f"[DASHBOARD DEBUG] ⏭  Keeping better badge for {challenge_key}, skipping {badge.badge_id}")

    challenge_badges = sorted(
        challenge_badge_map.values(),
        key=lambda b: b.earned_at or datetime.min,
        reverse=True
    )
    print(f"[DASHBOARD DEBUG] Final badges per challenge type: {len(challenge_badges)}")

    # 🔧 PRODUCTION FIX: Validate badges against actual challenge completion
    # Only show badges where the challenge is ACTUALLY completed at 100%
    # This prevents showing badges that were incorrectly awarded at 75% threshold
    
    # Create a map of challenge scores for validation
    challenge_score_map = {
        'crimping': crimping_challenge,
        'osi': osi_challenge,
        'troubleshooting': troubleshooting_challenge,
        'quiz': quiz_challenge
    }
    
    validated_badges = []
    for badge in challenge_badges:
        challenge_type = badge.challenge_type
        challenge = challenge_score_map.get(challenge_type)
        
        if challenge:
            # 🔧 MVP FIX: For Link Up!, check sub-item completion (all 26 items must be complete)
            if challenge_type == 'troubleshooting':
                if challenge.challenge_metadata:
                    completed_count = len(challenge.challenge_metadata.get('completed_challenges', []))
                    TOTAL_LINK_UP_ITEMS = 26  # Foundation (17) + Easy (3) + Intermediate (3) + Hard (3)
                    is_truly_completed = completed_count >= TOTAL_LINK_UP_ITEMS
                    print(f"[DASHBOARD DEBUG] Link Up! validation: {completed_count}/{TOTAL_LINK_UP_ITEMS} sub-items")
                else:
                    is_truly_completed = False
                    print(f"[DASHBOARD DEBUG] Link Up! has no metadata")
            else:
                # For other challenges, use existing validation
                is_truly_completed = ChallengeScore.is_effectively_completed(challenge)
                effective_score = ChallengeScore.effective_best_score(challenge)
                is_truly_completed = is_truly_completed and effective_score >= 100
            
            if is_truly_completed:
                validated_badges.append(badge)
                print(f"[DASHBOARD DEBUG] ✅ VALID BADGE: {badge.badge_id} for {challenge_type}")
            else:
                if challenge_type == 'troubleshooting':
                    print(f"[DASHBOARD DEBUG] ❌ INVALID BADGE FILTERED: {badge.badge_id} for {challenge_type} (not all sub-items complete)")
                else:
                    effective_score = ChallengeScore.effective_best_score(challenge)
                    print(f"[DASHBOARD DEBUG] ❌ INVALID BADGE FILTERED: {badge.badge_id} for {challenge_type} (score: {effective_score}%)")
        else:
            print(f"[DASHBOARD DEBUG] ⚠️ No challenge data for badge: {badge.badge_id} ({challenge_type})")
    
    user_badges_list = [badge.to_dict() for badge in validated_badges]
    
    print(f"[DASHBOARD DEBUG] Final badges sent to template: {len(user_badges_list)}")
    for badge_dict in user_badges_list:
        print(f"  → {badge_dict['badge_id']}: {badge_dict['badge_name']} ({badge_dict['challenge_type']})")

    # Record raw badge count for optional UI messaging
    total_badges_recorded = len(user_badges) if user_badges else 0
    
    # FIX: Count VALIDATED badges (only those with 100% completion)
    # This ensures consistency with challenge completion count
    unique_badge_challenges = len(validated_badges)
    
    print(f"\n[DASHBOARD DEBUG] Badge Count Metrics:")
    print(f"  Total badges in DB: {total_badges_recorded}")
    print(f"  Unique badges after badge_id dedup: {len(deduped_badges)}")
    print(f"  Unique badges after challenge filter: {len(challenge_badges)}")
    print(f"  Unique challenge types with badges: {unique_badge_challenges}")
    challenge_types_with_badges = set(challenge_badge_map.keys())
    print(f"  Challenge types: {challenge_types_with_badges}")
    
    # Get challenge data for display (4 challenges total)
    challenge_data = []
    print(f"\n[DASHBOARD DEBUG] Challenge Completion Status:")
    for challenge in [crimping_challenge, osi_challenge, troubleshooting_challenge, quiz_challenge]:
        if challenge:
            effective_score = ChallengeScore.effective_best_score(challenge)
            effective_completed = ChallengeScore.is_effectively_completed(challenge)
            challenge_dict = challenge.to_dict()
            challenge_dict['effective_best_score'] = effective_score
            challenge_dict['effective_completed'] = effective_completed
            challenge_data.append(challenge_dict)
            print(
                f"  {challenge.challenge_type}: stored={challenge.best_score}% | "
                f"effective={effective_score}% | Completed Flags -> raw:{challenge.is_completed} | effective:{effective_completed}"
            )
        else:
            print(f"  (No data for this challenge type)")

    try:
        # MVP: Enhanced leaderboard data from ChallengeScore table for accurate challenge tracking
        user_best_scores = []
        
        # Get all users with challenge scores including profile image
        users_with_scores = (
            db.session.query(UserModel.id, UserModel.username, UserModel.profile_img)
            .join(ChallengeScore)
            .distinct()
            .all()
        )
        
        # For each user, get their highest challenge score entry
        for user_id, username, profile_img in users_with_scores:
            highest_score_entry = (
                db.session.query(ChallengeScore)
                .filter(ChallengeScore.user_id == user_id)
                .order_by(ChallengeScore.best_score.desc(), ChallengeScore.updated_at.desc())
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
                    score=highest_score_entry.best_score,
                    category=highest_score_entry.challenge_type,
                    date_attempted=highest_score_entry.updated_at,
                    profile_img=profile_img
                )
                user_best_scores.append(entry)
        
        # Sort by score (highest first)
        leaderboard_data = sorted(user_best_scores, key=lambda x: x.score, reverse=True)
        
        # MVP: Category-specific leaderboards from ChallengeScore table
        # Map legacy category names to challenge_type names
        challenge_type_map = {
            'topology': 'troubleshooting',  # Legacy topology = troubleshooting challenge
            'crimping': 'crimping',
            'troubleshoot': 'troubleshooting',
            'riddle': 'quiz',  # Legacy riddle = quiz challenge
            'osi': 'osi'
        }
        
        categories = ['topology', 'crimping', 'osi', 'troubleshoot', 'riddle']
        category_leaderboards = {}
        for category in categories:
            challenge_type = challenge_type_map.get(category, category)
            category_leaderboards[f"{category}_leaderboard"] = (
                db.session.query(
                    UserModel.username, 
                    UserModel.profile_img,
                    ChallengeScore.best_score.label('highest_score'), 
                    ChallengeScore.updated_at.label('latest_attempt')
                )
                .join(ChallengeScore)
                .filter(ChallengeScore.challenge_type == challenge_type)
                .group_by(UserModel.id, UserModel.username, UserModel.profile_img, ChallengeScore.best_score, ChallengeScore.updated_at)
                .order_by(ChallengeScore.best_score.desc())
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
    topology_score=topology_score_value,
    crimping_score=crimping_score_value,
    osi_score=osi_score_value,
    quiz_score=quiz_score_value,
    linkup_score=linkup_score_value,  # Same as topology_score (Link Up! = troubleshooting challenge)
        # MVP: New challenge-based stats (4 total challenges)
        completed_challenges=challenge_stats['total_challenges_completed'],
        total_challenges=challenge_stats['total_challenges'],
        avg_score=round(challenge_stats['average_score'], 1),
        total_attempts=challenge_stats['total_attempts'],
        user_badges=user_badges_list,
    badge_count=unique_badge_challenges,  # FIX: Show unique challenge types, not total badges
    total_badges=total_badges_recorded,  # Preserve raw recorded total for optional messaging
        challenge_data=challenge_data,
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
    
    # MVP: Get challenge scores from ChallengeScore table for accurate tracking
    challenge_scores = ChallengeScore.query.filter_by(user_id=user.id).all()
    
    # Convert to list format for template compatibility (with legacy Score table structure)
    user_scores = []
    for cs in challenge_scores:
        # Create a score object that mimics the old Score structure
        class ScoreDisplay:
            def __init__(self, challenge_score):
                self.id = challenge_score.id
                self.user_id = challenge_score.user_id
                self.score = challenge_score.best_score
                self.category = challenge_score.challenge_type
                self.date_attempted = challenge_score.updated_at
                self.attempts = challenge_score.total_attempts
                self.average_score = challenge_score.average_score
                self.latest_score = challenge_score.latest_score
                self.is_completed = challenge_score.is_completed
        
        user_scores.append(ScoreDisplay(cs))
    
    # Sort by date (most recent first)
    user_scores.sort(key=lambda x: x.date_attempted, reverse=True)
    
    # Calculate statistics from ChallengeScore data
    total_attempts = sum(cs.total_attempts or 0 for cs in challenge_scores)
    total_score = sum(cs.best_score or 0 for cs in challenge_scores)
    average_score = total_score / len(challenge_scores) if challenge_scores else 0
    highest_score = max((cs.best_score or 0 for cs in challenge_scores), default=0)
    
    # Category statistics from ChallengeScore table
    # Map challenge types to display categories
    challenge_type_to_category = {
        'crimping': 'crimping',
        'osi': 'osi',
        'troubleshooting': 'troubleshoot',
        'quiz': 'riddle'
    }
    
    categories = ['topology', 'crimping', 'troubleshoot', 'riddle']
    category_stats = {}
    for category in categories:
        # Map category to challenge_type
        if category == 'topology':
            challenge_type = 'troubleshooting'
        elif category == 'riddle':
            challenge_type = 'quiz'
        else:
            challenge_type = category
        
        category_challenge = next((cs for cs in challenge_scores if cs.challenge_type == challenge_type), None)
        
        if category_challenge:
            category_stats[category] = {
                'attempts': category_challenge.total_attempts or 0,
                'best_score': category_challenge.best_score or 0,
                'average': category_challenge.average_score or 0
            }
        else:
            category_stats[category] = {
                'attempts': 0,
                'best_score': 0,
                'average': 0
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
            from instructor.models.troubleshooting import Troubleshooting
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

@user_bp.route('/challenges')
@user_login_required
def challenges():
    """Challenges Hub - MVP with Accurate Progress Tracking"""
    from user.models.challenge_score import ChallengeScore
    
    user = UserModel.query.get(session['user_id'])
    
    # Calculate progress for each challenge type
    challenge_progress = {}
    
    # 🔧 FIX: Crimping Challenge Progress - Based on 3 difficulty completions (Easy, Medium, Hard)
    crimping_score = ChallengeScore.query.filter_by(
        user_id=user.id, 
        challenge_type='crimping'
    ).first()
    
    if crimping_score and crimping_score.challenge_metadata:
        easy_completed = crimping_score.challenge_metadata.get('easyCompleted', False)
        medium_completed = crimping_score.challenge_metadata.get('mediumCompleted', False)
        hard_completed = crimping_score.challenge_metadata.get('hardCompleted', False)
        
        completed_count = sum([easy_completed, medium_completed, hard_completed])
        crimping_progress_value = (completed_count / 3) * 100.0
    else:
        crimping_progress_value = 0.0
    
    challenge_progress['crimping'] = {
        'completed': crimping_progress_value >= 100.0,
        'progress': min(crimping_progress_value / 100, 1.0),
        'badge_image': 'Cable_Badge.png'
    }
    
    # 🔧 FIX: OSI Model Challenge Progress - Show 100% when both levels are 100%, not 50%
    osi_score = ChallengeScore.query.filter_by(
        user_id=user.id,
        challenge_type='osi'
    ).first()
    
    if osi_score and osi_score.challenge_metadata:
        challenge_data = osi_score.challenge_metadata.get('challenge_data', {})
        level1_score = challenge_data.get('level1_score', 0)
        level2_score = challenge_data.get('level2_score', 0)
        both_levels_complete = challenge_data.get('both_levels_complete', False)
        
        # If both levels complete at 100%, show 100% progress
        if both_levels_complete and level1_score == 100 and level2_score == 100:
            osi_progress_value = 100.0
        else:
            # Otherwise use average of two levels
            osi_progress_value = (level1_score + level2_score) / 2
    else:
        osi_progress_value = 0.0
    
    osi_progress = min(osi_progress_value / 100, 1.0)
    challenge_progress['osi'] = {
        'completed': osi_progress_value >= 100.0,
        'progress': osi_progress,
        'badge_image': 'OSI_Badge.png'
    }
    
    # 🔧 MVP FIX: Link Up! Challenge Progress - Calculate from ALL sub-items across difficulty levels
    troubleshoot_score = ChallengeScore.query.filter_by(
        user_id=user.id,
        challenge_type='troubleshooting'
    ).first()
    
    # Get sub-item completion data from metadata
    if troubleshoot_score and troubleshoot_score.challenge_metadata:
        completed_challenges = troubleshoot_score.challenge_metadata.get('completed_challenges', [])
        # 🔧 MVP FIX: Total required: Foundation (17) + Easy (3) + Intermediate (3) + Hard (3) = 26 items
        TOTAL_LINK_UP_ITEMS = 26
        troubleshoot_progress_value = (len(completed_challenges) / TOTAL_LINK_UP_ITEMS) * 100.0
    else:
        troubleshoot_progress_value = 0.0
    
    challenge_progress['troubleshooting'] = {
        'completed': troubleshoot_progress_value >= 100.0,
        'progress': min(troubleshoot_progress_value / 100, 1.0),
        'badge_image': 'Troubleshoot_Badge.png'
    }
    
    # 🔧 FIX: Quiz Challenge Progress - Based on 3 question set completions
    quiz_score = ChallengeScore.query.filter_by(
        user_id=user.id,
        challenge_type='quiz'
    ).first()
    
    if quiz_score and quiz_score.challenge_metadata:
        completed_sets = quiz_score.challenge_metadata.get('completedSets', [])
        quiz_progress_value = (len(completed_sets) / 3) * 100.0
    else:
        quiz_progress_value = 0.0
    
    quiz_progress = min(quiz_progress_value / 100, 1.0)
    challenge_progress['quiz'] = {
        'completed': quiz_progress_value >= 100.0,
        'progress': quiz_progress,
        'badge_image': 'Quiz_Badge.png'
    }
    
    return render_template('user/challenges.html', 
                         title="Challenges Hub", 
                         user=user,
                         challenge_progress=challenge_progress)

@user_bp.route('/osi-simulation')
@user_login_required
def osi_simulation():
    """OSI Model Simulation - Interactive learning tool for understanding the 7-layer OSI model"""
    user = UserModel.query.get(session['user_id'])
    
    # Check if user has already completed levels
    osi_challenge = ChallengeScore.query.filter_by(user_id=user.id, challenge_type='osi').first()
    
    level_completion_data = {
        'level1_complete': False,
        'level2_complete': False,
        'level1_score': 0,
        'level2_score': 0,
        'combined_score': 0
    }
    
    if osi_challenge and osi_challenge.challenge_metadata:
        challenge_data = osi_challenge.challenge_metadata.get('challenge_data', {})
        both_levels_complete = bool(challenge_data.get('both_levels_complete', False))
        level2_score_val = challenge_data.get('level2_score', 0)
        level_completion_data = {
            'level1_complete': challenge_data.get('level1_score', 0) > 0,  # Any score means completed
            # Consider level 2 complete if explicit score exists OR final flag is set
            'level2_complete': (level2_score_val if isinstance(level2_score_val, (int, float)) else 0) > 0 or both_levels_complete,
            'level1_score': challenge_data.get('level1_score', 0),
            'level2_score': level2_score_val if isinstance(level2_score_val, (int, float)) else 0,
            'combined_score': osi_challenge.best_score,
            'both_levels_complete': both_levels_complete
        }
    
    return render_template('user/osi-simulation.html', 
                         title="OSI Model Simulation", 
                         user=user,
                         level_completion=level_completion_data)

@user_bp.route('/save_crimping_score', methods=['POST'])
@user_login_required
def save_crimping_score():
    """Save crimping simulation score (MVP with Badge System)"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        score = data.get('score', 0)
        wiring_type = data.get('wiring_type', 'unknown')
        completion_time = data.get('completion_time', 0)
        
        # Extract difficulty completion data from frontend
        easy_completed = data.get('easyCompleted', False)
        medium_completed = data.get('mediumCompleted', False)
        hard_completed = data.get('hardCompleted', False)
        easy_score = data.get('easyScore', 0)
        medium_score = data.get('mediumScore', 0)
        hard_score = data.get('hardScore', 0)
        
        print(f"[MVP Backend] Received score submission:")
        print(f"  - User ID: {user_id}")
        print(f"  - Score: {score}")
        print(f"  - Wiring Type: {wiring_type}")
        print(f"  - Completion Time: {completion_time}s")
        print(f"  - Difficulty Progress:")
        print(f"    - Easy: {'✓' if easy_completed else '✗'} ({easy_score}%)")
        print(f"    - Medium: {'✓' if medium_completed else '✗'} ({medium_score}%)")
        print(f"    - Hard: {'✓' if hard_completed else '✗'} ({hard_score}%)")
        
        # Save to legacy Score table for backward compatibility
        new_score = UserScore(
            user_id=user_id,
            score=score,
            category='crimping'
        )
        db.session.add(new_score)
        
        # Build metadata with difficulty tracking
        metadata = {
            'wiring_type': wiring_type,
            'easyCompleted': easy_completed,
            'mediumCompleted': medium_completed,
            'hardCompleted': hard_completed,
            'easyScore': easy_score,
            'mediumScore': medium_score,
            'hardScore': hard_score
        }
        
        # Save to new ChallengeScore table with detailed tracking
        from user.models.challenge_score import ChallengeScore
        challenge_score = ChallengeScore.save_score(
            user_id=user_id,
            challenge_type='crimping',
            score=score,
            metadata=metadata,
            completion_time=completion_time
        )
        
        # Check and award badges
        from user.services.badge_service import BadgeService
        newly_earned_badges = BadgeService.check_and_award_badges(
            user_id=user_id,
            challenge_type='crimping',
            score=score,
            metadata=metadata
        )
        
        db.session.commit()
        
        print(f"[MVP Backend] [OK] Score saved (ID: {new_score.id}, Badges: {len(newly_earned_badges)})")
        
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
                    'badges_earned': newly_earned_badges,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=f'user_{user_id}')
                print(f"[MVP Backend] WebSocket notification sent")
        except Exception as e:
            print(f"[MVP Backend] WebSocket notification failed: {e}")
        
        return jsonify({
            'status': 'success',
            'message': 'Crimping score saved successfully!',
            'score': score,
            'saved_id': new_score.id,
            'badges_earned': newly_earned_badges,
            'challenge_completed': challenge_score.is_completed
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"[MVP Backend] [ERROR] Error saving crimping score: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Failed to save score: {str(e)}'
        }), 500

@user_bp.route('/save_osi_score', methods=['POST'])
@user_login_required
def save_osi_score():
    """Save OSI simulation score (MVP with Badge System)"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        score = data.get('score', 0)
        layer_accuracy = data.get('layer_accuracy', {})
        completion_time = data.get('completion_time', 0)
        challenge_data = data.get('challenge_data', {})  # Get two-level challenge data
        skip_badge_check = data.get('skip_badge_check', False)  # MVP: New flag
        
        # Save to legacy Score table
        new_score = UserScore(
            user_id=user_id,
            score=score,
            category='osi'
        )
        db.session.add(new_score)
        
        # Get existing challenge score to merge metadata
        from user.models.challenge_score import ChallengeScore
        existing_challenge = ChallengeScore.query.filter_by(
            user_id=user_id, 
            challenge_type='osi'
        ).first()
        
        # Merge existing challenge_data with new data
        merged_challenge_data = {}
        if existing_challenge and existing_challenge.challenge_metadata:
            merged_challenge_data = existing_challenge.challenge_metadata.get('challenge_data', {}).copy()
        
        # Update with new challenge data
        if challenge_data:
            merged_challenge_data.update(challenge_data)
        
        # Track previous completion timestamps before the record_attempt mutation
        previous_completed = existing_challenge.is_completed if existing_challenge else False
        previous_first_completed = existing_challenge.first_completed_at if existing_challenge else None
        previous_last_completed = existing_challenge.last_completed_at if existing_challenge else None

        # Evaluate progress state based on the merged challenge data
        level1_score_val = ChallengeScore._normalize_score(merged_challenge_data.get('level1_score'))
        level2_score_val = ChallengeScore._normalize_score(merged_challenge_data.get('level2_score'))
        combined_score_val = ChallengeScore._normalize_score(
            merged_challenge_data.get('combined_score', score)
        )
        both_levels_complete_flag = bool(
            merged_challenge_data.get('both_levels_complete', False)
            or (level1_score_val == 100.0 and level2_score_val == 100.0)
        )
        final_completion_flag = bool(
            both_levels_complete_flag and level1_score_val == 100.0 and level2_score_val == 100.0
        )

        # Use averaged progress (both levels weighted equally) until the final completion
        partial_progress = (level1_score_val + level2_score_val) / 2.0
        effective_score = combined_score_val if final_completion_flag else partial_progress

        # Prepare metadata for ChallengeScore
        metadata = {'layer_accuracy': layer_accuracy}
        if merged_challenge_data:
            metadata['challenge_data'] = merged_challenge_data
        
        # Save to new ChallengeScore table
        challenge_score = ChallengeScore.save_score(
            user_id=user_id,
            challenge_type='osi',
            score=effective_score,
            metadata=metadata,
            completion_time=completion_time
        )

        # Ensure the ChallengeScore reflects the real completion status
        if final_completion_flag:
            challenge_score.is_completed = True
            challenge_score.best_score = max(challenge_score.best_score or 0, combined_score_val)
            challenge_score.latest_score = combined_score_val
            if not previous_completed:
                challenge_score.first_completed_at = datetime.utcnow()
            challenge_score.last_completed_at = datetime.utcnow()
        else:
            if previous_completed:
                # Preserve historical completion if the user already cleared the challenge
                challenge_score.is_completed = True
                challenge_score.first_completed_at = previous_first_completed
                challenge_score.last_completed_at = previous_last_completed
            else:
                challenge_score.is_completed = False
                challenge_score.first_completed_at = None
                challenge_score.last_completed_at = None
                challenge_score.latest_score = partial_progress
                if (challenge_score.best_score or 0) < partial_progress:
                    challenge_score.best_score = partial_progress
        
        # MVP FIX: Only check badges if both levels complete AND not skipping
        newly_earned_badges = []
        if not skip_badge_check:
            # Check and award badges - pass complete metadata with challenge_data
            from user.services.badge_service import BadgeService
            newly_earned_badges = BadgeService.check_and_award_badges(
                user_id=user_id,
                challenge_type='osi',
                score=score,
                metadata=metadata
            )
        
        db.session.commit()
        
        # Debug: Log saved challenge data
        print(f"[OSI Score Save] User {user_id}:")
        print(f"  Score: {score}")
        print(f"  Challenge Data: {merged_challenge_data}")
        print(f"  Skip Badge Check: {skip_badge_check}")
        
        # MVP FIX: Return early for Level 1 completion (skip badge check)
        if skip_badge_check:
            return jsonify({
                'status': 'success',
                'message': 'Level 1 progress saved',
                'score': score,
                'badges_earned': [],
                'challenge_completed': False
            })
        
        # WebSocket notification (only for Level 2 completion)
        try:
            from socket_events import socketio
            socketio.emit('score_updated', {
                'user_id': user_id,
                'category': 'osi',
                'new_score': score,
                'badges_earned': newly_earned_badges,
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'user_{user_id}')
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        # Check if both levels are complete for badge awarding
        both_levels_complete = challenge_data.get('both_levels_complete', False)
        
        return jsonify({
            'status': 'success',
            'message': 'Challenge complete!' if both_levels_complete else 'OSI simulation score saved successfully!',
            'score': score,
            'badges_earned': newly_earned_badges,
            'challenge_completed': both_levels_complete
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving OSI score: {e}")
        traceback.print_exc()  # Print full traceback for debugging
        return jsonify({
            'status': 'error',
            'message': f'Failed to save score: {str(e)}'
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
            # Notify Instructor of user logout
            socketio.emit('user_login_activity', {
                'user_id': user_id,
                'username': username,
                'action': 'logout',
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
            }, room='instructor_room')
            
            # Send logout notification to user's personal room
            socketio.emit('logout_complete', {
                'status': 'success',
                'message': f'Goodbye, {username}!',
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'user_{user_id}')
            
            print(f"WebSocket logout notifications sent for user: {username}")
    except Exception as ws_error:
        print(f"WebSocket logout notification failed: {str(ws_error)}")
    
    # Terminate the database session
    session_token = session.get('session_token')
    if session_token:
        from user.models.user_session import UserSession
        db_session = UserSession.get_session_by_token(session_token)
        if db_session:
            db_session.terminate()
            db.session.commit()
            print(f"[OK] Terminated database session for user {user_id}")
    
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
        # Check if user is already logged in
        if 'user_id' in session:
            user = UserModel.query.get(session['user_id'])
            if user:
                return redirect(url_for('user.dashboard'))
        
        # Only propagate a safe next for display; unsafe values are dropped
        requested_next = request.args.get('next', '')
        next_url = requested_next if safe_next_or_fallback(requested_next, 'user', '/') == requested_next else ''
        return render_template('user/index.html', next=next_url)
    
    # Otherwise, handle the login POST request
    # Session hardening: drop any pre-existing session to prevent poisoning/fixation
    try:
        session.clear()
    except Exception:
        pass
    email = request.form.get('email')  # Changed from username
    password = request.form.get('password')
    otp = request.form.get('otp')
    
    # Debug info
    print(f"Login attempt for: {email}")  # Changed from username
    print(f"OTP provided: {'Yes' if otp else 'No'}")
    
    # Send WebSocket notification for login attempt start
    try:
        socketio = get_socketio()
        if socketio:
            socketio.emit('user_login_activity', {
                'email': email,  # Changed from username
                'action': 'login_attempt_started',
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': request.environ.get('REMOTE_ADDR', 'unknown'),
                'user_agent': request.headers.get('User-Agent', 'unknown')
            }, room='instructor_room')
    except Exception as ws_error:
        print(f"WebSocket login attempt notification failed: {str(ws_error)}")
    
    # Find the user by email instead of username
    user = UserModel.query.filter_by(email=email).first()
    
    if not user:
        print(f"User not found: {email}")
        
        # Send WebSocket notification for failed login (user not found)
        try:
            socketio = get_socketio()
            if socketio:
                socketio.emit('user_login_activity', {
                    'email': email,
                    'action': 'login_failed',
                    'reason': 'user_not_found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                }, room='instructor_room')
        except Exception as ws_error:
            print(f"WebSocket login failure notification failed: {str(ws_error)}")
        
        return render_template('user/index.html', message='Invalid email address.')
    
    # Debug info
    print(f"User found: {user.username}, TOTP enabled: {user.totp_enabled}, TOTP secret exists: {'Yes' if user.totp_secret else 'No'}")
      # Validate password
    if not user.check_password(password):
        print(f"Invalid password for user: {email}")
        
        # Send WebSocket notification for failed login (invalid password)
        try:
            socketio = get_socketio()
            if socketio:
                socketio.emit('user_login_activity', {
                    'user_id': user.id,
                    'email': email,
                    'username': user.username,
                    'action': 'login_failed',
                    'reason': 'invalid_password',
                    'timestamp': datetime.utcnow().isoformat(),
                    'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                }, room='instructor_room')
        except Exception as ws_error:
            print(f"WebSocket login failure notification failed: {str(ws_error)}")
        
        return render_template('user/index.html', message='Invalid email or password.')      # Validate OTP if TOTP is enabled for this user
    if user.totp_enabled:
        if not otp:
            print(f"OTP required but not provided for user: {email}")
            
            # Send WebSocket notification for missing OTP
            try:
                socketio = get_socketio()
                if socketio:
                    socketio.emit('user_login_activity', {
                        'user_id': user.id,
                        'email': email,
                        'username': user.username,
                        'action': 'login_failed',
                        'reason': 'otp_required_but_not_provided',
                        'timestamp': datetime.utcnow().isoformat(),
                        'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                    }, room='instructor_room')
            except Exception as ws_error:
                print(f"WebSocket OTP missing notification failed: {str(ws_error)}")
            
            return render_template('user/index.html', message='OTP is required for this account. Please click "Request OTP" to receive a code via email.')
        
        try:
            # Check if OTP matches and hasn't expired (10 minute validity)
            if user.otp != otp:
                print(f"Invalid OTP code for user: {email}")
                
                # Send WebSocket notification for invalid OTP
                try:
                    socketio = get_socketio()
                    if socketio:
                        socketio.emit('user_login_activity', {
                            'user_id': user.id,
                            'email': email,
                            'username': user.username,
                            'action': 'login_failed',
                            'reason': 'invalid_otp',
                            'timestamp': datetime.utcnow().isoformat(),
                            'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                        }, room='instructor_room')
                except Exception as ws_error:
                    print(f"WebSocket invalid OTP notification failed: {str(ws_error)}")
                
                return render_template('user/index.html', message='Invalid OTP code. Please try again or request a new code.')
                
            # Check if OTP is expired (10 minutes)
            current_time = datetime.now()
            if user.otp_generated_at:
                otp_age = current_time - user.otp_generated_at
                if otp_age.total_seconds() > 600:  # 10 minutes in seconds
                    print(f"Expired OTP code for user: {email}")
                    
                    # Send WebSocket notification for expired OTP
                    try:
                        socketio = get_socketio()
                        if socketio:
                            socketio.emit('user_login_activity', {
                                'user_id': user.id,
                                'email': email,
                                'username': user.username,
                                'action': 'login_failed',
                                'reason': 'otp_expired',
                                'otp_age_minutes': round(otp_age.total_seconds() / 60, 2),
                                'timestamp': datetime.utcnow().isoformat(),
                                'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                            }, room='instructor_room')
                    except Exception as ws_error:
                        print(f"WebSocket expired OTP notification failed: {str(ws_error)}")
                    
                    return render_template('user/index.html', message='OTP code has expired. Please click "Request OTP" for a new code.')
            else:
                print(f"OTP generation timestamp missing for user: {email}")
                
                # Send WebSocket notification for missing OTP timestamp
                try:
                    socketio = get_socketio()
                    if socketio:
                        socketio.emit('user_login_activity', {
                            'user_id': user.id,
                            'email': email,
                            'username': user.username,
                            'action': 'login_failed',
                            'reason': 'otp_timestamp_missing',
                            'timestamp': datetime.utcnow().isoformat(),
                            'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                        }, room='instructor_room')
                except Exception as ws_error:
                    print(f"WebSocket OTP timestamp missing notification failed: {str(ws_error)}")
                
                return render_template('user/index.html', message='Invalid OTP. Please click "Request OTP" for a new code.')
                
            # Clear the OTP after successful validation
            user.otp = None
            user.otp_generated_at = None
            db.session.commit()
            
        except Exception as e:
            print(f"Error validating OTP for user {email}: {str(e)}")
            
            # Send WebSocket notification for OTP validation error
            try:
                socketio = get_socketio()
                if socketio:
                    socketio.emit('user_login_activity', {
                        'user_id': user.id,
                        'email': email,
                        'username': user.username,
                        'action': 'login_failed',
                        'reason': 'otp_validation_error',
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat(),
                        'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                    }, room='instructor_room')
            except Exception as ws_error:
                print(f"WebSocket OTP validation error notification failed: {str(ws_error)}")
            
            return render_template('user/index.html', message=f'Error validating OTP: {str(e)}. Please try again.')
    
    # CHECK FOR EXISTING ACTIVE SESSION - Prevent concurrent logins
    from utils.session_guard import check_existing_session, terminate_existing_sessions
    from user.models.user_session import UserSession
    
    has_active_session, session_info = check_existing_session(user.id, namespace='user')
    
    if has_active_session:
        print(f"[WARNING] User {user.username} (ID: {user.id}) already has an active session")
        print(f"   Session info: IP={session_info.get('ip_address')}, Last activity={session_info.get('last_activity')}")
        
        # Terminate the existing session
        terminated_count = terminate_existing_sessions(user.id, namespace='user')
        print(f"[OK] Terminated {terminated_count} existing session(s) for user {user.username}")
        
        # Notify via WebSocket about session termination
        try:
            socketio = get_socketio()
            if socketio:
                socketio.emit('session_terminated', {
                    'reason': 'new_login_from_different_device',
                    'message': 'Your session has been terminated because you logged in from another device.',
                    'timestamp': datetime.utcnow().isoformat()
                }, room=f'user_{user.id}')
        except Exception as ws_error:
            print(f"WebSocket session termination notification failed: {str(ws_error)}")
    
    # Create new session for this login
    new_session = UserSession.create_session(
        user_id=user.id,
        expiry_hours=24,
        request_obj=request
    )
    db.session.commit()
    
    # Set user in session (FIXED INDENTATION)
    session['user_id'] = user.id
    session['auth_namespace'] = 'user'  # CRITICAL FIX: Set user namespace
    session['session_token'] = new_session.session_token  # Store session token for validation
    session.permanent = True  # Make session permanent
    print(f"Login successful for user: {user.username}, email: {email}, user_id: {user.id}, namespace: {session.get('auth_namespace')}, session_token: {new_session.session_token[:16]}...")
    
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
                
                # Send Instructor notification for high-value accounts or security alerts
                if hasattr(user, 'is_instructor') and user.is_instructor:
                    notification_service.send_admin_notification(
                        notification_type=NotificationType.SECURITY_ALERT,
                        title="Instructor Login Detected",
                        message=f"Instructor user {user.username} (email: {email}) logged in from {request.environ.get('REMOTE_ADDR', 'unknown')}",
                        priority=NotificationPriority.HIGH
                    )
            except Exception as enhanced_error:
                print(f"Enhanced notification failed, using legacy: {enhanced_error}")
                
                # Fallback to legacy notifications
                # Notify Instructor of successful login
                socketio.emit('user_login_activity', {
                    'user_id': user.id,
                    'username': user.username,
                    'email': email,
                    'action': 'login_successful',
                    'timestamp': datetime.utcnow().isoformat(),
                    'ip_address': request.environ.get('REMOTE_ADDR', 'unknown'),
                    'user_agent': request.headers.get('User-Agent', 'unknown')
                }, room='instructor_room')
                
                # Send welcome notification to user's personal room
                socketio.emit('login_success', {
                    'status': 'success',
                    'message': f'Welcome back, {user.username}!',
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'user_{user.id}')
            
            print(f"WebSocket login success notifications sent for user: {user.username} (email: {email})")
    except Exception as ws_error:
        print(f"WebSocket login success notification failed: {str(ws_error)}")
    
    # Check if there's a next parameter in the query string or form and validate for user namespace
    next_url = request.args.get('next') or request.form.get('next') or ''
    target = safe_next_or_fallback(
        next_url=next_url,
        namespace='user',
        fallback=url_for('user.dashboard')
    )
    if target != url_for('user.dashboard'):
        print(f"Redirecting to: {target}")
        return redirect(target)
    
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
        
        # Validate password strength
        is_valid, errors = validate_password(password)
        if not is_valid:
            return jsonify({'status': 'error', 'message': errors[0]}), 400
        
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
        
        # Validate password strength
        is_valid, errors = validate_password(password)
        if not is_valid:
            return render_template('user/index.html', message=errors[0])
        
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
            email = data.get('email')
            
            if not email:
                return jsonify({'status': 'error', 'message': 'Email address is required'}), 400
            
            # Find the user in the database by email
            user = UserModel.query.filter_by(email=email).first()
            if not user:
                return jsonify({'status': 'error', 'message': 'User not found with this email address'}), 404
            
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
            
            # Send WebSocket notification to Instructor for real-time monitoring
            try:
                socketio = get_socketio()
                if socketio:
                    # Notify Instructor room about OTP request
                    socketio.emit('user_otp_activity', {
                        'user_id': user.id,
                        'username': user.username,
                        'email': email,
                        'action': 'otp_requested',
                        'timestamp': datetime.utcnow().isoformat(),
                        'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
                    }, room='instructor_room')
                    
                    # Send real-time notification to user's personal room
                    socketio.emit('otp_request_received', {
                        'status': 'processing',
                        'message': 'OTP request received, sending email...',
                        'timestamp': datetime.utcnow().isoformat()
                    }, room=f'user_{user.id}')
                    
                    print(f"WebSocket notifications sent for OTP request: {user.username} (email: {email})")
            except Exception as ws_error:
                print(f"WebSocket notification failed: {str(ws_error)}")
            
            # Send OTP via email using optimized direct SMTP connection
            success = send_otp_email_direct(user.email, user.username, otp)
            
            if success:
                # Send WebSocket success notification
                try:
                    socketio = get_socketio()
                    if socketio:
                        # Notify Instructor of successful OTP delivery
                        socketio.emit('user_otp_activity', {
                            'user_id': user.id,
                            'username': user.username,
                            'email': email,
                            'action': 'otp_sent_successfully',
                            'timestamp': datetime.utcnow().isoformat()
                        }, room='instructor_room')
                        
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
                        # Notify Instructor of failed OTP delivery
                        socketio.emit('user_otp_activity', {
                            'user_id': user.id,
                            'username': user.username,
                            'email': email,
                            'action': 'otp_failed',
                            'error': 'SMTP delivery failed',
                            'timestamp': datetime.utcnow().isoformat()
                        }, room='instructor_room')
                        
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
                        'email': email if 'email' in locals() else 'unknown',
                        'action': 'otp_error',
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }, room='instructor_room')
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
    """Save a topology/Link Up score with badge integration (MVP)"""
    data = request.json
    user_id = current_user.id
    
    if not data or 'score' not in data or 'category' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    try:
        score_value = float(data['score'])
        category = data['category']
        # [OK] FIX: Use challenge_type from request, default to 'linkup' for Link Up challenges
        challenge_type = data.get('challenge_type', 'linkup')
        
        print(f"[SAVE] Saving score: user_id={user_id}, score={score_value}, category={category}, challenge_type={challenge_type}")
        
        # Save to legacy UserScore table for backward compatibility
        try:
            new_score = UserScore(
                user_id=user_id,
                score=int(score_value),  # Ensure it's an integer
                category=category
            )
            db.session.add(new_score)
            db.session.flush()  # Get the ID without committing
            print(f"[OK] UserScore saved with ID: {new_score.id}")
        except Exception as score_error:
            print(f"[ERROR] Error saving UserScore: {score_error}")
            import traceback
            traceback.print_exc()
            # Continue even if legacy save fails
            new_score = None
        
        # Save to new ChallengeScore table with detailed tracking
        challenge_score = None
        newly_earned_badges = []
        
        try:
            from user.models.challenge_score import ChallengeScore
            challenge_score = ChallengeScore.save_score(
                user_id=user_id,
                challenge_type=challenge_type,  # [OK] FIX: Use dynamic challenge_type
                score=score_value,
                metadata={
                    'category': category,
                    'difficulty': data.get('difficulty', 'unknown'),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            print(f"[OK] ChallengeScore saved with ID: {challenge_score.id if challenge_score else 'None'}")
        except Exception as cs_error:
            print(f"[ERROR] Error saving ChallengeScore: {cs_error}")
            import traceback
            traceback.print_exc()
        
        # Check and award badges automatically
        try:
            from user.services.badge_service import BadgeService
            newly_earned_badges = BadgeService.check_and_award_badges(
                user_id=user_id,
                challenge_type=challenge_type,  # [OK] FIX: Use dynamic challenge_type
                score=score_value,
                metadata={
                    'category': category,
                    'difficulty': data.get('difficulty', 'unknown')
                }
            )
            print(f"[OK] Badges checked, earned: {len(newly_earned_badges)}")
        except Exception as badge_error:
            print(f"[ERROR] Error checking badges: {badge_error}")
            import traceback
            traceback.print_exc()
        
        db.session.commit()
        
        print(f"[Link Up MVP] [OK] Score saved (Type: {challenge_type}, Category: {category}, Badges: {len(newly_earned_badges)})")
        
        return jsonify({
            'status': 'success', 
            'message': 'Score saved successfully',
            'saved_id': new_score.id if new_score else None,
            'challenge_score_id': challenge_score.id if challenge_score else None,
            'badges_earned': newly_earned_badges
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[Link Up Error] [ERROR] Failed to save score: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to save score: {str(e)}'
        }), 500

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
            
            # Emit to Instructor room for monitoring
            socketio.emit('user_activity', {
                'user_id': current_user.id,
                'username': current_user.username,
                'activity_type': activity_type,
                'page': page,
                'details': details,
                'timestamp': datetime.utcnow().isoformat()
            }, room='instructor_room')
            
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
            
            # Notify Instructor of user joining topology
            socketio.emit('user_topology_activity', {
                'user_id': current_user.id,
                'username': current_user.username,
                'action': 'joined',
                'topology_type': topology_type,
                'timestamp': datetime.utcnow().isoformat()
            }, room='instructor_room')
            
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
            
            # Emit progress to Instructor room for monitoring
            socketio.emit('user_topology_progress', {
                'user_id': current_user.id,
                'username': current_user.username,
                'topology_type': topology_type,
                'progress': progress,
                'score': score,
                'completed': completed,
                'timestamp': datetime.utcnow().isoformat()
            }, room='instructor_room')
            
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
                
                # Emit to Instructor room for monitoring
                socketio.emit('user_score_achieved', {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'category': category,
                    'score': score,
                    'timestamp': datetime.utcnow().isoformat()
                }, room='instructor_room')
                
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
        """Handle OTP request notifications for Instructor monitoring"""
        try:
            username = data.get('username', current_user.username)
            
            # Notify Instructor of OTP request
            socketio.emit('user_otp_activity', {
                'user_id': current_user.id,
                'username': username,
                'action': 'otp_requested',
                'timestamp': datetime.utcnow().isoformat()
            }, room='instructor_room')
            
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
            
            # Notify Instructor of login attempt
            socketio.emit('user_login_activity', {
                'username': username,
                'success': success,
                'method': method,
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': request.environ.get('REMOTE_ADDR', 'unknown')
            }, room='instructor_room')
            
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
    from instructor.models.simulation import Simulation
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
    from instructor.models.simulation import Simulation
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
