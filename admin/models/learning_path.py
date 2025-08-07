"""
Disabled Learning Path Models - Feature Removed
===============================================

This file contains placeholder models to prevent import errors.
The Learning Path feature has been completely removed from RiddleNet.
"""

from admin import db

class LearningPath:
    """Placeholder class - Learning Paths feature removed"""
    
    @staticmethod
    def query():
        """Return empty query object"""
        return EmptyQuery()

class LearningPathSimulation:
    """Placeholder class - Learning Paths feature removed"""
    
    @staticmethod
    def query():
        """Return empty query object"""
        return EmptyQuery()

class UserLearningProgress:
    """Placeholder class - Learning Paths feature removed"""
    
    @staticmethod
    def query():
        """Return empty query object"""
        return EmptyQuery()

class EmptyQuery:
    """Empty query object that returns no results"""
    
    def filter_by(self, **kwargs):
        return self
    
    def filter(self, *args):
        return self
    
    def order_by(self, *args):
        return self
    
    def all(self):
        return []
    
    def first(self):
        return None
    
    def get(self, id):
        return None
    
    def get_or_404(self, id):
        from flask import abort
        abort(404)
    
    def count(self):
        return 0
