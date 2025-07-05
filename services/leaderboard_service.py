"""
Live Leaderboard Service for RiddleNet
Handles real-time leaderboard updates and calculations
"""

import datetime
from sqlalchemy import func, desc
from __init__ import db


class LeaderboardService:
    """Optimized leaderboard service for real-time updates"""
    
    @staticmethod
    def get_live_leaderboard(category='all', time_period='all_time', limit=50):
        """Get optimized leaderboard data with caching"""
        try:
            from user.models.score import Score
            from user.models.user import User
            
            # Build base query with proper joins and indexes
            base_query = db.session.query(
                User.id.label('user_id'),
                User.username,
                User.profile_img,
                func.max(Score.score).label('best_score'),
                func.max(Score.date_attempted).label('latest_attempt'),
                Score.category
            ).select_from(User).join(Score, User.id == Score.user_id)
            
            # Apply category filter
            if category and category != 'all':
                base_query = base_query.filter(Score.category == category)
            
            # Apply time period filter
            if time_period != 'all_time':
                cutoff_date = LeaderboardService._get_time_cutoff(time_period)
                base_query = base_query.filter(Score.date_attempted >= cutoff_date)
            
            # Group by user and get their best score
            results = base_query.group_by(
                User.id, 
                User.username, 
                User.profile_img,
                Score.category
            ).order_by(desc('best_score')).limit(limit).all()
            
            # Format results
            leaderboard_entries = []
            for rank, entry in enumerate(results, 1):
                leaderboard_entries.append({
                    'rank': rank,
                    'user_id': entry.user_id,
                    'username': entry.username,
                    'profile_img': entry.profile_img,
                    'score': entry.best_score,
                    'category': entry.category,
                    'date_attempted': entry.latest_attempt.isoformat() if entry.latest_attempt else None
                })
            
            return leaderboard_entries
            
        except Exception as e:
            print(f"❌ Error in leaderboard service: {str(e)}")
            return []
    
    @staticmethod
    def get_user_rank(user_id, category='all'):
        """Get specific user's rank in leaderboard"""
        try:
            from user.models.score import Score
            from user.models.user import User
            
            # Get user's best score in category
            user_score_subquery = db.session.query(
                func.max(Score.score).label('user_best_score')
            ).filter(Score.user_id == user_id)
            
            if category != 'all':
                user_score_subquery = user_score_subquery.filter(Score.category == category)
            
            user_best_score = user_score_subquery.scalar()
            
            if not user_best_score:
                return None
            
            # Get all users' best scores and count those better than current user
            all_users_best = db.session.query(
                Score.user_id,
                func.max(Score.score).label('best_score')
            ).group_by(Score.user_id)
            
            if category != 'all':
                all_users_best = all_users_best.filter(Score.category == category)
            
            # Count users with better scores
            users_above = all_users_best.filter(
                func.max(Score.score) > user_best_score
            ).count()
            
            return users_above + 1
            
        except Exception as e:
            print(f"❌ Error getting user rank: {str(e)}")
            return None
    
    @staticmethod
    def get_category_leaderboards():
        """Get leaderboards for all categories"""
        categories = ['networking', 'troubleshooting', 'collaboration', 'topology', 'crimping', 'riddle']
        category_leaderboards = {}
        
        for category in categories:
            category_leaderboards[category] = LeaderboardService.get_live_leaderboard(
                category=category, 
                limit=10
            )
        
        return category_leaderboards
    
    @staticmethod
    def get_recent_achievements(limit=10):
        """Get recent score achievements for activity feed"""
        try:
            from user.models.score import Score
            from user.models.user import User
            
            recent_scores = db.session.query(
                Score.score,
                Score.category,
                Score.date_attempted,
                User.username,
                User.profile_img
            ).join(User).order_by(
                desc(Score.date_attempted)
            ).limit(limit).all()
            
            achievements = []
            for score in recent_scores:
                achievements.append({
                    'username': score.username,
                    'profile_img': score.profile_img,
                    'score': score.score,
                    'category': score.category,
                    'date_attempted': score.date_attempted.isoformat() if score.date_attempted else None
                })
            
            return achievements
            
        except Exception as e:
            print(f"❌ Error getting recent achievements: {str(e)}")
            return []
    
    @staticmethod
    def get_user_statistics(user_id):
        """Get comprehensive statistics for a specific user"""
        try:
            from user.models.score import Score
            from sqlalchemy import distinct
            
            stats = db.session.query(
                func.count(Score.id).label('total_attempts'),
                func.max(Score.score).label('best_score'),
                func.avg(Score.score).label('average_score'),
                func.count(distinct(Score.category)).label('categories_attempted')
            ).filter(Score.user_id == user_id).first()
            
            # Get category breakdown
            category_stats = db.session.query(
                Score.category,
                func.max(Score.score).label('best_score'),
                func.count(Score.id).label('attempts')
            ).filter(Score.user_id == user_id).group_by(Score.category).all()
            
            category_breakdown = {}
            for cat_stat in category_stats:
                category_breakdown[cat_stat.category] = {
                    'best_score': cat_stat.best_score,
                    'attempts': cat_stat.attempts
                }
            
            return {
                'total_attempts': stats.total_attempts or 0,
                'best_score': stats.best_score or 0,
                'average_score': round(stats.average_score or 0, 2),
                'categories_attempted': stats.categories_attempted or 0,
                'category_breakdown': category_breakdown
            }
            
        except Exception as e:
            print(f"❌ Error getting user statistics: {str(e)}")
            return {}
    
    @staticmethod
    def _get_time_cutoff(time_period):
        """Get datetime cutoff for time period filter"""
        now = datetime.utcnow()
        
        if time_period == 'daily':
            return now - datetime.timedelta(days=1)
        elif time_period == 'weekly':
            return now - datetime.timedelta(weeks=1)
        elif time_period == 'monthly':
            return now - datetime.timedelta(days=30)
        elif time_period == 'yearly':
            return now - datetime.timedelta(days=365)
        else:
            return now - datetime.timedelta(days=365)  # Default to yearly


# Global service instance
leaderboard_service = LeaderboardService()

