from admin import db
from datetime import datetime

# Association table for many-to-many relationship between classes and Quiz
class_question_groups = db.Table('class_question_groups',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('question_group_id', db.Integer, db.ForeignKey('question_groups.id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

# Association table for many-to-many relationship between classes and students (users)
# IMPORTANT: This is defined here to break circular imports
class_students = db.Table('class_students',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('joined_date', db.DateTime, default=datetime.utcnow),
    db.Column('status', db.String(20), default='active'),  # active, inactive, pending
    extend_existing=True
)

class Class(db.Model):
    """Class model for managing student classes"""
    __tablename__ = 'classes'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(20), nullable=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    max_students = db.Column(db.Integer, default=30)
    status = db.Column(db.String(20), default='active')  # active, inactive, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Ownership: which admin created/owns this class
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)

    # Optional relationship to the Admin who created the class. Use string import to avoid circular import.
    creator = db.relationship('Admin', backref=db.backref('created_classes', lazy='dynamic'), foreign_keys=[created_by])
    
    # Relationships
    question_groups = db.relationship(
        'QuestionGroup',
        secondary=class_question_groups,
        backref=db.backref('classes', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # Use string-based relationship to avoid circular imports
    # The backref will be available on User model as 'enrolled_classes'
    students = db.relationship(
        'User',
        secondary=class_students,
        backref=db.backref('enrolled_classes', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f"<Class {self.name} ({self.code})>"
    
    def to_dict(self):
        """Convert class object to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'section': self.section,
            'code': self.code,
            'description': self.description,
            'createdBy': self.created_by,
            'createdByUsername': getattr(self.creator, 'username', None) if getattr(self, 'creator', None) else None,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'maxStudents': self.max_students,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'questionGroups': [qg.id for qg in self.question_groups] if self.question_groups else [],
            'studentCount': self.students.count() if self.students else 0
        }
        
    def to_dict_with_question_groups(self):
        """Convert class object to dictionary with detailed Quiz data"""
        data = self.to_dict()
        
        # Add detailed Quiz data
        question_groups_data = []
        for qg in self.question_groups:
            question_types = set()
            question_count = 0
            
            # Extract question types if the relationship exists
            if hasattr(qg, 'questions'):
                question_count = len(qg.questions)
                for q in qg.questions:
                    if hasattr(q, 'type'):
                        question_types.add(q.type)
                    elif hasattr(q, 'question_type'):
                        question_types.add(q.question_type)
            
            question_groups_data.append({
                'id': qg.id,
                'name': qg.name,
                'description': qg.description,
                'question_count': question_count,
                'question_types': list(question_types)
            })
        
        data['questionGroupsDetailed'] = question_groups_data
        return data