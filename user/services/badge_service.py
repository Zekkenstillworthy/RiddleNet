"""
Badge Service - MVP
Automatic badge awarding based on challenge completion criteria
"""
from user.models.user_badge import UserBadge, BADGE_DEFINITIONS
from user.models.challenge_score import ChallengeScore
from __init__ import db


class BadgeService:
    """
    Service layer for checking badge eligibility and awarding badges
    """
    
    @staticmethod
    def check_and_award_badges(user_id, challenge_type, score, metadata=None):
        """
        Check if user earned any new badges and award them
        
        Args:
            user_id: User ID
            challenge_type: Type of challenge ('crimping', 'osi', 'troubleshooting', 'quiz')
            score: Score achieved (0-100)
            metadata: Optional dict with mode, difficulty, etc.
        
        Returns:
            List of newly earned badges (as dicts)
        """
        newly_earned_badges = []
        
        # Normalize challenge type to handle variants
        # 'linkup_easy', 'troubleshooting_medium', 'troubleshooting_hard' -> 'troubleshooting'
        normalized_type = challenge_type
        if challenge_type.startswith('linkup') or challenge_type.startswith('troubleshooting'):
            normalized_type = 'troubleshooting'
        elif challenge_type == 'quiz_challenge':
            normalized_type = 'quiz'
        
        if normalized_type == 'crimping':
            badges = BadgeService._check_crimping_badges(user_id, score, metadata)
            newly_earned_badges.extend(badges)
        
        elif normalized_type == 'osi':
            badges = BadgeService._check_osi_badges(user_id, score, metadata)
            newly_earned_badges.extend(badges)
        
        elif normalized_type == 'troubleshooting':
            badges = BadgeService._check_troubleshooting_badges(user_id, score, metadata)
            newly_earned_badges.extend(badges)
        
        elif normalized_type == 'quiz':
            badges = BadgeService._check_quiz_badges(user_id, score, metadata)
            newly_earned_badges.extend(badges)
        
        return newly_earned_badges
    
    @staticmethod
    def _check_crimping_badges(user_id, score, metadata):
        """Check and award crimping-related badges - ONE badge per challenge"""
        badges = []
        
        if score == 100:
            # Cable Master - Perfect score (legendary badge only)
            badge, is_new = UserBadge.award_badge(
                user_id=user_id,
                badge_id='cable_master',
                badge_name='Cable Master',
                badge_description='Perfect Score in Cable Crimping!',
                challenge_type='crimping',
                earned_score=score,
                badge_rarity='legendary',
                metadata=metadata
            )
            if is_new:
                badges.append(badge.to_dict())
        
        return badges
    
    @staticmethod
    def _check_osi_badges(user_id, score, metadata):
        """Check and award OSI-related badges - ONE badge per challenge"""
        badges = []
        
        # Check if both levels are complete
        challenge_data = metadata.get('challenge_data', {}) if metadata else {}
        both_levels_complete = challenge_data.get('both_levels_complete', False)
        level1_score = challenge_data.get('level1_score', 0)
        level2_score = challenge_data.get('level2_score', 0)
        
        if both_levels_complete and level1_score == 100 and level2_score == 100:
            badge_payload = {
                'level1_score': level1_score,
                'level2_score': level2_score,
                'combined_score': score,
                'completion_date': metadata.get('completion_time') if metadata else None
            }

            # Award only the legendary badge (OSI & TCP/IP Master)
            badge, is_new = UserBadge.award_badge(
                user_id=user_id,
                badge_id='osi_tcp_master',
                badge_name='OSI & TCP/IP Master',
                badge_description='Perfect Score in Both OSI & TCP/IP Challenges!',
                challenge_type='osi',
                earned_score=score,
                badge_rarity='legendary',
                metadata=badge_payload
            )
            if is_new:
                badges.append(badge.to_dict())
        
        return badges
    
    @staticmethod
    def _check_troubleshooting_badges(user_id, score, metadata):
        """Check and award troubleshooting-related badges - ONE badge per challenge"""
        badges = []
        
        # Simplified: Award badge for 100% score
        if score == 100:
            badge_metadata = metadata or {}

            # Award only the legendary badge (Troubleshooting Pro)
            badge, is_new = UserBadge.award_badge(
                user_id=user_id,
                badge_id='troubleshooting_pro',
                badge_name='Troubleshooting Pro',
                badge_description='Perfect score in Link Up challenge!',
                challenge_type='troubleshooting',
                earned_score=score,
                badge_rarity='legendary',
                metadata=badge_metadata
            )
            if is_new:
                badges.append(badge.to_dict())
                print(f"[Badge Award] [OK] Troubleshooting Pro badge awarded to user {user_id}!")
        
        return badges
    
    @staticmethod
    def _check_quiz_badges(user_id, score, metadata):
        """Check and award quiz-related badges - ONE badge per challenge"""
        badges = []
        
        if score == 100:
            # Award only the legendary badge (Quiz Champion)
            badge, is_new = UserBadge.award_badge(
                user_id=user_id,
                badge_id='quiz_champion',
                badge_name='Quiz Champion',
                badge_description='Perfect Quiz Performance!',
                challenge_type='quiz',
                earned_score=score,
                badge_rarity='legendary',
                metadata=metadata
            )
            if is_new:
                badges.append(badge.to_dict())
        
        return badges
    
    @staticmethod
    def get_all_badge_definitions():
        """Get all available badge definitions"""
        return BADGE_DEFINITIONS
    
    @staticmethod
    def get_user_badge_progress(user_id):
        """
        Get user's progress towards all badges
        Returns dict with earned and available badges
        """
        earned_badges = UserBadge.get_user_badges(user_id)
        earned_badge_ids = {badge.badge_id for badge in earned_badges}
        
        available_badges = []
        for badge_id, badge_info in BADGE_DEFINITIONS.items():
            if badge_id not in earned_badge_ids:
                available_badges.append({
                    'badge_id': badge_id,
                    **badge_info
                })
        
        return {
            'earned': [badge.to_dict() for badge in earned_badges],
            'available': available_badges,
            'total_earned': len(earned_badges),
            'total_available': len(BADGE_DEFINITIONS)
        }
