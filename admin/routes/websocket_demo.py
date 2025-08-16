# Admin WebSocket Demo Route
# Add this to your admin routes file

from flask import Blueprint, render_template, jsonify, request
from admin.utils.auth_decorators import admin_required
from datetime import datetime

# Create blueprint for WebSocket demo
websocket_demo_bp = Blueprint('websocket_demo', __name__, url_prefix='/admin/websocket')

@websocket_demo_bp.route('/demo')
@admin_required
def websocket_demo():
    """Demo page showing WebSocket functionality"""
    return render_template('admin/websocket_demo.html', 
                         page_title="WebSocket Demo",
                         current_page='websocket-debug')

@websocket_demo_bp.route('/monitoring')
@admin_required
def websocket_monitoring():
    """WebSocket monitoring panel"""
    return render_template('admin/websocket_monitoring.html',
                         page_title="WebSocket Monitoring",
                         current_page='websocket-debug')

@websocket_demo_bp.route('/api/stats')
@admin_required
def websocket_stats_api():
    """API endpoint for WebSocket statistics"""
    # This would normally query your WebSocket manager for real stats
    stats = {
        'connected_users': 45,
        'active_rooms': 12,
        'messages_per_minute': 28,
        'avg_latency': 42,
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(stats)

@websocket_demo_bp.route('/api/active-users')
@admin_required
def active_users_api():
    """API endpoint for active users"""
    # This would normally query your user management system
    users = [
        {
            'id': 1,
            'username': 'student1',
            'profile_img': '/static/img/default-avatar.png',
            'current_activity': 'Simulation Builder',
            'connected_at': datetime.utcnow().isoformat(),
            'status': 'online'
        },
        {
            'id': 2,
            'username': 'student2',
            'profile_img': '/static/img/default-avatar.png',
            'current_activity': 'Dashboard',
            'connected_at': datetime.utcnow().isoformat(),
            'status': 'online'
        }
    ]
    return jsonify({'users': users})

@websocket_demo_bp.route('/api/collaboration-sessions')
@admin_required
def collaboration_sessions_api():
    """API endpoint for active collaboration sessions"""
    # This would normally query your collaboration system
    sessions = [
        {
            'id': 'session_1',
            'activity_name': 'Network Troubleshooting Lab',
            'participants': ['student1', 'student2'],
            'status': 'active',
            'duration': '15m',
            'type': 'troubleshooting'
        }
    ]
    return jsonify({'sessions': sessions})

# Register the blueprint in your main admin app
# app.register_blueprint(websocket_demo_bp)
