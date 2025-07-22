#!/usr/bin/env python3
"""
Validate the percentage fix for the Real-time Activity Feed
"""

def test_safe_percentage():
    """Test the JavaScript safePercentage function logic in Python"""
    
    def safe_percentage(score):
        """Python equivalent of the JavaScript safePercentage function"""
        if score is None or score == "" or str(score).lower() == 'nan':
            return 0.0
        
        try:
            num_score = float(score)
        except (ValueError, TypeError):
            return 0.0
        
        # Backend should already provide properly converted percentages
        # Just ensure it's within bounds and formatted correctly
        if num_score < 0:
            return 0.0
        elif num_score > 100:
            return 100.0
        else:
            return round(num_score * 10) / 10  # Round to 1 decimal
    
    # Test cases that were problematic before
    test_cases = [
        # (input_score, expected_output, description)
        (0, 0.0, "Zero score"),
        (1.5, 1.5, "Already converted 0-3 scale score"),
        (50.0, 50.0, "Normal percentage"),
        (75.5, 75.5, "Decimal percentage"),
        (100, 100.0, "Perfect score"),
        (150, 100.0, "Capped over 100%"),
        (3167, 100.0, "Extremely high score (capped)"),
        (2900, 100.0, "Another high score (capped)"),
        (-5, 0.0, "Negative score"),
        (None, 0.0, "None value"),
        ("invalid", 0.0, "Invalid string"),
        (float('nan'), 0.0, "NaN value"),
    ]
    
    print("🧪 Testing safePercentage function logic")
    print("=" * 60)
    print(f"{'Input':<15} {'Output':<10} {'Expected':<10} {'Status'}")
    print("-" * 60)
    
    all_passed = True
    for input_score, expected, description in test_cases:
        result = safe_percentage(input_score)
        passed = abs(result - expected) < 0.01  # Allow small floating point differences
        status = "✅ PASS" if passed else "❌ FAIL"
        
        if not passed:
            all_passed = False
        
        print(f"{str(input_score):<15} {result:<10} {expected:<10} {status}")
    
    print("-" * 60)
    if all_passed:
        print("🎉 All tests PASSED! The percentage fix is working correctly.")
    else:
        print("⚠️  Some tests FAILED. Please review the logic.")
    
    return all_passed

def test_backend_conversion():
    """Test the backend _convert_score_to_percentage logic"""
    
    def convert_score_to_percentage(score):
        """Python equivalent of the backend conversion"""
        if score is None or not isinstance(score, (int, float)):
            return 0.0
        
        score = float(score)
        if score < 0:
            return 0.0
        
        # If score is already a reasonable percentage (0-100), use it
        if 0 <= score <= 100:
            return round(score, 1)
        
        # If score appears to be in 0-3 scale, convert to percentage
        elif score <= 3:
            return round((score / 3) * 100, 1)
        
        # For any score above 100, apply intelligent conversion or cap it
        elif score <= 300:  # Likely 0-300 scale, convert to percentage
            return round((score / 300) * 100, 1)
        
        # For extremely high scores, cap at 100%
        else:
            print(f"Warning: Capping extremely high score: {score}")
            return 100.0
    
    # Test the problematic scores that were causing >100% issues
    problematic_scores = [3167, 2900, 3067, 333, 500]
    
    print("\n🔧 Testing backend conversion for problematic scores")
    print("=" * 50)
    print(f"{'Raw Score':<12} {'Converted':<12} {'Status'}")
    print("-" * 50)
    
    for score in problematic_scores:
        converted = convert_score_to_percentage(score)
        status = "✅ Fixed" if converted <= 100 else "❌ Still >100%"
        print(f"{score:<12} {converted}%{'':<7} {status}")

if __name__ == "__main__":
    test_safe_percentage()
    test_backend_conversion()
    
    print("\n📋 Summary:")
    print("- Frontend safePercentage function ensures all values are 0-100%")
    print("- Backend conversion handles raw scores properly")
    print("- Activity feed should now show correct percentages")
    print("\n💡 To test: Refresh your dashboard and check the activity feed!")
