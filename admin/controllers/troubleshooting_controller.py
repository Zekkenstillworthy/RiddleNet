from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from admin import db
from admin.models.troubleshooting import Troubleshooting
from datetime import datetime
from flask_login import login_required, current_user

# Create troubleshooting blueprint
troubleshooting_bp = Blueprint('troubleshooting', __name__)

@troubleshooting_bp.route('/troubleshooting')
@login_required
def index():
    """
    Display all troubleshooting scenarios
    """
    troubleshooting_items = Troubleshooting.query.all()
    
    return render_template('admin/troubleshooting.html', 
                          active_page='troubleshooting',
                          troubleshooting_items=troubleshooting_items)

class TroubleshootingController:

    def get_all_troubleshooting(self):
        try:
            items = Troubleshooting.query.all()
            return [item.to_dict() for item in items]
        except Exception as e:
            return {"error": str(e)}

    def get_troubleshooting(self, troubleshooting_id):
        try:
            item = Troubleshooting.query.get(troubleshooting_id)
            if not item:
                return {"error": f"Troubleshooting with ID {troubleshooting_id} not found"}
            return item.to_dict()
        except Exception as e:
            return {"error": str(e)}

    def create_troubleshooting(self, data):
        if not data or not all(k in data for k in ['title', 'description', 'scenario', 'solution']):
            return {"error": "Missing required fields"}
        try:
            new_item = Troubleshooting(
                title=data['title'],
                description=data['description'],
                difficulty=data.get('difficulty', 'medium'),
                problem_type=data.get('problem_type', 'network'),
                scenario=data['scenario'],
                solution=data['solution'],
                is_active=data.get('is_active', True),
                time_limit=data.get('time_limit', 15),
                base_score=data.get('base_score', 10),
                time_bonus=data.get('time_bonus', 5),
                solution_bonus=data.get('solution_bonus', 5)
            )
            if 'hints' in data:
                new_item.hints = data['hints']
                
            # Set additional scoring metrics if provided
            if 'scoring_metrics' in data:
                new_item.scoring_metrics = data['scoring_metrics']
            
            # Set topology data if provided
            if 'initial_topology' in data:
                new_item.initial_topology = data['initial_topology']
                
            if 'solution_topology' in data:
                new_item.solution_topology = data['solution_topology']
                
            # Set required steps if provided
            if 'required_steps' in data:
                new_item.required_steps = data['required_steps']
                
            db.session.add(new_item)
            db.session.commit()
            return {"message": "Troubleshooting created successfully", "id": new_item.id}
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}

    def update_troubleshooting(self, troubleshooting_id, data):
        try:
            item = Troubleshooting.query.get(troubleshooting_id)
            if not item:
                return {"error": f"Troubleshooting with ID {troubleshooting_id} not found"}
                
            if not data:
                return {"error": "No data provided"}
                
            for field in ['title', 'description', 'difficulty', 'problem_type', 'scenario', 'solution', 
                          'is_active', 'time_limit', 'base_score', 'time_bonus', 'solution_bonus']:
                if field in data:
                    setattr(item, field, data[field])
                    
            if 'hints' in data:
                item.hints = data['hints']
                
            # Update scoring metrics if provided
            if 'scoring_metrics' in data:
                item.scoring_metrics = data['scoring_metrics']
                
            # Update topology data if provided
            if 'initial_topology' in data:
                item.initial_topology = data['initial_topology']
                
            if 'solution_topology' in data:
                item.solution_topology = data['solution_topology']
                
            # Update required steps if provided
            if 'required_steps' in data:
                item.required_steps = data['required_steps']
                
            item.updated_at = datetime.utcnow()
            db.session.commit()
            return {"message": "Troubleshooting updated successfully", "id": item.id}
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}

    def delete_troubleshooting(self, troubleshooting_id):
        try:
            item = Troubleshooting.query.get(troubleshooting_id)
            if not item:
                return {"error": f"Troubleshooting with ID {troubleshooting_id} not found"}
                
            db.session.delete(item)
            db.session.commit()
            return {"message": "Troubleshooting deleted successfully"}
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}
            
    def toggle_active_status(self, troubleshooting_id):
        """Toggle the active status of a troubleshooting scenario"""
        try:
            item = Troubleshooting.query.get(troubleshooting_id)
            if not item:
                return {"error": f"Troubleshooting with ID {troubleshooting_id} not found"}
            
            item.is_active = not item.is_active
            db.session.commit()
            
            return {
                "message": f"Troubleshooting is now {'active' if item.is_active else 'inactive'}",
                "is_active": item.is_active
            }
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}
            
    def preview_troubleshooting(self, troubleshooting_id):
        """Get a troubleshooting scenario in a format suitable for previewing"""
        try:
            item = Troubleshooting.query.get(troubleshooting_id)
            if not item:
                return {"error": f"Troubleshooting with ID {troubleshooting_id} not found"}
            
            preview_data = {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "difficulty": item.difficulty,
                "problem_type": item.problem_type,
                "scenario": item.scenario,
                "hints": item.hints,
                "initial_topology": item.initial_topology,
                "time_limit": item.time_limit,
                "is_active": item.is_active
            }
            
            return {"preview": preview_data}
        except Exception as e:
            return {"error": str(e)}
            
    def validate_solution(self, troubleshooting_id, user_solution, time_taken=None, hints_used=0):
        """Validate a user's solution against the troubleshooting scenario"""
        try:
            item = Troubleshooting.query.get(troubleshooting_id)
            if not item:
                return {"error": f"Troubleshooting with ID {troubleshooting_id} not found"}
            
            # Default scoring values
            base_score = item.base_score
            time_bonus = 0
            solution_bonus = 0
            hint_penalty = min(hints_used, base_score // 2)  # Cap hint penalty at half the base score
            
            # Calculate time bonus if applicable
            if time_taken is not None and item.time_limit > 0:
                time_limit_seconds = item.time_limit * 60
                if time_taken < time_limit_seconds:
                    # More time remaining = higher bonus
                    time_factor = (time_limit_seconds - time_taken) / time_limit_seconds
                    time_bonus = int(item.time_bonus * time_factor)
            
            # Validate solution based on problem type
            is_correct = False
            match_percentage = 0.0
            
            if item.problem_type == 'network':
                # For network problems, compare topology configurations
                solution_result = self._validate_network_solution(item.solution_topology, user_solution)
                is_correct = solution_result['is_correct']
                match_percentage = solution_result['match_percentage']
                
                # Award solution bonus if match is high
                if match_percentage > 0.9:
                    solution_bonus = item.solution_bonus
                elif match_percentage > 0.7:
                    solution_bonus = item.solution_bonus // 2
            else:
                # For other problem types, check required steps completion
                solution_result = self._validate_steps_solution(item.required_steps, user_solution)
                is_correct = solution_result['is_correct']
                match_percentage = solution_result['match_percentage']
                
                # Award solution bonus if all required steps are completed correctly
                if is_correct:
                    solution_bonus = item.solution_bonus
            
            # Calculate final score
            total_score = base_score + time_bonus + solution_bonus - hint_penalty
            
            # Ensure score is at least 1 if correct, or 0 if incorrect
            if is_correct:
                total_score = max(1, total_score)
            else:
                total_score = 0
            
            return {
                "is_correct": is_correct,
                "match_percentage": match_percentage,
                "score": total_score,
                "base_score": base_score,
                "time_bonus": time_bonus,
                "solution_bonus": solution_bonus,
                "hint_penalty": hint_penalty,
                "feedback": "Your solution is correct!" if is_correct else "Your solution is incorrect. Try again!"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _validate_network_solution(self, expected_topology, user_topology):
        """
        Validate a network topology solution
        Returns dict with is_correct and match_percentage
        """
        try:
            # Default values
            is_correct = False
            match_percentage = 0.0
            
            # Simple validation logic - can be expanded for more sophisticated checks
            if not user_topology or not expected_topology:
                return {"is_correct": False, "match_percentage": 0.0}
            
            # Check devices
            expected_devices = set(d.get('id') for d in expected_topology.get('devices', []))
            user_devices = set(d.get('id') for d in user_topology.get('devices', []))
            
            if not expected_devices or not user_devices:
                return {"is_correct": False, "match_percentage": 0.0}
                
            device_match = len(expected_devices.intersection(user_devices)) / max(len(expected_devices), len(user_devices))
            
            # Check connections
            expected_connections = set((c.get('source'), c.get('target')) for c in expected_topology.get('connections', []))
            user_connections = set((c.get('source'), c.get('target')) for c in user_topology.get('connections', []))
            
            connection_match = 1.0  # Default to full match if no connections expected
            if expected_connections:
                connection_match = len(expected_connections.intersection(user_connections)) / max(len(expected_connections), 1)
            
            # Calculate overall match percentage
            match_percentage = 0.5 * device_match + 0.5 * connection_match
            
            # Solution is correct if match percentage is above 0.8 (80%)
            is_correct = match_percentage > 0.8
            
            return {
                "is_correct": is_correct, 
                "match_percentage": match_percentage
            }
        except Exception as e:
            # Log error but don't crash
            print(f"Error validating network solution: {str(e)}")
            return {"is_correct": False, "match_percentage": 0.0}
    
    def _validate_steps_solution(self, required_steps, user_steps):
        """
        Validate steps-based solution 
        Returns dict with is_correct and match_percentage
        """
        try:
            # Default values
            is_correct = False
            match_percentage = 0.0
            
            if not required_steps or not user_steps:
                return {"is_correct": False, "match_percentage": 0.0}
            
            # Convert to sets of step IDs for comparison
            required_step_ids = set(step.get('id') for step in required_steps)
            user_step_ids = set(step.get('id') for step in user_steps)
            
            if not required_step_ids:
                return {"is_correct": False, "match_percentage": 0.0}
                
            # Calculate match percentage
            completed_steps = required_step_ids.intersection(user_step_ids)
            match_percentage = len(completed_steps) / len(required_step_ids)
            
            # Solution is correct if all required steps are completed
            is_correct = match_percentage >= 1.0
            
            return {
                "is_correct": is_correct,
                "match_percentage": match_percentage
            }
        except Exception as e:
            # Log error but don't crash
            print(f"Error validating steps solution: {str(e)}")
            return {"is_correct": False, "match_percentage": 0.0}