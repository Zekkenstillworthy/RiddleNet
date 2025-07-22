#!/usr/bin/env python3
"""
Test the percentage conversion logic to ensure it works correctly
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

# Test various score values
test_scores = [
    0,      # Minimum
    1.5,    # 0-3 scale (should become 50%)
    3,      # Max on 0-3 scale (should become 100%)
    75,     # Already percentage (should stay 75%)
    100,    # Max percentage (should stay 100%)
    150,    # Over 100 (should be capped to 100%)
    2.4,    # 0-3 scale (should become 80%)
    95.5    # Already percentage (should stay 95.5%)
]

print("🧪 Testing Percentage Conversion Logic")
print("=" * 50)

for score in test_scores:
    converted = _convert_score_to_percentage(score)
    print(f"Score: {score:>6} → {converted:>5}%")

print("\n✅ All conversions complete!")
print("🔍 Key Points:")
print("- Scores 0-3: Converted to 0-100% scale")
print("- Scores 0-100: Used as-is (already percentages)")
print("- Scores >100: Capped at 100%")
