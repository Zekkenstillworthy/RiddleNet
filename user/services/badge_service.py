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
        print(f"\n{'='*80}")
        print(f"[BADGE SERVICE] Check and Award Badges")
        print(f"  User ID: {user_id}")
        print(f"  Challenge Type: {challenge_type}")
        print(f"  Score: {score}%")
        print(f"  Metadata: {metadata}")
        print(f"{'='*80}")
        
        newly_earned_badges = []
        
        # Normalize challenge type to handle variants
        # 'linkup_easy', 'troubleshooting_medium', 'troubleshooting_hard' -> 'troubleshooting'
        normalized_type = challenge_type
        if challenge_type.startswith('linkup') or challenge_type.startswith('troubleshooting'):
            normalized_type = 'troubleshooting'
            print(f"[BADGE SERVICE] Normalized '{challenge_type}' → '{normalized_type}'")
        elif challenge_type == 'quiz_challenge':
            normalized_type = 'quiz'
            print(f"[BADGE SERVICE] Normalized '{challenge_type}' → '{normalized_type}'")
        
        if normalized_type == 'crimping':
            print(f"[BADGE SERVICE] Checking crimping badges...")
            badges = BadgeService._check_crimping_badges(user_id, score, metadata)
            newly_earned_badges.extend(badges)
            print(f"[BADGE SERVICE] Crimping check result: {len(badges)} new badge(s)")
        
        elif normalized_type == 'osi':
            print(f"[BADGE SERVICE] Checking OSI badges...")
            badges = BadgeService._check_osi_badges(user_id, score, metadata)
            newly_earned_badges.extend(badges)
            print(f"[BADGE SERVICE] OSI check result: {len(badges)} new badge(s)")
        
        elif normalized_type == 'troubleshooting':
            print(f"[BADGE SERVICE] Checking troubleshooting badges...")
            badges = BadgeService._check_troubleshooting_badges(user_id, score, metadata)
            newly_earned_badges.extend(badges)
            print(f"[BADGE SERVICE] Troubleshooting check result: {len(badges)} new badge(s)")
        
        elif normalized_type == 'quiz':
            print(f"[BADGE SERVICE] Checking quiz badges...")
            badges = BadgeService._check_quiz_badges(user_id, score, metadata)
            newly_earned_badges.extend(badges)
            print(f"[BADGE SERVICE] Quiz check result: {len(badges)} new badge(s)")
        
        print(f"\n[BADGE SERVICE] ✅ Total newly earned badges: {len(newly_earned_badges)}")
        for badge in newly_earned_badges:
            print(f"  → {badge['badge_id']}: {badge['badge_name']}")
        print(f"{'='*80}\n")
        
        return newly_earned_badges
    
    @staticmethod
    def _check_crimping_badges(user_id, score, metadata):
        """Check and award crimping-related badges - ONE badge per challenge"""
        badges = []
        
        print(f"[BADGE SERVICE] Crimping Badge Check: score={score}%")
        if score == 100:
            print(f"[BADGE SERVICE] ✅ Score is 100% - awarding Cable Master badge")
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
                print(f"[BADGE SERVICE] 🎉 NEW BADGE AWARDED: Cable Master to user {user_id}")
                badges.append(badge.to_dict())
            else:
                print(f"[BADGE SERVICE] ℹ️ Badge already exists (Cable Master)")
        else:
            print(f"[BADGE SERVICE] ❌ Score {score}% < 100% - No badge awarded")
        
        return badges
    
    @staticmethod
    def _check_osi_badges(user_id, score, metadata):
        """Check and award OSI-related badges - ONE badge per challenge"""
        badges = []
        
        print(f"[BADGE SERVICE] OSI Badge Check: score={score}%")
        # Check if both levels are complete
        challenge_data = metadata.get('challenge_data', {}) if metadata else {}
        both_levels_complete = challenge_data.get('both_levels_complete', False)
        level1_score = challenge_data.get('level1_score', 0)
        level2_score = challenge_data.get('level2_score', 0)
        
        print(f"[BADGE SERVICE] OSI Challenge Data:")
        print(f"  Both levels complete: {both_levels_complete}")
        print(f"  Level 1 score: {level1_score}%")
        print(f"  Level 2 score: {level2_score}%")
        
        if both_levels_complete and level1_score == 100 and level2_score == 100:
            print(f"[BADGE SERVICE] ✅ Both levels at 100% - awarding OSI & TCP/IP Master badge")
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
                print(f"[BADGE SERVICE] 🎉 NEW BADGE AWARDED: OSI & TCP/IP Master (ID: {badge.id})")
                badges.append(badge.to_dict())
            else:
                print(f"[BADGE SERVICE] ℹ️ Badge already exists: OSI & TCP/IP Master")
        else:
            print(f"[BADGE SERVICE] ❌ Requirements not met for OSI badge")
        
        return badges
    
    @staticmethod
    def _check_troubleshooting_badges(user_id, score, metadata):
        """Check and award troubleshooting-related badges - ONE badge per challenge"""
        badges = []
        
        print(f"[BADGE SERVICE] Troubleshooting Badge Check: score={score}%")
        
        # Simplified: Award badge for 100% score
        if score == 100:
            print(f"[BADGE SERVICE] ✅ Score is 100% - awarding Troubleshooting Pro badge")
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
                print(f"[BADGE SERVICE] 🎉 NEW BADGE AWARDED: Troubleshooting Pro (ID: {badge.id})")
                badges.append(badge.to_dict())
            else:
                print(f"[BADGE SERVICE] ℹ️ Badge already exists: Troubleshooting Pro")
        else:
            print(f"[BADGE SERVICE] ❌ Score {score}% < 100% - No badge awarded")
        
        return badges
    
    @staticmethod
    def _check_quiz_badges(user_id, score, metadata):
        """Check and award quiz-related badges - ONE badge per challenge"""
        badges = []
        
        print(f"[BADGE SERVICE] Quiz Badge Check: score={score}%")
        
        if score == 100:
            print(f"[BADGE SERVICE] ✅ Score is 100% - awarding Quiz Champion badge")
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
                print(f"[BADGE SERVICE] 🎉 NEW BADGE AWARDED: Quiz Champion (ID: {badge.id})")
                badges.append(badge.to_dict())
            else:
                print(f"[BADGE SERVICE] ℹ️ Badge already exists: Quiz Champion")
        else:
            print(f"[BADGE SERVICE] ❌ Score {score}% < 100% - No badge awarded")
        
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
