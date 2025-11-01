"""
Advanced Deadline and Late Policy Models
Supports sophisticated penalty structures, availability windows, and deadline management
"""

from __init__ import db
from datetime import datetime, timedelta
import json

class DeadlinePolicy(db.Model):
    """
    Model for sophisticated deadline and late submission policies
    """
    __tablename__ = 'deadline_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Policy Type
    policy_type = db.Column(db.String(50), default='tiered')  # simple, tiered, exponential, fixed
    
    # Simple Policy (single percentage per day)
    simple_penalty_per_day = db.Column(db.Float, default=10.0)
    
    # Maximum Penalty Cap
    max_penalty_percentage = db.Column(db.Float, default=100.0)  # Maximum penalty (100% = zero points)
    
    # Grace Period
    grace_period_hours = db.Column(db.Integer, default=0)  # Hours after due date with no penalty
    
    # Cutoff Settings
    hard_cutoff_enabled = db.Column(db.Boolean, default=False)  # No submissions after cutoff
    hard_cutoff_days = db.Column(db.Integer, default=7)  # Days after due date for hard cutoff
    
    # Weekend/Holiday Considerations
    exclude_weekends = db.Column(db.Boolean, default=False)  # Don't count weekends in penalty calculation
    exclude_holidays = db.Column(db.Boolean, default=False)  # Don't count holidays
    
    # Advanced Settings
    allow_partial_credit = db.Column(db.Boolean, default=True)  # Allow partial credit for late submissions
    round_penalty_up = db.Column(db.Boolean, default=False)  # Round penalties up to next whole number
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('instructor_users.id'), nullable=False)
    
    def _frontend_type(self):
        """Return simplified type label for UI consumption."""
        if self.policy_type == 'fixed':
            return 'fixed'
        if self.policy_type == 'simple':
            if self.hard_cutoff_enabled and ((self.hard_cutoff_days or 0) == 0 or (self.simple_penalty_per_day or 0) >= 100):
                return 'zero'
            return 'grace' if (self.grace_period_hours or 0) > 0 else 'percentage'
        if self.policy_type in {'tiered', 'exponential'}:
            return self.policy_type
        return self.policy_type or 'percentage'

    def to_dict(self):
        """Convert policy to dictionary"""
        penalty_rate = None
        if self.simple_penalty_per_day is not None:
            penalty_rate = round(self.simple_penalty_per_day, 2)

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'policy_type': self.policy_type,
            'type': self._frontend_type(),
            'penalty_rate': penalty_rate,
            'penalty_interval': getattr(self, 'penalty_interval', 'day'),
            'is_default': getattr(self, 'is_default', False),
            'simple_penalty_per_day': self.simple_penalty_per_day,
            'max_penalty_percentage': self.max_penalty_percentage,
            'grace_period_hours': self.grace_period_hours,
            'hard_cutoff_enabled': self.hard_cutoff_enabled,
            'hard_cutoff_days': self.hard_cutoff_days,
            'exclude_weekends': self.exclude_weekends,
            'exclude_holidays': self.exclude_holidays,
            'allow_partial_credit': self.allow_partial_credit,
            'round_penalty_up': self.round_penalty_up,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'penalty_tiers': [tier.to_dict() for tier in self.penalty_tiers]
        }

class PenaltyTier(db.Model):
    """
    Model for tiered penalty structures (e.g., 5% for days 1-2, 10% for days 3-5, etc.)
    """
    __tablename__ = 'penalty_tiers'
    
    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('deadline_policies.id'), nullable=False)
    
    # Tier Settings
    start_day = db.Column(db.Integer, nullable=False)  # Start day for this tier (1 = first day late)
    end_day = db.Column(db.Integer, nullable=True)  # End day for this tier (None = unlimited)
    penalty_percentage = db.Column(db.Float, nullable=False)  # Penalty percentage for this tier
    penalty_type = db.Column(db.String(20), default='per_day')  # per_day, flat, cumulative
    
    # Tier Description
    description = db.Column(db.String(255), nullable=True)
    
    # Relationships
    policy = db.relationship('DeadlinePolicy', backref='penalty_tiers')
    
    def to_dict(self):
        """Convert tier to dictionary"""
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'start_day': self.start_day,
            'end_day': self.end_day,
            'penalty_percentage': self.penalty_percentage,
            'penalty_type': self.penalty_type,
            'description': self.description
        }

class AssignmentAvailabilityWindow(db.Model):
    """
    Model for assignment availability windows and access controls
    """
    __tablename__ = 'assignment_availability_windows'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('class_assignments.id'), nullable=False)
    
    # Availability Window
    available_from = db.Column(db.DateTime, nullable=True)  # When assignment becomes available
    available_until = db.Column(db.DateTime, nullable=True)  # When assignment becomes unavailable
    
    # Due Date Management
    due_date = db.Column(db.DateTime, nullable=True)  # Primary due date
    extended_due_date = db.Column(db.DateTime, nullable=True)  # Extended due date for accommodations
    
    # Late Submission Settings
    late_submission_enabled = db.Column(db.Boolean, default=True)
    late_submission_until = db.Column(db.DateTime, nullable=True)  # Hard cutoff for late submissions
    
    # Penalty Policy
    deadline_policy_id = db.Column(db.Integer, db.ForeignKey('deadline_policies.id'), nullable=True)
    custom_penalty_enabled = db.Column(db.Boolean, default=False)
    custom_penalty_per_day = db.Column(db.Float, nullable=True)
    
    # Access Controls
    require_password = db.Column(db.Boolean, default=False)
    access_password = db.Column(db.String(255), nullable=True)
    ip_restrictions = db.Column(db.Text, nullable=True)  # JSON array of allowed IP ranges
    
    # Time Limits
    time_limit_enabled = db.Column(db.Boolean, default=False)
    time_limit_minutes = db.Column(db.Integer, nullable=True)  # Time limit for completion
    
    # Attempts
    max_attempts = db.Column(db.Integer, default=1)  # Maximum submission attempts
    allow_save_and_resume = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignment = db.relationship('ClassAssignment', backref='availability_window', uselist=False)
    deadline_policy = db.relationship('DeadlinePolicy', backref='assignments')
    
    def to_dict(self):
        """Convert availability window to dictionary"""
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'available_until': self.available_until.isoformat() if self.available_until else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'extended_due_date': self.extended_due_date.isoformat() if self.extended_due_date else None,
            'late_submission_enabled': self.late_submission_enabled,
            'late_submission_until': self.late_submission_until.isoformat() if self.late_submission_until else None,
            'deadline_policy_id': self.deadline_policy_id,
            'custom_penalty_enabled': self.custom_penalty_enabled,
            'custom_penalty_per_day': self.custom_penalty_per_day,
            'require_password': self.require_password,
            'ip_restrictions': json.loads(self.ip_restrictions) if self.ip_restrictions else [],
            'time_limit_enabled': self.time_limit_enabled,
            'time_limit_minutes': self.time_limit_minutes,
            'max_attempts': self.max_attempts,
            'allow_save_and_resume': self.allow_save_and_resume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_available_now(self):
        """Check if assignment is currently available"""
        now = datetime.utcnow()
        
        if self.available_from and now < self.available_from:
            return False
            
        if self.available_until and now > self.available_until:
            return False
            
        return True
    
    def is_past_due(self):
        """Check if assignment is past due"""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date
    
    def can_submit_late(self):
        """Check if late submissions are allowed"""
        if not self.late_submission_enabled:
            return False
            
        if self.late_submission_until:
            return datetime.utcnow() <= self.late_submission_until
            
        return True

class StudentDeadlineExtension(db.Model):
    """
    Model for individual student deadline extensions and accommodations
    """
    __tablename__ = 'student_deadline_extensions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('class_assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Extension Details
    original_due_date = db.Column(db.DateTime, nullable=False)
    extended_due_date = db.Column(db.DateTime, nullable=False)
    extension_hours = db.Column(db.Integer, nullable=False)  # Total hours of extension
    
    # Reason and Approval
    reason = db.Column(db.Text, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('instructor_users.id'), nullable=False)
    approval_notes = db.Column(db.Text, nullable=True)
    
    # Penalty Override
    waive_late_penalty = db.Column(db.Boolean, default=False)
    custom_penalty_rate = db.Column(db.Float, nullable=True)  # Custom penalty rate for this student
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    used = db.Column(db.Boolean, default=False)  # Whether student has submitted with this extension
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignment = db.relationship('ClassAssignment', backref='deadline_extensions')
    approver = db.relationship('InstructorUser', foreign_keys=[approved_by], backref='granted_extensions')
    
    def to_dict(self):
        """Convert extension to dictionary"""
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'original_due_date': self.original_due_date.isoformat() if self.original_due_date else None,
            'extended_due_date': self.extended_due_date.isoformat() if self.extended_due_date else None,
            'extension_hours': self.extension_hours,
            'reason': self.reason,
            'approved_by': self.approved_by,
            'approval_notes': self.approval_notes,
            'waive_late_penalty': self.waive_late_penalty,
            'custom_penalty_rate': self.custom_penalty_rate,
            'is_active': self.is_active,
            'used': self.used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DeadlineCalculationLog(db.Model):
    """
    Model for logging deadline penalty calculations for auditing and transparency
    """
    __tablename__ = 'deadline_calculation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('assignment_submissions.id'), nullable=False)
    
    # Calculation Details
    due_date = db.Column(db.DateTime, nullable=False)
    submission_date = db.Column(db.DateTime, nullable=False)
    days_late = db.Column(db.Float, nullable=False)  # Can be fractional
    hours_late = db.Column(db.Float, nullable=False)
    
    # Policy Applied
    policy_id = db.Column(db.Integer, db.ForeignKey('deadline_policies.id'), nullable=True)
    policy_name = db.Column(db.String(255), nullable=True)
    
    # Penalty Calculation
    base_penalty_percentage = db.Column(db.Float, nullable=False)
    applied_penalty_percentage = db.Column(db.Float, nullable=False)
    grace_period_applied = db.Column(db.Boolean, default=False)
    extension_applied = db.Column(db.Boolean, default=False)
    extension_id = db.Column(db.Integer, db.ForeignKey('student_deadline_extensions.id'), nullable=True)
    
    # Score Impact
    original_score = db.Column(db.Float, nullable=True)
    penalty_amount = db.Column(db.Float, nullable=True)
    final_score = db.Column(db.Float, nullable=True)
    
    # Calculation Method
    calculation_method = db.Column(db.String(100), nullable=False)  # simple, tiered, exponential, etc.
    calculation_details = db.Column(db.Text, nullable=True)  # JSON with detailed breakdown
    
    # Timestamps
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = db.relationship('AssignmentSubmission', backref='penalty_logs')
    policy = db.relationship('DeadlinePolicy', backref='calculation_logs')
    extension = db.relationship('StudentDeadlineExtension', backref='calculation_logs')
    
    def to_dict(self):
        """Convert calculation log to dictionary"""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None,
            'days_late': self.days_late,
            'hours_late': self.hours_late,
            'policy_id': self.policy_id,
            'policy_name': self.policy_name,
            'base_penalty_percentage': self.base_penalty_percentage,
            'applied_penalty_percentage': self.applied_penalty_percentage,
            'grace_period_applied': self.grace_period_applied,
            'extension_applied': self.extension_applied,
            'extension_id': self.extension_id,
            'original_score': self.original_score,
            'penalty_amount': self.penalty_amount,
            'final_score': self.final_score,
            'calculation_method': self.calculation_method,
            'calculation_details': json.loads(self.calculation_details) if self.calculation_details else {},
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }
