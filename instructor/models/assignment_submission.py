"""
Assignment Submission Models
Handles student assignment submissions, file uploads, and grading
"""

from datetime import datetime
from __init__ import db

class AssignmentSubmission(db.Model):
    """
    Model for student assignment submissions
    """
    __tablename__ = 'assignment_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('class_assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Changed from 'users' to 'user'
    
    # Submission Details
    submission_text = db.Column(db.Text, nullable=True)  # Text submission content
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status and Grading
    status = db.Column(db.String(20), default='submitted')  # submitted, graded, returned, late
    grade = db.Column(db.Float, nullable=True)  # Points earned
    max_points = db.Column(db.Integer, nullable=True)  # Points possible (copied from assignment)
    
    # Instructor Feedback
    feedback = db.Column(db.Text, nullable=True)
    graded_at = db.Column(db.DateTime, nullable=True)
    # Grading information
    graded_by = db.Column(db.Integer, db.ForeignKey('instructor_users.id'), nullable=True)
    
    # Late Submission Handling
    is_late = db.Column(db.Boolean, default=False)
    late_penalty_applied = db.Column(db.Float, default=0.0)  # Percentage penalty
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Using foreign_keys to be explicit about the join conditions
    assignment = db.relationship('ClassAssignment', backref='submissions')
    # Note: We'll use student_id directly rather than a relationship to avoid import issues
    # student = db.relationship('User', foreign_keys=[student_id], backref='assignment_submissions')
    grader = db.relationship('InstructorUser', foreign_keys=[graded_by], backref='graded_submissions')
    
    def to_dict(self):
        """Convert submission to dictionary"""
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'submission_text': self.submission_text,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'status': self.status,
            'grade': self.grade,
            'max_points': self.max_points,
            'feedback': self.feedback,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'graded_by': self.graded_by,
            'is_late': self.is_late,
            'late_penalty_applied': self.late_penalty_applied,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'attachments': [attachment.to_dict() for attachment in self.attachments]
        }

class SubmissionAttachment(db.Model):
    """
    Model for file attachments to assignment submissions
    """
    __tablename__ = 'submission_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('assignment_submissions.id'), nullable=False)
    
    # File Details
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)  # UUID-based filename
    file_path = db.Column(db.String(500), nullable=False)  # Relative path from uploads/
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100), nullable=False)
    
    # File Validation
    is_valid = db.Column(db.Boolean, default=True)
    validation_error = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = db.relationship('AssignmentSubmission', backref='attachments')
    
    def to_dict(self):
        """Convert attachment to dictionary"""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'is_valid': self.is_valid,
            'validation_error': self.validation_error,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'download_url': f'/api/submissions/attachments/{self.id}/download'
        }

class AssignmentSubmissionHistory(db.Model):
    """
    Model for tracking submission history and versions
    """
    __tablename__ = 'assignment_submission_history'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('assignment_submissions.id'), nullable=False)
    
    # Change Tracking
    action = db.Column(db.String(50), nullable=False)  # submitted, resubmitted, graded, updated
    old_grade = db.Column(db.Float, nullable=True)
    new_grade = db.Column(db.Float, nullable=True)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=True)
    
    # Who made the change
    changed_by = db.Column(db.Integer, nullable=False)  # User ID (student or instructor)
    changed_by_type = db.Column(db.String(10), nullable=False)  # 'student' or 'instructor'
    
    # Notes
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamp
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = db.relationship('AssignmentSubmission', backref='history')
    
    def to_dict(self):
        """Convert history entry to dictionary"""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'action': self.action,
            'old_grade': self.old_grade,
            'new_grade': self.new_grade,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'changed_by': self.changed_by,
            'changed_by_type': self.changed_by_type,
            'notes': self.notes,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None
        }
