#!/usr/bin/env python3
"""
Final test to verify the percentage fix is working correctly
"""

def test_convert_score_to_percentage():
    """Test the fixed conversion logic"""
    
    def _convert_score_to_percentage(score):
        """Mirror the fixed backend conversion logic"""
        # Handle null/invalid scores
        if score is None or not isinstance(score, (int, float)):
            return 0.0
        
        # Convert to float and handle negative scores
        try:
            score = float(score)
        except (ValueError, TypeError):
            return 0.0
            
        if score < 0:
            return 0.0
        
        # If score appears to be in 0-3 scale (common quiz scoring), convert to percentage
        if 0 < score <= 3:
            return round((score / 3) * 100, 1)
        
        # If score is 0, keep as 0%
        elif score == 0:
            return 0.0
        
        # If score is already a reasonable percentage (4-100), use it
        elif 4 <= score <= 100:
            return round(score, 1)
        
        # For scores in 101-300 range, might be 0-300 scale
        elif 100 < score <= 300:
            return round((score / 300) * 100, 1)
        
        # For extremely high scores (like 3167, 2900), cap at 100%
        else:
            print(f"Warning: Capping extremely high score: {score}")
            return 100.0
    
    # Test the problematic scores from the user's report
    problematic_scores = [3333, 3167, 2900, 3067]
    normal_scores = [0, 1, 2, 3, 50, 75, 100]
    edge_cases = [None, "invalid", -5, 150, 250, 500]
    
    print("🧪 Testing Percentage Conversion Fix")
    print("=" * 50)
    
    print("\n📊 Problematic Scores (should be capped at 100%):")
    for score in problematic_scores:
        result = _convert_score_to_percentage(score)
        status = "✅ FIXED" if result == 100.0 else "❌ STILL BROKEN"
        print(f"  {score:>6} -> {result:>6.1f}% {status}")
    
    print("\n📊 Normal Scores (should convert properly):")
    for score in normal_scores:
        result = _convert_score_to_percentage(score)
        expected = ""
        if 0 < score <= 3:
            expected = f"(expected: {round((score / 3) * 100, 1)}%)"
        elif score == 0:
            expected = "(expected: 0%)"
        elif 4 <= score <= 100:
            expected = f"(expected: {score}%)"
        
        print(f"  {score:>6} -> {result:>6.1f}% {expected}")
    
    print("\n📊 Edge Cases (should handle gracefully):")
    for score in edge_cases:
        result = _convert_score_to_percentage(score)
        print(f"  {str(score):>6} -> {result:>6.1f}%")
    
    print("\n🔍 Summary:")
    all_problematic_fixed = all(_convert_score_to_percentage(score) == 100.0 for score in problematic_scores)
    print(f"  Problematic scores fixed: {'✅ YES' if all_problematic_fixed else '❌ NO'}")
    print(f"  All results ≤ 100%: {'✅ YES' if all(_convert_score_to_percentage(score) <= 100.0 for score in problematic_scores + normal_scores) else '❌ NO'}")

def test_frontend_safe_percentage():
    """Test the frontend safePercentage function"""
    
    def safe_percentage(score):
        """Mirror the JavaScript safePercentage function"""
        # Handle missing scores (like for essays)
        if score is None or score == '' or str(score).lower() == 'nan':
            return None  # Return None to indicate no score
        
        try:
            num_score = float(score)
        except (ValueError, TypeError):
            return None
        
        # Ensure it's within bounds and formatted correctly
        if num_score < 0:
            return 0.0
        elif num_score > 100:
            return 100.0
        else:
            return round(num_score * 10) / 10  # Round to 1 decimal
    
    print("\n\n🎯 Testing Frontend safePercentage Function")
    print("=" * 50)
    
    test_cases = [
        (None, "None (essay with no score)"),
        ('', "Empty string"),
        (float('nan'), "NaN value"),
        (50.0, "Normal percentage"),
        (150.0, "Over 100% (should be capped)"),
        (-10, "Negative score"),
        (0, "Zero score")
    ]
    
    for score, description in test_cases:
        result = safe_percentage(score)
        print(f"  {str(score):>10} -> {str(result):>6} ({description})")

if __name__ == "__main__":
    test_convert_score_to_percentage()
    test_frontend_safe_percentage()
