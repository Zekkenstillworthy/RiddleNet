"""
Debug route to test authentication and API responses
"""
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from admin.controllers.dashboard_controller import dashboard_bp

@dashboard_bp.route('/api/debug/auth-status')
def debug_auth_status():
    """Debug authentication status"""
    return jsonify({
        'is_authenticated': current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False,
        'user_id': getattr(current_user, 'id', None),
        'username': getattr(current_user, 'username', None),
        'session_info': dict(request.session) if hasattr(request, 'session') else {},
        'request_headers': dict(request.headers),
        'endpoint_test': 'auth-status-working'
    })

@dashboard_bp.route('/api/debug/test-analytics')
@login_required
def debug_test_analytics():
    """Test analytics functionality with debug info"""
    try:
        from admin.services.analytics_service import AnalyticsService
        analytics = AnalyticsService()
        
        # Test a simple analytics call
        metrics = analytics.get_real_time_metrics()
        
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
