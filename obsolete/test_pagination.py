#!/usr/bin/env python3
"""
Test the updated Bazarr API calls with pagination
"""

import requests

def test_bazarr_pagination():
    url = "http://192.168.90.3:30046"
    api_key = "900109438dd185938a382344cd28c88a"
    
    print("🧪 Testing Bazarr API with Pagination")
    print("=" * 50)
    
    # Test series with pagination
    print("\n📺 Testing Series API...")
    try:
        response = requests.get(f"{url}/api/series", 
                              headers={"X-API-KEY": api_key},
                              params={"start": 0, "length": -1})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} series")
            if data:
                print(f"First series: {data[0].get('title', 'Unknown')}")
        else:
            print(f"❌ Error: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test movies with pagination
    print("\n🎬 Testing Movies API...")
    try:
        response = requests.get(f"{url}/api/movies", 
                              headers={"X-API-KEY": api_key},
                              params={"start": 0, "length": -1})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} movies")
            if data:
                print(f"First movie: {data[0].get('title', 'Unknown')}")
        else:
            print(f"❌ Error: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_bazarr_pagination()
