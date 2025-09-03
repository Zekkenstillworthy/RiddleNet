"""
Enhanced User Simulation Runner
Connects to admin-created simulations in the database
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, current_app, flash
from flask_login import login_required, current_user
from admin.models.simulation import Simulation, SimulationAttempt
from admin.models.class_model import Class
from admin.models.class_content import ClassAssignment
from admin.models.assignment_submission import AssignmentSubmission, AssignmentSubmissionHistory
from admin.models.rubric import Rubric, RubricCriterion, RubricAssessment
from admin.models.module import Module, Lesson
from admin import db
from datetime import datetime
import json
from services.deadline_service import DeadlineService

# Create blueprint for user simulation runner
user_simulation_bp = Blueprint('user_simulation', __name__, url_prefix='/simulation')

class UserSimulationController:
    """Controller for user-facing simulation functionality"""
    
    @staticmethod
    def get_available_simulations(user_id):
        """Get simulations available to a user based on their enrolled classes"""
        try:
            from user.models.user import User as UserModel
            user = UserModel.query.get(user_id)
            
            if not user:
                return []
            
            # Get user's enrolled classes
            enrolled_classes = user.enrolled_classes.all()
            
            if not enrolled_classes:
                # If no classes, return all public simulations
                return Simulation.query.filter_by(
                    is_active=True,
                    is_published=True
                ).all()
            
            # Get simulations for enrolled classes
            available_simulations = set()
            
            for class_obj in enrolled_classes:
                # Get modules for this class
                modules = Module.query.filter_by(class_id=class_obj.id).all()
                
                for module in modules:
                    # Get lessons for this module
                    lessons = Lesson.query.filter_by(module_id=module.id).all()
                    
                    for lesson in lessons:
                        # Get simulations assigned to this lesson
                        if lesson.simulation_ids:
                            for sim_id in lesson.simulation_ids:
                                simulation = Simulation.query.filter_by(
                                    id=sim_id,
                                    is_active=True,
                                    is_published=True
                                ).first()
                                
                                if simulation:
                                    available_simulations.add(simulation)
            
            # Also include general simulations not assigned to specific lessons
            general_simulations = Simulation.query.filter_by(
                is_active=True,
                is_published=True
            ).filter(~Simulation.id.in_([sim.id for sim in available_simulations])).all()
            
            # Filter general simulations by category matching user's class level
            for simulation in general_simulations:
                for class_obj in enrolled_classes:
                    class_level = class_obj.name.lower()
                    sim_category = (simulation.category or '').lower()
                    
                    # Basic matching logic
                    if 'networking 1' in class_level and 'networking' in sim_category and '1' in sim_category:
                        available_simulations.add(simulation)
                    elif 'networking 2' in class_level and 'networking' in sim_category and '2' in sim_category:
                        available_simulations.add(simulation)
                    elif 'security' in class_level and 'security' in sim_category:
                        available_simulations.add(simulation)
                        
            return list(available_simulations)
            
        except Exception as e:
            current_app.logger.error(f"Error getting available simulations: {str(e)}")
            return []
    
    @staticmethod
    def get_simulation_attempt(user_id, simulation_id):
        """Get or create a simulation attempt for the user"""
        try:
            # Check for existing incomplete attempt
            existing_attempt = SimulationAttempt.query.filter_by(
                user_id=user_id,
                simulation_id=simulation_id,
                is_completed=False
            ).first()
            
            if existing_attempt:
                return existing_attempt
                
            # Create new attempt
            attempt = SimulationAttempt(
                user_id=user_id,
                simulation_id=simulation_id,
                started_at=datetime.utcnow(),
                current_step=0,
                step_responses=[],
                is_completed=False,
                total_score=0
            )
            
            db.session.add(attempt)
            db.session.commit()
            
            return attempt
            
        except Exception as e:
            current_app.logger.error(f"Error getting simulation attempt: {str(e)}")
            return None
    
    @staticmethod
    def update_attempt_progress(attempt_id, step_data):
        """Update progress for a simulation attempt"""
        try:
            attempt = SimulationAttempt.query.get(attempt_id)
            if not attempt:
                return {'success': False, 'error': 'Attempt not found'}
                
            # Update step responses
            if not attempt.step_responses:
                attempt.step_responses = []
                
            attempt.step_responses.append(step_data)
            attempt.current_step = len(attempt.step_responses)
            attempt.updated_at = datetime.utcnow()
            
            # Calculate score for this step
            step_score = step_data.get('score', 0)
            attempt.total_score += step_score
            
            db.session.commit()
            
            return {'success': True, 'attempt': attempt}
            
        except Exception as e:
            current_app.logger.error(f"Error updating attempt progress: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def complete_simulation_attempt(attempt_id, final_score=None):
        """Complete a simulation attempt"""
        try:
            attempt = SimulationAttempt.query.get(attempt_id)
            if not attempt:
                return {'success': False, 'error': 'Attempt not found'}
                
            attempt.is_completed = True
            attempt.completed_at = datetime.utcnow()
            
            if final_score is not None:
                attempt.total_score = final_score
                
            # Calculate duration
            if attempt.started_at and attempt.completed_at:
                duration = attempt.completed_at - attempt.started_at
                attempt.duration_minutes = duration.total_seconds() / 60
                
            db.session.commit()
            
            return {'success': True, 'attempt': attempt}
            
        except Exception as e:
            current_app.logger.error(f"Error completing simulation attempt: {str(e)}")
            return {'success': False, 'error': str(e)}

# Initialize controller
simulation_controller = UserSimulationController()

@user_simulation_bp.route('/dashboard')
@login_required
def simulation_dashboard():
    """Show user's simulation dashboard"""
    try:
        # Get available simulations
        available_simulations = simulation_controller.get_available_simulations(current_user.id)
        
        # Group by category
        simulations_by_category = {}
        for simulation in available_simulations:
            category = simulation.category or 'General'
            
            if category not in simulations_by_category:
                simulations_by_category[category] = []
                
            # Get user's best attempt for this simulation
            best_attempt = SimulationAttempt.query.filter_by(
                user_id=current_user.id,
                simulation_id=simulation.id,
                is_completed=True
            ).order_by(SimulationAttempt.total_score.desc()).first()
            
            simulation_data = {
                'simulation': simulation,
                'best_score': best_attempt.total_score if best_attempt else 0,
                'completed': bool(best_attempt),
                'attempts': SimulationAttempt.query.filter_by(
                    user_id=current_user.id,
                    simulation_id=simulation.id
                ).count()
            }
            
            simulations_by_category[category].append(simulation_data)
        
        # Get recent attempts
        recent_attempts = SimulationAttempt.query.filter_by(
            user_id=current_user.id
        ).order_by(SimulationAttempt.started_at.desc()).limit(5).all()
        
        return render_template('user/simulation_dashboard.html',
                             simulations_by_category=simulations_by_category,
                             recent_attempts=recent_attempts,
                             user=current_user)
                             
    except Exception as e:
        current_app.logger.error(f"Error loading simulation dashboard: {str(e)}")
        flash('Error loading simulation dashboard', 'error')
        return redirect(url_for('user.dashboard'))

@user_simulation_bp.route('/<int:simulation_id>')
@login_required
def run_simulation(simulation_id):
    """Run a specific simulation"""
    try:
        # Get simulation
        simulation = Simulation.query.filter_by(
            id=simulation_id,
            is_active=True,
            is_published=True
        ).first()
        
        if not simulation:
            flash('Simulation not found or not available', 'error')
            return redirect(url_for('user_simulation.simulation_dashboard'))
        
        # Check if user has access to this simulation
        available_simulations = simulation_controller.get_available_simulations(current_user.id)
        if simulation not in available_simulations:
            flash('You do not have access to this simulation', 'error')
            return redirect(url_for('user_simulation.simulation_dashboard'))
        
        # Get or create simulation attempt
        attempt = simulation_controller.get_simulation_attempt(current_user.id, simulation_id)
        
        if not attempt:
            flash('Error starting simulation', 'error')
            return redirect(url_for('user_simulation.simulation_dashboard'))
        
        # Prepare simulation data for the template
        simulation_data = {
            'id': simulation.id,
            'title': simulation.title,
            'description': simulation.description,
            'simulation_type': simulation.simulation_type,
            'category': simulation.category,
            'difficulty': simulation.difficulty,
            'estimated_duration': simulation.estimated_duration,
            'learning_objectives': simulation.learning_objectives or [],
            'step_definitions': simulation.step_definitions or [],
            'validation_rules': simulation.validation_rules or {},
            'scoring_config': simulation.scoring_config or {'total_points': 100}
        }
        
        # Prepare attempt data
        attempt_data = {
            'id': attempt.id,
            'current_step': attempt.current_step,
            'total_score': attempt.total_score,
            'step_responses': attempt.step_responses or [],
            'started_at': attempt.started_at.isoformat() if attempt.started_at else None
        }
        
        return render_template('user/simulation_runner.html',
                             simulation=simulation_data,
                             attempt=attempt_data,
                             user=current_user)
                             
    except Exception as e:
        current_app.logger.error(f"Error running simulation {simulation_id}: {str(e)}")
        flash('Error loading simulation', 'error')
        return redirect(url_for('user_simulation.simulation_dashboard'))

@user_simulation_bp.route('/<int:simulation_id>/results/<int:attempt_id>')
@login_required
def simulation_results(simulation_id, attempt_id):
    """Show results for a completed simulation attempt"""
    try:
        # Get attempt
        attempt = SimulationAttempt.query.filter_by(
            id=attempt_id,
            user_id=current_user.id,
            simulation_id=simulation_id,
            is_completed=True
        ).first()
        
        if not attempt:
            flash('Simulation results not found', 'error')
            return redirect(url_for('user_simulation.simulation_dashboard'))
        
        # Get simulation
        simulation = Simulation.query.get(simulation_id)
        
        # Calculate detailed results
        total_possible_score = simulation.scoring_config.get('total_points', 100) if simulation.scoring_config else 100
        percentage = (attempt.total_score / total_possible_score) * 100 if total_possible_score > 0 else 0
        
        # Get step-by-step results
        step_results = []
        step_definitions = simulation.step_definitions or []
        step_responses = attempt.step_responses or []
        
        for i, step_def in enumerate(step_definitions):
            step_response = step_responses[i] if i < len(step_responses) else None
            
            step_results.append({
                'step_number': i + 1,
                'step_title': step_def.get('title', f'Step {i + 1}'),
                'step_type': step_def.get('type', 'instruction'),
                'user_response': step_response.get('response', '') if step_response else '',
                'correct': step_response.get('correct', False) if step_response else False,
                'score': step_response.get('score', 0) if step_response else 0,
                'feedback': step_response.get('feedback', '') if step_response else ''
            })
        
        results_data = {
            'attempt': attempt,
            'simulation': simulation,
            'total_score': attempt.total_score,
            'percentage': round(percentage, 1),
            'duration_minutes': attempt.duration_minutes or 0,
            'step_results': step_results
        }
        
        return render_template('user/simulation_results.html',
                             results=results_data,
                             user=current_user)
                             
    except Exception as e:
        current_app.logger.error(f"Error showing simulation results: {str(e)}")
        flash('Error loading simulation results', 'error')
        return redirect(url_for('user_simulation.simulation_dashboard'))

# API Routes for simulation interaction
@user_simulation_bp.route('/api/<int:simulation_id>/submit-step', methods=['POST'])
@login_required
def submit_step(simulation_id):
    """Submit a step response"""
    try:
        data = request.get_json()
        attempt_id = data.get('attempt_id')
        step_number = data.get('step_number')
        response = data.get('response')
        
        if not all([attempt_id, step_number is not None, response is not None]):
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
        
        # Get simulation and attempt
        simulation = Simulation.query.get(simulation_id)
        attempt = SimulationAttempt.query.filter_by(
            id=attempt_id,
            user_id=current_user.id,
            simulation_id=simulation_id
        ).first()
        
        if not simulation or not attempt:
            return jsonify({'success': False, 'error': 'Simulation or attempt not found'}), 404
        
        # Validate step number
        step_definitions = simulation.step_definitions or []
        if step_number >= len(step_definitions):
            return jsonify({'success': False, 'error': 'Invalid step number'}), 400
        
        step_definition = step_definitions[step_number]
        validation_rules = simulation.validation_rules or {}
        
        # Score the response
        is_correct = False
        score = 0
        feedback = ""
        
        if step_definition.get('type') == 'question':
            # Handle different question types
            expected_answer = step_definition.get('expected_answer', '')
            
            if step_definition.get('question_type') == 'multiple_choice':
                is_correct = response.strip().lower() == expected_answer.strip().lower()
            else:
                # Text-based answer
                is_correct = response.strip().lower() in expected_answer.strip().lower()
            
            if is_correct:
                score = step_definition.get('points', 10)
                feedback = "Correct!"
            else:
                feedback = f"Incorrect. The correct answer was: {expected_answer}"
                
        elif step_definition.get('type') == 'configuration':
            # Validate configuration commands
            expected_commands = step_definition.get('expected_commands', [])
            user_commands = response.strip().split('\n')
            
            # Simple validation - check if key commands are present
            correct_commands = 0
            for expected_cmd in expected_commands:
                if any(expected_cmd.lower() in user_cmd.lower() for user_cmd in user_commands):
                    correct_commands += 1
            
            if correct_commands >= len(expected_commands) * 0.7:  # 70% threshold
                is_correct = True
                score = step_definition.get('points', 10)
                feedback = "Configuration looks correct!"
            else:
                feedback = "Configuration incomplete or incorrect. Please review the requirements."
                
        else:
            # For instruction steps, award points for completion
            is_correct = True
            score = step_definition.get('points', 5)
            feedback = "Step completed!"
        
        # Create step data
        step_data = {
            'step_number': step_number,
            'response': response,
            'correct': is_correct,
            'score': score,
            'feedback': feedback,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Update attempt progress
        result = simulation_controller.update_attempt_progress(attempt_id, step_data)
        
        if not result['success']:
            return jsonify(result), 500
        
        return jsonify({
            'success': True,
            'correct': is_correct,
            'score': score,
            'feedback': feedback,
            'total_score': result['attempt'].total_score
        })
        
    except Exception as e:
        current_app.logger.error(f"Error submitting step: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@user_simulation_bp.route('/api/<int:simulation_id>/complete', methods=['POST'])
@login_required
def complete_simulation(simulation_id):
    """Complete a simulation"""
    try:
        data = request.get_json()
        attempt_id = data.get('attempt_id')
        validation = data.get('validation') or {}

        if not attempt_id:
            return jsonify({'success': False, 'error': 'Missing attempt ID'}), 400

        # Strict validation gating based on simulation rules
        sim_obj = Simulation.query.get(simulation_id)
        rules = (sim_obj.validation_rules or {}) if sim_obj else {}
        if bool(rules.get('enforce_strict', False)):
            if not isinstance(validation, dict) or not validation.get('passed', False):
                return jsonify({'success': False, 'error': 'Validation requirements not met. Please pass all required checks before submission.'}), 400

        # Complete the attempt
        result = simulation_controller.complete_simulation_attempt(attempt_id)
        if not result['success']:
            return jsonify(result), 500
        attempt = result['attempt']

        # Attempt to sync grade to an assignment referencing this simulation
        try:
            candidate = None
            user_classes = None
            try:
                user_classes = current_user.enrolled_classes
            except Exception:
                user_classes = None
            assignments = ClassAssignment.query.filter_by(simulation_id=simulation_id, is_published=True).all()
            if assignments:
                if user_classes is not None and hasattr(user_classes, 'all'):
                    class_ids = [c.id for c in user_classes.all()]
                    assignments = [a for a in assignments if a.class_id in class_ids]
                upcoming = [a for a in assignments if not a.due_date or a.due_date >= datetime.utcnow()]
                if upcoming:
                    candidate = sorted(upcoming, key=lambda a: a.due_date or datetime.max)[0]
                else:
                    candidate = sorted(assignments, key=lambda a: a.created_at or datetime.min, reverse=True)[0]

            if candidate:
                submission = AssignmentSubmission.query.filter_by(assignment_id=candidate.id, student_id=current_user.id).first()
                is_resub = False
                if not submission:
                    submission = AssignmentSubmission(
                        assignment_id=candidate.id,
                        student_id=current_user.id,
                        submission_text=f"Auto-submitted from simulation attempt {attempt.id}",
                        max_points=candidate.points,
                        submitted_at=datetime.utcnow(),
                        status='submitted'
                    )
                    db.session.add(submission)
                else:
                    is_resub = True
                    submission.submission_text = f"Auto-resubmitted from simulation attempt {attempt.id}"
                    submission.submitted_at = datetime.utcnow()
                    submission.status = 'resubmitted'

                rubric = Rubric.query.filter_by(assignment_id=candidate.id).first()
                total_points_assignment = candidate.points or 100
                sim_total = (sim_obj.scoring_config.get('total_points') if sim_obj and sim_obj.scoring_config else None) or 100
                try:
                    proportion = max(0.0, min(1.0, (attempt.total_score or 0) / float(sim_total)))
                except Exception:
                    proportion = 0.0

                if rubric and rubric.criteria:
                    try:
                        RubricAssessment.query.filter_by(submission_id=submission.id).delete()
                    except Exception:
                        pass
                    max_total = sum(float(c.max_points or 0.0) for c in rubric.criteria)
                    awarded_total = 0.0
                    for c in sorted(rubric.criteria, key=lambda x: x.order_index or 0):
                        c_max = float(getattr(c, 'max_points', 0.0) or 0.0)
                        award = round(proportion * c_max, 2)
                        db.session.add(RubricAssessment(
                            submission_id=submission.id,
                            rubric_id=rubric.id,
                            criterion_id=c.id,
                            awarded_points=award,
                            feedback=None
                        ))
                        awarded_total += award
                    grade = round(awarded_total * (total_points_assignment / max_total), 2) if max_total > 0 else round(proportion * total_points_assignment, 2)
                else:
                    grade = round(proportion * total_points_assignment, 2)

                submission.grade = grade
                submission.status = 'graded'
                submission.graded_at = datetime.utcnow()
                submission.feedback = (submission.feedback or '')

                # Apply late penalty
                try:
                    final_grade, penalty_info = DeadlineService.apply_penalty_to_grade(submission, submission.grade)
                    submission.grade = final_grade
                    if penalty_info.get('is_late'):
                        submission.is_late = True
                        submission.late_penalty_applied = penalty_info.get('penalty_percentage', 0.0)
                except Exception as e:
                    current_app.logger.error(f"Late penalty application failed: {e}")

                db.session.add(AssignmentSubmissionHistory(
                    submission_id=submission.id,
                    action='graded',
                    old_grade=None,
                    new_grade=submission.grade,
                    old_status='submitted' if not is_resub else 'resubmitted',
                    new_status='graded',
                    changed_by=current_user.id,
                    changed_by_type='admin' if getattr(current_user, 'role', '') == 'admin' else 'student',
                    notes='Auto-graded from simulation completion'
                ))
                db.session.commit()
        except Exception as sync_err:
            current_app.logger.error(f"Error syncing simulation to assignment: {sync_err}")

        return jsonify({
            'success': True,
            'final_score': attempt.total_score,
            'duration_minutes': attempt.duration_minutes,
            'validation': validation,
            'results_url': url_for('user_simulation.simulation_results', simulation_id=simulation_id, attempt_id=attempt_id)
        })
    except Exception as e:
        current_app.logger.error(f"Error completing simulation: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@user_simulation_bp.route('/api/<int:simulation_id>/restart', methods=['POST'])
@login_required
def restart_simulation(simulation_id):
    """Restart a simulation (create new attempt)"""
    try:
        # Mark any existing incomplete attempts as abandoned
        existing_attempts = SimulationAttempt.query.filter_by(
            user_id=current_user.id,
            simulation_id=simulation_id,
            is_completed=False
        ).all()
        
        for attempt in existing_attempts:
            attempt.is_completed = True
            attempt.completed_at = datetime.utcnow()
            # Mark as abandoned with a special flag or status
        
        db.session.commit()
        
        # Redirect to start the simulation again
        return jsonify({
            'success': True,
            'redirect_url': url_for('user_simulation.run_simulation', simulation_id=simulation_id)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error restarting simulation: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Export blueprint
__all__ = ['user_simulation_bp']
