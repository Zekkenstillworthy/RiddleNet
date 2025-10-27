"""
Class Content Models for Dynamic Content Management
Supports announcements, assignments, materials, and other class content
"""

from __init__ import db
from datetime import datetime
import json

class ClassAnnouncement(db.Model):
    """
    Model for storing class announcements
    """
    __tablename__ = 'class_announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    
    # Organization - moved from topic to module
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('instructor_users.id'), nullable=False)
    
    # Relationships
    class_obj = db.relationship('Class', backref='announcements')
    # Removed topic relationship - now using module relationship
    
    def to_dict(self):
        """Convert announcement to dictionary"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'title': self.title,
            'message': self.message,
            'is_published': self.is_published,
            'module_id': self.module_id,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }

class ClassAssignment(db.Model):
    """
    Model for storing class assignments
    """
    __tablename__ = 'class_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    
    # Assignment Details
    due_date = db.Column(db.DateTime, nullable=True)
    points = db.Column(db.Integer, default=100)
    assignment_type = db.Column(db.String(50), default='assignment')  # assignment, quiz, project
    is_published = db.Column(db.Boolean, default=False)
    
    # Submission Settings
    allow_file_uploads = db.Column(db.Boolean, default=True)
    allowed_file_types = db.Column(db.String(500), default='pdf,doc,docx,txt,jpg,png,zip')  # Comma-separated
    max_file_size_mb = db.Column(db.Integer, default=10)  # Maximum file size in MB
    max_files = db.Column(db.Integer, default=5)  # Maximum number of files
    allow_text_submission = db.Column(db.Boolean, default=True)
    allow_late_submissions = db.Column(db.Boolean, default=True)
    late_penalty_per_day = db.Column(db.Float, default=10.0)  # Percentage penalty per day late
    allow_resubmission = db.Column(db.Boolean, default=True)
    
    # Organization - moved from topic to module
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # Related Content
    question_group_id = db.Column(db.Integer, db.ForeignKey('question_groups.id'), nullable=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('instructor_users.id'), nullable=False)
    
    # Relationships
    class_obj = db.relationship('Class', backref='assignments')
    # Removed topic relationship - now using module relationship
    question_group = db.relationship('QuestionGroup', backref='class_assignments')
    
    def to_dict(self):
        """Convert assignment to dictionary"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'points': self.points,
            'assignment_type': self.assignment_type,
            'is_published': self.is_published,
            'allow_file_uploads': getattr(self, 'allow_file_uploads', True),
            'allowed_file_types': getattr(self, 'allowed_file_types', 'pdf,doc,docx,txt,jpg,png,zip'),
            'max_file_size_mb': getattr(self, 'max_file_size_mb', 10),
            'max_files': getattr(self, 'max_files', 5),
            'allow_text_submission': getattr(self, 'allow_text_submission', True),
            'allow_late_submissions': getattr(self, 'allow_late_submissions', True),
            'late_penalty_per_day': getattr(self, 'late_penalty_per_day', 10.0),
            'allow_resubmission': getattr(self, 'allow_resubmission', True),
            'module_id': self.module_id,
            'sort_order': self.sort_order,
            'question_group_id': self.question_group_id,
            'simulation_id': self.simulation_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }

class ClassMaterial(db.Model):
    """
    Model for storing class materials
    """
    __tablename__ = 'class_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Material Details
    material_type = db.Column(db.String(50), default='document')  # document, link, video, image
    file_path = db.Column(db.String(500), nullable=True)
    external_url = db.Column(db.String(500), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)  # in bytes
    mime_type = db.Column(db.String(100), nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    
    # Organization - moved from topic to module
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('instructor_users.id'), nullable=False)
    
    # Relationships
    class_obj = db.relationship('Class', backref='materials')
    # Removed topic relationship - now using module relationship
    
    def to_dict(self):
        """Convert material to dictionary"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'title': self.title,
            'description': self.description,
            'material_type': self.material_type,
            'file_path': self.file_path,
            'external_url': self.external_url,
            'url': self.file_path or self.external_url,  # Combined URL property for template compatibility
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'is_published': self.is_published,
            'module_id': self.module_id,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }

"""
DEPRECATED: ClassTopic model - content is now organized under Modules instead of Topics
Keeping this commented out for migration purposes
"""
"""
class ClassTopic(db.Model):
    \"\"\"
    DEPRECATED: Model for organizing class content into topics
    Content is now organized under Modules instead of Topics
    \"\"\"
    __tablename__ = 'class_topics'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default='#3B82F6')  # Hex color for topic
    is_collapsed = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('instructor_users.id'), nullable=False)
    
    # Relationships
    class_obj = db.relationship('Class', backref='topics')
    
    def to_dict(self):
        \"\"\"Convert topic to dictionary\"\"\"
        # Calculate content count safely
        content_count = 0
        try:
            # Count announcements, assignments, and materials for this topic
            from __init__ import db
            content_count += db.session.query(ClassAnnouncement).filter_by(topic_id=self.id).count()
            content_count += db.session.query(ClassAssignment).filter_by(topic_id=self.id).count()
            content_count += db.session.query(ClassMaterial).filter_by(topic_id=self.id).count()
        except:
            content_count = 0
            
        return {
            'id': self.id,
            'class_id': self.class_id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'is_collapsed': self.is_collapsed,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'content_count': content_count
        }
"""
