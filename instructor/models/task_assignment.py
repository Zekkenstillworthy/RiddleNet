from __init__ import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from decimal import Decimal

class TaskAssignment(db.Model):
    """
    Model for tracking instructor-assigned network configuration tasks
    Students complete tasks with specific device, connection, and CLI requirements
    """
    __tablename__ = 'task_assignments'
    __table_args__ = {'extend_existing': True}
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='SET NULL'), nullable=True)
    
    # Assignment Metadata
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    
    # Progress Tracking (JSONB for flexibility)
    devices_placed = db.Column(JSONB, default=list, nullable=False)  # List of placed device IDs
    devices_configured = db.Column(JSONB, default=dict, nullable=False)  # {device_id: config_data}
    connections_made = db.Column(JSONB, default=list, nullable=False)  # List of connection objects
    cli_history = db.Column(JSONB, default=list, nullable=False)  # List of CLI commands executed
    activity_log = db.Column(JSONB, default=list, nullable=False)  # Detailed activity tracking
    
    # Grading
    auto_grade_score = db.Column(db.Numeric(5, 2), default=Decimal('0.00'))
    instructor_grade = db.Column(db.Numeric(5, 2), nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    
    # Status Management
    status = db.Column(
        db.String(20), 
        default='pending',
        nullable=False
    )  # pending, in_progress, submitted, graded, returned
    
    # Timestamps
    started_at = db.Column(db.DateTime, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)
    graded_at = db.Column(db.DateTime, nullable=True)
    returned_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Validation Results (store last validation)
    validation_results = db.Column(JSONB, default=dict, nullable=False)
    
    # Attempt Tracking
    attempt_count = db.Column(db.Integer, default=0)
    last_activity_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    simulation = db.relationship('Simulation', backref='task_assignments')
    user = db.relationship('User', backref='task_assignments', foreign_keys=[user_id])
    
    def __repr__(self):
        return f"TaskAssignment(id={self.id}, simulation_id={self.simulation_id}, user_id={self.user_id}, status='{self.status}')"
    
    @property
    def is_overdue(self):
        """Check if assignment is past due date"""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and self.status not in ['submitted', 'graded']
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.utcnow()
        return delta.days
    
    @property
    def completion_percentage(self):
        """Calculate overall completion percentage based on requirements (capped at 100%)"""
        if not self.simulation or not self.simulation.task_config:
            return 0
        
        task_config = self.simulation.task_config
        if not task_config.get('enabled'):
            return 0
        
        total_weight = 0
        completed_weight = 0
        
        # Device requirements
        device_reqs = task_config.get('device_requirements', [])
        if device_reqs:
            device_weight = 25
            total_weight += device_weight
            placed_count = len(self.devices_placed or [])
            required_count = len(device_reqs)
            if required_count > 0:
                # Cap at 100% - don't exceed required count
                completion_ratio = min(placed_count / required_count, 1.0)
                completed_weight += completion_ratio * device_weight
        
        # Connection requirements
        conn_reqs = task_config.get('connection_requirements', [])
        if conn_reqs:
            conn_weight = 25
            total_weight += conn_weight
            made_count = len(self.connections_made or [])
            required_count = len(conn_reqs)
            if required_count > 0:
                # Cap at 100% - don't exceed required count
                completion_ratio = min(made_count / required_count, 1.0)
                completed_weight += completion_ratio * conn_weight
        
        # CLI requirements
        cli_reqs = task_config.get('cli_requirements', {})
        if cli_reqs:
            cli_weight = 50
            total_weight += cli_weight
            total_required = sum(len(cmds) for cmds in cli_reqs.values())
            executed_count = len(self.cli_history or [])
            if total_required > 0:
                # Cap at 100% - don't exceed required count
                completion_ratio = min(executed_count / total_required, 1.0)
                completed_weight += completion_ratio * cli_weight
        
        return round((completed_weight / total_weight * 100) if total_weight > 0 else 0, 2)
    
    @property
    def final_score(self):
        """Get final score (instructor grade takes precedence)"""
        if self.instructor_grade is not None:
            return float(self.instructor_grade)
        return float(self.auto_grade_score or 0)
    
    def start_assignment(self):
        """Mark assignment as started"""
        if self.status == 'pending':
            self.status = 'in_progress'
            self.started_at = datetime.utcnow()
            self.attempt_count += 1
    
    def submit_assignment(self, auto_grade_score=None):
        """Submit assignment for grading"""
        self.status = 'submitted'
        self.submitted_at = datetime.utcnow()
        if auto_grade_score is not None:
            self.auto_grade_score = Decimal(str(auto_grade_score))
    
    def grade_assignment(self, instructor_grade, feedback=None):
        """Instructor grades the assignment"""
        self.instructor_grade = Decimal(str(instructor_grade))
        self.feedback = feedback
        self.status = 'graded'
        self.graded_at = datetime.utcnow()
    
    def return_assignment(self):
        """Return graded assignment to student"""
        if self.status == 'graded':
            self.status = 'returned'
            self.returned_at = datetime.utcnow()
    
    def update_progress(self, devices_placed=None, devices_configured=None, 
                       connections_made=None, cli_history=None):
        """Update progress tracking fields"""
        if devices_placed is not None:
            self.devices_placed = devices_placed
        if devices_configured is not None:
            self.devices_configured = devices_configured
        if connections_made is not None:
            self.connections_made = connections_made
        if cli_history is not None:
            self.cli_history = cli_history
        
        # Auto-start assignment if it's still pending
        if self.status == 'pending':
            self.start_assignment()
    
    def validate_progress(self):
        """
        Validate current progress against task requirements
        Returns validation results and auto-grade score
        """
        if not self.simulation or not self.simulation.task_config:
            return {'valid': False, 'message': 'No task configuration found'}
        
        task_config = self.simulation.task_config
        grading_rubric = task_config.get('grading_rubric', {})
        
        results = {
            'device_placement': self._validate_devices(task_config.get('device_requirements', [])),
            'device_configuration': self._validate_configurations(task_config.get('device_requirements', [])),
            'connections': self._validate_connections(task_config.get('connection_requirements', [])),
            'cli_commands': self._validate_cli_commands(task_config.get('cli_requirements', {}))
        }
        
        # Calculate auto-grade score
        total_score = 0
        total_score += results['device_placement']['score'] * (grading_rubric.get('device_placement', 10) / 100)
        total_score += results['device_configuration']['score'] * (grading_rubric.get('device_configuration', 40) / 100)
        total_score += results['connections']['score'] * (grading_rubric.get('connectivity_tests', 30) / 100)
        total_score += results['cli_commands']['score'] * (grading_rubric.get('cli_accuracy', 20) / 100)
        
        self.validation_results = results
        self.auto_grade_score = Decimal(str(round(total_score, 2)))
        
        return {
            'validation': results,
            'auto_grade_score': float(self.auto_grade_score),
            'completion_percentage': self.completion_percentage
        }
    
    def _validate_devices(self, required_devices):
        """Validate device placement"""
        placed_ids = set(self.devices_placed or [])
        required_ids = set(d['id'] for d in required_devices)
        
        correct_count = len(placed_ids & required_ids)
        total_count = len(required_ids)
        
        return {
            'correct': correct_count,
            'total': total_count,
            'score': (correct_count / total_count * 100) if total_count > 0 else 0,
            'missing': list(required_ids - placed_ids),
            'extra': list(placed_ids - required_ids)
        }
    
    def _validate_configurations(self, required_devices):
        """Validate device configurations"""
        configured = self.devices_configured or {}
        placed_ids = set(self.devices_placed or [])
        correct_count = 0
        total_count = len(required_devices)
        
        details = []
        for req_device in required_devices:
            device_id = req_device['id']
            req_config = req_device.get('required_config', {})
            
            # If no specific configuration is required (None, empty dict, or missing key), just check if device is placed
            if req_config is None or (isinstance(req_config, dict) and len(req_config) == 0):
                if device_id in placed_ids:
                    correct_count += 1
                    details.append({'device': device_id, 'status': 'correct', 'reason': 'device_placed'})
                else:
                    details.append({'device': device_id, 'status': 'missing', 'reason': 'device_not_placed'})
            # If configuration is required, validate it
            else:
                # Device must be in configured dict if config is required
                if device_id in configured:
                    actual_config = configured.get(device_id, {})
                    
                    # Check if required config fields match
                    config_valid = True
                    for key, value in req_config.items():
                        if actual_config.get(key) != value:
                            config_valid = False
                            break
                    
                    if config_valid:
                        correct_count += 1
                        details.append({'device': device_id, 'status': 'correct', 'reason': 'config_matches'})
                    else:
                        details.append({'device': device_id, 'status': 'incorrect', 'reason': 'config_mismatch'})
                elif device_id in placed_ids:
                    # Device is placed but not configured - if device is placed, give partial credit
                    correct_count += 1
                    details.append({'device': device_id, 'status': 'correct', 'reason': 'device_placed_no_config'})
                else:
                    details.append({'device': device_id, 'status': 'missing', 'reason': 'device_not_placed'})
        
        return {
            'correct': correct_count,
            'total': total_count,
            'score': (correct_count / total_count * 100) if total_count > 0 else 0,
            'details': details
        }
    
    def _validate_connections(self, required_connections):
        """Validate network connections with flexible field matching"""
        made_connections = self.connections_made or []
        correct_count = 0
        
        for req_conn in required_connections:
            # Get required source and target (support multiple field names)
            req_source = (req_conn.get('source_device') or req_conn.get('from') or 
                         req_conn.get('device1') or req_conn.get('source'))
            req_target = (req_conn.get('target_device') or req_conn.get('to') or 
                         req_conn.get('device2') or req_conn.get('target'))
            
            if not req_source or not req_target:
                continue
                
            for made_conn in made_connections:
                # Get made connection source and target (support multiple field names)
                made_source = (made_conn.get('source_device') or made_conn.get('from') or 
                             made_conn.get('device1') or made_conn.get('source'))
                made_target = (made_conn.get('target_device') or made_conn.get('to') or 
                             made_conn.get('device2') or made_conn.get('target'))
                
                # Check bidirectional match (A->B or B->A)
                if ((made_source == req_source and made_target == req_target) or
                    (made_source == req_target and made_target == req_source)):
                    correct_count += 1
                    break
        
        total_count = len(required_connections)
        return {
            'correct': correct_count,
            'total': total_count,
            'score': (correct_count / total_count * 100) if total_count > 0 else 0
        }
    
    def _validate_cli_commands(self, required_cli):
        """Validate CLI command execution"""
        executed = self.cli_history or []
        total_required = sum(len(cmds) for cmds in required_cli.values())
        
        if total_required == 0:
            return {'correct': 0, 'total': 0, 'score': 100}
        
        # Simple validation: check if required commands were executed
        required_commands = []
        for device_id, commands in required_cli.items():
            required_commands.extend([cmd['command'] for cmd in commands if cmd.get('required')])
        
        executed_commands = [cmd.get('command', '') for cmd in executed]
        correct_count = sum(1 for req_cmd in required_commands if req_cmd in executed_commands)
        
        return {
            'correct': correct_count,
            'total': len(required_commands),
            'score': (correct_count / len(required_commands) * 100) if required_commands else 0,
            'executed_count': len(executed_commands)
        }
    
    def to_dict(self, include_validation=False, include_simulation=False):
        """Convert to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'simulation_id': self.simulation_id,
            'user_id': self.user_id,
            'class_id': self.class_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'completion_percentage': self.completion_percentage,
            'auto_grade_score': float(self.auto_grade_score),
            'instructor_grade': float(self.instructor_grade) if self.instructor_grade else None,
            'final_score': self.final_score,
            'feedback': self.feedback,
            'is_overdue': self.is_overdue,
            'days_until_due': self.days_until_due,
            'attempt_count': self.attempt_count,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None
        }
        
        if include_validation:
            data['validation_results'] = self.validation_results
            data['devices_placed'] = self.devices_placed
            data['connections_made'] = self.connections_made
            data['cli_history'] = self.cli_history
        
        if include_simulation and self.simulation:
            data['simulation'] = {
                'id': self.simulation.id,
                'title': self.simulation.title,
                'task_config': self.simulation.task_config
            }
        
        return data
