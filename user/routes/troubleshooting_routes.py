from flask import Blueprint, render_template, request, jsonify, g
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
    # Get active scenarios from controller
    scenarios = controller.get_active_scenarios()
    return render_template('user/troubleshooting.html', scenarios=scenarios)

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
