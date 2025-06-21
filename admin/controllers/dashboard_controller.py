from flask import Blueprint, redirect, url_for, flash, jsonify, request, render_template
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, extract, or_
import json
from flask_login import login_required, current_user

# Import models
from __init__ import db  # Use the main app db instance
from user.models.user import User  # Import the regular User model
from user.models.score import Score  # Import the regular Score model
from admin.models.question import Question
from admin.models.essay_response import EssayResponse
from admin.models.activity_log import ActivityLog
from utils.render_utils import render_safe_template

# Create dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/admin')

@dashboard_bp.route('/')
@login_required
def index():    # Get basic stats - ensure we're using the correct tables
    total_users = User.query.count()
    total_scores = Score.query.count()
    
    # Handle case where questions might be in either question or questions table
    # We'll detect which one has data and use it
    question_count_main = Question.query.count()
    
    # Get recent scores for dashboard table
    recent_scores = Score.query.order_by(desc(Score.date_attempted)).limit(10).all()
    
    # Enhanced Score Analytics for Dashboard Overview
    
    # 1. Score distribution data for chart - adjusted based on actual score data
    score_dist = {
        'very_low': Score.query.filter(Score.score < 0.6).count(),  # Less than 20%
        'low': Score.query.filter(and_(Score.score >= 0.6, Score.score < 1.2)).count(),  # 20-40%
        'medium': Score.query.filter(and_(Score.score >= 1.2, Score.score < 1.8)).count(),  # 40-60%
        'high': Score.query.filter(and_(Score.score >= 1.8, Score.score < 2.4)).count(),  # 60-80%
        'very_high': Score.query.filter(Score.score >= 2.4).count()  # 80%+
    }
    
    # 2. Performance trends - last 30 days
    today = datetime.now().date()
    last_30_days = [(today - timedelta(days=i)) for i in range(29, -1, -1)]
    
    # Daily score averages for trend analysis
    daily_performance = []
    for date_obj in last_30_days:
        daily_avg = Score.query.filter(
            func.date(Score.date_attempted) == date_obj
        ).with_entities(func.avg(Score.score)).scalar() or 0
        daily_performance.append({
            'date': date_obj.strftime('%Y-%m-%d'),
            'avg_score': round(float(daily_avg) * 100 / 3, 1) if daily_avg else 0
        })
    
    # 3. User activity data - last 7 days for dashboard
    activity_dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
      # Count active users per day (users who attempted a quiz)
    active_users = []
    for date_str in activity_dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        count = Score.query.filter(
            func.date(Score.date_attempted) == date_obj
        ).with_entities(Score.user_id).distinct().count()
        active_users.append(count)
      # 4. Enhanced category analytics
    categories = ['riddle', 'topology', 'troubleshoot', 'crimping']
    category_analytics = {}
    category_avg = {}
    
    for cat in categories:
        scores = Score.query.filter(Score.category == cat).all()
        if scores:
            score_values = [s.score for s in scores]
            avg_score = sum(score_values) / len(score_values)
            category_analytics[cat] = {
                'avg_score': round(avg_score * 100 / 3, 1),  # Convert to percentage
                'total_attempts': len(scores),
                'unique_users': len(set(s.user_id for s in scores)),
                'highest_score': round(max(score_values) * 100 / 3, 1),
                'improvement_trend': 'up' if len(scores) > 5 else 'stable'  # Simplified trend
            }
            category_avg[cat] = round(avg_score * 100 / 3, 1)  # For template charts
        else:
            category_analytics[cat] = {
                'avg_score': 0, 'total_attempts': 0, 'unique_users': 0, 
                'highest_score': 0, 'improvement_trend': 'no_data'
            }
            category_avg[cat] = 0
    
    # 5. Top performing users (for dashboard overview)
    top_performers = (
        db.session.query(
            User.username,
            func.max(Score.score).label('highest_score'),
            func.avg(Score.score).label('avg_score'),
            func.count(Score.id).label('total_attempts')
        )
        .join(Score)
        .group_by(User.id, User.username)
        .order_by(desc(func.max(Score.score)))
        .limit(5)
        .all()
    )
    
    # 6. Score insights and alerts
    score_insights = {
        'total_this_week': Score.query.filter(
            Score.date_attempted >= (today - timedelta(days=7))
        ).count(),
        'avg_this_week': 0,
        'trend_vs_last_week': 'stable'
    }
    
    # Calculate weekly average
    this_week_scores = Score.query.filter(
        Score.date_attempted >= (today - timedelta(days=7))
    ).all()
    
    if this_week_scores:
        week_avg = sum(s.score for s in this_week_scores) / len(this_week_scores)
        score_insights['avg_this_week'] = round(week_avg * 100 / 3, 1)
    
    # ...existing code for question difficulty, activity logs, etc...
    
    # Question difficulty distribution
    question_difficulty = {
        'easy': EssayResponse.query.filter(EssayResponse.graded_score >= 80).count(),
        'medium': EssayResponse.query.filter(and_(EssayResponse.graded_score >= 60, 
                                                 EssayResponse.graded_score < 80)).count(),
        'hard': EssayResponse.query.filter(EssayResponse.graded_score < 60).count()
    }
    
    if sum(question_difficulty.values()) == 0:
        question_difficulty = {'easy': 2, 'medium': 1, 'hard': 1}
    
    # Recent system activity logs
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
        else:
            essays = EssayResponse.query.order_by(desc(EssayResponse.submission_date)).limit(4).all()
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
    
    # System alerts
    system_alerts = []
    unreviewed_essays = EssayResponse.query.filter_by(is_graded=False).count()
    if unreviewed_essays > 0:
        system_alerts.append({
            'message': f'{unreviewed_essays} unreviewed essay responses require attention',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
      # Low performance alert
    recent_low_scores = Score.query.filter(
        and_(Score.date_attempted >= (today - timedelta(days=7)), Score.score < 1.0)
    ).count()
    if recent_low_scores > 5:
        system_alerts.append({
            'message': f'{recent_low_scores} low scores this week - consider reviewing content difficulty',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_safe_template('admin/dashboard.html',
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
    from admin.models.user import Admin
    
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
    
    # Get admin users from the Admin model
    admins = Admin.query.all()
    
    return render_template('admin/user_management.html', 
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

@dashboard_bp.route('/websocket-panel')
@login_required
def websocket_panel():
    """WebSocket monitoring and real-time panel"""
    return render_safe_template('admin/websocket_panel.html', 
                               active_page='websocket')

@dashboard_bp.route('/simulation-builder')
@login_required
def simulation_builder():
    """Simulation Builder page for creating and editing network simulations"""
    return render_safe_template('admin/simulation_builder.html', 
                               active_page='simulation_builder')

@dashboard_bp.route('/manage-simulations')
@login_required
def manage_simulations():
    """Manage existing simulations page"""
    return render_safe_template('admin/manage_simulations.html', 
                               active_page='manage_simulations')

@dashboard_bp.route('/module-builder')
@login_required
def module_builder():
    """Module Builder page for creating learning modules"""
    return render_safe_template('admin/module_builder.html', 
                               active_page='module_builder')

# Redundant route - use learning_path.learning_path_builder instead
# @dashboard_bp.route('/path-designer')
# @login_required
# def path_designer():
#     """Learning Path Designer page for creating educational pathways"""
#     return render_safe_template('admin/path_designer.html', 
#                                active_page='path_designer')

