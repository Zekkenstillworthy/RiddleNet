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
        level1_score = float(challenge_data.get('level1_score', 0))
        level2_score = float(challenge_data.get('level2_score', 0))
        
        print(f"[BADGE SERVICE] OSI Challenge Data:")
        print(f"  Both levels complete flag: {both_levels_complete}")
        print(f"  Level 1 score: {level1_score}%")
        print(f"  Level 2 score: {level2_score}%")
        
        # STRICT VALIDATION: All three conditions must be TRUE
        # 1. both_levels_complete flag must be True
        # 2. level1_score must be EXACTLY 100.0
        # 3. level2_score must be EXACTLY 100.0
        if both_levels_complete and level1_score == 100.0 and level2_score == 100.0:
            print(f"[BADGE SERVICE] ✅ All validation passed - awarding OSI & TCP/IP Master badge")
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
        """
        Check and award troubleshooting-related badges - ONE badge per challenge
        
        🔧 MVP FIX: Badge is awarded ONLY when ALL 12 Link Up! sub-challenges are completed at 100%
        
        Sub-challenges:
        - Foundation (3): basic network scenarios
        - Easy (3): vlan-basics, default-gateway, dhcp-client
        - Medium (3): extended-ring-redundancy, hybrid-star-ring, partial-mesh-ospf
        - Hard (3): mpls-vpn-complex, datacenter-fabric, sd-wan-overlay
        
        Badge requirements: CompletedItems == TotalItems (12/12)
        """
        badges = []
        
        # Get completed challenges from metadata
        completed_challenges = metadata.get('completed_challenges', []) if metadata else []
        challenge_counts = metadata.get('challenge_counts', {}) if metadata else {}
        
        # 🔧 MVP FIX: Update total to include Foundation (3) + Easy (3) + Medium (3) + Hard (3) = 12
        TOTAL_REQUIRED = 12  # Foundation (3) + Easy (3) + Medium (3) + Hard (3)
        total_completed = len(completed_challenges)  # Use direct count from completed_challenges list
        
        print(f"[BADGE SERVICE] Troubleshooting (Link Up!) Badge Check")
        print(f"  Completed challenges: {total_completed}/{TOTAL_REQUIRED}")
        print(f"  Foundation: {challenge_counts.get('foundation', 0)}/3")
        print(f"  Easy: {challenge_counts.get('easy', 0)}/3")
        print(f"  Medium: {challenge_counts.get('medium', 0)}/3")
        print(f"  Hard: {challenge_counts.get('hard', 0)}/3")
        print(f"  List: {completed_challenges}")
        
        # 🔧 MVP FIX: Award badge ONLY when ALL 12 challenges are completed
        # This implements the requirement: Badges = Earned only when CompletedItems == TotalItems
        if total_completed >= TOTAL_REQUIRED:
            print(f"[BADGE SERVICE] ✅ All {TOTAL_REQUIRED} Link Up! challenges complete - awarding badge!")
            
            badge_metadata = {
                'completed_challenges': completed_challenges,
                'total_challenges': TOTAL_REQUIRED,
                'challenge_counts': challenge_counts
            }
            
            # Award only the legendary badge (Troubleshooting Pro)
            badge, is_new = UserBadge.award_badge(
                user_id=user_id,
                badge_id='troubleshooting_pro',
                badge_name='Troubleshooting Pro',
                badge_description='Completed all 12 Link Up! challenges at 100%!',
                challenge_type='troubleshooting',
                earned_score=100.0,  # Badge represents 100% completion
                badge_rarity='legendary',
                metadata=badge_metadata
            )
            
            if is_new:
                print(f"[BADGE SERVICE] 🎉 NEW BADGE AWARDED: Troubleshooting Pro (ID: {badge.id})")
                badges.append(badge.to_dict())
            else:
                print(f"[BADGE SERVICE] ℹ️ Badge already exists: Troubleshooting Pro")
        else:
            remaining = TOTAL_REQUIRED - total_completed
            print(f"[BADGE SERVICE] ❌ Only {total_completed}/{TOTAL_REQUIRED} complete - No badge yet")
            print(f"[BADGE SERVICE] Still need: {remaining} more challenge(s)")
            print(f"[BADGE SERVICE] Progress breakdown:")
            print(f"  - Foundation: {challenge_counts.get('foundation', 0)}/3 (need {3 - challenge_counts.get('foundation', 0)} more)")
            print(f"  - Easy: {challenge_counts.get('easy', 0)}/3 (need {3 - challenge_counts.get('easy', 0)} more)")
            print(f"  - Medium: {challenge_counts.get('medium', 0)}/3 (need {3 - challenge_counts.get('medium', 0)} more)")
            print(f"  - Hard: {challenge_counts.get('hard', 0)}/3 (need {3 - challenge_counts.get('hard', 0)} more)")
        
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
