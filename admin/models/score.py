from datetime import datetime
from __init__ import db
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

class AdminScore(db.Model):
    """
    Score model for the admin section - references admin_users table
    """
    __tablename__ = 'admin_scores'
    
    id = Column(Integer, primary_key=True)
    score = Column(Float, nullable=False)  # Changed to float based on your data
    date_attempted = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('admin_users.id'), nullable=False)
    category = Column(String(50), nullable=True, default='riddle')
    
    # Define user relationship explicitly with a string
    # We'll use a query-time join instead of a persistent relationship
    def get_user(self):
        """Get the user associated with this score"""
        from admin.models.user import AdminUser
        return AdminUser.query.get(self.user_id)
    
    # Add a property to mimic the relationship behavior for the template
    @property
    def user(self):
        """Property that returns the user object - used by templates"""
        user = self.get_user()
        # Sometimes the relationship might be broken, so provide a fallback
        if not user:
            print(f"Warning: User with ID {self.user_id} not found for score {self.id}")
            from admin.models.user import AdminUser
            # Create a dummy user object for templates
            dummy = AdminUser()
            dummy.id = self.user_id
            dummy.username = f"User {self.user_id}"
            return dummy
        return user
    
    def __repr__(self):
        return f'<Score {self.id}: {self.score}>'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        user_obj = self.user
        user_data = None
        if user_obj:
            user_data = {
                'id': user_obj.id, 
                'username': user_obj.username if hasattr(user_obj, 'username') else f'User {user_obj.id}'
            }
            
        return {
            'id': self.id,
            'score': self.score,
            'date_attempted': self.date_attempted.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': self.user_id,
            'category': self.category,
            'user': user_data
        }
