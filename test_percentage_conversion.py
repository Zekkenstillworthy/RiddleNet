#!/usr/bin/env python3
"""
Test script to verify percentage conversion logic for activity feed
"""

def _convert_score_to_percentage(score: float) -> float:
    """Standardized score to percentage conversion"""
    # If score appears to be in 0-3 scale (common quiz scoring)
    # We assume if score is <= 3 AND not 0, it's likely 0-3 scale
    if 0 < score <= 3:
        return round((score / 3) * 100, 1)
    # If score is 0, keep as 0%
    elif score == 0:
        return 0.0
    # If score is in 4-100 range (already a percentage)
    elif score > 3 and score <= 100:
        return round(score, 1)
    # If score is somehow above 100, cap it
    else:
        return 100.0

# Test cases
test_scores = [
    # 0-3 scale scores
    0, 0.5, 1, 1.5, 2, 2.5, 3,
    # Already percentage scores
    4, 10, 25, 50, 75, 85, 90, 95, 100,
    # Edge cases
    101, 150, 200, 250, 300, 333, 500
]

print("Testing score to percentage conversion:")
print("=" * 50)
print(f"{'Score':<8} {'Percentage':<12} {'Expected':<12}")
print("-" * 50)

for score in test_scores:
    percentage = _convert_score_to_percentage(score)
    
    # Determine expected behavior
    if 0 < score <= 3:
        expected = f"{round((score / 3) * 100, 1)}%"
    elif score == 0:
        expected = "0.0%"
    elif 3 < score <= 100:
        expected = f"{round(score, 1)}%"
    else:
        expected = "100.0% (capped)"
    
    status = "✓" if percentage <= 100 else "❌"
    print(f"{score:<8} {percentage}%{'':<7} {expected:<12} {status}")

print("\nProblematic scores (>100%):")
problematic = [score for score in test_scores if _convert_score_to_percentage(score) > 100]
print(f"Found {len(problematic)} problematic scores: {problematic}")

print("\nChecking potential database scenarios:")
# Simulate some common problematic scenarios
scenarios = [
    ("Quiz score 3/3", 3),
    ("Quiz score 2/3", 2), 
    ("Already percentage 85%", 85),
    ("Raw score 333 (3/3 * 111)", 333),
    ("Raw score 200", 200),
    ("Raw score 150", 150),
]

for description, score in scenarios:
    percentage = _convert_score_to_percentage(score)
    status = "✓" if percentage <= 100 else "⚠️  OVER 100%"
    print(f"{description:<25}: {score} → {percentage}% {status}")
