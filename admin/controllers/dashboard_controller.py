
from flask import Blueprint, redirect, url_for, flash, jsonify, request, render_template, send_file, current_app
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, extract, or_
import json
import os
import logging
from flask_login import login_required, current_user

# Import models
from __init__ import db  # Use the main app db instance
from user.models.user import User  # Import the regular User model
from user.models.score import Score  # Import the regular Score model
from admin.models.question import Question
from admin.models.essay_response import EssayResponse
from admin.models.activity_log import ActivityLog
from utils.render_utils import render_safe_template

# Import analytics service
from admin.services.analytics_service import AnalyticsService

# Initialize logger
logger = logging.getLogger(__name__)

# Create dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/admin')

# Initialize analytics service
analytics_service = AnalyticsService()

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
        
        # Convert to percentage properly
        if daily_avg >= 0 and daily_avg <= 100:  # Already in percentage
            percentage_avg = round(daily_avg, 1)
        elif daily_avg <= 3:  # 0-3 scale
            percentage_avg = round((daily_avg / 3) * 100, 1)
        else:  # Cap at 100%
            percentage_avg = 100.0
        
        daily_performance.append({
            'date': date_obj.strftime('%Y-%m-%d'),
            'avg_score': percentage_avg
        })    # 3. User activity data - last 7 days for dashboard
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
                'avg_score': avg_percentage,
                'total_attempts': len(scores),
                'unique_users': len(set(s.user_id for s in scores)),
                'highest_score': max_percentage,
                'improvement_trend': 'up' if len(scores) > 5 else 'stable'  # Simplified trend
            }
            category_avg[cat] = avg_percentage  # For template charts
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
        # Convert to percentage properly
        if week_avg >= 0 and week_avg <= 100:  # Already in percentage
            score_insights['avg_this_week'] = round(week_avg, 1)
        elif week_avg <= 3:  # 0-3 scale
            score_insights['avg_this_week'] = round((week_avg / 3) * 100, 1)
        else:  # Cap at 100%
            score_insights['avg_this_week'] = 100.0
    
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
    try:
        from admin.controllers.simulation_controller import SimulationController
        simulation_controller = SimulationController()
        
        # Get only active simulations by default (exclude deleted ones)
        simulations_data = simulation_controller.get_all_simulations(include_inactive=False)
        
        return render_safe_template('admin/manage_simulations.html', 
                                   active_page='manage_simulations',
                                   simulations=simulations_data.get('simulations', []),
                                   total_count=simulations_data.get('total_count', 0))
    except Exception as e:
        current_app.logger.error(f"Error loading manage simulations: {str(e)}")
        return render_safe_template('admin/manage_simulations.html', 
                                   active_page='manage_simulations',
                                   simulations=[],
                                   total_count=0)

@dashboard_bp.route('/module-builder')
@login_required
def module_builder():
    """Module Builder page for creating learning modules"""
    return render_safe_template('admin/module_builder.html', 
                               active_page='module_builder')

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
        
        return render_safe_template('admin/analytics_dashboard.html',
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
    return render_safe_template('admin/reports.html', 
                               active_page='reports')

# Redundant route - use learning_path.learning_path_builder instead
# @dashboard_bp.route('/path-designer')
# @login_required
# def path_designer():
#     """Learning Path Designer page for creating educational pathways"""
#     return render_safe_template('admin/path_designer.html', 
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

