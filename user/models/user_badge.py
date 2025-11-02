"""
User Badge Model - MVP
Track badge awards for user achievements
"""
from __init__ import db
from datetime import datetime


class UserBadge(db.Model):
    """
    Track badges earned by users through challenge completions
    """
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_id = db.Column(db.String(50), nullable=False, index=True)  # 'cable_master', 'osi_master', etc.
    
    # Badge information
    badge_name = db.Column(db.String(100), nullable=False)
    badge_description = db.Column(db.String(255), nullable=True)
    badge_rarity = db.Column(db.String(20), nullable=True)  # 'common', 'rare', 'legendary'
    
    # Earning information
    challenge_type = db.Column(db.String(50), nullable=False)  # Which challenge unlocked this badge
    earned_score = db.Column(db.Float, nullable=False)  # Score that unlocked the badge
    earned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Metadata (renamed from 'metadata' to avoid SQLAlchemy reserved word)
    badge_metadata = db.Column(db.JSON, nullable=True)  # Additional info like mode, difficulty
    
    # Relationships
    user = db.relationship('User', backref=db.backref('badges', lazy='dynamic'))
    
    # Composite unique constraint - one badge per user per badge_id
    __table_args__ = (
        db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),
    )
    
    def __repr__(self):
        return f'<UserBadge {self.user_id}-{self.badge_id}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'badge_name': self.badge_name,
            'badge_description': self.badge_description,
            'badge_rarity': self.badge_rarity,
            'challenge_type': self.challenge_type,
            'earned_score': self.earned_score,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
            'badge_metadata': self.badge_metadata
        }
    
    @staticmethod
    def award_badge(user_id, badge_id, badge_name, badge_description, challenge_type, 
                    earned_score, badge_rarity='common', metadata=None):
        """
        Award a badge to a user (if they don't already have it)
        Returns: (badge, is_new)
        """
        # Check if badge already exists
        existing_badge = UserBadge.query.filter_by(
            user_id=user_id,
            badge_id=badge_id
        ).first()
        
        if existing_badge:
            return existing_badge, False
        
        # Create new badge
        badge = UserBadge(
            user_id=user_id,
            badge_id=badge_id,
            badge_name=badge_name,
            badge_description=badge_description,
            badge_rarity=badge_rarity,
            challenge_type=challenge_type,
            earned_score=earned_score,
            badge_metadata=metadata or {}
        )
        
        db.session.add(badge)
        db.session.commit()
        
        return badge, True
    
    @staticmethod
    def get_user_badges(user_id):
        """Get all badges for a user"""
        return UserBadge.query.filter_by(user_id=user_id).order_by(UserBadge.earned_at.desc()).all()
    
    @staticmethod
    def has_badge(user_id, badge_id):
        """Check if user has a specific badge"""
        return UserBadge.query.filter_by(user_id=user_id, badge_id=badge_id).first() is not None


# Badge definitions
BADGE_DEFINITIONS = {
    'cable_master': {
        'name': 'Cable Master',
        'description': 'Perfect Score in Cable Crimping!',
        'rarity': 'legendary',
        'image': 'img/Cable_Badge.png',
        'requirements': 'Score 100% in Crimping Simulation'
    },
    'crimping_expert': {
        'name': 'Crimping Expert',
        'description': 'Master of Rollover Cables!',
        'rarity': 'rare',
        'image': 'img/Cable_Badge.png',
        'requirements': 'Score 100% on Rollover (Hard) mode'
    },
    'osi_tcp_master': {
        'name': 'OSI & TCP/IP Master',
        'description': 'Perfect Score in OSI Model Simulation!',
        'rarity': 'legendary',
        'image': 'img/OSI_Badge.png',
        'requirements': 'Score 100% in OSI Simulation'
    },
    'layer_master': {
        'name': 'Layer Master',
        'description': 'Expert Understanding of Network Layers!',
        'rarity': 'rare',
        'image': 'img/OSI_Badge.png',
        'requirements': 'Score 100% in OSI Simulation'
    },
    'troubleshooting_pro': {
        'name': 'Troubleshooting Pro',
        'description': 'Zero Mistakes Achievement!',
        'rarity': 'legendary',
        'image': 'img/Troubleshoot_Badge.png',
        'requirements': 'Complete Link Up with perfect score'
    },
    'network_detective': {
        'name': 'Network Detective',
        'description': 'Strong Troubleshooting Skills!',
        'rarity': 'rare',
        'image': 'img/Troubleshoot_Badge.png',
        'requirements': 'Score 100% in Link Up'
    },
    'quiz_champion': {
        'name': 'Quiz Champion',
        'description': 'Perfect Quiz Performance!',
        'rarity': 'legendary',
        'image': 'img/Quiz_Badge.png',
        'requirements': 'Answer all quiz questions correctly'
    },
    'quiz_master': {
        'name': 'Quiz Master',
        'description': 'Excellent Quiz Knowledge!',
        'rarity': 'rare',
        'image': 'img/Quiz_Badge.png',
        'requirements': 'Score 100% in Quiz Challenge'
    }
}
