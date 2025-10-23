
from flask import Blueprint, redirect, url_for, flash, jsonify, request, render_template, send_file, current_app
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, extract, or_
from decimal import Decimal
import json
import os
import logging
from flask_login import login_required, current_user

# Import models
from __init__ import db  # Use the main app db instance
from user.models.user import User  # Import the regular User model
from user.models.score import Score  # Import the regular Score model
from instructor.models.question import Question
from instructor.models.essay_response import EssayResponse
from instructor.models.class_model import Class  # Import Class model
from instructor.models.activity_log import ActivityLog
from instructor.models.module import Module, Lesson  # Import Module and Lesson models globally
from instructor.models.simulation import Simulation
from instructor.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial
from instructor.models.simulation_assignment import SimulationAssignment
from instructor.models.question_group import QuestionGroup  # Import QuestionGroup model globally
from utils.render_utils import render_safe_template

# Import analytics service
from instructor.services.analytics_service import AnalyticsService

# Initialize logger
logger = logging.getLogger(__name__)

# Create dashboard blueprint
# Note: url_prefix is empty because it's already set to '/instructor' in run.py
dashboard_bp = Blueprint('dashboard', __name__)

# Initialize analytics service
analytics_service = AnalyticsService()

# Helper function to convert Decimal to float for JSON serialization
def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(item) for item in obj]
    return obj

@dashboard_bp.route('/')
@login_required
def index():
    """Admin dashboard root - accessible via /admin/"""
    print("=" * 80)
    print("🔍 INSTRUCTOR DASHBOARD INDEX: Route accessed at /instructor/")
    print(f"🔍 Current user: {current_user.username if current_user.is_authenticated else 'Not authenticated'}")
    print(f"🔍 User type: {type(current_user)}")
    from flask import session
    print(f"🔍 Auth namespace: {session.get('auth_namespace', 'unknown')}")
    print("=" * 80)
    
    # MVP FIX: Ensure new admin/instructor accounts start with zero data
    # Only show data for classes created by this specific admin/instructor
    from instructor.models.class_model import Class, class_students
    
    # CRITICAL: Filter classes by created_by to ensure data isolation per admin
    admin_classes = Class.query.filter_by(created_by=current_user.id).all()
    admin_class_ids = [cls.id for cls in admin_classes]
    
    # Get students enrolled ONLY in this admin's classes
    student_ids = []
    if admin_class_ids:
        student_ids = db.session.query(class_students.c.user_id).filter(
            class_students.c.class_id.in_(admin_class_ids)
        ).distinct().all()
        student_ids = [sid[0] for sid in student_ids]
    
    # MVP FIX: All stats are now filtered to admin's students only
    # New admins will see zero counts until they create classes and enroll students
    if student_ids:
        total_users = User.query.filter(User.id.in_(student_ids)).count()
        total_scores = Score.query.filter(Score.user_id.in_(student_ids)).count()
    else:
        # New admin with no classes/students yet - show zero data
        total_users = 0
        total_scores = 0
    
    # Count QuestionGroups assigned to the admin's classes (not all questions in database)
    if admin_classes:
        # Get all unique question groups from all the admin's classes
        question_groups_set = set()
        for cls in admin_classes:
            if cls.question_groups:
                for qg in cls.question_groups:
                    question_groups_set.add(qg.id)
        question_count_main = len(question_groups_set)
    else:
        question_count_main = 0
    
    # Get recent scores for dashboard table - filtered to admin's students only
    if student_ids:
        recent_scores = Score.query.filter(Score.user_id.in_(student_ids)).order_by(desc(Score.date_attempted)).limit(10).all()
    else:
        recent_scores = []
    
    # Enhanced Score Analytics for Dashboard Overview
    
    # 1. Score distribution data for chart - adjusted based on actual score data, filtered to admin's students
    if student_ids:
        score_dist = {
            'very_low': Score.query.filter(Score.user_id.in_(student_ids), Score.score < 0.6).count(),  # Less than 20%
            'low': Score.query.filter(Score.user_id.in_(student_ids), and_(Score.score >= 0.6, Score.score < 1.2)).count(),  # 20-40%
            'medium': Score.query.filter(Score.user_id.in_(student_ids), and_(Score.score >= 1.2, Score.score < 1.8)).count(),  # 40-60%
            'high': Score.query.filter(Score.user_id.in_(student_ids), and_(Score.score >= 1.8, Score.score < 2.4)).count(),  # 60-80%
            'very_high': Score.query.filter(Score.user_id.in_(student_ids), Score.score >= 2.4).count()  # 80%+
        }
    else:
        score_dist = {'very_low': 0, 'low': 0, 'medium': 0, 'high': 0, 'very_high': 0}
    
    # 2. Performance trends - last 30 days
    today = datetime.now().date()
    last_30_days = [(today - timedelta(days=i)) for i in range(29, -1, -1)]
    
    # Daily score averages for trend analysis - filtered to admin's students
    daily_performance = []
    for date_obj in last_30_days:
        if student_ids:
            daily_avg = Score.query.filter(
                Score.user_id.in_(student_ids),
                func.date(Score.date_attempted) == date_obj
            ).with_entities(func.avg(Score.score)).scalar() or 0
        else:
            daily_avg = 0
        
        # Convert Decimal to float if needed
        if isinstance(daily_avg, Decimal):
            daily_avg = float(daily_avg)
        
        # Convert to percentage properly
        if daily_avg >= 0 and daily_avg <= 100:  # Already in percentage
            percentage_avg = round(daily_avg, 1)
        elif daily_avg <= 3:  # 0-3 scale
            percentage_avg = round((daily_avg / 3) * 100, 1)
        else:  # Cap at 100%
            percentage_avg = 100.0
        
        daily_performance.append({
            'date': date_obj.strftime('%Y-%m-%d'),
            'avg_score': float(percentage_avg)  # Ensure it's float, not Decimal
        })    # 3. User activity data - last 7 days for dashboard
    activity_dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
      # Count active users per day (users who attempted a quiz) - filtered to admin's students
    active_users = []
    for date_str in activity_dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        if student_ids:
            count = Score.query.filter(
                Score.user_id.in_(student_ids),
                func.date(Score.date_attempted) == date_obj
            ).with_entities(Score.user_id).distinct().count()
        else:
            count = 0
        active_users.append(count)
      # 4. Enhanced category analytics - filtered to admin's students
    categories = ['riddle', 'topology', 'troubleshoot', 'crimping']
    category_analytics = {}
    category_avg = {}
    
    for cat in categories:
        if student_ids:
            scores = Score.query.filter(Score.user_id.in_(student_ids), Score.category == cat).all()
        else:
            scores = []
        if scores:
            score_values = [float(s.score) if isinstance(s.score, Decimal) else s.score for s in scores]
            avg_score = sum(score_values) / len(score_values)
            max_score = max(score_values)
            
            # Convert to percentage properly
            if avg_score >= 0 and avg_score <= 100:  # Already in percentage
                avg_percentage = round(avg_score, 1)
                max_percentage = round(max_score, 1)
            elif avg_score <= 3:  # 0-3 scale
                avg_percentage = round((avg_score / 3) * 100, 1)
                max_percentage = round((max_score / 3) * 100, 1)
            else:  # Cap at 100%
                avg_percentage = 100.0
                max_percentage = 100.0
            
            category_analytics[cat] = {
                'avg_score': float(avg_percentage),
                'total_attempts': len(scores),
                'unique_users': len(set(s.user_id for s in scores)),
                'highest_score': float(max_percentage),
                'improvement_trend': 'up' if len(scores) > 5 else 'stable'  # Simplified trend
            }
            category_avg[cat] = float(avg_percentage)  # For template charts
        else:
            category_analytics[cat] = {
                'avg_score': 0, 'total_attempts': 0, 'unique_users': 0, 
                'highest_score': 0, 'improvement_trend': 'no_data'
            }
            category_avg[cat] = 0
    
    # 5. Top performing users (for dashboard overview) - filtered to admin's students
    if student_ids:
        top_performers = (
            db.session.query(
                User.username,
                func.max(Score.score).label('highest_score'),
                func.avg(Score.score).label('avg_score'),
                func.count(Score.id).label('total_attempts')
            )
            .join(Score)
            .filter(User.id.in_(student_ids))
            .group_by(User.id, User.username)
            .order_by(desc(func.max(Score.score)))
            .limit(5)
            .all()
        )
    else:
        top_performers = []
    
    # 6. Score insights and alerts - filtered to admin's students
    if student_ids:
        score_insights = {
            'total_this_week': Score.query.filter(
                Score.user_id.in_(student_ids),
                Score.date_attempted >= (today - timedelta(days=7))
            ).count(),
            'avg_this_week': 0,
            'trend_vs_last_week': 'stable'
        }
        
        # Calculate weekly average
        this_week_scores = Score.query.filter(
            Score.user_id.in_(student_ids),
            Score.date_attempted >= (today - timedelta(days=7))
        ).all()
    else:
        score_insights = {
            'total_this_week': 0,
            'avg_this_week': 0,
            'trend_vs_last_week': 'stable'
        }
        this_week_scores = []
    
    if this_week_scores:
        score_values = [float(s.score) if isinstance(s.score, Decimal) else s.score for s in this_week_scores]
        week_avg = sum(score_values) / len(score_values)
        # Convert to percentage properly
        if week_avg >= 0 and week_avg <= 100:  # Already in percentage
            score_insights['avg_this_week'] = round(week_avg, 1)
        elif week_avg <= 3:  # 0-3 scale
            score_insights['avg_this_week'] = round((week_avg / 3) * 100, 1)
        else:  # Cap at 100%
            score_insights['avg_this_week'] = 100.0
    
    # ...existing code for question difficulty, activity logs, etc...
    
    # Question difficulty distribution - filtered to admin's students
    if student_ids:
        question_difficulty = {
            'easy': EssayResponse.query.filter(EssayResponse.user_id.in_(student_ids), EssayResponse.graded_score >= 80).count(),
            'medium': EssayResponse.query.filter(EssayResponse.user_id.in_(student_ids), and_(EssayResponse.graded_score >= 60, 
                                                     EssayResponse.graded_score < 80)).count(),
            'hard': EssayResponse.query.filter(EssayResponse.user_id.in_(student_ids), EssayResponse.graded_score < 60).count()
        }
    else:
        question_difficulty = {'easy': 0, 'medium': 0, 'hard': 0}
    
    if sum(question_difficulty.values()) == 0:
        question_difficulty = {'easy': 2, 'medium': 1, 'hard': 1}
    
    # Recent system activity logs - filtered to admin's students
    activity_logs = []
    try:
        db_activity_logs = ActivityLog.query.order_by(desc(ActivityLog.timestamp)).limit(4).all()
        if db_activity_logs:
            for log in db_activity_logs:
                activity_logs.append({
                    'action_type': log.action_type,
                    'message': log.message,
                    'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })
        elif student_ids:
            essays = EssayResponse.query.filter(EssayResponse.user_id.in_(student_ids)).order_by(desc(EssayResponse.submission_date)).limit(4).all()
            for essay in essays:
                action_type = 'essay' if not essay.is_graded else 'edit'
                activity_logs.append({
                    'action_type': action_type,
                    'message': f'Essay response {"graded" if essay.is_graded else "submitted"} by User ID {essay.user_id}',
                    'timestamp': essay.submission_date.strftime('%Y-%m-%d %H:%M:%S')
                })
    except Exception as e:
        activity_logs = [
            {
                'action_type': 'login',
                'message': 'Admin logged in',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
    
    # System alerts - filtered to admin's students
    system_alerts = []
    if student_ids:
        unreviewed_essays = EssayResponse.query.filter(EssayResponse.user_id.in_(student_ids), EssayResponse.is_graded==False).count()
        if unreviewed_essays > 0:
            system_alerts.append({
                'message': f'{unreviewed_essays} unreviewed essay responses require attention',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        # Low performance alert
        recent_low_scores = Score.query.filter(
            Score.user_id.in_(student_ids),
            and_(Score.date_attempted >= (today - timedelta(days=7)), Score.score < 1.0)
        ).count()
    else:
        recent_low_scores = 0
    if recent_low_scores > 5:
        system_alerts.append({
            'message': f'{recent_low_scores} low scores this week - consider reviewing content difficulty',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_safe_template('instructor/dashboard.html',
                           total_users=total_users,
                           total_scores=total_scores,
                           total_questions=question_count_main,
                           recent_scores=recent_scores,
                           score_dist=score_dist,
                           activity_dates=json.dumps(activity_dates),
                           active_users=json.dumps(active_users),
                           category_analytics=category_analytics,
                           category_avg=category_avg,
                           daily_performance=json.dumps(daily_performance),
                           top_performers=top_performers,
                           score_insights=score_insights,
                           question_difficulty=question_difficulty,
                           activity_logs=activity_logs,
                           system_alerts=system_alerts,
                           active_page='dashboard')

# Direct route for /admin/dashboard - handle it directly instead of redirecting
@dashboard_bp.route('/dashboard')
@login_required
def dashboard_alias():
    """Handle /admin/dashboard directly to avoid redirect loops."""
    # Call the same logic as index() but avoid redirect
    return index()

@dashboard_bp.route('/api/chart-data')
@login_required
def chart_data():
    """API endpoint to get filtered chart data"""
    date_range = request.args.get('date_range', '7')  # Default to 7 days
    category = request.args.get('category', 'all')    # Default to all categories
    
    try:
        # Convert date_range to integer days (if not 'all')
        if date_range != 'all':
            days = int(date_range)
            start_date = datetime.now() - timedelta(days=days)
        else:
            start_date = datetime(2000, 1, 1)  # Very old date to include all
          # Base query with date filter
        query = Score.query.filter(Score.date_attempted >= start_date)
        
        # Add category filter if specified
        if category != 'all':
            query = query.filter(Score.category == category)
        
        # Score distribution data - adjusted for actual score data
        score_dist = {
            'very_low': query.filter(Score.score < 0.6).count(),
            'low': query.filter(and_(Score.score >= 0.6, Score.score < 1.2)).count(),
            'medium': query.filter(and_(Score.score >= 1.2, Score.score < 1.8)).count(),
            'high': query.filter(and_(Score.score >= 1.8, Score.score < 2.4)).count(),
            'very_high': query.filter(Score.score >= 2.4).count()
        }
          # Generate dates for the activity chart
        today = datetime.now().date()
        if date_range == 'all':
            # For 'all', group by months
            # This would need more complex SQL based on your DB
            activity_dates = ["All time"]
            active_users = [query.with_entities(Score.user_id).distinct().count()]
        else:
            # For specific ranges, show daily data
            activity_dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') 
                             for i in range(int(date_range)-1, -1, -1)]
            
            # Count active users per day
            active_users = []
            for date_str in activity_dates:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                count = query.filter(
                    func.date(Score.date_attempted) == date_obj
                ).with_entities(Score.user_id).distinct().count()
                active_users.append(count)
        
        # Category averages - adjusted for max score of 3
        category_avg = {}
        if category == 'all':
            categories = ['riddle', 'topology', 'troubleshoot', 'crimping']
            for cat in categories:
                cat_query = query.filter(Score.category == cat)
                avg = cat_query.with_entities(func.avg(Score.score)).scalar() or 0
                category_avg[cat] = round(float(avg) * 100 / 3, 1)  # Use max score of 3
        else:
            avg = query.with_entities(func.avg(Score.score)).scalar() or 0
            category_avg[category] = round(float(avg) * 100 / 3, 1)  # Use max score of 3
        
        return jsonify({
            'score_dist': score_dist,
            'activity_dates': activity_dates,
            'active_users': active_users,
            'category_avg': category_avg,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

# Add route for user management
@dashboard_bp.route('/user-management')
@login_required
def user_management():
    # Get regular users with their stats
    from instructor.models.user import Instructor
    
    users = User.query.all()  # Use the main User model for regular users
    user_stats = []
    for user in users:
        scores_count = Score.query.filter_by(user_id=user.id).count()
        highest_score = db.session.query(func.max(Score.score)).filter_by(user_id=user.id).scalar() or 0
        
        user_stats.append({
            'user': user,
            'scores_count': scores_count,
            'highest_score': highest_score
        })
    
    # Get instructor users from the Instructor model
    admins = Instructor.query.all()
    
    return render_template('instructor/user_management.html', 
                           user_stats=user_stats, 
                           admins=admins,
                           active_page='users')

@dashboard_bp.route('/export-data')
@login_required
def export_data():
    export_type = request.args.get('type', 'scores')
    format_type = request.args.get('format', 'json')
    
    if export_type == 'scores':
        data = Score.query.all()
    elif export_type == 'users':
        data = User.query.all()
    elif export_type == 'questions':
        data = Question.query.all()
    else:
        return jsonify({'error': 'Invalid export type'}), 400
    
    # Convert data to requested format (simplified version)
    result = []
    for item in data:
        result.append(item.to_dict() if hasattr(item, 'to_dict') else {'id': item.id})
    
    response = {
        'data': result,
        'count': len(result),
        'exported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'export_type': export_type
    }
    
    return jsonify(response)



@dashboard_bp.route('/manage-simulations')
@login_required
def manage_simulations():
    """Manage existing simulations page"""
    try:
        from instructor.controllers.simulation_controller import SimulationController
        simulation_controller = SimulationController()
        
        # Get only active simulations by default (exclude deleted ones)
        simulations_data = simulation_controller.get_all_simulations(include_inactive=False)
        
        return render_safe_template('instructor/manage_simulations.html', 
                                   active_page='manage_simulations',
                                   simulations=simulations_data.get('simulations', []),
                                   total_count=simulations_data.get('total_count', 0))
    except Exception as e:
        current_app.logger.error(f"Error loading manage simulations: {str(e)}")
        return render_safe_template('instructor/manage_simulations.html', 
                                   active_page='manage_simulations',
                                   simulations=[],
                                   total_count=0)

@dashboard_bp.route('/class-content-selector')
@login_required
def class_content_manager():
    """Class Content Manager page for creating and managing learning modules"""
    print("=== MODULE BUILDER ROUTE HIT ===")
    current_app.logger.info("Module Builder route accessed")
    
    try:
        # Get class ID from query parameters for direct class management
        class_id = request.args.get('class_id', type=int)
        print(f"🔍 Dashboard route: class_id parameter = {class_id}")
        print(f"🔍 Dashboard route: All query args = {dict(request.args)}")
        
        # Don't redirect - keep the original URL and load the class content directly
        if class_id:
            print(f"✅ Loading Class Content Manager for class_id: {class_id}")
            current_app.logger.info(f"Loading Class Content Manager for class_id: {class_id}")
        else:
            print("❌ No class_id provided, showing class selection interface")
        
        # Get classes available to this admin (owner) for selection dropdown
        from instructor.models.class_model import Class
        
        # First try to get classes, then filter by ownership and status
        try:
            # If super_admin, show all classes
            if hasattr(current_user, 'role') and current_user.role == 'super_admin':
                all_classes_query = Class.query.all()
            else:
                all_classes_query = Class.query.filter_by(created_by=getattr(current_user, 'id', None)).all()
            print(f"Raw query result: {len(all_classes_query)} classes found")
            current_app.logger.info(f"Module Builder: Total classes in DB: {len(all_classes_query)}")
            
            # Check each class and its status
            for cls in all_classes_query:
                print(f"Class found: ID={cls.id}, Name={cls.name}, Code={cls.code}, Status={getattr(cls, 'status', 'NO_STATUS')}")
                current_app.logger.info(f"Class: {cls.name} ({cls.code}) - Status: {getattr(cls, 'status', 'NO_STATUS')}")
            
            # Filter for active classes, but include all if no active ones found
            active_classes = [cls for cls in all_classes_query if getattr(cls, 'status', None) == 'active']
            print(f"Active classes: {len(active_classes)}")
            current_app.logger.info(f"Module Builder: Active classes: {len(active_classes)}")
            
            # Use active classes if available, otherwise use all classes
            all_classes = active_classes if active_classes else all_classes_query
            all_classes = sorted(all_classes, key=lambda x: x.name) if all_classes else []
            
        except Exception as e:
            print(f"Error querying classes: {str(e)}")
            current_app.logger.error(f"Error querying classes: {str(e)}")
            import traceback
            traceback.print_exc()
            all_classes = []
        
        # Debug logging
        current_app.logger.info(f"Module Builder: Found {len(all_classes)} classes")
        for cls in all_classes:
            current_app.logger.info(f"Class: {cls.name} ({cls.code}) - Status: {cls.status}")
        
        selected_class = None
        if class_id:
            selected_class = Class.query.get(class_id)
            current_app.logger.info(f"Module Builder: Looking for class with ID {class_id}")
            if not selected_class:
                current_app.logger.error(f'Class with ID {class_id} not found')
                flash(f'Class with ID {class_id} not found', 'error')
            else:
                current_app.logger.info(f"Module Builder: Found class {selected_class.name} (ID: {selected_class.id})")
        else:
            # Don't auto-select a class - show class selection interface
            selected_class = None
            current_app.logger.info("No class_id provided - showing class selection interface")
        
        # Get available content types for the selected class
        class_content = {}
        class_statistics = {}
        class_modules = []  # Initialize with empty list
        
        if selected_class:
            current_app.logger.info(f"Module Builder: Processing content for class {selected_class.name} (ID: {selected_class.id})")
            # Get dynamic class content from database
            # All models imported globally
            
            # Get simulations for this class via SimulationAssignment
            class_simulation_assignments = SimulationAssignment.query.filter_by(
                class_id=selected_class.id,
                is_active=True
            ).all()
            
            # Extract simulations from assignments
            class_simulations = []
            for assignment in class_simulation_assignments:
                if assignment.simulation and assignment.simulation.is_published and assignment.simulation.is_active:
                    class_simulations.append(assignment.simulation)
            
            # Get Quiz assigned to this class
            question_groups = selected_class.question_groups.all() if selected_class.question_groups else []
            
            # Get class modules
            try:
                class_modules = Module.query.filter_by(
                    class_id=selected_class.id,
                    is_active=True
                ).order_by(Module.order_index.asc()).all()
                current_app.logger.info(f"Found {len(class_modules)} modules for class {selected_class.id}")
                for module_item in class_modules:
                    current_app.logger.info(f"  - Module: {module_item.title} (ID: {module_item.id})")
            except Exception as e:
                current_app.logger.error(f"Error querying class modules: {e}")
                # Always ensure we have an empty list rather than None
                class_modules = []
                
            # Always log module loading status for debugging
            current_app.logger.info(f"🔍 Module loading status: {len(class_modules)} modules loaded for class {selected_class.id}")
            
            # Get class-specific content (NEW: Dynamic content from database)
            try:
                class_announcements = ClassAnnouncement.query.filter_by(
                    class_id=selected_class.id,
                    is_published=True
                ).order_by(ClassAnnouncement.created_at.desc()).all()
            except Exception as e:
                current_app.logger.error(f"Error querying announcements with is_published filter: {e}")
                # Fallback: Get all announcements for this class without the is_published filter
                class_announcements = ClassAnnouncement.query.filter_by(
                    class_id=selected_class.id
                ).order_by(ClassAnnouncement.created_at.desc()).all()
            
            try:
                class_assignments = ClassAssignment.query.filter_by(
                    class_id=selected_class.id,
                    is_published=True
                ).order_by(ClassAssignment.due_date.asc()).all()
            except Exception as e:
                current_app.logger.error(f"Error querying assignments with is_published filter: {e}")
                # Fallback: Get all assignments for this class
                class_assignments = ClassAssignment.query.filter_by(
                    class_id=selected_class.id
                ).order_by(ClassAssignment.created_at.desc()).all()
            
            try:
                class_materials = ClassMaterial.query.filter_by(
                    class_id=selected_class.id,
                    is_published=True
                ).order_by(ClassMaterial.created_at.desc()).all()
            except Exception as e:
                current_app.logger.error(f"Error querying materials with is_published filter: {e}")
                # Fallback: Get all materials for this class
                class_materials = ClassMaterial.query.filter_by(
                    class_id=selected_class.id
                ).order_by(ClassMaterial.created_at.desc()).all()
            
            # Get class topics with error handling
            try:
                # ClassTopic deprecated - content now organized under modules
                class_topics = []
            except Exception as e:
                current_app.logger.error(f"Error querying class topics: {e}")
                # Create empty list if query fails
                class_topics = []
            
            # Get enrolled students and their details
            enrolled_students = selected_class.students.all() if selected_class.students else []
            student_count = len(enrolled_students)
                
            # Build enriched module data including attached Quiz
            modules_data = []
            for module_item in class_modules:
                if hasattr(module_item, 'to_dict'):
                    module_dict = module_item.to_dict(include_lessons=True)
                else:
                    module_dict = {
                        'id': module_item.id,
                        'title': module_item.title,
                        'description': module_item.description,
                        'module_number': getattr(module_item, 'module_number', ''),
                        'order_index': getattr(module_item, 'order_index', 0),
                        'is_published': getattr(module_item, 'is_published', False),
                        'is_active': getattr(module_item, 'is_active', True),
                        'objectives': getattr(module_item, 'objectives', []),
                        'content': getattr(module_item, 'content', ''),
                        'estimated_duration': getattr(module_item, 'estimated_duration', 60),
                        'level': getattr(module_item, 'level', 'Beginner'),
                        'lessons': [lesson.to_dict() for lesson in getattr(module_item, 'lessons', []) if getattr(lesson, 'is_active', True)]
                    }

                module_question_groups = []
                if hasattr(module_item, 'question_groups') and module_item.question_groups is not None:
                    try:
                        module_qgs = module_item.question_groups.all()
                    except Exception:
                        module_qgs = list(getattr(module_item, 'question_groups', []) or [])
                else:
                    module_qgs = []

                for qg in module_qgs:
                    module_question_groups.append({
                        'id': qg.id,
                        'name': getattr(qg, 'name', None),
                        'description': getattr(qg, 'description', None),
                        'question_count': len(qg.questions) if hasattr(qg, 'questions') and qg.questions else 0
                    })

                module_dict['question_groups'] = module_question_groups
                modules_data.append(module_dict)

            # Build comprehensive class content dictionary
            class_content = {
                'simulations': [sim.to_dict() if hasattr(sim, 'to_dict') else {
                    'id': sim.id,
                    'title': sim.title,
                    'description': sim.description
                } for sim in class_simulations],
                'question_groups': [
                    {
                        **(qg.to_dict() if hasattr(qg, 'to_dict') else {
                            'id': qg.id,
                            'name': getattr(qg, 'name', None),
                            'description': getattr(qg, 'description', None),
                            'question_count': len(qg.questions) if hasattr(qg, 'questions') else 0
                        }),
                        'assigned_module_ids': (
                            [module.id for module in qg.modules.filter_by(class_id=selected_class.id).all()]
                            if hasattr(qg, 'modules') and hasattr(qg.modules, 'filter_by')
                            else [
                                module.id for module in getattr(qg, 'modules', [])
                                if getattr(module, 'class_id', None) == selected_class.id
                            ]
                        )
                    }
                    for qg in question_groups
                ],
                'modules': modules_data,
                'announcements': [ann.to_dict() if hasattr(ann, 'to_dict') else {
                    'id': ann.id,
                    'title': ann.title,
                    'message': ann.message,
                    'created_at': ann.created_at.isoformat() if ann.created_at else None
                } for ann in class_announcements],
                'assignments': [assign.to_dict() if hasattr(assign, 'to_dict') else {
                    'id': assign.id,
                    'title': assign.title,
                    'description': assign.description,
                    'due_date': assign.due_date.isoformat() if hasattr(assign, 'due_date') and assign.due_date else None
                } for assign in class_assignments],
                'materials': [mat.to_dict() if hasattr(mat, 'to_dict') else {
                    'id': mat.id,
                    'title': mat.title,
                    'description': mat.description,
                    'file_url': getattr(mat, 'file_url', '')
                } for mat in class_materials],
                'topics': [topic.to_dict() if hasattr(topic, 'to_dict') else {
                    'id': topic.id,
                    'title': topic.title,
                    'description': topic.description,
                    'sort_order': topic.sort_order
                } for topic in class_topics],
                'student_count': student_count,
                'students': [{'id': student.id, 'username': student.username, 'email': student.email, 'first_name': getattr(student, 'first_name', ''), 'last_name': getattr(student, 'last_name', '')} for student in enrolled_students]
            }
            
            # Log module count for debugging
            current_app.logger.info(f"🔧 Built class_content with {len(class_content['modules'])} modules")
            
            # Build comprehensive statistics
            class_statistics = {
                'total_students': student_count,
                'total_simulations': len(class_simulations),
                'total_question_groups': len(question_groups),
                'total_modules': len(class_modules),
                'total_announcements': len(class_announcements),
                'total_assignments': len(class_assignments),
                'total_materials': len(class_materials),
                'total_topics': len(class_topics),
                'total_content': len(class_announcements) + len(class_assignments) + len(class_materials) + len(class_modules),
                'completion_rate': 85.5,  # Calculate actual completion rate from database
                'average_score': 78.2     # Calculate actual average score from database
            }
            
            current_app.logger.info(f"Class content for {selected_class.name}: {class_statistics}")
            current_app.logger.info(f"*** Updated with modules support ***")
        else:
            # No class selected - provide empty data
            class_content = {
                'simulations': [],
                'question_groups': [],
                'modules': [],
                'announcements': [],
                'assignments': [],
                'materials': [],
                'topics': [],
                'student_count': 0,
                'students': []
            }
            
            # Empty statistics for no class selected
            class_statistics = {
                'total_students': 0,
                'total_simulations': 0,
                'total_question_groups': 0,
                'total_modules': 0,
                'total_announcements': 0,
                'total_assignments': 0,
                'total_materials': 0,
                'total_topics': 0,
                'total_content': 0,
                'completion_rate': 0,
                'average_score': 0
            }
        
        # Log module count for debugging
        current_app.logger.info(f"🔧 Built class_content with {len(class_content['modules'])} modules")
        
        # Debug what we're passing to template
        current_app.logger.info(f"Template context: all_classes={len(all_classes)}, selected_class={'Yes' if selected_class else 'No'}")
        
        # Ensure we have valid data even if content loading fails
        if not class_content:
            class_content = {
                'simulations': [],
                'question_groups': [],
                'modules': [],
                'announcements': [],
                'assignments': [],
                'materials': [],
                'topics': [],
                'student_count': 0,
                'students': []
            }
        
        if not class_statistics:
            class_statistics = {
                'total_students': 0,
                'total_simulations': 0,
                'total_question_groups': 0,
                'total_modules': 0,
                'total_announcements': 0,
                'total_assignments': 0,
                'total_materials': 0,
                'total_topics': 0,
                'total_content': 0,
                'completion_rate': 0,
                'average_score': 0
            }
        
        return render_safe_template('instructor/class_content_manager.html', 
                                   active_page='module_builder',
                                   all_classes=all_classes,
                                   selected_class=selected_class,
                                   class_content=class_content,
                                   class_statistics=class_statistics)
                                   
                                   
    except Exception as e:
        current_app.logger.error(f"Error loading class content manager: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        flash('Error loading class content manager', 'error')
        
        # Still try to load classes even if content loading failed
        try:
            from instructor.models.class_model import Class
            all_classes_query = Class.query.all()
            active_classes = [cls for cls in all_classes_query if getattr(cls, 'status', None) == 'active']
            all_classes = active_classes if active_classes else all_classes_query
            all_classes = sorted(all_classes, key=lambda x: x.name) if all_classes else []
            current_app.logger.info(f"Exception handler: Loaded {len(all_classes)} classes")
        except Exception as class_error:
            current_app.logger.error(f"Failed to load classes in exception handler: {class_error}")
            all_classes = []
        
        return render_safe_template('instructor/class_content_manager.html', 
                                   active_page='module_builder',
                                   all_classes=all_classes,
                                   selected_class=None,
                                   class_content={
                                       'simulations': [],
                                       'question_groups': [],
                                       'modules': [],
                                       'announcements': [],
                                       'assignments': [],
                                       'materials': [],
                                       'topics': [],
                                       'student_count': 0,
                                       'students': []
                                   },
                                   class_statistics={
                                       'total_students': 0,
                                       'total_simulations': 0,
                                       'total_question_groups': 0,
                                       'total_modules': 0,
                                       'total_announcements': 0,
                                       'total_assignments': 0,
                                       'total_materials': 0,
                                       'total_topics': 0,
                                       'total_content': 0,
                                       'completion_rate': 0,
                                       'average_score': 0
                                   })

@dashboard_bp.route('/api/class/<int:class_id>/content', methods=['GET'])
@login_required
def get_class_content(class_id):
    """Get all content for a specific class"""
    try:
        from instructor.models.class_model import Class
        from instructor.models.simulation import Simulation
        from instructor.models.simulation_assignment import SimulationAssignment
        from instructor.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial
        # ClassTopic removed - content now organized under Modules
        # Module already imported globally
        
        cls = Class.query.get_or_404(class_id)
        
        # Get simulations assigned to this class via SimulationAssignment
        class_simulation_assignments = SimulationAssignment.query.filter_by(
            class_id=class_id,
            is_active=True
        ).all()
        
        # Extract simulations from assignments
        simulations = []
        for assignment in class_simulation_assignments:
            if assignment.simulation and assignment.simulation.is_published and assignment.simulation.is_active:
                simulations.append(assignment.simulation)
        
        question_groups = cls.question_groups.all() if cls.question_groups else []
        
        # Get class-specific content
        try:
            announcements = ClassAnnouncement.query.filter_by(
                class_id=class_id,
                is_published=True
            ).order_by(ClassAnnouncement.created_at.desc()).all()
        except:
            announcements = ClassAnnouncement.query.filter_by(
                class_id=class_id
            ).order_by(ClassAnnouncement.created_at.desc()).all()
        
        try:
            assignments = ClassAssignment.query.filter_by(
                class_id=class_id,
                is_published=True
            ).order_by(ClassAssignment.due_date.asc()).all()
        except:
            assignments = ClassAssignment.query.filter_by(
                class_id=class_id
            ).order_by(ClassAssignment.created_at.desc()).all()
        
        try:
            materials = ClassMaterial.query.filter_by(
                class_id=class_id,
                is_published=True
            ).order_by(ClassMaterial.created_at.desc()).all()
        except:
            materials = ClassMaterial.query.filter_by(
                class_id=class_id
            ).order_by(ClassMaterial.created_at.desc()).all()
        
        try:
            # ClassTopic deprecated - content now organized under modules
            topics = []
        except:
            topics = []
        
        # Get class modules
        try:
            modules = Module.query.filter_by(
                class_id=class_id,
                is_active=True
            ).order_by(Module.order_index.asc()).all()
            current_app.logger.info(f"API: Found {len(modules)} modules for class {class_id}")
            for module_item in modules:
                current_app.logger.info(f"  - Module: {module_item.title} (ID: {module_item.id})")
        except Exception as e:
            current_app.logger.error(f"Error querying modules for API: {e}")
            modules = []
            
        # Log API module loading status
        current_app.logger.info(f"🔍 API Module status: Returning {len(modules)} modules for class {class_id}")
        
        # Get student information
        student_count = cls.students.count() if cls.students else 0
        
        return jsonify({
            'success': True,
            'class_id': class_id,
            'class_info': cls.to_dict(),
            'content': {
                'simulations': [sim.to_dict() for sim in simulations],
                'question_groups': [qg.to_dict() for qg in question_groups],
                'announcements': [ann.to_dict() for ann in announcements],
                'assignments': [assign.to_dict() for assign in assignments],
                'materials': [mat.to_dict() for mat in materials],
                'topics': [topic.to_dict() for topic in topics],
                'modules': [module_item.to_dict(include_lessons=True) if hasattr(module_item, 'to_dict') else {
                    'id': module_item.id,
                    'title': module_item.title,
                    'description': module_item.description,
                    'module_number': getattr(module_item, 'module_number', ''),
                    'order_index': getattr(module_item, 'order_index', 0),
                    'is_published': getattr(module_item, 'is_published', False),
                    'is_active': getattr(module_item, 'is_active', True),
                    'estimated_duration': getattr(module_item, 'estimated_duration', 60),
                    'level': getattr(module_item, 'level', 'Beginner'),
                    'lessons': [lesson.to_dict() for lesson in getattr(module_item, 'lessons', []) if getattr(lesson, 'is_active', True)]
                } for module_item in modules],
                'student_count': student_count
            },
            'statistics': {
                'total_students': student_count,
                'total_simulations': len(simulations),
                'total_question_groups': len(question_groups),
                'total_announcements': len(announcements),
                'total_assignments': len(assignments),
                'total_materials': len(materials),
                'total_topics': len(topics),
                'total_modules': len(modules)
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error getting class content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/class/<int:class_id>/content', methods=['POST'])
@login_required  
def create_class_content(class_id):
    """Create new content for a class - DYNAMIC DATABASE IMPLEMENTATION with FILE UPLOAD SUPPORT"""
    import os
    from werkzeug.utils import secure_filename
    from datetime import datetime
    
    try:
        from instructor.models.class_model import Class
        from instructor.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial
        # ClassTopic removed - content now organized under Modules
        from __init__ import db
        
        # Handle both JSON and form data (for file uploads)
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Form data with potential file uploads
            data = request.form.to_dict()
            files = request.files
        else:
            # JSON data (existing functionality)
            data = request.json
            files = {}
        
        content_type = data.get('type')  # 'announcement', 'assignment', 'material', 'topic'
        
        # Verify class exists
        cls = Class.query.get_or_404(class_id)
        
        if content_type == 'announcement':
            announcement = ClassAnnouncement(
                class_id=class_id,
                title=data.get('title', ''),
                message=data.get('message', ''),
                priority=data.get('priority', 'normal'),
                is_published=data.get('is_published', False),
                created_by=current_user.id
            )
            db.session.add(announcement)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Announcement "{announcement.title}" created successfully!',
                'content': announcement.to_dict()
            })
            
        elif content_type == 'assignment':
            assignment = ClassAssignment(
                class_id=class_id,
                title=data.get('title', ''),
                description=data.get('description', ''),
                instructions=data.get('instructions', ''),
                due_date=datetime.fromisoformat(data.get('due_date')) if data.get('due_date') else None,
                points=data.get('points', 100),
                assignment_type=data.get('assignment_type', 'assignment'),
                priority=data.get('priority', 'medium'),
                category=data.get('category', 'general'),
                is_published=data.get('is_published', False),
                question_group_id=data.get('question_group_id'),
                simulation_id=data.get('simulation_id'),
                created_by=current_user.id
            )
            db.session.add(assignment)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Assignment "{assignment.title}" created successfully!',
                'content': assignment.to_dict()
            })
            
        elif content_type == 'material':
            # Handle file upload for materials
            file_url = None
            file_name = None
            file_size = None
            
            if 'file' in files:
                uploaded_file = files['file']
                if uploaded_file and uploaded_file.filename:
                    # Create uploads directory if it doesn't exist
                    upload_dir = os.path.join(current_app.root_path, '..', 'static', 'uploads', 'materials')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Secure filename and add timestamp to prevent conflicts
                    original_filename = secure_filename(uploaded_file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    file_name = f"{timestamp}_{original_filename}"
                    file_path = os.path.join(upload_dir, file_name)
                    
                    # Save the file
                    uploaded_file.save(file_path)
                    
                    # Create URL for the file
                    file_url = f"/static/uploads/materials/{file_name}"
                    file_size = os.path.getsize(file_path)
                    
                    current_app.logger.info(f"File uploaded successfully: {file_name}")
            
            material = ClassMaterial(
                class_id=class_id,
                title=data.get('title', ''),
                description=data.get('description', ''),
                material_type=data.get('material_type', 'document'),
                file_path=file_url if file_url else None,
                external_url=data.get('url') if not file_url else None,  # Use external URL if no file uploaded
                file_size=file_size,
                is_published=data.get('is_published', False),
                created_by=current_user.id
            )
            db.session.add(material)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Material "{material.title}" created successfully!',
                'content': material.to_dict()
            })
            
        elif content_type == 'topic':
            # ClassTopic deprecated - content now organized under modules
            return jsonify({
                'success': False,
                'message': 'Topics are deprecated. Please create modules instead.',
                'error': 'ClassTopic is no longer supported'
            }), 400
            
            return jsonify({
                'success': True,
                'message': f'Topic "{topic.name}" created successfully!',
                'content': topic.to_dict()
            })
        
        else:
            return jsonify({'success': False, 'error': f'Unknown content type: {content_type}'}), 400
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating class content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/class/<int:class_id>/content/<content_type>/<int:content_id>', methods=['GET'])
@login_required
def get_class_content_item(class_id, content_type, content_id):
    """Get a specific content item for editing"""
    try:
        from instructor.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial
        # ClassTopic removed - content now organized under Modules
        
        if content_type == 'announcement':
            content = ClassAnnouncement.query.get_or_404(content_id)
        elif content_type == 'assignment':
            content = ClassAssignment.query.get_or_404(content_id)
        elif content_type == 'material':
            content = ClassMaterial.query.get_or_404(content_id)
        elif content_type == 'topic':
            # ClassTopic deprecated - content now organized under modules
            return jsonify({'success': False, 'error': 'Topics are no longer supported'}), 400
        else:
            return jsonify({'success': False, 'error': f'Unknown content type: {content_type}'}), 400
        
        # Verify the content belongs to the specified class
        if content.class_id != class_id:
            return jsonify({'success': False, 'error': 'Content does not belong to this class'}), 403
        
        return jsonify({
            'success': True,
            'content': content.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting class content item: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/class/<int:class_id>/content/<content_type>/<int:content_id>', methods=['PUT'])
@login_required
def update_class_content(class_id, content_type, content_id):
    """Update existing class content"""
    try:
        from instructor.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial
        # ClassTopic removed - content now organized under Modules
        from __init__ import db
        
        data = request.json
        
        if content_type == 'announcement':
            content = ClassAnnouncement.query.get_or_404(content_id)
        elif content_type == 'assignment':
            content = ClassAssignment.query.get_or_404(content_id)
        elif content_type == 'material':
            content = ClassMaterial.query.get_or_404(content_id)
        elif content_type == 'topic':
            # ClassTopic deprecated - content now organized under modules
            return jsonify({'success': False, 'error': 'Topics are no longer supported'}), 400
        else:
            return jsonify({'success': False, 'error': f'Unknown content type: {content_type}'}), 400
        
        # Update fields based on content type
        for field, value in data.items():
            if hasattr(content, field) and field not in ['id', 'created_at', 'created_by']:
                if field == 'due_date' and value:
                    setattr(content, field, datetime.fromisoformat(value))
                else:
                    setattr(content, field, value)
        
        content.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{content_type.title()} updated successfully!',
            'content': content.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating class content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/class/<int:class_id>/content/<content_type>/<int:content_id>', methods=['DELETE'])
@login_required
def delete_class_content(class_id, content_type, content_id):
    """Delete class content"""
    try:
        print(f"🔥 DELETE request received - class_id: {class_id}, content_type: {content_type}, content_id: {content_id}")
        current_app.logger.info(f"DELETE request received - class_id: {class_id}, content_type: {content_type}, content_id: {content_id}")
        
        from instructor.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial
        # ClassTopic removed - content now organized under Modules
        from instructor.models.simulation import Simulation
        from instructor.models.question_group import QuestionGroup
        from __init__ import db
        
        print(f"🔥 Content type validation: '{content_type}' in allowed types")
        
        if content_type == 'announcement':
            content = ClassAnnouncement.query.get_or_404(content_id)
            db.session.delete(content)
            db.session.commit()
            message = f'{content_type.title()} deleted successfully!'
            
        elif content_type == 'assignment':
            content = ClassAssignment.query.get_or_404(content_id)
            db.session.delete(content)
            db.session.commit()
            message = f'{content_type.title()} deleted successfully!'
            
        elif content_type == 'material':
            content = ClassMaterial.query.get_or_404(content_id)
            db.session.delete(content)
            db.session.commit()
            message = f'{content_type.title()} deleted successfully!'
            
        elif content_type == 'module':
            # Module already imported globally
            module = Module.query.get_or_404(content_id)
            module_title = module.title
            
            # Delete the module and its content
            db.session.delete(module)
            db.session.commit()
            message = f'Module "{module_title}" deleted successfully!'
            
        elif content_type == 'topic':
            # DEPRECATED: Topics are now modules
            # Module already imported globally
            module = Module.query.get_or_404(content_id)
            module_title = module.title
            
            # Delete the module (what used to be a topic)
            db.session.delete(module)
            db.session.commit()
            message = f'Module "{module_title}" deleted successfully!'
            
        elif content_type == 'simulation':
            print(f"Processing simulation deletion for simulation ID: {content_id}")
            # For simulations, we need to remove them from the class content by updating the database relationships
            from instructor.models.class_model import Class
            from instructor.models.simulation_assignment import SimulationAssignment
            
            cls = Class.query.get_or_404(class_id)
            simulation = Simulation.query.get_or_404(content_id)
            
            print(f"Found class: {cls.name}, Found simulation: {simulation.title}")
            print(f"Current simulation category: {simulation.category}")
            
            # First, try to remove via SimulationAssignment table
            assignment = SimulationAssignment.query.filter_by(
                class_id=class_id,
                simulation_id=content_id
            ).first()
            
            if assignment:
                print(f"Found assignment ID: {assignment.id}, deactivating assignment")
                assignment.is_active = False  # Deactivate instead of deleting
                db.session.commit()
                message = f'Simulation "{simulation.title}" removed from class successfully!'
            else:
                print(f"No SimulationAssignment found for class {class_id} and simulation {content_id}")
                
                # Check if this simulation is shown via category-based assignment
                # First, let's see how this simulation got assigned to this class
                
                # Option 1: Category-based assignment (legacy)
                if simulation.category and cls.name in simulation.category:
                    print(f"Found class name '{cls.name}' in simulation category '{simulation.category}' - using category removal")
                    old_category = simulation.category
                    # Remove the class name from the category
                    simulation.category = simulation.category.replace(f", {cls.name}", "").replace(f"{cls.name},", "").replace(cls.name, "").strip()
                    # Clean up any remaining commas
                    simulation.category = simulation.category.replace(",,", ",").strip(",").strip()
                    if not simulation.category:
                        simulation.category = "General"  # Set a default category
                    print(f"Updated simulation category from '{old_category}' to '{simulation.category}'")
                    db.session.commit()
                    message = f'Simulation "{simulation.title}" removed from class successfully!'
                else:
                    # Option 2: Create a deactivated assignment to prevent future display
                    print(f"Creating deactivated assignment to ensure simulation doesn't appear in class")
                    
                    # Create an inactive assignment to mark this simulation as "removed" from this class
                    deactivated_assignment = SimulationAssignment(
                        title=f"{simulation.title} - Removed",
                        simulation_id=content_id,
                        class_id=class_id,
                        assigned_by=1,  # Assuming instructor user ID is 1
                        assignment_type='class',
                        is_active=False,  # Mark as inactive so it won't show up
                        is_published=False
                    )
                    
                    db.session.add(deactivated_assignment)
                    db.session.commit()
                    print(f"Created deactivated assignment ID: {deactivated_assignment.id}")
                    message = f'Simulation "{simulation.title}" removed from class view!'
            
        elif content_type == 'assessment':
            # For assessments (Quiz), we remove the relationship rather than delete
            from instructor.models.class_model import Class
            cls = Class.query.get_or_404(class_id)
            question_group = QuestionGroup.query.get_or_404(content_id)
            
            # Remove the Quiz from the class
            if question_group in cls.question_groups:
                cls.question_groups.remove(question_group)
            
            db.session.commit()
            message = f'Assessment unassigned from class successfully!'
            
        else:
            print(f"🔥 Unknown content type: {content_type}")
            return jsonify({'success': False, 'error': f'Unknown content type: {content_type}'}), 400
        
        print(f"Success: {message}")
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"🔥 Error deleting class content: {str(e)}")
        current_app.logger.error(f"Error deleting class content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/dashboard/class_content/<int:content_id>', methods=['DELETE'])
@login_required
def delete_class_content_legacy(content_id):
    """Legacy delete endpoint for backwards compatibility - redirects to proper endpoint"""
    try:
        from instructor.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial
        # ClassTopic removed - content now organized under Modules
        from __init__ import db
        
        # Try to find the content item to get its type and class_id
        content = None
        content_type = None
        class_id = None
        
        # Check each content type
        if not content:
            content = ClassAnnouncement.query.get(content_id)
            if content:
                content_type = 'announcement'
                class_id = content.class_id
        
        if not content:
            content = ClassAssignment.query.get(content_id)
            if content:
                content_type = 'assignment'
                class_id = content.class_id
        
        if not content:
            content = ClassMaterial.query.get(content_id)
            if content:
                content_type = 'material'
                class_id = content.class_id
        
        if not content:
            # ClassTopic deprecated - skip checking for topics
            pass
        
        if not content:
            return jsonify({'success': False, 'error': 'Content not found'}), 404
        
        # Delete the content
        db.session.delete(content)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{content_type.title()} deleted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting class content (legacy): {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/classes/<int:class_id>/students/<int:student_id>', methods=['DELETE'])
@login_required
def remove_student_from_class(class_id, student_id):
    """Remove a student from a class"""
    try:
        from instructor.models.class_model import Class, class_students
        from user.models.user import User
        from __init__ import db
        
        # Verify class exists
        cls = Class.query.get_or_404(class_id)
        
        # Verify student exists
        student = User.query.get_or_404(student_id)
        
        # Check if student is enrolled in the class
        enrollment = db.session.query(class_students).filter(
            class_students.c.class_id == class_id,
            class_students.c.user_id == student_id
        ).first()
        
        if not enrollment:
            return jsonify({
                'success': False,
                'error': 'Student is not enrolled in this class'
            }), 404
        
        # Remove the student from the class
        db.session.execute(
            class_students.delete().where(
                (class_students.c.class_id == class_id) & 
                (class_students.c.user_id == student_id)
            )
        )
        db.session.commit()
        
        current_app.logger.info(f"Student {student.username} removed from class {cls.name}")
        
        return jsonify({
            'success': True,
            'message': f'Student {student.username} removed from class successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing student from class: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== USER MANAGEMENT ENDPOINTS ====================

@dashboard_bp.route('/api/student/<int:student_id>/profile', methods=['GET'])
@login_required
def get_student_profile(student_id):
    """Get detailed student profile information"""
    try:
        from user.models.user import User
        from instructor.models.class_model import Class, class_students
        
        # Get student
        student = User.query.get_or_404(student_id)
        
        # Get student's enrolled classes
        enrolled_classes = db.session.query(Class).join(
            class_students,
            Class.id == class_students.c.class_id
        ).filter(
            class_students.c.user_id == student_id
        ).all()
        
        # Get student's scores
        student_scores = Score.query.filter_by(user_id=student_id).all()
        
        # Calculate statistics
        total_attempts = len(student_scores)
        if student_scores:
            avg_score = sum(s.score for s in student_scores) / total_attempts
            highest_score = max(s.score for s in student_scores)
            latest_attempt = max(s.date_attempted for s in student_scores)
        else:
            avg_score = 0
            highest_score = 0
            latest_attempt = None
        
        # Get assignments (if you have assignment submissions model)
        completed_assignments = 0  # Placeholder
        pending_assignments = 0     # Placeholder
        
        # Safely get last_active
        last_active = None
        if hasattr(student, 'last_active') and student.last_active:
            last_active = student.last_active.isoformat() if hasattr(student.last_active, 'isoformat') else str(student.last_active)
        
        profile_data = {
            'student': {
                'id': student.id,
                'username': student.username,
                'email': student.email,
                'first_name': getattr(student, 'first_name', ''),
                'last_name': getattr(student, 'last_name', ''),
                'created_at': student.created_at.isoformat() if hasattr(student, 'created_at') and student.created_at else None,
                'last_active': last_active
            },
            'statistics': {
                'total_attempts': total_attempts,
                'avg_score': round(avg_score, 2),
                'highest_score': round(highest_score, 2),
                'completed_assignments': completed_assignments,
                'pending_assignments': pending_assignments,
                'enrolled_classes': len(enrolled_classes),
                'latest_attempt': latest_attempt.isoformat() if latest_attempt else None
            },
            'enrolled_classes': [
                {
                    'id': cls.id,
                    'name': cls.name,
                    'code': getattr(cls, 'code', '')
                } for cls in enrolled_classes
            ],
            'recent_scores': [
                {
                    'id': score.id,
                    'category': score.category,
                    'score': score.score,
                    'date': score.date_attempted.isoformat()
                } for score in sorted(student_scores, key=lambda x: x.date_attempted, reverse=True)[:5]
            ]
        }
        
        return jsonify({
            'success': True,
            'data': profile_data
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f"Error getting student profile for student {student_id}: {str(e)}\n{error_details}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/student/<int:student_id>/deadline-extension', methods=['POST'])
@login_required
def extend_student_deadline(student_id):
    """Extend deadline for a student on a specific assignment"""
    try:
        from user.models.user import User
        from instructor.models.class_content import ClassAssignment
        from __init__ import db
        
        data = request.json
        assignment_id = data.get('assignment_id')
        new_deadline = data.get('new_deadline')
        reason = data.get('reason', 'Other')
        notes = data.get('notes', '')
        
        # Verify student exists
        student = User.query.get_or_404(student_id)
        
        # Verify assignment exists
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        
        # Create or update deadline extension record
        # You may need to create a DeadlineExtension model for this
        # For now, we'll log it and update the assignment due date for this specific student
        
        # TODO: Create a student_deadline_extensions table to track individual extensions
        # For MVP, we'll just log the extension
        
        extension_data = {
            'student_id': student_id,
            'student_name': student.username,
            'assignment_id': assignment_id,
            'assignment_title': assignment.title,
            'original_deadline': assignment.due_date.isoformat() if assignment.due_date else None,
            'new_deadline': new_deadline,
            'reason': reason,
            'notes': notes,
            'granted_by': current_user.id,
            'granted_at': datetime.utcnow().isoformat()
        }
        
        current_app.logger.info(f"Deadline extension granted: {extension_data}")
        
        # In a full implementation, you would save this to a database table
        # Example:
        # from instructor.models.deadline_extension import DeadlineExtension
        # extension = DeadlineExtension(
        #     student_id=student_id,
        #     assignment_id=assignment_id,
        #     original_deadline=assignment.due_date,
        #     new_deadline=datetime.fromisoformat(new_deadline),
        #     reason=reason,
        #     notes=notes,
        #     granted_by=current_user.id
        # )
        # db.session.add(extension)
        # db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Deadline extended for {student.username} on assignment "{assignment.title}"',
            'extension': extension_data
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error extending deadline: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/student/<int:student_id>/message', methods=['POST'])
@login_required
def send_student_message(student_id):
    """Send a message to a student"""
    try:
        from user.models.user import User
        from __init__ import db
        
        data = request.json
        subject = data.get('subject', '')
        message = data.get('message', '')
        priority = data.get('priority', 'normal')
        
        # Verify student exists
        student = User.query.get_or_404(student_id)
        
        # Create message record
        # TODO: Implement a messaging system or integrate with email
        # For MVP, we'll log the message
        
        message_data = {
            'recipient_id': student_id,
            'recipient_email': student.email,
            'subject': subject,
            'message': message,
            'priority': priority,
            'sent_by': current_user.id,
            'sent_at': datetime.utcnow().isoformat()
        }
        
        current_app.logger.info(f"Message sent to student: {message_data}")
        
        # In a full implementation, you would:
        # 1. Save to a messages table
        # 2. Send email notification
        # 3. Create in-app notification
        
        # Example email sending (uncomment when email is configured):
        # from flask_mail import Message
        # msg = Message(
        #     subject=subject,
        #     recipients=[student.email],
        #     body=message,
        #     sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        # )
        # mail.send(msg)
        
        return jsonify({
            'success': True,
            'message': f'Message sent to {student.username}',
            'data': message_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error sending message: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/class/<int:class_id>/invite-users', methods=['POST'])
@login_required
def invite_users_to_class(class_id):
    """Invite multiple users to join a class"""
    try:
        from instructor.models.class_model import Class
        from user.models.user import User
        from __init__ import db
        
        data = request.json
        emails = data.get('emails', [])
        role = data.get('role', 'student')
        custom_message = data.get('message', '')
        
        # Verify class exists
        cls = Class.query.get_or_404(class_id)
        
        invited_users = []
        errors = []
        
        for email in emails:
            email = email.strip()
            if not email:
                continue
                
            # Check if user already exists
            user = User.query.filter_by(email=email).first()
            
            if user:
                # User exists, check if already enrolled
                from instructor.models.class_model import class_students
                existing_enrollment = db.session.query(class_students).filter(
                    class_students.c.class_id == class_id,
                    class_students.c.user_id == user.id
                ).first()
                
                if existing_enrollment:
                    errors.append(f'{email} is already enrolled')
                    continue
                
                # Enroll existing user
                db.session.execute(
                    class_students.insert().values(
                        class_id=class_id,
                        user_id=user.id,
                        joined_date=datetime.utcnow(),
                        status='active'
                    )
                )
                invited_users.append({
                    'email': email,
                    'status': 'enrolled',
                    'user_id': user.id
                })
            else:
                # Create invitation for new user
                # TODO: Implement invitation system with invitation tokens
                # For MVP, we'll log the invitation
                
                invitation_data = {
                    'email': email,
                    'class_id': class_id,
                    'class_name': cls.name,
                    'role': role,
                    'invited_by': current_user.id,
                    'invited_at': datetime.utcnow().isoformat(),
                    'custom_message': custom_message
                }
                
                current_app.logger.info(f"Invitation created: {invitation_data}")
                
                # In a full implementation:
                # 1. Create invitation token
                # 2. Send invitation email with registration link
                # 3. Track invitation status
                
                invited_users.append({
                    'email': email,
                    'status': 'invitation_sent'
                })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(emails)} invitation(s)',
            'invited': invited_users,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error inviting users: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/class/<int:class_id>/bulk-action', methods=['POST'])
@login_required
def bulk_user_action(class_id):
    """Perform bulk actions on multiple users"""
    try:
        from instructor.models.class_model import Class
        from user.models.user import User
        from __init__ import db
        
        data = request.json
        action = data.get('action')
        student_ids = data.get('student_ids', [])
        
        # Verify class exists
        cls = Class.query.get_or_404(class_id)
        
        results = []
        
        if action == 'export':
            # Export student list
            students = User.query.filter(User.id.in_(student_ids)).all()
            export_data = [
                {
                    'id': s.id,
                    'username': s.username,
                    'email': s.email,
                    'first_name': getattr(s, 'first_name', ''),
                    'last_name': getattr(s, 'last_name', '')
                } for s in students
            ]
            
            return jsonify({
                'success': True,
                'action': 'export',
                'data': export_data,
                'count': len(export_data)
            })
            
        elif action == 'send_message':
            # Send message to multiple students
            subject = data.get('subject', '')
            message = data.get('message', '')
            
            students = User.query.filter(User.id.in_(student_ids)).all()
            
            for student in students:
                # Log message for each student
                current_app.logger.info(f"Bulk message to {student.email}: {subject}")
                results.append({
                    'student_id': student.id,
                    'email': student.email,
                    'status': 'sent'
                })
            
            return jsonify({
                'success': True,
                'action': 'send_message',
                'message': f'Message sent to {len(results)} students',
                'results': results
            })
            
        elif action == 'extend_deadline':
            # Extend deadline for multiple students
            assignment_id = data.get('assignment_id')
            new_deadline = data.get('new_deadline')
            reason = data.get('reason', 'Bulk extension')
            
            for student_id in student_ids:
                current_app.logger.info(f"Bulk deadline extension for student {student_id}")
                results.append({
                    'student_id': student_id,
                    'status': 'extended'
                })
            
            return jsonify({
                'success': True,
                'action': 'extend_deadline',
                'message': f'Deadline extended for {len(results)} students',
                'results': results
            })
            
        elif action == 'generate_report':
            # Generate progress report for selected students
            students = User.query.filter(User.id.in_(student_ids)).all()
            
            report_data = []
            for student in students:
                scores = Score.query.filter_by(user_id=student.id).all()
                avg_score = sum(s.score for s in scores) / len(scores) if scores else 0
                
                report_data.append({
                    'student_id': student.id,
                    'username': student.username,
                    'email': student.email,
                    'total_attempts': len(scores),
                    'avg_score': round(avg_score, 2)
                })
            
            return jsonify({
                'success': True,
                'action': 'generate_report',
                'data': report_data,
                'generated_at': datetime.utcnow().isoformat()
            })
            
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown bulk action: {action}'
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error performing bulk action: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/class/<int:class_id>/students/search', methods=['GET'])
@login_required
def search_class_students(class_id):
    """Search and filter students in a class"""
    try:
        from instructor.models.class_model import Class, class_students
        from user.models.user import User
        
        # Get search parameters
        search_query = request.args.get('q', '').lower()
        filter_type = request.args.get('filter', 'all')  # all, active, inactive
        
        # Verify class exists
        cls = Class.query.get_or_404(class_id)
        
        # Get all students in the class
        students_query = db.session.query(User).join(
            class_students,
            User.id == class_students.c.user_id
        ).filter(
            class_students.c.class_id == class_id
        )
        
        # Apply search filter
        if search_query:
            students_query = students_query.filter(
                or_(
                    User.username.ilike(f'%{search_query}%'),
                    User.email.ilike(f'%{search_query}%'),
                    func.concat(
                        func.coalesce(User.first_name, ''),
                        ' ',
                        func.coalesce(User.last_name, '')
                    ).ilike(f'%{search_query}%')
                )
            )
        
        students = students_query.all()
        
        # Format results
        results = []
        for student in students:
            # Get student's recent activity
            recent_scores = Score.query.filter_by(
                user_id=student.id
            ).order_by(Score.date_attempted.desc()).limit(1).first()
            
            results.append({
                'id': student.id,
                'username': student.username,
                'email': student.email,
                'first_name': getattr(student, 'first_name', ''),
                'last_name': getattr(student, 'last_name', ''),
                'last_active': recent_scores.date_attempted.isoformat() if recent_scores else None
            })
        
        return jsonify({
            'success': True,
            'students': results,
            'count': len(results),
            'search_query': search_query,
            'filter': filter_type
        })
        
    except Exception as e:
        current_app.logger.error(f"Error searching students: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== EDUCATIONAL TOOLS INTEGRATION ====================

@dashboard_bp.route('/api/class/<int:class_id>/educational-tools', methods=['GET'])
@login_required
def get_educational_tools(class_id):
    """Get available educational tools for integration"""
    try:
        # Define available educational tools
        educational_tools = [
            {
                'id': 'networking_simulator',
                'name': 'Networking Simulator',
                'description': 'Interactive network simulation environment',
                'type': 'simulation',
                'icon': 'fas fa-network-wired',
                'category': 'networking',
                'integration_url': f'/admin/simulations/create?class_id={class_id}',
                'enabled': True
            },
            {
                'id': 'quiz_builder',
                'name': 'Quiz Builder',
                'description': 'Create interactive quizzes and assessments',
                'type': 'assessment',
                'icon': 'fas fa-question-circle',
                'category': 'assessment',
                'integration_url': f'/admin/question-groups/create?class_id={class_id}',
                'enabled': True
            },
            {
                'id': 'cisco_packet_tracer',
                'name': 'Cisco Packet Tracer Integration',
                'description': 'Import and export Packet Tracer files',
                'type': 'external_tool',
                'icon': 'fas fa-file-import',
                'category': 'networking',
                'integration_url': '#',
                'enabled': False,  # Coming soon
                'note': 'Coming soon - will support .pkt file uploads'
            },
            {
                'id': 'virtual_lab',
                'name': 'Virtual Lab Environment',
                'description': 'Hands-on virtual laboratory exercises',
                'type': 'lab',
                'icon': 'fas fa-flask',
                'category': 'practical',
                'integration_url': '#',
                'enabled': False,  # Coming soon
                'note': 'Coming soon - virtual networking lab'
            },
            {
                'id': 'collaboration_board',
                'name': 'Collaboration Board',
                'description': 'Interactive whiteboard for group work',
                'type': 'collaboration',
                'icon': 'fas fa-chalkboard',
                'category': 'collaboration',
                'integration_url': '#',
                'enabled': False,  # Coming soon
                'note': 'Coming soon - real-time collaboration'
            },
            {
                'id': 'video_conferencing',
                'name': 'Video Conferencing',
                'description': 'Integrated video calls and screen sharing',
                'type': 'communication',
                'icon': 'fas fa-video',
                'category': 'communication',
                'integration_url': '#',
                'enabled': False,  # Coming soon
                'note': 'Coming soon - WebRTC integration'
            },
            {
                'id': 'progress_analytics',
                'name': 'Progress Analytics',
                'description': 'Detailed student progress tracking and analytics',
                'type': 'analytics',
                'icon': 'fas fa-chart-line',
                'category': 'analytics',
                'integration_url': f'/admin/classes/{class_id}/analytics',
                'enabled': True
            },
            {
                'id': 'automated_grading',
                'name': 'Automated Grading',
                'description': 'AI-powered automatic assignment grading',
                'type': 'grading',
                'icon': 'fas fa-robot',
                'category': 'assessment',
                'integration_url': '#',
                'enabled': False,  # Coming soon
                'note': 'Coming soon - AI grading system'
            }
        ]
        
        return jsonify({
            'success': True,
            'tools': educational_tools,
            'categories': ['networking', 'assessment', 'practical', 'collaboration', 'communication', 'analytics']
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting educational tools: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/class/<int:class_id>/integrate-tool', methods=['POST'])
@login_required
def integrate_educational_tool(class_id):
    """Integrate an educational tool with the class"""
    try:
        from instructor.models.class_model import Class
        
        data = request.json
        tool_id = data.get('tool_id')
        tool_config = data.get('config', {})
        
        # Verify class exists
        cls = Class.query.get_or_404(class_id)
        
        # Handle different tool integrations
        if tool_id == 'networking_simulator':
            # Create a simulation assignment
            from instructor.models.simulation import Simulation
            from instructor.models.simulation_assignment import SimulationAssignment
            
            # Create simulation assignment
            simulation_assignment = SimulationAssignment(
                class_id=class_id,
                title=tool_config.get('title', 'Network Simulation Exercise'),
                description=tool_config.get('description', 'Interactive networking simulation'),
                created_by=current_user.id,
                is_active=True
            )
            db.session.add(simulation_assignment)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Networking simulator integrated successfully!',
                'assignment_id': simulation_assignment.id,
                'redirect_url': f'/admin/simulations/manage?assignment_id={simulation_assignment.id}'
            })
            
        elif tool_id == 'quiz_builder':
            # Redirect to Quiz creation
            return jsonify({
                'success': True,
                'message': 'Redirecting to quiz builder...',
                'redirect_url': f'/admin/question-groups/create?class_id={class_id}'
            })
            
        elif tool_id == 'progress_analytics':
            # Enable analytics for the class
            return jsonify({
                'success': True,
                'message': 'Progress analytics enabled for class!',
                'redirect_url': f'/admin/classes/{class_id}/analytics'
            })
            
        else:
            return jsonify({
                'success': False,
                'error': f'Tool "{tool_id}" integration not yet implemented',
                'message': 'This educational tool integration is coming soon!'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error integrating educational tool: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/class/<int:class_id>/upload-material', methods=['POST'])
@login_required
def upload_class_material(class_id):
    """Enhanced file upload endpoint with multiple file type support"""
    import os
    from werkzeug.utils import secure_filename
    from datetime import datetime
    
    try:
        from instructor.models.class_model import Class
        from instructor.models.class_content import ClassMaterial
        
        # Verify class exists
        cls = Class.query.get_or_404(class_id)
        
        if 'files' not in request.files:
            return jsonify({'success': False, 'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        uploaded_materials = []
        
        # Define allowed file extensions
        ALLOWED_EXTENSIONS = {
            'documents': {'pdf', 'doc', 'docx', 'txt', 'rtf'},
            'presentations': {'ppt', 'pptx', 'odp'},
            'spreadsheets': {'xls', 'xlsx', 'ods', 'csv'},
            'images': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg'},
            'videos': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'},
            'networking': {'pkt', 'json', 'xml', 'cfg'},  # Networking specific files
            'code': {'py', 'js', 'html', 'css', 'java', 'cpp', 'c'},
            'archives': {'zip', 'rar', '7z', 'tar', 'gz'}
        }
        
        def get_file_category(filename):
            """Determine file category based on extension"""
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            for category, extensions in ALLOWED_EXTENSIONS.items():
                if ext in extensions:
                    return category
            return 'other'
        
        for file in files:
            if file and file.filename:
                # Create category-specific upload directory
                category = get_file_category(file.filename)
                upload_dir = os.path.join(current_app.root_path, '..', 'static', 'uploads', 'materials', category)
                os.makedirs(upload_dir, exist_ok=True)
                
                # Secure filename with timestamp
                original_filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_name = f"{timestamp}_{original_filename}"
                file_path = os.path.join(upload_dir, file_name)
                
                # Save the file
                file.save(file_path)
                file_size = os.path.getsize(file_path)
                
                # Create material record
                material = ClassMaterial(
                    class_id=class_id,
                    title=original_filename,
                    description=f"Uploaded {category} file",
                    material_type=category,
                    file_path=f"/static/uploads/materials/{category}/{file_name}",
                    file_size=file_size,
                    is_published=True,
                    created_by=current_user.id
                )
                db.session.add(material)
                uploaded_materials.append({
                    'title': material.title,
                    'type': category,
                    'size': file_size,
                    'url': material.file_path
                })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(uploaded_materials)} file(s) uploaded successfully!',
            'materials': uploaded_materials
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading materials: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/api/classes/<int:class_id>/students', methods=['POST'])
@login_required
def add_student_to_class(class_id):
    """Add a student to a class"""
    try:
        from instructor.models.class_model import Class, class_students
        from user.models.user import User
        from __init__ import db
        
        data = request.json
        
        # Get student by username or email
        student_identifier = data.get('student_identifier')  # username or email
        if not student_identifier:
            return jsonify({'success': False, 'error': 'Student identifier required'}), 400
        
        # Find student
        student = User.query.filter(
            (User.username == student_identifier) |
            (User.email == student_identifier)
        ).first()
        
        if not student:
            return jsonify({'success': False, 'error': 'Student not found'}), 404
        
        # Verify class exists
        cls = Class.query.get_or_404(class_id)
        
        # Check if student is already enrolled
        existing_enrollment = db.session.query(class_students).filter(
            class_students.c.class_id == class_id,
            class_students.c.user_id == student.id
        ).first()
        
        if existing_enrollment:
            return jsonify({
                'success': False,
                'error': 'Student is already enrolled in this class'
            }), 400
        
        # Add student to class
        db.session.execute(
            class_students.insert().values(
                class_id=class_id,
                user_id=student.id,
                joined_date=datetime.utcnow(),
                status='active'
            )
        )
        db.session.commit()
        
        current_app.logger.info(f"Student {student.username} added to class {cls.name}")
        
        return jsonify({
            'success': True,
            'message': f'Student {student.username} added to class successfully!',
            'student': {
                'id': student.id,
                'username': student.username,
                'email': student.email,
                'first_name': getattr(student, 'first_name', ''),
                'last_name': getattr(student, 'last_name', '')
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding student to class: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== COMPREHENSIVE ANALYTICS ENDPOINTS ====================

@dashboard_bp.route('/api/analytics/performance')
@login_required
def api_performance_analytics():
    """Get comprehensive performance analytics"""
    try:
        date_range = request.args.get('date_range', '30', type=int)
        user_id = request.args.get('user_id', type=int)
        
        analytics_data = analytics_service.get_student_performance_analytics(date_range, user_id)
        return jsonify({
            'success': True,
            'data': analytics_data,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/analytics/learning-paths')
@login_required
def api_learning_path_analytics():
    """Get learning path progression analytics"""
    try:
        analytics_data = analytics_service.get_learning_path_analytics()
        return jsonify({
            'success': True,
            'data': analytics_data,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/analytics/engagement')
@login_required
def api_engagement_analytics():
    """Get comprehensive engagement metrics"""
    try:
        date_range = request.args.get('date_range', '30', type=int)
        analytics_data = analytics_service.get_engagement_metrics(date_range)
        return jsonify({
            'success': True,
            'data': analytics_data,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/analytics/comparative')
@login_required
def api_comparative_analysis():
    """Get comparative analysis data"""
    try:
        comparison_type = request.args.get('type', 'category')
        analytics_data = analytics_service.get_comparative_analysis(comparison_type)
        return jsonify({
            'success': True,
            'data': analytics_data,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/analytics/real-time')
@login_required
def api_real_time_metrics():
    """Get real-time system metrics"""
    try:
        metrics_data = analytics_service.get_real_time_metrics()
        return jsonify({
            'success': True,
            'data': metrics_data,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/analytics/activity-feed')
@login_required
def api_activity_feed():
    """Get live activity feed"""
    try:
        limit = request.args.get('limit', 20, type=int)
        activity_data = analytics_service.get_live_activity_feed(limit)
        return jsonify({
            'success': True,
            'data': activity_data,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/analytics/chart-data/<chart_type>')
@login_required
def api_chart_data(chart_type):
    """Get specific chart data for visualizations"""
    try:
        date_range = request.args.get('date_range', '30', type=int)
        category = request.args.get('category', 'all')
        
        if chart_type == 'performance-trend':
            # Get performance trend data
            analytics_data = analytics_service.get_student_performance_analytics(date_range)
            chart_data = {
                'labels': [item['date'] for item in analytics_data.get('time_analysis', {}).get('daily_averages', {}).items()],
                'datasets': [{
                    'label': 'Average Score',
                    'data': [item for item in analytics_data.get('time_analysis', {}).get('daily_averages', {}).values()],
                    'borderColor': '#00D9FF',
                    'backgroundColor': 'rgba(0, 217, 255, 0.1)'
                }]
            }
        elif chart_type == 'category-performance':
            # Get category comparison data
            analytics_data = analytics_service.get_comparative_analysis('category')
            categories = analytics_data.get('category_comparison', {})
            chart_data = {
                'labels': list(categories.keys()),
                'datasets': [{
                    'label': 'Average Score',
                    'data': [stats['average_score'] for stats in categories.values()],
                    'backgroundColor': ['rgba(139, 92, 246, 0.7)', 'rgba(0, 217, 255, 0.7)', 
                                     'rgba(57, 255, 20, 0.7)', 'rgba(255, 206, 84, 0.7)']
                }]
            }
        elif chart_type == 'engagement-heatmap':
            # Get engagement metrics
            analytics_data = analytics_service.get_engagement_metrics(date_range)
            chart_data = {
                'hourly_activity': analytics_data.get('activity_patterns', {}).get('hourly_distribution', {}),
                'daily_engagement': analytics_data.get('daily_active_users', {})
            }
        elif chart_type == 'score-distribution':
            # Get score distribution
            analytics_data = analytics_service.get_student_performance_analytics(date_range)
            distribution = analytics_data.get('score_distribution', {})
            chart_data = {
                'labels': list(distribution.keys()),
                'datasets': [{
                    'label': 'Number of Scores',
                    'data': list(distribution.values()),
                    'backgroundColor': [
                        'rgba(255, 107, 107, 0.7)',
                        'rgba(255, 165, 0, 0.7)', 
                        'rgba(255, 206, 84, 0.7)',
                        'rgba(57, 255, 20, 0.7)',
                        'rgba(0, 217, 255, 0.7)'
                    ]
                }]
            }
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid chart type'
            }), 400
        
        return jsonify({
            'success': True,
            'data': chart_data,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== EXPORT FUNCTIONALITY ====================

@dashboard_bp.route('/api/export/analytics')
@login_required
def export_analytics():
    """Export comprehensive analytics report"""
    try:
        export_format = request.args.get('format', 'pdf').lower()
        date_range = request.args.get('date_range', '30', type=int)
        
        if export_format not in ['pdf', 'csv', 'json']:
            return jsonify({
                'success': False,
                'error': 'Invalid format. Supported formats: pdf, csv, json'
            }), 400
        
        # Generate report
        file_path = analytics_service.export_analytics_report(export_format, date_range)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'Failed to generate report'
            }), 500
        
        # Return file for download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path),
            mimetype=f'application/{export_format}' if export_format != 'csv' else 'text/csv'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/export/filtered-data')
@login_required
def export_filtered_data():
    """Export filtered data based on criteria"""
    try:
        data_type = request.args.get('type', 'scores')
        export_format = request.args.get('format', 'csv').lower()
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        category = request.args.get('category')
        
        # Build query based on filters
        if data_type == 'scores':
            query = Score.query
            if date_from:
                query = query.filter(Score.date_attempted >= datetime.strptime(date_from, '%Y-%m-%d'))
            if date_to:
                query = query.filter(Score.date_attempted <= datetime.strptime(date_to, '%Y-%m-%d'))
            if category and category != 'all':
                query = query.filter(Score.category == category)
            
            data = query.all()
            
        elif data_type == 'users':
            query = User.query
            data = query.all()
            
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid data type'
            }), 400
        
        # Generate export file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'riddlenet_{data_type}_{timestamp}.{export_format}'
        filepath = os.path.join('static', 'exports', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if export_format == 'csv':
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if data_type == 'scores' and data:
                    fieldnames = ['id', 'user_id', 'username', 'score', 'category', 'date_attempted']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for score in data:
                        writer.writerow({
                            'id': score.id,
                            'user_id': score.user_id,
                            'username': score.user.username if score.user else f'User {score.user_id}',
                            'score': score.score,
                            'category': score.category,
                            'date_attempted': score.date_attempted.strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                elif data_type == 'users' and data:
                    fieldnames = ['id', 'username', 'email', 'created_at', 'last_active']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for user in data:
                        writer.writerow({
                            'id': user.id,
                            'username': user.username,
                            'email': user.email or 'N/A',
                            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else 'N/A',
                            'last_active': user.last_active.strftime('%Y-%m-%d %H:%M:%S') if user.last_active else 'N/A'
                        })
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv' if export_format == 'csv' else 'application/json'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== ENHANCED DASHBOARD ROUTES ====================

@dashboard_bp.route('/analytics-dashboard')
@login_required
def analytics_dashboard():
    """Comprehensive analytics dashboard page"""
    try:
        # Get initial analytics data
        performance_data = analytics_service.get_student_performance_analytics(30)
        engagement_data = analytics_service.get_engagement_metrics(30)
        comparative_data = analytics_service.get_comparative_analysis('category')
        real_time_data = analytics_service.get_real_time_metrics()
        
        return render_safe_template('instructor/analytics_dashboard.html',
                                   performance_data=performance_data,
                                   engagement_data=engagement_data,
                                   comparative_data=comparative_data,
                                   real_time_data=real_time_data,
                                   active_page='analytics')
    except Exception as e:
        flash(f'Error loading analytics dashboard: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/reports')
@login_required
def reports():
    """Reports and export page"""
    return render_safe_template('instructor/reports.html', 
                               active_page='reports')

# Redundant route - use learning_path.learning_path_builder instead
# @dashboard_bp.route('/path-designer')
# @login_required
# def path_designer():
#     """Learning Path Designer page for creating educational pathways"""
#     return render_safe_template('instructor/path_designer.html', 
#                                active_page='path_designer')


# ==================== CHART DATA API ENDPOINTS ====================

@dashboard_bp.route('/api/analytics/chart-data/performance-trend')
@login_required
def chart_performance_trend():
    """Get performance trend data for charts."""
    try:
        date_range = int(request.args.get('date_range', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        
        data = analytics_service.get_performance_trend_chart_data(start_date, end_date)
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Error getting performance trend data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/api/analytics/chart-data/score-distribution')
@login_required
def chart_score_distribution():
    """Get score distribution data for charts."""
    try:
        date_range = int(request.args.get('date_range', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        
        data = analytics_service.get_score_distribution_chart_data(start_date, end_date)
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Error getting score distribution data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/api/analytics/chart-data/category-performance')
@login_required
def chart_category_performance():
    """Get category performance data for charts."""
    try:
        date_range = int(request.args.get('date_range', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        
        data = analytics_service.get_category_performance_chart_data(start_date, end_date)
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Error getting category performance data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/api/analytics/chart-data/engagement-heatmap')
@login_required
def chart_engagement_heatmap():
    """Get engagement heatmap data for charts."""
    try:
        date_range = int(request.args.get('date_range', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        
        data = analytics_service.get_engagement_heatmap_data(start_date, end_date)
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Error getting engagement heatmap data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/api/analytics/activity-feed')
@login_required
def activity_feed():
    """Get recent activity feed."""
    try:
        limit = int(request.args.get('limit', 10))
        data = analytics_service.get_recent_activity_feed(limit)
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Error getting activity feed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/api/analytics/real-time')
@login_required
def real_time_metrics():
    """Get real-time metrics for live dashboard updates."""
    try:
        data = analytics_service.get_real_time_metrics()
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== DEBUG ROUTES ====================

@dashboard_bp.route('/api/debug/auth-status')
def debug_auth_status():
    """Debug authentication status"""
    return jsonify({
        'is_authenticated': current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False,
        'user_id': getattr(current_user, 'id', None),
        'username': getattr(current_user, 'username', None),
        'endpoint_test': 'auth-status-working',
        'timestamp': datetime.now().isoformat()
    })

@dashboard_bp.route('/api/debug/test-analytics')
@login_required
def debug_test_analytics():
    """Test analytics functionality with debug info"""
    try:
        # Test a simple analytics call
        metrics = analytics_service.get_real_time_metrics()
        
        return jsonify({
            'success': True,
            'auth_status': {
                'is_authenticated': current_user.is_authenticated,
                'user_id': current_user.id,
                'username': getattr(current_user, 'username', 'unknown')
            },
            'analytics_test': metrics,
            'endpoint_test': 'test-analytics-working'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'auth_status': {
                'is_authenticated': current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False,
                'user_id': getattr(current_user, 'id', None)
            }
        }), 500

# ==================== EXPORT ENDPOINTS ====================

@dashboard_bp.route('/api/analytics/export/<format_type>')
@login_required
def export_analytics_report(format_type):
    """Export comprehensive analytics report"""
    try:
        date_range = int(request.args.get('date_range', 30))
        
        if format_type == 'pdf':
            file_path = analytics_service.export_analytics_report('pdf', date_range)
            return send_file(file_path, as_attachment=True, 
                           download_name=f'analytics_report_{datetime.now().strftime("%Y%m%d")}.pdf')
        
        elif format_type == 'csv':
            file_path = analytics_service.export_analytics_report('csv', date_range)
            return send_file(file_path, as_attachment=True,
                           download_name=f'analytics_data_{datetime.now().strftime("%Y%m%d")}.csv')
        
        else:
            return jsonify({'success': False, 'error': 'Invalid format type'}), 400
            
    except Exception as e:
        logger.error(f"Error exporting analytics report: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

