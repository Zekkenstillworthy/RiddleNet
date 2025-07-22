#!/usr/bin/env python3
"""
Test script to check the activity feed API response and debug percentage calculation
"""
import requests
import json

def test_percentage_conversion():
    """Test the percentage conversion logic"""
    def convert_score_to_percentage(score):
        """Mirror the backend conversion logic for testing"""
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
    
    # Test some problematic scores from the screenshot
    test_scores = [3167, 2900, 3067, 100, 75, 3, 2.5, 1.5, 0]
    
    print("Testing score conversion logic:")
    print("-" * 40)
    for score in test_scores:
        converted = convert_score_to_percentage(score)
        print(f"Score {score:>6} -> {converted:>6.1f}%")

def test_api():
    """Test the actual API"""
    try:
        url = "http://localhost:5001/admin/api/analytics/activity-feed?limit=3"
        response = requests.get(url, timeout=5)
        
        print(f"\nAPI Test:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Raw API Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"API test failed: {e}")

if __name__ == "__main__":
    test_percentage_conversion()
    test_api()
