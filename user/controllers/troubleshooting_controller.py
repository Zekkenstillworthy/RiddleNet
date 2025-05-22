from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from admin.models.troubleshooting import Troubleshooting
from admin.models.troubleshooting_progress import TroubleshootingProgress
from __init__ import db
from datetime import datetime
import json
import numpy as np

class TroubleshootingController:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # The controller doesn't directly register routes, this is done in run.py
        # using the blueprint from user.routes.troubleshooting_routes
        pass

    def get_active_scenarios(self):
        """Get all active troubleshooting scenarios"""
        return Troubleshooting.query.filter_by(is_active=True).all()
    
    def get_scenario_by_id(self, scenario_id):
        """Get scenario by ID without exposing solutions"""
        scenario = Troubleshooting.query.get_or_404(scenario_id)
        scenario_data = scenario.to_dict()
        
        # Don't send sensitive data to client
        if 'solution' in scenario_data:
            del scenario_data['solution']
            
        if 'expected_topology' in scenario_data:
            del scenario_data['expected_topology']
        
        return scenario_data
        
    def submit_solution(self, user_id, data):
        """Submit a solution for scoring"""
        if not data or 'scenario_id' not in data or 'user_solution' not in data:
            return {"error": "Missing required fields"}, 400
        
        scenario_id = data['scenario_id']
        user_solution = data['user_solution']
        time_taken = data.get('time_taken', 0)
        
        # Get the scenario
        scenario = Troubleshooting.query.get_or_404(scenario_id)
        
        # Calculate match percentage
        match_percentage = self.calculate_match_percentage(user_solution, scenario.expected_topology)
        
        # Calculate score
        base_score = scenario.base_score
        
        # Time bonus calculation
        time_bonus = 0
        if time_taken > 0:
            max_time = 15 * 60  # 15 minutes in seconds
            min_time = 5 * 60   # 5 minutes in seconds
            
            if time_taken <= min_time:
                time_bonus = scenario.time_bonus
            elif time_taken < max_time:
                # Scale linearly between min and max time
                time_bonus = int(scenario.time_bonus * (max_time - time_taken) / (max_time - min_time))
        
        # Match score based on topology match percentage
        match_score = int(scenario.perfect_match_bonus * (match_percentage / 100))
        
        # Calculate total score
        total_score = base_score + time_bonus + match_score
        
        # Save the progress
        progress = TroubleshootingProgress(
            user_id=user_id,
            troubleshooting_id=scenario_id,
            score=total_score,
            time_taken=time_taken,
            is_completed=True,
            topology_match_percentage=match_percentage,
            user_solution=user_solution
        )
        
        # Check if this is a retry
        existing_progress = TroubleshootingProgress.query.filter_by(
            user_id=user_id,
            troubleshooting_id=scenario_id
        ).first()
        
        if existing_progress:
            progress.attempts = existing_progress.attempts + 1
        
        # Save to database
        db.session.add(progress)
        db.session.commit()
        
        # Generate feedback based on match percentage
        feedback = self.generate_feedback(match_percentage, scenario)
        
        # Prepare response
        response = {
            "score": total_score,
            "base_score": base_score,
            "time_bonus": time_bonus,
            "match_score": match_score,
            "topology_match_percentage": match_percentage,
            "feedback": feedback,
            "expected_topology": scenario.expected_topology  # Now share the expected topology
        }
        
        return response

    def calculate_match_percentage(self, user_solution, expected_solution):
        """Calculate match percentage between two topologies"""
        try:
            # Device count comparison
            user_devices = len(user_solution.get('devices', []))
            expected_devices = len(expected_solution.get('devices', []))
            device_count_match = min(user_devices / max(1, expected_devices), 1.0) if expected_devices > 0 else 0
            
            # Connection count comparison
            user_connections = len(user_solution.get('connections', []))
            expected_connections = len(expected_solution.get('connections', []))
            connection_count_match = min(user_connections / max(1, expected_connections), 1.0) if expected_connections > 0 else 0
            
            # For now, use a simple weighted average
            match_percentage = (device_count_match * 0.4 + connection_count_match * 0.6) * 100
            return round(match_percentage, 1)
        except Exception as e:
            print(f"Error calculating match percentage: {e}")
            return 0.0

    def generate_feedback(self, match_percentage, scenario):
        """Generate feedback based on match percentage"""
        if match_percentage >= 90:
            return f"""
            <p class="success">Excellent work! Your solution is very close to the expected one.</p>
            <p>You've demonstrated a strong understanding of the scenario and how to resolve it properly.</p>
            <p>Here's the correct approach:</p>
            <div class="solution-steps">{scenario.solution}</div>
            """
        elif match_percentage >= 70:
            return f"""
            <p class="good">Good job! Your solution addresses most of the key issues.</p>
            <p>There are a few small differences between your solution and the ideal approach.</p>
            <p>Here's the correct approach:</p>
            <div class="solution-steps">{scenario.solution}</div>
            """
        elif match_percentage >= 50:
            return f"""
            <p class="warning">You're on the right track, but there are some important differences.</p>
            <p>Review the scenario requirements carefully and compare your solution with the expected one.</p>
            <p>Here's the correct approach:</p>
            <div class="solution-steps">{scenario.solution}</div>
            """
        else:
            return f"""
            <p class="danger">There are significant differences between your solution and the expected one.</p>
            <p>Take some time to review the scenario requirements and the expected solution.</p>
            <p>Here's the correct approach:</p>
            <div class="solution-steps">{scenario.solution}</div>
            """

    def get_user_progress(self, user_id):
        """Get user's progress on troubleshooting scenarios"""
        progress = TroubleshootingProgress.query.filter_by(user_id=user_id).all()
        return progress