"""
Password Validation Utility Module
Provides comprehensive password strength validation for RiddleNet application
"""

import re
from typing import Dict, List, Tuple


class PasswordValidator:
    """
    Validates password strength according to security requirements
    
    Requirements:
    - At least 8 characters long
    - At least one lowercase letter (a-z)
    - At least one uppercase letter (A-Z)
    - At least one number (0-9)
    - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
    """
    
    # Minimum password length
    MIN_LENGTH = 8
    
    # Special characters allowed
    SPECIAL_CHARS = r"!@#$%^&*()_+\-=\[\]{}|;:,.<>?"
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength
        
        Args:
            password: The password string to validate
            
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
            - is_valid: True if password meets all requirements
            - errors: List of error messages for failed requirements
        """
        errors = []
        
        # Check if password is provided
        if not password:
            errors.append("Password is required")
            return False, errors
        
        # Check minimum length
        if len(password) < PasswordValidator.MIN_LENGTH:
            errors.append(f"Password must be at least {PasswordValidator.MIN_LENGTH} characters long")
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter (a-z)")
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter (A-Z)")
        
        # Check for digit
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number (0-9)")
        
        # Check for special character
        if not re.search(f'[{PasswordValidator.SPECIAL_CHARS}]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*)")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def get_password_strength(password: str) -> Dict[str, any]:
        """
        Get detailed password strength information
        
        Args:
            password: The password string to evaluate
            
        Returns:
            Dictionary with strength details:
            {
                'is_valid': bool,
                'strength': str ('weak', 'medium', 'strong'),
                'score': int (0-100),
                'requirements': {
                    'length': bool,
                    'lowercase': bool,
                    'uppercase': bool,
                    'number': bool,
                    'special': bool
                },
                'errors': List[str]
            }
        """
        is_valid, errors = PasswordValidator.validate_password(password)
        
        # Check individual requirements
        requirements = {
            'length': len(password) >= PasswordValidator.MIN_LENGTH,
            'lowercase': bool(re.search(r'[a-z]', password)),
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'number': bool(re.search(r'\d', password)),
            'special': bool(re.search(f'[{PasswordValidator.SPECIAL_CHARS}]', password))
        }
        
        # Calculate strength score (0-100)
        score = 0
        if requirements['length']:
            score += 20
        if requirements['lowercase']:
            score += 20
        if requirements['uppercase']:
            score += 20
        if requirements['number']:
            score += 20
        if requirements['special']:
            score += 20
        
        # Determine strength level
        if score == 100:
            strength = 'strong'
        elif score >= 60:
            strength = 'medium'
        else:
            strength = 'weak'
        
        return {
            'is_valid': is_valid,
            'strength': strength,
            'score': score,
            'requirements': requirements,
            'errors': errors
        }
    
    @staticmethod
    def get_requirements_list() -> List[str]:
        """
        Get a list of password requirements
        
        Returns:
            List of requirement strings
        """
        return [
            f"At least {PasswordValidator.MIN_LENGTH} characters long",
            "At least one lowercase letter (a-z)",
            "At least one uppercase letter (A-Z)",
            "At least one number (0-9)",
            "At least one special character (!@#$%^&*)"
        ]


# Convenience functions for quick validation
def validate_password(password: str) -> Tuple[bool, List[str]]:
    """Quick validation function"""
    return PasswordValidator.validate_password(password)


def get_password_strength(password: str) -> Dict[str, any]:
    """Quick strength evaluation function"""
    return PasswordValidator.get_password_strength(password)


def get_password_requirements() -> List[str]:
    """Get password requirements list"""
    return PasswordValidator.get_requirements_list()
