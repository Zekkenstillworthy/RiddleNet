"""
Dynamic Simulation Routes Generator
Automatically creates routes for admin-created simulations - Learning Paths feature removed
"""

from flask import Blueprint, render_template, session, request, jsonify, redirect, url_for, flash
from user.models.user import User as UserModel
from admin.models.simulation import Simulation
from admin.models.class_model import Class
# Learning Path models removed - import stubs to prevent errors
from admin.models.learning_path import LearningPath, LearningPathSimulation, UserLearningProgress
from admin import db
from functools import wraps
import json

# Create dynamic blueprint
dynamic_sim_bp = Blueprint('dynamic_simulations', __name__, url_prefix='/dynamic')

def user_login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_from_session():
    """Get current user from session"""
    if 'user_id' in session:
        return UserModel.query.get(session['user_id'])
    return None

class DynamicSimulationController:
    """Controller for handling dynamic simulations and learning paths"""
    
    @staticmethod
    def get_user_class_simulations(user_id):
        """Get simulations available to user based on their class"""
        try:
            user = UserModel.query.get(user_id)
            if not user:
                return []
            
            # Get user's enrolled classes
            user_classes = user.enrolled_classes.all()
            if not user_classes:
                return []
            
            simulations = []
            
            # Get simulations for all enrolled classes
            for user_class in user_classes:
                class_level = user_class.name.lower()
                
                # Get published simulations for this class level
                if 'networking 1' in class_level:
                    class_simulations = Simulation.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).filter(
                        Simulation.simulation_type.ilike('%networking 1%')
                    ).all()
                elif 'networking 2' in class_level:
                    class_simulations = Simulation.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).filter(
                        Simulation.simulation_type.ilike('%networking 2%')
                    ).all()
                else:
                    class_simulations = Simulation.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).all()
                
                simulations.extend(class_simulations)
            
            # Remove duplicates
            unique_simulations = []
            seen_ids = set()
            for sim in simulations:
                if sim.id not in seen_ids:
                    unique_simulations.append(sim)
                    seen_ids.add(sim.id)
            
            return unique_simulations
            
        except Exception as e:
            print(f"Error getting user class simulations: {e}")
            return []
    
    @staticmethod
    def get_user_learning_paths(user_id):
        """Get learning paths available to user"""
        try:
            user = UserModel.query.get(user_id)
            if not user:
                return []
            
            # Get user's enrolled classes
            user_classes = user.enrolled_classes.all()
            if not user_classes:
                return []
            
            learning_paths = []
            
            # Get learning paths for all enrolled classes
            for user_class in user_classes:
                class_level = user_class.name.lower()
                
                # Get published learning paths for this class level
                if 'networking 1' in class_level:
                    class_paths = LearningPath.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).filter(
                        LearningPath.course_level.ilike('%networking 1%')
                    ).all()
                elif 'networking 2' in class_level:
                    class_paths = LearningPath.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).filter(
                        LearningPath.course_level.ilike('%networking 2%')
                    ).all()
                else:
                    class_paths = LearningPath.query.filter_by(
                        is_published=True,
                        is_active=True
                    ).all()
                
                learning_paths.extend(class_paths)
            
            # Remove duplicates
            unique_paths = []
            seen_ids = set()
            for path in learning_paths:
                if path.id not in seen_ids:
                    unique_paths.append(path)
                    seen_ids.add(path.id)
            
            return unique_paths
            
        except Exception as e:
            print(f"Error getting user learning paths: {e}")
            return []
    
    @staticmethod
    def get_simulation_progress(user_id, simulation_id):
        """Get user's progress for a specific simulation"""
        try:
            progress = UserLearningProgress.query.filter_by(
                user_id=user_id,
                simulation_id=simulation_id
            ).first()
            
            if progress:
                return {
                    'status': progress.status,
                    'attempts': progress.attempts_count,
                    'best_score': progress.best_score,
                    'completion_percentage': 100 if progress.status == 'completed' else 0
                }
            
            return {
                'status': 'not_started',
                'attempts': 0,
                'best_score': 0,
                'completion_percentage': 0
            }
            
        except Exception as e:
            print(f"Error getting simulation progress: {e}")
            return None
    
    @staticmethod
    def can_access_simulation(user_id, simulation_id):
        """Check if user can access a simulation based on learning path requirements"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return False
            
            # Check if simulation is in a learning path
            path_associations = LearningPathSimulation.query.filter_by(
                simulation_id=simulation_id
            ).all()
            
            if not path_associations:
                # If not in learning path, check if simulation is published
                return simulation.is_published and simulation.is_active
            
            # Check learning path requirements
            for assoc in path_associations:
                learning_path = assoc.learning_path
                
                # Check if user has access to this learning path
                user = UserModel.query.get(user_id)
                if not user:
                    continue
                
                user_classes = user.enrolled_classes.all()
                if not user_classes:
                    continue
                
                # Check if any of user's classes match the learning path
                has_access = False
                for user_class in user_classes:
                    class_level = user_class.name.lower()
                    if class_level in learning_path.course_level.lower():
                        has_access = True
                        break
                
                if not has_access:
                    continue
                
                # Check if prerequisites are met
                if assoc.order_index > 0:
                    # Get previous simulation in path
                    prev_assoc = LearningPathSimulation.query.filter_by(
                        learning_path_id=assoc.learning_path_id,
                        order_index=assoc.order_index - 1
                    ).first()
                    
                    if prev_assoc:
                        prev_progress = UserLearningProgress.query.filter_by(
                            user_id=user_id,
                            simulation_id=prev_assoc.simulation_id
                        ).first()
                        
                        if not prev_progress or prev_progress.status != 'completed':
                            return False
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error checking simulation access: {e}")
            return False

# Route Handlers
@dynamic_sim_bp.route('/dashboard')
def simulations_dashboard():
    """Show user's available simulations dashboard"""
    user = get_user_from_session()
    category_filter = request.args.get('category')
    class_filter = request.args.get('class')  # New: allow filtering by specific class
    
    try:
        # Get user's enrolled classes
        user_classes = []
        selected_class = None
        
        if user:
            user_classes = user.enrolled_classes.all()
            
            # If user specified a class filter, use that
            if class_filter:
                selected_class = next((cls for cls in user_classes if str(cls.id) == class_filter), None)
            # If user is enrolled in only one class, use that
            elif len(user_classes) == 1:
                selected_class = user_classes[0]
            # If user is enrolled in multiple classes but no filter specified, default to first class
            elif len(user_classes) > 1:
                selected_class = user_classes[0]  # Could be made smarter by user preference
        
        # Get simulations and learning paths based on selected class
        if selected_class:
            class_level = selected_class.name.lower()  # Use class name instead of class_type
            
            # Filter simulations by selected class level
            if 'networking 1' in class_level:
                simulations = Simulation.query.filter_by(is_active=True, is_published=True).filter(
                    Simulation.simulation_type.ilike('%networking 1%')
                ).all()
                learning_paths = LearningPath.query.filter_by(is_active=True, is_published=True).filter(
                    LearningPath.course_level.ilike('%networking 1%')
                ).all()
            elif 'networking 2' in class_level:
                simulations = Simulation.query.filter_by(is_active=True, is_published=True).filter(
                    Simulation.simulation_type.ilike('%networking 2%')
                ).all()
                learning_paths = LearningPath.query.filter_by(is_active=True, is_published=True).filter(
                    LearningPath.course_level.ilike('%networking 2%')
                ).all()
            else:
                # For other class types, show all simulations
                simulations = Simulation.query.filter_by(is_active=True, is_published=True).all()
                learning_paths = LearningPath.query.filter_by(is_active=True, is_published=True).all()
        else:
            # If no class assigned, show all simulations
            simulations = Simulation.query.filter_by(is_active=True, is_published=True).all()
            learning_paths = LearningPath.query.filter_by(is_active=True, is_published=True).all()
        
        # Apply additional category filter if provided
        if category_filter:
            # Handle special cases for networking1/networking2 filters
            if category_filter.lower() == 'networking1':
                simulations = [sim for sim in simulations if sim.simulation_type == 'Networking 1']
                learning_paths = [path for path in learning_paths if 'networking 1' in path.course_level.lower()]
            elif category_filter.lower() == 'networking2':
                simulations = [sim for sim in simulations if sim.simulation_type == 'Networking 2']
                learning_paths = [path for path in learning_paths if 'networking 2' in path.course_level.lower()]
            else:
                # Regular category filter
                simulations = [sim for sim in simulations if category_filter.lower() in (sim.category or '').lower()]
        
        # Group simulations by category
        simulations_by_category = {}
        
        for sim in simulations:
            category = sim.category or 'General'
            
            if category not in simulations_by_category:
                simulations_by_category[category] = []
            
            sim_data = {
                'simulation': {
                    'id': sim.id,
                    'title': sim.title,
                    'description': sim.description or '',
                    'difficulty': sim.difficulty or 'Beginner',
                    'estimated_duration': sim.estimated_duration or 30,
                    'simulation_type': sim.simulation_type or 'General',
                    'category': sim.category or 'General'
                },
                'can_access': True,
                'progress': {
                    'status': 'not_started',
                    'completion_percentage': 0,
                    'attempts': 0,
                    'best_score': 0
                }
            }
            
            simulations_by_category[category].append(sim_data)
        
        # Process learning paths
        learning_paths_data = []
        for path in learning_paths:
            # Get actual simulation count for this path
            simulation_count = path.simulation_count
            
            # Get user progress if user is logged in
            user_progress = {
                'completion_percentage': 0,
                'completed_count': 0,
                'in_progress_count': 0,
                'not_started_count': simulation_count
            }
            
            if user and user.id:
                user_progress = path.calculate_user_progress(user.id)
            
            path_data = {
                'path': {
                    'id': path.id,
                    'title': path.title,
                    'description': path.description or '',
                    'course_level': path.course_level,
                    'difficulty': getattr(path, 'difficulty_level', 'Beginner')
                },
                'category': path.course_level,
                'difficulty': getattr(path, 'difficulty_level', 'Beginner'),
                'estimated_duration': getattr(path, 'estimated_total_duration', 0),
                'simulation_count': simulation_count,
                'total_simulations': simulation_count,
                'progress': user_progress
            }
            learning_paths_data.append(path_data)
        
        # Prepare dashboard data
        dashboard_data = {
            'simulations_by_category': simulations_by_category,
            'learning_paths': learning_paths_data,
            'recent_attempts': [],
            'user_stats': {
                'total_simulations_available': len(simulations),
                'total_learning_paths_available': len(learning_paths),
                'total_attempts': 0,
                'completed_simulations': 0
            }
        }
        
        return render_template('user/dynamic_simulations_dashboard.html',
                             user=user,
                             dashboard_data=dashboard_data,
                             user_classes=user_classes,
                             selected_class=selected_class)
    
    except Exception as e:
        # Log the error and return empty data
        print(f"Dashboard Error: {e}")
        dashboard_data = {
            'simulations_by_category': {},
            'learning_paths': [],
            'recent_attempts': [],
            'user_stats': {
                'total_simulations_available': 0,
                'total_learning_paths_available': 0,
                'total_attempts': 0,
                'completed_simulations': 0
            }
        }
        return render_template('user/dynamic_simulations_dashboard.html',
                             user=user,
                             dashboard_data=dashboard_data,
                             user_classes=[],
                             selected_class=None)

@dynamic_sim_bp.route('/my-simulations', endpoint='my_simulations')
@user_login_required
def my_simulations():
    """Show user's available simulations"""
    user = get_user_from_session()
    controller = DynamicSimulationController()
    
    try:
        # Get user's simulations
        simulations = controller.get_user_class_simulations(user.id)
        
        # Get progress for each simulation
        simulation_data = []
        for sim in simulations:
            progress = controller.get_simulation_progress(user.id, sim.id)
            can_access = controller.can_access_simulation(user.id, sim.id)
            
            simulation_data.append({
                'simulation': sim,
                'progress': progress,
                'can_access': can_access
            })
        
        return render_template('user/my_simulations.html',
                             user=user,
                             simulations=simulation_data)
    
    except Exception as e:
        print(f"Error in my_simulations: {e}")
        flash(f'Error loading simulations: {str(e)}', 'error')
        return render_template('user/my_simulations.html',
                             user=user,
                             simulations=[])

@dynamic_sim_bp.route('/simulation/<int:simulation_id>')
@user_login_required
def run_simulation(simulation_id):
    """Run a specific simulation"""
    user = get_user_from_session()
    
    try:
        # Get simulation from database
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Parse simulation data from the correct schema
        simulation_config = simulation.simulation_config or {}
        step_definitions = simulation.step_definitions or []
        validation_rules = simulation.validation_rules or {}
        
        # Prepare simulation data for the template
        simulation_data = {
            'id': simulation.id,
            'title': simulation.title,
            'description': simulation.description,
            'simulation_type': simulation.simulation_type,
            'category': simulation.category,
            'difficulty': simulation.difficulty,
            'estimated_duration': simulation.estimated_duration,
            'learning_objectives': simulation.learning_objectives if isinstance(simulation.learning_objectives, list) else [],
            
            # Process scenario steps
            'steps': step_definitions,
            'validation': validation_rules,
            'topology': simulation_config,
            
            # Default values for new fields
            'total_steps': len(step_definitions),
            'base_score': simulation.base_score or 100,
            'time_bonus': simulation.time_bonus or 20,
            'perfect_completion_bonus': simulation.perfect_completion_bonus or 30
        }
        
        # Check if user has an existing attempt
        progress = {
            'attempted': False,
            'completed': False,
            'current_step': 0,
            'best_score': 0,
            'attempts_count': 0
        }
        
        return render_template('user/dynamic_simulation.html',
                             user=user,
                             simulation=simulation_data,
                             progress=progress)
    
    except Exception as e:
        print(f"Error loading simulation {simulation_id}: {e}")
        flash(f'Error loading simulation: {str(e)}', 'error')
        return redirect(url_for('dynamic_simulations.simulations_dashboard'))

@dynamic_sim_bp.route('/learning-path/<int:path_id>')
@user_login_required
def learning_path_view(path_id):
    """View learning path with simulations"""
    user = get_user_from_session()
    controller = DynamicSimulationController()
    
    learning_path = LearningPath.query.get_or_404(path_id)
    
    # Check if user has access to this learning path
    user_classes = user.enrolled_classes.all()
    if not user_classes:
        return render_template('user/access_denied.html',
                             user=user,
                             message="You must be enrolled in a class to access learning paths.")
    
    # Check if any of user's classes match the learning path
    has_access = False
    for user_class in user_classes:
        class_level = user_class.name.lower()
        if class_level in learning_path.course_level.lower():
            has_access = True
            break
    
    if not has_access:
        return render_template('user/access_denied.html',
                             user=user,
                             message="This learning path is not available for your class level.")
    
    # Get ordered simulations with progress
    ordered_simulations = learning_path.get_ordered_simulations()
    simulation_data = []
    
    for assoc in ordered_simulations:
        progress = controller.get_simulation_progress(user.id, assoc.simulation_id)
        can_access = controller.can_access_simulation(user.id, assoc.simulation_id)
        
        simulation_data.append({
            'association': assoc,
            'simulation': assoc.simulation,
            'progress': progress,
            'can_access': can_access
        })
    
    # Get overall path progress
    path_progress = learning_path.calculate_user_progress(user.id)
    
    return render_template('user/learning_path.html',
                         user=user,
                         learning_path=learning_path,
                         simulations=simulation_data,
                         path_progress=path_progress)

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/start', methods=['POST'])
@user_login_required
def start_simulation(simulation_id):
    """Start a simulation and track progress"""
    try:
        user = get_user_from_session()
        controller = DynamicSimulationController()
        
        if not controller.can_access_simulation(user.id, simulation_id):
            return jsonify({'error': 'Access denied'}), 403
        
        # Create or update progress record
        progress = UserLearningProgress.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id
        ).first()
        
        if not progress:
            # Find learning path if simulation is part of one
            path_assoc = LearningPathSimulation.query.filter_by(
                simulation_id=simulation_id
            ).first()
            
            progress = UserLearningProgress(
                user_id=user.id,
                simulation_id=simulation_id,
                learning_path_id=path_assoc.learning_path_id if path_assoc else None,
                status='in_progress'
            )
            db.session.add(progress)
        else:
            progress.status = 'in_progress'
            if not progress.started_at:
                progress.started_at = db.func.now()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Simulation started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dynamic_sim_bp.route('/api/simulation/<int:simulation_id>/complete', methods=['POST'])
@user_login_required
def complete_simulation(simulation_id):
    """Complete a simulation and update progress"""
    try:
        user = get_user_from_session()
        data = request.get_json()
        
        # Get or create progress record
        progress = UserLearningProgress.query.filter_by(
            user_id=user.id,
            simulation_id=simulation_id
        ).first()
        
        if not progress:
            return jsonify({'error': 'Simulation not started'}), 400
        
        # Update progress
        progress.update_progress({
            'completed': True,
            'score': data.get('score', 0),
            'time_spent_seconds': data.get('time_spent', 0)
        })
        
        db.session.commit()
        
        # Check if this unlocks new simulations
        unlocked_simulations = []
        
        # If simulation is part of learning path, check next simulation
        if progress.learning_path_id:
            learning_path = LearningPath.query.get(progress.learning_path_id)
            next_sim = learning_path.get_next_simulation_for_user(user.id)
            if next_sim:
                unlocked_simulations.append({
                    'id': next_sim.id,
                    'title': next_sim.title
                })
        
        return jsonify({
            'success': True,
            'message': 'Simulation completed successfully',
            'unlocked_simulations': unlocked_simulations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Register routes dynamically
def register_dynamic_routes(app):
    """Register all dynamic simulation routes"""
    app.register_blueprint(dynamic_sim_bp)

# Export the blueprint for direct import
__all__ = ['dynamic_sim_bp', 'register_dynamic_routes']
