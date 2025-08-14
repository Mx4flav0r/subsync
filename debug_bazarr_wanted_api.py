#!/usr/bin/env python3
"""
Debug Bazarr API endpoints to find the correct wanted series endpoint
"""

import requests
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from credential_manager import CredentialManager
from database_manager import DatabaseManager

def test_bazarr_endpoints():
    """Test various Bazarr API endpoints to find wanted series"""
    try:
        # Initialize components
        db_manager = DatabaseManager()
        cred_manager = CredentialManager(db_manager)
        
        url = cred_manager.bazarr_url
        api_key = cred_manager.bazarr_api_key
        
        if not url or not api_key:
            print("❌ Bazarr credentials not configured")
            return
        
        headers = {'X-API-KEY': api_key}
        print(f"🔍 Testing Bazarr API endpoints at: {url}")
        print(f"   Using API key: {api_key[:8]}...")
        
        # Test endpoints that might have wanted series
        endpoints_to_test = [
            "/api/series/wanted",
            "/api/episodes/wanted", 
            "/api/wanted",
            "/api/wanted/series",
            "/api/wanted/episodes",
            "/api/episodes?wanted=true",
            "/api/episodes",
            "/api/series/wanted?length=10",
            "/api/episodes/wanted?length=10"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                print(f"\n🧪 Testing: {endpoint}")
                response = requests.get(f"{url}{endpoint}", headers=headers, timeout=10)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"   ✅ Found list with {len(data)} items")
                            if data:
                                print(f"   Sample item keys: {list(data[0].keys())}")
                        elif isinstance(data, dict):
                            print(f"   ✅ Found dict with keys: {list(data.keys())}")
                            if 'data' in data:
                                items = data['data']
                                print(f"   Items in 'data': {len(items) if isinstance(items, list) else 'not a list'}")
                        else:
                            print(f"   ✅ Response type: {type(data)}")
                    except json.JSONDecodeError as e:
                        print(f"   ❌ JSON decode error: {e}")
                        print(f"   Raw response: {response.text[:200]}...")
                else:
                    print(f"   ❌ Failed with status {response.status_code}")
                    if response.text:
                        print(f"   Error: {response.text[:100]}...")
                        
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        
        print(f"\n📊 Endpoint testing complete")
        
    except Exception as e:
        print(f"❌ Failed to test endpoints: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bazarr_endpoints()
