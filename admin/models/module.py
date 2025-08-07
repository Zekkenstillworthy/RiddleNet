"""
Module and Lesson Models for Dynamic Course Structure
Supports hierarchical learning organization with sequential progression
Includes user session tracking integration
"""

from admin import db
from datetime import datetime
import json
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import or_, and_

class Module(db.Model):
    """
    Course Module Model - represents major learning units
    Example: "Module 1: Computer Network Fundamentals", "Module 2: OSI Model"
    """
    __tablename__ = 'modules'
    __table_args__ = {'extend_existing': True}
    
    # Basic Information
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    module_number = db.Column(db.String(10), nullable=False, index=True)  # "1", "1.1", "2", etc.
    course_type = db.Column(db.String(50), nullable=False, index=True)  # "Networking 1", "Networking 2"
    
    # Learning Structure
    learning_objectives = db.Column(JSON, default=list)
    prerequisites = db.Column(JSON, default=list)
    estimated_duration = db.Column(db.Integer, default=60)  # minutes
    
    # Hierarchy and Ordering
    parent_module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=True)
    order_index = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)  # 1=main module, 2=sub-module, etc.
    
    # Class Integration
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=True)
    
    # Status and Settings
    is_active = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=True)
    requires_sequential_completion = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='module', lazy='dynamic', 
                            order_by='Lesson.order_index', cascade='all, delete-orphan')
    children = db.relationship('Module', backref=db.backref('parent', remote_side=[id]), 
                             lazy='dynamic', order_by='Module.order_index')
    user_progress = db.relationship('ModuleProgress', backref='module', lazy='dynamic')
    
    def __repr__(self):
        return f"Module('{self.module_number}', '{self.title}', '{self.course_type}')"
    
    @property
    def full_title(self):
        """Get formatted title with module number"""
        return f"Module {self.module_number}: {self.title}"
    
    @property
    def total_lessons(self):
        """Get total number of lessons in this module"""
        return self.lessons.filter_by(is_active=True).count()
    
    @property
    def total_simulations(self):
        """Get total number of simulations across all lessons"""
        return sum(lesson.simulation_count for lesson in self.lessons if lesson.is_active)
    
    def get_user_progress(self, user_id):
        """Get user's progress in this module"""
        progress = self.user_progress.filter_by(user_id=user_id).first()
        if not progress:
            return {
                'completed_lessons': 0,
                'total_lessons': self.total_lessons,
                'progress_percentage': 0,
                'is_completed': False,
                'current_lesson': None
            }
        
        return {
            'completed_lessons': progress.completed_lessons,
            'total_lessons': self.total_lessons,
            'progress_percentage': progress.progress_percentage,
            'is_completed': progress.is_completed,
            'current_lesson': progress.current_lesson_id
        }
    
    def is_unlocked_for_user(self, user_id):
        """Check if module is unlocked for user based on sequential requirements"""
        if not self.requires_sequential_completion:
            return True
        
        # Check if previous module is completed
        if self.parent_module_id:
            parent_progress = Module.query.get(self.parent_module_id).get_user_progress(user_id)
            return parent_progress['is_completed']
        
        # Check previous modules in same course
        prev_modules = Module.query.filter(
            Module.course_type == self.course_type,
            Module.order_index < self.order_index,
            Module.level == self.level,
            Module.is_active == True
        ).all()
        
        for prev_module in prev_modules:
            prev_progress = prev_module.get_user_progress(user_id)
            if not prev_progress['is_completed']:
                return False
        
        return True
    
    def to_dict(self, include_lessons=False, user_id=None):
        """Convert module to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'full_title': self.full_title,
            'description': self.description,
            'module_number': self.module_number,
            'course_type': self.course_type,
            'learning_objectives': self.learning_objectives,
            'estimated_duration': self.estimated_duration,
            'order_index': self.order_index,
            'level': self.level,
            'total_lessons': self.total_lessons,
            'total_simulations': self.total_simulations,
            'is_active': self.is_active,
            'is_published': self.is_published,
            'requires_sequential_completion': self.requires_sequential_completion
        }
        
        if user_id:
            data['user_progress'] = self.get_user_progress(user_id)
            data['is_unlocked'] = self.is_unlocked_for_user(user_id)
        
        if include_lessons:
            data['lessons'] = [lesson.to_dict(user_id=user_id) for lesson in self.lessons if lesson.is_active]
        
        return data


class Lesson(db.Model):
    """
    Individual Lesson Model - represents specific learning topics within modules
    Example: "1.1: Introduction to Networks", "1.2: Network Types"
    """
    __tablename__ = 'lessons'
    __table_args__ = {'extend_existing': True}
    
    # Basic Information
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    lesson_number = db.Column(db.String(10), nullable=False, index=True)  # "1.1", "1.2", etc.
    
    # Content
    content = db.Column(db.Text, nullable=True)  # HTML content for the lesson
    learning_objectives = db.Column(JSON, default=list)
    key_concepts = db.Column(JSON, default=list)
    
    # Module Relationship
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    order_index = db.Column(db.Integer, default=0)
    
    # Simulation Integration
    simulation_ids = db.Column(JSON, default=list)  # List of simulation IDs for this lesson
    
    # Settings
    estimated_duration = db.Column(db.Integer, default=30)  # minutes
    is_active = db.Column(db.Boolean, default=True)
    requires_simulation_completion = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_progress = db.relationship('LessonProgress', backref='lesson', lazy='dynamic')
    
    def __repr__(self):
        return f"Lesson('{self.lesson_number}', '{self.title}')"
    
    @property
    def full_title(self):
        """Get formatted title with lesson number"""
        return f"Lesson {self.lesson_number}: {self.title}"
    
    @property
    def simulation_count(self):
        """Get number of simulations in this lesson"""
        return len(self.simulation_ids) if self.simulation_ids else 0
    
    def get_simulations(self):
        """Get simulation objects for this lesson"""
        if not self.simulation_ids:
            return []
        
        from admin.models.simulation import Simulation
        return Simulation.query.filter(
            Simulation.id.in_(self.simulation_ids),
            Simulation.is_active == True,
            Simulation.is_published == True
        ).order_by(Simulation.title).all()
    
    def get_user_progress(self, user_id):
        """Get user's progress in this lesson"""
        progress = self.user_progress.filter_by(user_id=user_id).first()
        if not progress:
            return {
                'completed_simulations': 0,
                'total_simulations': self.simulation_count,
                'progress_percentage': 0,
                'is_completed': False,
                'started_at': None,
                'completed_at': None
            }
        
        return {
            'completed_simulations': progress.completed_simulations,
            'total_simulations': self.simulation_count,
            'progress_percentage': progress.progress_percentage,
            'is_completed': progress.is_completed,
            'started_at': progress.started_at,
            'completed_at': progress.completed_at
        }
    
    def is_unlocked_for_user(self, user_id):
        """Check if lesson is unlocked for user"""
        # Check if previous lesson in module is completed
        prev_lesson = Lesson.query.filter(
            Lesson.module_id == self.module_id,
            Lesson.order_index < self.order_index,
            Lesson.is_active == True
        ).order_by(Lesson.order_index.desc()).first()
        
        if prev_lesson:
            prev_progress = prev_lesson.get_user_progress(user_id)
            return prev_progress['is_completed']
        
        return True
    
    def to_dict(self, user_id=None, include_simulations=False):
        """Convert lesson to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'full_title': self.full_title,
            'description': self.description,
            'lesson_number': self.lesson_number,
            'content': self.content,
            'learning_objectives': self.learning_objectives,
            'key_concepts': self.key_concepts,
            'simulation_count': self.simulation_count,
            'estimated_duration': self.estimated_duration,
            'order_index': self.order_index,
            'is_active': self.is_active,
            'requires_simulation_completion': self.requires_simulation_completion
        }
        
        if user_id:
            data['user_progress'] = self.get_user_progress(user_id)
            data['is_unlocked'] = self.is_unlocked_for_user(user_id)
        
        if include_simulations:
            data['simulations'] = [sim.to_dict() for sim in self.get_simulations()]
        
        return data


class ModuleProgress(db.Model):
    """
    Track user progress through modules with session integration
    """
    __tablename__ = 'module_progress'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    
    # Progress Tracking
    completed_lessons = db.Column(db.Integer, default=0)
    progress_percentage = db.Column(db.Float, default=0.0)
    is_completed = db.Column(db.Boolean, default=False)
    current_lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    
    # Session Tracking
    total_time_spent = db.Column(db.Integer, default=0)  # Total time in seconds
    session_count = db.Column(db.Integer, default=0)  # Number of sessions in this module
    last_session_id = db.Column(db.String(255), nullable=True)  # Last session that accessed this module
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    def update_progress(self, session_id=None):
        """Update progress based on completed lessons and session data"""
        total_lessons = self.module.total_lessons
        if total_lessons > 0:
            self.progress_percentage = (self.completed_lessons / total_lessons) * 100
            self.is_completed = self.completed_lessons >= total_lessons
            
            if self.is_completed and not self.completed_at:
                self.completed_at = datetime.utcnow()
        
        self.last_accessed = datetime.utcnow()
        
        # Update session tracking
        if session_id and session_id != self.last_session_id:
            self.session_count += 1
            self.last_session_id = session_id
    
    def add_session_time(self, seconds):
        """Add time spent in this module during a session"""
        self.total_time_spent += seconds
        self.last_accessed = datetime.utcnow()
    
    @property
    def total_time_hours(self):
        """Get total time spent in hours"""
        return round(self.total_time_spent / 3600, 2) if self.total_time_spent else 0
    
    @property
    def total_time_minutes(self):
        """Get total time spent in minutes"""
        return round(self.total_time_spent / 60, 1) if self.total_time_spent else 0


class LessonProgress(db.Model):
    """
    Track user progress through individual lessons with session integration
    """
    __tablename__ = 'lesson_progress'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    
    # Progress Tracking
    completed_simulations = db.Column(db.Integer, default=0)
    progress_percentage = db.Column(db.Float, default=0.0)
    is_completed = db.Column(db.Boolean, default=False)
    
    # Session Tracking
    total_time_spent = db.Column(db.Integer, default=0)  # Total time in seconds
    session_count = db.Column(db.Integer, default=0)  # Number of sessions in this lesson
    last_session_id = db.Column(db.String(255), nullable=True)  # Last session that accessed this lesson
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    def update_progress(self, session_id=None):
        """Update progress based on completed simulations and session data"""
        total_simulations = self.lesson.simulation_count
        if total_simulations > 0:
            self.progress_percentage = (self.completed_simulations / total_simulations) * 100
            self.is_completed = self.completed_simulations >= total_simulations
            
            if self.is_completed and not self.completed_at:
                self.completed_at = datetime.utcnow()
        
        self.last_accessed = datetime.utcnow()
        
        # Update session tracking
        if session_id and session_id != self.last_session_id:
            self.session_count += 1
            self.last_session_id = session_id
    
    def add_session_time(self, seconds):
        """Add time spent in this lesson during a session"""
        self.total_time_spent += seconds
        self.last_accessed = datetime.utcnow()
    
    @property
    def total_time_minutes(self):
        """Get total time spent in minutes"""
        return round(self.total_time_spent / 60, 1) if self.total_time_spent else 0
