#!/usr/bin/env python3
"""
Quick test script for Bazarr API credentials
"""

import requests

def test_bazarr_api():
    url = "http://192.168.90.3:30046"
    api_key = "900109438dd185938a382344cd28c88a"
    
    print("🧪 Testing Bazarr API Credentials")
    print("=" * 40)
    print(f"URL: {url}")
    print(f"API Key: ***{api_key[-4:]}")
    
    # Test system status
    try:
        print("\n📊 Testing system status...")
        response = requests.get(f"{url}/api/system/status", headers={"X-API-KEY": api_key})
        print(f"Status endpoint: {response.status_code}")
        if response.status_code == 200:
            print("✅ System status OK")
        else:
            print(f"❌ System status failed: {response.text[:100]}")
    except Exception as e:
        print(f"❌ System status error: {e}")
    
    # Test movies endpoint
    try:
        print("\n🎬 Testing movies endpoint...")
        response = requests.get(f"{url}/api/movies", headers={"X-API-KEY": api_key})
        print(f"Movies endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Movies API OK - Found {len(data)} movies")
            if data:
                print(f"First movie: {data[0].get('title', 'Unknown')}")
        else:
            print(f"❌ Movies API failed: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Movies API error: {e}")
    
    # Test series endpoint
    try:
        print("\n📺 Testing series endpoint...")
        response = requests.get(f"{url}/api/series", headers={"X-API-KEY": api_key})
        print(f"Series endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Series API OK - Found {len(data)} series")
            if data:
                print(f"First series: {data[0].get('title', 'Unknown')}")
        else:
            print(f"❌ Series API failed: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Series API error: {e}")

if __name__ == "__main__":
    test_bazarr_api()
