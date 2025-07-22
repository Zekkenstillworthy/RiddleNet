import requests
import json

# Test the analytics API endpoints
base_url = "http://localhost:5001/admin/api/analytics"

endpoints = [
    "real-time",
    "activity-feed?limit=10",
    "chart-data/performance-trend?date_range=30",
    "chart-data/score-distribution?date_range=30",
    "chart-data/category-performance?date_range=30",
    "chart-data/engagement-heatmap?date_range=30"
]

print("🔍 Testing Analytics API Endpoints...")
print("=" * 50)

for endpoint in endpoints:
    try:
        url = f"{base_url}/{endpoint}"
        response = requests.get(url)
        
        print(f"\n📊 Testing: {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print("✅ Success: API returned valid data")
                    if 'data' in data:
                        print(f"📈 Data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else type(data['data'])}")
                else:
                    print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text[:100]}...")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Request failed: {e}")

print("\n" + "=" * 50)
print("🎯 Analytics API Test Complete!")
