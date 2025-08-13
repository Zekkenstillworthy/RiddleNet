"""
User-facing lesson routes
"""
from flask import Blueprint, request, render_template, jsonify, redirect, url_for, session, current_app
from flask_login import login_required, current_user
from admin import db
from admin.models.module import Module, Lesson, LessonProgress
from admin.models.class_model import Class
from admin.models.simulation import Simulation, SimulationAttempt
from services.progression_service import ProgressionService
from utils.auth_decorators import user_required
from datetime import datetime
import json

lesson_bp = Blueprint('user_lesson', __name__, url_prefix='/lesson')

@lesson_bp.route('/class/<int:class_id>/lesson/<int:lesson_id>')
@user_required
def view_lesson(class_id, lesson_id):
    """Display a specific lesson for the user"""
    try:
        # Get the lesson with module relationship
        lesson = Lesson.query.options(
            db.joinedload(Lesson.module)
        ).get_or_404(lesson_id)
        
        # Verify the lesson belongs to the specified class
        if lesson.module.class_id != class_id:
            return redirect(url_for('user.dashboard'))
            
        # Check if user is enrolled in this class
        class_obj = Class.query.get_or_404(class_id)
        if current_user not in class_obj.students:
            return redirect(url_for('user.dashboard'))
        
        # Get or create lesson progress
        lesson_progress = LessonProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        if not lesson_progress:
            lesson_progress = LessonProgress(
                user_id=current_user.id,
                lesson_id=lesson_id,
                started_at=datetime.utcnow()
            )
            db.session.add(lesson_progress)
            db.session.commit()
        
        # Get previous and next lessons in the module
        previous_lesson = Lesson.query.filter(
            Lesson.module_id == lesson.module_id,
            Lesson.id < lesson_id
        ).order_by(Lesson.id.desc()).first()
        
        next_lesson = Lesson.query.filter(
            Lesson.module_id == lesson.module_id,
            Lesson.id > lesson_id
        ).order_by(Lesson.id.asc()).first()
        
        # Get simulation progress if lesson has simulations
        simulation_progress = {}
        if lesson.simulation_ids:
            for sim_id in lesson.simulation_ids:
                sim = Simulation.query.get(sim_id)
                if sim:
                    user_sim_progress = SimulationAttempt.query.filter_by(
                        user_id=current_user.id,
                        simulation_id=sim.id,
                        is_completed=True
                    ).first()
                    simulation_progress[sim.id] = {
                        'completed': user_sim_progress is not None,
                        'score': user_sim_progress.total_score if user_sim_progress else 0,
                        'attempts': SimulationAttempt.query.filter_by(
                            user_id=current_user.id,
                            simulation_id=sim.id
                        ).count()
                    }
        
        # Mark lesson as viewed if not already
        if not lesson_progress.last_accessed:
            lesson_progress.last_accessed = datetime.utcnow()
            db.session.commit()
            
        return render_template('user/lesson/view.html',
                             lesson=lesson,
                             class_obj=class_obj,
                             lesson_progress=lesson_progress,
                             previous_lesson=previous_lesson,
                             next_lesson=next_lesson,
                             simulation_progress=simulation_progress)
                             
    except Exception as e:
        current_app.logger.error(f"Error viewing lesson {lesson_id}: {str(e)}")
        return redirect(url_for('user.dashboard'))

@lesson_bp.route('/class/<int:class_id>/lesson/<int:lesson_id>/complete', methods=['POST'])
@user_required
def complete_lesson(class_id, lesson_id):
    """Mark a lesson as complete"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Verify the lesson belongs to the specified class
        if lesson.module.class_id != class_id:
            return jsonify({'success': False, 'message': 'Invalid lesson'}), 400
            
        # Check if user is enrolled in this class
        class_obj = Class.query.get_or_404(class_id)
        if current_user not in class_obj.students:
            return jsonify({'success': False, 'message': 'Not enrolled'}), 403
        
        # Check if lesson requires simulation completion
        if lesson.requires_simulation_completion and lesson.simulation_ids:
            incomplete_simulations = []
            for sim_id in lesson.simulation_ids:
                sim = Simulation.query.get(sim_id)
                if sim:
                    user_progress = SimulationAttempt.query.filter_by(
                        user_id=current_user.id,
                        simulation_id=sim.id,
                        is_completed=True
                    ).first()
                    if not user_progress:
                        incomplete_simulations.append(sim.title)
            
            if incomplete_simulations:
                return jsonify({
                    'success': False,
                    'message': f'Please complete the following simulations first: {", ".join(incomplete_simulations)}'
                }), 400
        
        # Get or create lesson progress
        lesson_progress = LessonProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        if not lesson_progress:
            lesson_progress = LessonProgress(
                user_id=current_user.id,
                lesson_id=lesson_id,
                started_at=datetime.utcnow()
            )
            db.session.add(lesson_progress)
        
        # Mark as complete
        lesson_progress.is_completed = True
        lesson_progress.completed_at = datetime.utcnow()
        lesson_progress.progress_percentage = 100
        
        # Update overall module progress
        progression_service = ProgressionService()
        progression_service.update_module_progress(current_user.id, lesson.module_id)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lesson marked as complete!',
            'completion_date': lesson_progress.completed_at.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error completing lesson {lesson_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Error completing lesson'}), 500

@lesson_bp.route('/class/<int:class_id>/lesson/<int:lesson_id>/progress', methods=['POST'])
@user_required
def update_progress(class_id, lesson_id):
    """Update lesson progress (for tracking reading progress, time spent, etc.)"""
    try:
        data = request.get_json()
        progress_percentage = data.get('progress_percentage', 0)
        time_spent = data.get('time_spent_minutes', 0)
        
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Verify the lesson belongs to the specified class
        if lesson.module.class_id != class_id:
            return jsonify({'success': False, 'message': 'Invalid lesson'}), 400
            
        # Check if user is enrolled in this class
        class_obj = Class.query.get_or_404(class_id)
        if current_user not in class_obj.students:
            return jsonify({'success': False, 'message': 'Not enrolled'}), 403
        
        # Get or create lesson progress
        lesson_progress = LessonProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        if not lesson_progress:
            lesson_progress = LessonProgress(
                user_id=current_user.id,
                lesson_id=lesson_id,
                started_at=datetime.utcnow()
            )
            db.session.add(lesson_progress)
        
        # Update progress
        lesson_progress.progress_percentage = max(lesson_progress.progress_percentage or 0, progress_percentage)
        lesson_progress.total_time_spent = (lesson_progress.total_time_spent or 0) + (time_spent * 60)  # Convert to seconds
        lesson_progress.last_accessed = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'progress_percentage': lesson_progress.progress_percentage
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating lesson progress {lesson_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Error updating progress'}), 500

@lesson_bp.route('/class/<int:class_id>/lesson/<int:lesson_id>/start-simulation/<int:simulation_id>')
@user_required
def start_simulation(class_id, lesson_id, simulation_id):
    """Start a simulation from within a lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Verify the lesson belongs to the specified class
        if lesson.module.class_id != class_id:
            return redirect(url_for('user.dashboard'))
            
        # Check if user is enrolled in this class
        class_obj = Class.query.get_or_404(class_id)
        if current_user not in class_obj.students:
            return redirect(url_for('user.dashboard'))
            
        # Verify simulation is attached to this lesson
        if simulation_id not in (lesson.simulation_ids or []):
            return redirect(url_for('user_lesson.view_lesson', class_id=class_id, lesson_id=lesson_id))
        
        # Store return URL in session for after simulation completion
        session['lesson_return_url'] = url_for('user_lesson.view_lesson', 
                                             class_id=class_id, lesson_id=lesson_id)
        
        # Redirect to simulation
        return redirect(url_for('user.simulation', simulation_id=simulation_id))
        
    except Exception as e:
        current_app.logger.error(f"Error starting simulation {simulation_id} from lesson {lesson_id}: {str(e)}")
        return redirect(url_for('user_lesson.view_lesson', class_id=class_id, lesson_id=lesson_id))

@lesson_bp.route('/api/class/<int:class_id>/lesson/<int:lesson_id>/analytics')
@user_required
def lesson_analytics(class_id, lesson_id):
    """Get lesson analytics for the current user (for progress tracking widgets)"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Verify the lesson belongs to the specified class
        if lesson.module.class_id != class_id:
            return jsonify({'success': False, 'message': 'Invalid lesson'}), 400
            
        # Check if user is enrolled in this class
        class_obj = Class.query.get_or_404(class_id)
        if current_user not in class_obj.students:
            return jsonify({'success': False, 'message': 'Not enrolled'}), 403
        
        # Get lesson progress
        lesson_progress = LessonProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        # Get simulation progress
        simulation_progress = []
        if lesson.simulation_ids:
            for sim_id in lesson.simulation_ids:
                sim = Simulation.query.get(sim_id)
                if sim:
                    user_sim_progress = SimulationAttempt.query.filter_by(
                        user_id=current_user.id,
                        simulation_id=sim.id,
                        is_completed=True
                    ).first()
                    simulation_progress.append({
                        'id': sim.id,
                        'title': sim.title,
                        'completed': user_sim_progress is not None,
                        'score': user_sim_progress.total_score if user_sim_progress else 0,
                        'attempts': SimulationAttempt.query.filter_by(
                            user_id=current_user.id,
                            simulation_id=sim.id
                        ).count()
                    })
        
        analytics_data = {
            'lesson_id': lesson_id,
            'completed': lesson_progress.is_completed if lesson_progress else False,
            'progress_percentage': lesson_progress.progress_percentage if lesson_progress else 0,
            'time_spent_minutes': lesson_progress.total_time_minutes if lesson_progress else 0,
            'started_at': lesson_progress.started_at.isoformat() if lesson_progress and lesson_progress.started_at else None,
            'completed_at': lesson_progress.completed_at.isoformat() if lesson_progress and lesson_progress.completed_at else None,
            'simulation_progress': simulation_progress,
            'requires_simulation_completion': lesson.requires_simulation_completion
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting lesson analytics {lesson_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Error loading analytics'}), 500
