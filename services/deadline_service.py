"""
Deadline Management Service
Handles sophisticated deadline calculations, penalty applications, and availability windows
"""

from datetime import datetime, timedelta
import json
import math
from typing import Dict, List, Optional, Tuple

from admin.models.deadline_policy import (
    DeadlinePolicy, PenaltyTier, AssignmentAvailabilityWindow,
    StudentDeadlineExtension, DeadlineCalculationLog
)
from admin.models.class_content import ClassAssignment
from admin.models.assignment_submission import AssignmentSubmission
from admin import db

class DeadlineService:
    """Service for managing deadlines and calculating penalties"""
    
    @staticmethod
    def calculate_late_penalty(submission: AssignmentSubmission, assignment: ClassAssignment) -> Dict:
        """
        Calculate late penalty for a submission using sophisticated policies
        
        Returns:
            Dict with penalty calculation details
        """
        # Get submission and due dates
        submission_date = submission.submitted_at
        due_date = assignment.due_date
        
        if not due_date or not submission_date:
            return {
                'is_late': False,
                'penalty_percentage': 0.0,
                'penalty_amount': 0.0,
                'days_late': 0.0,
                'hours_late': 0.0,
                'calculation_method': 'no_due_date',
                'details': 'No due date specified'
            }
        
        # Check if submission is late
        if submission_date <= due_date:
            return {
                'is_late': False,
                'penalty_percentage': 0.0,
                'penalty_amount': 0.0,
                'days_late': 0.0,
                'hours_late': 0.0,
                'calculation_method': 'on_time',
                'details': 'Submitted on time'
            }
        
        # Check for individual student extensions
        extension = DeadlineService._get_active_extension(assignment.id, submission.student_id)
        effective_due_date = due_date
        
        if extension:
            effective_due_date = extension.extended_due_date
            if submission_date <= effective_due_date:
                return {
                    'is_late': False,
                    'penalty_percentage': 0.0,
                    'penalty_amount': 0.0,
                    'days_late': 0.0,
                    'hours_late': 0.0,
                    'calculation_method': 'extension_used',
                    'details': f'Extension granted until {extension.extended_due_date}',
                    'extension_id': extension.id
                }
        
        # Calculate time late
        time_diff = submission_date - effective_due_date
        hours_late = time_diff.total_seconds() / 3600
        days_late = hours_late / 24
        
        # Get availability window and policy
        availability = DeadlineService._get_availability_window(assignment.id)
        policy = None
        
        if availability and availability.deadline_policy_id:
            policy = DeadlinePolicy.query.get(availability.deadline_policy_id)
        
        # Check hard cutoff
        if availability and availability.late_submission_until:
            if submission_date > availability.late_submission_until:
                return {
                    'is_late': True,
                    'penalty_percentage': 100.0,
                    'penalty_amount': submission.max_points or 0,
                    'days_late': days_late,
                    'hours_late': hours_late,
                    'calculation_method': 'hard_cutoff',
                    'details': 'Submitted after hard cutoff deadline',
                    'cutoff_exceeded': True
                }
        
        # Apply penalty calculation
        if policy:
            penalty_result = DeadlineService._apply_policy_penalty(
                policy, days_late, hours_late, submission, extension
            )
        else:
            # Fallback to simple penalty from assignment
            penalty_per_day = getattr(assignment, 'late_penalty_per_day', 10.0)
            penalty_result = DeadlineService._apply_simple_penalty(
                penalty_per_day, days_late, hours_late
            )
        
        # Log the calculation
        DeadlineService._log_penalty_calculation(
            submission, assignment, effective_due_date, penalty_result, extension, policy
        )
        
        return penalty_result
    
    @staticmethod
    def _get_active_extension(assignment_id: int, student_id: int) -> Optional[StudentDeadlineExtension]:
        """Get active deadline extension for a student"""
        return StudentDeadlineExtension.query.filter_by(
            assignment_id=assignment_id,
            student_id=student_id,
            is_active=True
        ).first()
    
    @staticmethod
    def _get_availability_window(assignment_id: int) -> Optional[AssignmentAvailabilityWindow]:
        """Get availability window for an assignment"""
        return AssignmentAvailabilityWindow.query.filter_by(
            assignment_id=assignment_id
        ).first()
    
    @staticmethod
    def _apply_policy_penalty(policy: DeadlinePolicy, days_late: float, hours_late: float, 
                            submission: AssignmentSubmission, extension: Optional[StudentDeadlineExtension]) -> Dict:
        """Apply sophisticated penalty policy"""
        
        # Check grace period
        if policy.grace_period_hours > 0 and hours_late <= policy.grace_period_hours:
            return {
                'is_late': True,
                'penalty_percentage': 0.0,
                'penalty_amount': 0.0,
                'days_late': days_late,
                'hours_late': hours_late,
                'calculation_method': 'grace_period',
                'details': f'Within {policy.grace_period_hours}-hour grace period',
                'grace_period_applied': True
            }
        
        # Apply extension penalty override
        if extension and extension.waive_late_penalty:
            return {
                'is_late': True,
                'penalty_percentage': 0.0,
                'penalty_amount': 0.0,
                'days_late': days_late,
                'hours_late': hours_late,
                'calculation_method': 'penalty_waived',
                'details': 'Late penalty waived by instructor',
                'extension_id': extension.id
            }
        
        # Calculate penalty based on policy type
        if policy.policy_type == 'simple':
            penalty_percentage = DeadlineService._calculate_simple_penalty(
                policy.simple_penalty_per_day, days_late
            )
        elif policy.policy_type == 'tiered':
            penalty_percentage = DeadlineService._calculate_tiered_penalty(
                policy, days_late
            )
        elif policy.policy_type == 'exponential':
            penalty_percentage = DeadlineService._calculate_exponential_penalty(
                policy, days_late
            )
        elif policy.policy_type == 'fixed':
            penalty_percentage = DeadlineService._calculate_fixed_penalty(
                policy, days_late
            )
        else:
            # Default to simple
            penalty_percentage = DeadlineService._calculate_simple_penalty(
                policy.simple_penalty_per_day, days_late
            )
        
        # Apply extension custom penalty rate
        if extension and extension.custom_penalty_rate is not None:
            penalty_percentage = min(penalty_percentage, extension.custom_penalty_rate * days_late)
        
        # Apply maximum penalty cap
        penalty_percentage = min(penalty_percentage, policy.max_penalty_percentage)
        
        # Round penalty if specified
        if policy.round_penalty_up:
            penalty_percentage = math.ceil(penalty_percentage)
        
        # Calculate penalty amount
        max_points = submission.max_points or 100
        penalty_amount = (penalty_percentage / 100) * max_points
        
        return {
            'is_late': True,
            'penalty_percentage': penalty_percentage,
            'penalty_amount': penalty_amount,
            'days_late': days_late,
            'hours_late': hours_late,
            'calculation_method': f'{policy.policy_type}_policy',
            'details': f'Applied {policy.name} policy',
            'policy_id': policy.id,
            'policy_name': policy.name,
            'max_penalty_reached': penalty_percentage >= policy.max_penalty_percentage
        }
    
    @staticmethod
    def _calculate_simple_penalty(penalty_per_day: float, days_late: float) -> float:
        """Calculate simple penalty (fixed percentage per day)"""
        return penalty_per_day * math.ceil(days_late)
    
    @staticmethod
    def _calculate_tiered_penalty(policy: DeadlinePolicy, days_late: float) -> float:
        """Calculate tiered penalty based on penalty tiers"""
        penalty_tiers = sorted(policy.penalty_tiers, key=lambda t: t.start_day)
        total_penalty = 0.0
        days_processed = 0
        
        for tier in penalty_tiers:
            if days_processed >= days_late:
                break
            
            # Determine days in this tier
            tier_start = max(tier.start_day, days_processed + 1)
            tier_end = min(tier.end_day or float('inf'), days_late)
            
            if tier_start <= tier_end:
                days_in_tier = tier_end - tier_start + 1
                
                if tier.penalty_type == 'per_day':
                    total_penalty += tier.penalty_percentage * days_in_tier
                elif tier.penalty_type == 'flat':
                    total_penalty += tier.penalty_percentage
                elif tier.penalty_type == 'cumulative':
                    total_penalty = tier.penalty_percentage  # Replace previous penalty
                
                days_processed = tier_end
        
        return total_penalty
    
    @staticmethod
    def _calculate_exponential_penalty(policy: DeadlinePolicy, days_late: float) -> float:
        """Calculate exponential penalty (increases exponentially with time)"""
        base_penalty = policy.simple_penalty_per_day or 5.0
        # Exponential formula: base_penalty * (1.5 ^ days_late)
        return base_penalty * (1.5 ** math.ceil(days_late))
    
    @staticmethod
    def _calculate_fixed_penalty(policy: DeadlinePolicy, days_late: float) -> float:
        """Calculate fixed penalty (same penalty regardless of how late)"""
        return policy.simple_penalty_per_day or 50.0
    
    @staticmethod
    def _apply_simple_penalty(penalty_per_day: float, days_late: float, hours_late: float) -> Dict:
        """Apply simple penalty calculation (fallback)"""
        penalty_percentage = penalty_per_day * math.ceil(days_late)
        
        return {
            'is_late': True,
            'penalty_percentage': penalty_percentage,
            'penalty_amount': 0.0,  # Will be calculated when grade is assigned
            'days_late': days_late,
            'hours_late': hours_late,
            'calculation_method': 'simple_fallback',
            'details': f'{penalty_per_day}% penalty per day'
        }
    
    @staticmethod
    def _log_penalty_calculation(submission: AssignmentSubmission, assignment: ClassAssignment,
                               due_date: datetime, penalty_result: Dict,
                               extension: Optional[StudentDeadlineExtension],
                               policy: Optional[DeadlinePolicy]) -> None:
        """Log penalty calculation for auditing"""
        try:
            log = DeadlineCalculationLog(
                submission_id=submission.id,
                due_date=due_date,
                submission_date=submission.submitted_at,
                days_late=penalty_result.get('days_late', 0),
                hours_late=penalty_result.get('hours_late', 0),
                policy_id=policy.id if policy else None,
                policy_name=policy.name if policy else None,
                base_penalty_percentage=penalty_result.get('penalty_percentage', 0),
                applied_penalty_percentage=penalty_result.get('penalty_percentage', 0),
                grace_period_applied=penalty_result.get('grace_period_applied', False),
                extension_applied=extension is not None,
                extension_id=extension.id if extension else None,
                calculation_method=penalty_result.get('calculation_method', 'unknown'),
                calculation_details=json.dumps(penalty_result)
            )
            
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            print(f"Error logging penalty calculation: {e}")
            db.session.rollback()
    
    @staticmethod
    def apply_penalty_to_grade(submission: AssignmentSubmission, original_grade: float) -> Tuple[float, Dict]:
        """
        Apply calculated penalty to a grade
        
        Returns:
            Tuple of (final_grade, penalty_details)
        """
        assignment = submission.assignment
        penalty_result = DeadlineService.calculate_late_penalty(submission, assignment)
        
        if not penalty_result['is_late'] or penalty_result['penalty_percentage'] == 0:
            return original_grade, penalty_result
        
        # Calculate final grade after penalty
        penalty_amount = (penalty_result['penalty_percentage'] / 100) * original_grade
        final_grade = max(0, original_grade - penalty_amount)
        
        # Update penalty result with grade information
        penalty_result.update({
            'original_grade': original_grade,
            'penalty_amount': penalty_amount,
            'final_grade': final_grade
        })
        
        # Update submission with penalty information
        submission.is_late = True
        submission.late_penalty_applied = penalty_result['penalty_percentage']
        
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error updating submission penalty: {e}")
            db.session.rollback()
        
        return final_grade, penalty_result
    
    @staticmethod
    def check_assignment_availability(assignment: ClassAssignment, student_id: int = None) -> Dict:
        """
        Check if an assignment is available for submission
        
        Returns:
            Dict with availability status and details
        """
        now = datetime.utcnow()
        availability = DeadlineService._get_availability_window(assignment.id)
        
        result = {
            'is_available': True,
            'can_submit': True,
            'messages': [],
            'availability_window': None,
            'time_remaining': None,
            'time_limit_active': False
        }
        
        if availability:
            result['availability_window'] = availability.to_dict()
            
            # Check availability window
            if availability.available_from and now < availability.available_from:
                result['is_available'] = False
                result['can_submit'] = False
                result['messages'].append(f"Assignment not available until {availability.available_from}")
            
            if availability.available_until and now > availability.available_until:
                result['is_available'] = False
                result['can_submit'] = False
                result['messages'].append(f"Assignment no longer available (closed {availability.available_until})")
            
            # Check due date and late submission settings
            if availability.due_date:
                if now > availability.due_date:
                    if not availability.late_submission_enabled:
                        result['can_submit'] = False
                        result['messages'].append("Late submissions not allowed")
                    elif availability.late_submission_until and now > availability.late_submission_until:
                        result['can_submit'] = False
                        result['messages'].append(f"Late submission period ended {availability.late_submission_until}")
                    else:
                        result['messages'].append("Assignment is past due - late penalty may apply")
                else:
                    # Calculate time remaining
                    time_diff = availability.due_date - now
                    hours_remaining = time_diff.total_seconds() / 3600
                    result['time_remaining'] = {
                        'hours': hours_remaining,
                        'days': hours_remaining / 24,
                        'formatted': DeadlineService._format_time_remaining(time_diff)
                    }
            
            # Check time limit
            if availability.time_limit_enabled and availability.time_limit_minutes:
                result['time_limit_active'] = True
                result['time_limit_minutes'] = availability.time_limit_minutes
            
            # Check student-specific extensions
            if student_id:
                extension = DeadlineService._get_active_extension(assignment.id, student_id)
                if extension:
                    result['has_extension'] = True
                    result['extension'] = extension.to_dict()
                    if now <= extension.extended_due_date:
                        # Recalculate time remaining with extension
                        time_diff = extension.extended_due_date - now
                        result['time_remaining'] = {
                            'hours': time_diff.total_seconds() / 3600,
                            'days': time_diff.total_seconds() / (3600 * 24),
                            'formatted': DeadlineService._format_time_remaining(time_diff)
                        }
                        result['messages'] = [msg for msg in result['messages'] if 'past due' not in msg]
                        result['messages'].append(f"Extended deadline: {extension.extended_due_date}")
        
        return result
    
    @staticmethod
    def _format_time_remaining(time_diff: timedelta) -> str:
        """Format time remaining in a human-readable way"""
        total_seconds = int(time_diff.total_seconds())
        
        if total_seconds <= 0:
            return "Overdue"
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0 and days == 0:  # Only show minutes if less than a day
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        if not parts:
            return "Less than a minute"
        
        return ", ".join(parts)
    
    @staticmethod
    def create_deadline_policy(name: str, policy_type: str = 'simple', **kwargs) -> DeadlinePolicy:
        """Create a new deadline policy"""
        policy = DeadlinePolicy(
            name=name,
            policy_type=policy_type,
            **kwargs
        )
        
        db.session.add(policy)
        db.session.commit()
        
        return policy
    
    @staticmethod
    def grant_extension(assignment_id: int, student_id: int, hours: int, 
                       reason: str = None, approved_by: int = None, **kwargs) -> StudentDeadlineExtension:
        """Grant a deadline extension to a student"""
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        
        # Calculate new due date
        original_due = assignment.due_date or datetime.utcnow()
        extended_due = original_due + timedelta(hours=hours)
        
        extension = StudentDeadlineExtension(
            assignment_id=assignment_id,
            student_id=student_id,
            original_due_date=original_due,
            extended_due_date=extended_due,
            extension_hours=hours,
            reason=reason,
            approved_by=approved_by,
            **kwargs
        )
        
        db.session.add(extension)
        db.session.commit()
        
        return extension
