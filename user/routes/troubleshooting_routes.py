from flask import Blueprint, render_template, request, jsonify, g, session
from flask_login import login_required, current_user
from admin.models.troubleshooting import Troubleshooting
from admin.models.troubleshooting_progress import TroubleshootingProgress
from __init__ import db
from datetime import datetime
import json
import numpy as np
from user.controllers.troubleshooting_controller import TroubleshootingController

# Create blueprint
troubleshooting_bp = Blueprint('troubleshooting', __name__, url_prefix='/troubleshooting')

# Initialize controller
controller = TroubleshootingController()
    
@troubleshooting_bp.route('/')
@login_required
def index():
    """Show troubleshooting scenarios page"""
    # Get user data from database like other routes to ensure consistent user data
    user = None
    
    # Try to get user from session first
    if 'user_id' in session:
        try:
            from user.models.user import User as UserModel
            user = UserModel.query.get(session['user_id'])
        except Exception as e:
            print(f"Error getting user from session: {e}")
    
    # If no session user found, fallback to current_user
    if not user and current_user.is_authenticated:
        user = current_user
    
    # If still no user, try to get authenticated user info another way
    if not user:
        try:
            from user.models.user import User as UserModel
            if hasattr(current_user, 'id') and current_user.id:
                user = UserModel.query.get(current_user.id)
        except Exception as e:
            print(f"Error getting current user: {e}")
    
    print(f"Troubleshooting route - User: {user.username if user else 'None'}")
    return render_template('user/troubleshoot.html', user=user)

@troubleshooting_bp.route('/api/<int:scenario_id>', methods=['GET'])
@login_required
def get_scenario(scenario_id):
    """Get scenario details"""
    # Use controller to get scenario data
    scenario_data = controller.get_scenario_by_id(scenario_id)
    return jsonify(scenario_data)

@troubleshooting_bp.route('/api/submit', methods=['POST'])
@login_required
def submit_solution():
    """Submit troubleshooting solution"""
    # Use controller to handle submission
    response = controller.submit_solution(current_user.id, request.json)
    
    # Check if response includes an error
    if isinstance(response, tuple) and len(response) == 2 and 'error' in response[0]:
        return jsonify(response[0]), response[1]
    
    return jsonify(response)

# Keep the utility functions for compatibility, but they're no longer used directly
def calculate_match_percentage(user_solution, expected_solution):
    """Calculate match percentage between two topologies"""
    return controller.calculate_match_percentage(user_solution, expected_solution)

def generate_feedback(match_percentage, scenario):
    """Generate feedback based on match percentage"""
    return controller.generate_feedback(match_percentage, scenario)
