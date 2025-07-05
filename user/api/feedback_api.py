from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from user.models.performance_feedback import PerformanceFeedback, FeedbackSession
from user.models.user import User
from admin.models.user import Admin
from __init__ import db
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json

feedback_api = Blueprint('feedback_api', __name__)

def is_admin():
    """Check if current user is admin"""
    return (hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins') or \
           (hasattr(current_user, 'is_admin') and current_user.is_admin)

@feedback_api.route('/api/feedback/sessions', methods=['GET'])
@login_required
def get_feedback_sessions():
    """Get feedback sessions for current user or all users (if admin)"""
    try:
        # Check if user is admin
        if is_admin():
            # Admin can see all sessions
            sessions = FeedbackSession.query.order_by(desc(FeedbackSession.start_time)).all()
        else:
            # Regular user can only see their own sessions
            sessions = FeedbackSession.query.filter_by(user_id=current_user.id).order_by(
                desc(FeedbackSession.start_time)
            ).all()
        
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@feedback_api.route('/api/feedback/sessions/<session_id>/analytics', methods=['GET'])
@login_required  
def get_session_analytics(session_id):
    """Get detailed analytics for a specific session"""
    try:
        session = FeedbackSession.query.filter_by(session_id=session_id).first()
        
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        # Check permissions
        if not is_admin() and session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        # Get all feedback for this session
        feedback_entries = PerformanceFeedback.query.filter_by(session_id=session_id).order_by(
            PerformanceFeedback.action_timestamp
        ).all()
        
        # Generate analytics
        analytics = {
            'session': session.to_dict(),
            'feedback_timeline': [f.to_dict() for f in feedback_entries],
            'summary': {
                'total_actions': len(feedback_entries),
                'successful_actions': len([f for f in feedback_entries if f.feedback_type == 'success']),
                'failed_actions': len([f for f in feedback_entries if f.feedback_type == 'error']),
                'warnings': len([f for f in feedback_entries if f.feedback_type == 'warning']),
                'hints_used': len([f for f in feedback_entries if f.action_type == 'hint_request']),
                'total_score': sum(f.feedback_score for f in feedback_entries),
                'average_response_time': session.average_response_time
            },
            'action_breakdown': {},
            'performance_trends': []
        }
        
        # Action breakdown
        for feedback in feedback_entries:
            action_type = feedback.action_type
            if action_type not in analytics['action_breakdown']:
                analytics['action_breakdown'][action_type] = {
                    'success': 0, 'error': 0, 'warning': 0, 'total': 0
                }
            analytics['action_breakdown'][action_type][feedback.feedback_type] += 1
            analytics['action_breakdown'][action_type]['total'] += 1
        
        # Performance trends
        cumulative_score = 0
        for feedback in feedback_entries:
            cumulative_score += feedback.feedback_score
            analytics['performance_trends'].append({
                'timestamp': feedback.action_timestamp.isoformat(),
                'cumulative_score': cumulative_score,
                'action_type': feedback.action_type,
                'feedback_type': feedback.feedback_type,
                'progress': feedback.scenario_progress
            })
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@feedback_api.route('/api/feedback/dashboard', methods=['GET'])
@login_required
def get_feedback_dashboard():
    """Get dashboard data for admin monitoring"""
    try:
        if not is_admin():
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        
        # Get time range from query params
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Active sessions
        active_sessions = FeedbackSession.query.filter(
            FeedbackSession.start_time >= start_date,
            FeedbackSession.is_completed == False
        ).count()
        
        # Completed sessions
        completed_sessions = FeedbackSession.query.filter(
            FeedbackSession.start_time >= start_date,
            FeedbackSession.is_completed == True
        ).count()
        
        # Total feedback entries
        total_feedback = PerformanceFeedback.query.filter(
            PerformanceFeedback.action_timestamp >= start_date
        ).count()
        
        # Average session duration
        avg_duration = db.session.query(func.avg(FeedbackSession.total_duration)).filter(
            FeedbackSession.start_time >= start_date,
            FeedbackSession.is_completed == True
        ).scalar() or 0
        
        # Top performing users
        top_users = db.session.query(
            User.username,
            func.avg(FeedbackSession.total_score).label('avg_score'),
            func.count(FeedbackSession.id).label('session_count')
        ).join(FeedbackSession).filter(
            FeedbackSession.start_time >= start_date,
            FeedbackSession.is_completed == True
        ).group_by(User.id).order_by(desc('avg_score')).limit(10).all()
        
        # Most challenging scenarios
        challenging_scenarios = db.session.query(
            FeedbackSession.scenario_id,
            func.avg(FeedbackSession.completion_percentage).label('avg_completion'),
            func.count(FeedbackSession.id).label('attempt_count')
        ).filter(
            FeedbackSession.start_time >= start_date
        ).group_by(FeedbackSession.scenario_id).order_by('avg_completion').limit(10).all()
        
        # Daily activity
        daily_activity = db.session.query(
            func.date(FeedbackSession.start_time).label('date'),
            func.count(FeedbackSession.id).label('sessions'),
            func.avg(FeedbackSession.total_score).label('avg_score')
        ).filter(
            FeedbackSession.start_time >= start_date
        ).group_by(func.date(FeedbackSession.start_time)).order_by('date').all()
        
        dashboard_data = {
            'overview': {
                'active_sessions': active_sessions,
                'completed_sessions': completed_sessions,
                'total_feedback_entries': total_feedback,
                'average_session_duration': round(avg_duration / 60, 2) if avg_duration else 0  # Convert to minutes
            },
            'top_users': [{
                'username': user.username,
                'average_score': round(user.avg_score, 1),
                'session_count': user.session_count
            } for user in top_users],
            'challenging_scenarios': [{
                'scenario_id': scenario.scenario_id,
                'average_completion': round(scenario.avg_completion, 1),
                'attempt_count': scenario.attempt_count
            } for scenario in challenging_scenarios],
            'daily_activity': [{
                'date': activity.date.isoformat(),
                'sessions': activity.sessions,
                'average_score': round(activity.avg_score, 1) if activity.avg_score else 0
            } for activity in daily_activity]
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@feedback_api.route('/api/feedback/user/<int:user_id>/summary', methods=['GET'])
@login_required
def get_user_feedback_summary(user_id):
    """Get feedback summary for a specific user"""
    try:
        # Check permissions
        if not is_admin() and current_user.id != user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get user's sessions
        sessions = FeedbackSession.query.filter_by(user_id=user_id).all()
        
        if not sessions:
            return jsonify({
                'success': True,
                'summary': {
                    'user_id': user_id,
                    'username': user.username,
                    'total_sessions': 0,
                    'completed_sessions': 0,
                    'average_score': 0,
                    'total_time_spent': 0,
                    'improvement_trend': 'no_data',
                    'strengths': [],
                    'areas_for_improvement': []
                }
            })
        
        completed_sessions = [s for s in sessions if s.is_completed]
        
        # Calculate metrics
        total_sessions = len(sessions)
        completed_sessions_count = len(completed_sessions)
        average_score = sum(s.total_score for s in completed_sessions) / completed_sessions_count if completed_sessions_count > 0 else 0
        total_time_spent = sum(s.total_duration for s in completed_sessions if s.total_duration) / 3600  # Convert to hours
        
        # Improvement trend (compare first half vs second half of sessions)
        improvement_trend = 'stable'
        if completed_sessions_count >= 4:
            mid_point = completed_sessions_count // 2
            first_half_avg = sum(s.total_score for s in completed_sessions[:mid_point]) / mid_point
            second_half_avg = sum(s.total_score for s in completed_sessions[mid_point:]) / (completed_sessions_count - mid_point)
            
            if second_half_avg > first_half_avg * 1.1:
                improvement_trend = 'improving'
            elif second_half_avg < first_half_avg * 0.9:
                improvement_trend = 'declining'
        
        # Analyze strengths and weaknesses
        feedback_entries = PerformanceFeedback.query.filter_by(user_id=user_id).all()
        action_performance = {}
        
        for feedback in feedback_entries:
            action_type = feedback.action_type
            if action_type not in action_performance:
                action_performance[action_type] = {'success': 0, 'total': 0}
            
            action_performance[action_type]['total'] += 1
            if feedback.feedback_type == 'success':
                action_performance[action_type]['success'] += 1
        
        # Calculate success rates
        action_success_rates = {}
        for action, stats in action_performance.items():
            action_success_rates[action] = stats['success'] / stats['total'] if stats['total'] > 0 else 0
        
        # Identify strengths (success rate > 70%)
        strengths = [action for action, rate in action_success_rates.items() if rate > 0.7 and action_performance[action]['total'] >= 3]
        
        # Identify areas for improvement (success rate < 50%)
        areas_for_improvement = [action for action, rate in action_success_rates.items() if rate < 0.5 and action_performance[action]['total'] >= 3]
        
        summary = {
            'user_id': user_id,
            'username': user.username,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions_count,
            'average_score': round(average_score, 1),
            'total_time_spent': round(total_time_spent, 2),
            'improvement_trend': improvement_trend,
            'strengths': strengths,
            'areas_for_improvement': areas_for_improvement,
            'action_performance': {
                action: {
                    'success_rate': round(rate * 100, 1),
                    'total_attempts': action_performance[action]['total']
                } for action, rate in action_success_rates.items()
            }
        }
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@feedback_api.route('/api/feedback/export/<session_id>', methods=['GET'])
@login_required
def export_session_data(session_id):
    """Export session data for research purposes"""
    try:
        session = FeedbackSession.query.filter_by(session_id=session_id).first()
        
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        # Check permissions
        if not is_admin() and session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        # Get all feedback for this session
        feedback_entries = PerformanceFeedback.query.filter_by(session_id=session_id).order_by(
            PerformanceFeedback.action_timestamp
        ).all()
        
        # Format for export
        export_data = {
            'session_metadata': session.to_dict(),
            'feedback_entries': [f.to_dict() for f in feedback_entries],
            'export_timestamp': datetime.utcnow().isoformat(),
            'exported_by': current_user.username
        }
        
        return jsonify({
            'success': True,
            'data': export_data,
            'filename': f'session_{session_id}_export.json'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
