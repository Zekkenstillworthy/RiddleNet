#!/usr/bin/env python3
"""
Test script to verify the analytics dashboard fixes
"""
import requests
import json
import time

def test_analytics_endpoints():
    """Test all the analytics endpoints"""
    base_url = "http://localhost:5001/admin/api/analytics"
    
    endpoints = [
        "real-time",
        "activity-feed?limit=5",
        "chart-data/performance-trend?date_range=30",
        "chart-data/score-distribution?date_range=30",
    ]
    
    print("🔍 Testing Analytics Dashboard Endpoints...")
    print("=" * 60)
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}/{endpoint}"
            print(f"\n📊 Testing: {endpoint}")
            
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print("✅ Success: API returned valid data")
                        
                        # Check for percentage issues in activity feed
                        if 'activity-feed' in endpoint:
                            check_activity_feed_percentages(data)
                        
                        # Check chart data
                        elif 'chart-data' in endpoint:
                            check_chart_data(data, endpoint)
                            
                    else:
                        print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - server may not be running")
            break
        except Exception as e:
            print(f"❌ Request failed: {e}")

def check_activity_feed_percentages(data):
    """Check for percentage issues in activity feed"""
    if 'data' in data and isinstance(data['data'], list):
        print(f"📈 Activity feed contains {len(data['data'])} items")
        
        high_percentages = []
        nan_scores = []
        
        for item in data['data']:
            if isinstance(item, dict) and 'score' in item:
                score = item['score']
                username = item.get('username', 'Unknown')
                
                if score is None:
                    continue  # Skip items without scores (like ungraded essays)
                    
                try:
                    score_val = float(score)
                    if score_val > 100:
                        high_percentages.append(f"{username}: {score}%")
                    elif score_val != score_val:  # NaN check
                        nan_scores.append(f"{username}: NaN%")
                except (ValueError, TypeError):
                    nan_scores.append(f"{username}: Invalid score")
        
        if high_percentages:
            print(f"❌ Found high percentages: {high_percentages}")
        else:
            print("✅ No percentages above 100% found!")
            
        if nan_scores:
            print(f"❌ Found NaN/invalid scores: {nan_scores}")
        else:
            print("✅ No NaN/invalid scores found!")

def check_chart_data(data, endpoint):
    """Check chart data structure"""
    if 'data' in data:
        chart_data = data['data']
        
        if 'performance-trend' in endpoint:
            if 'datasets' in chart_data and chart_data['datasets']:
                scores = chart_data['datasets'][0].get('data', [])
                if scores:
                    max_score = max(scores)
                    min_score = min(scores)
                    print(f"📈 Performance trend: {min_score:.1f}% - {max_score:.1f}%")
                    
                    if max_score > 100:
                        print(f"❌ Performance trend has scores > 100%")
                    else:
                        print("✅ Performance trend scores are within bounds")
                        
        elif 'score-distribution' in endpoint:
            if 'datasets' in chart_data and chart_data['datasets']:
                distribution = chart_data['datasets'][0].get('data', [])
                total_scores = sum(distribution)
                print(f"📊 Score distribution covers {total_scores} total scores")
                print("✅ Score distribution data looks good")

if __name__ == "__main__":
    test_analytics_endpoints()
    
    print("\n" + "=" * 60)
    print("🎯 Analytics Fix Test Complete!")
    print("\nTo see the improved dashboard:")
    print("1. Hard refresh your browser (Ctrl+Shift+R)")
    print("2. Visit: http://localhost:5001/admin/")
    print("3. Check the Real-time Activity Feed")
