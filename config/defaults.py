"""
Centralized defaults and thresholds for RiddleNet.
These can be overridden via environment variables or admin settings.
"""

DEFAULTS = {
    'grading': {
        'rounding': 'nearest',  # nearest, up, down
        'min_passing_percentage': 60,
        'partial_credit_enabled': True,
    },
    'deadlines': {
        'late_penalty_per_day': 10.0,
        'grace_minutes': 10,
        'allow_late_submissions': True,
    },
    'gamification': {
        'hint_penalty_points': 5,
        'combo_bonus': 10,
    },
    'validation': {
        'max_connectivity_tests': 50,
        'max_devices': 50,
    },
}

def get_default(path: str, fallback=None):
    parts = path.split('.')
    node = DEFAULTS
    for p in parts:
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            return fallback
    return node
