from typing import Dict, List


class OnboardingService:
    DEFAULT_STEPS = {
        'instructor': [
            {'key': 'role', 'title': 'Choose your role', 'content': 'Confirm you are an instructor.'},
            {'key': 'dashboard', 'title': 'Instructor Dashboard', 'content': 'Create and manage labs.'},
            {'key': 'rubric', 'title': 'Rubric Builder', 'content': 'Define grading criteria with weights.'},
            {'key': 'export', 'title': 'Export & Import', 'content': 'Backup labs with integrity hashing.'},
        ],
        'student': [
            {'key': 'role', 'title': 'Choose your role', 'content': 'Confirm you are a student.'},
            {'key': 'lab', 'title': 'Lab UI', 'content': 'Configure IPs and validate topology.'},
            {'key': 'points', 'title': 'Points', 'content': 'Earn points and spend on hints.'},
            {'key': 'submit', 'title': 'Submission', 'content': 'Submit before deadline to avoid penalties.'},
        ],
    }

    @staticmethod
    def get_steps(role: str) -> List[Dict]:
        return OnboardingService.DEFAULT_STEPS.get(role, [])
