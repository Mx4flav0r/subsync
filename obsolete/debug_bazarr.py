#!/usr/bin/env python3
"""
Debug script to test the bazarr instance and series data
"""

def test_bazarr_debug():
    print("🔍 DEBUGGING BAZARR INSTANCE")
    print("=" * 50)
    
    # Import and test
    from bazarr import bazarr
    
    print(f"1. Bazarr type: {type(bazarr)}")
    print(f"2. Has get_series method: {hasattr(bazarr, 'get_series')}")
    
    # Test method call
    print("\n📺 Testing get_series()...")
    series = bazarr.get_series()
    
    print(f"3. Series type: {type(series)}")
    print(f"4. Series length: {len(series) if hasattr(series, '__len__') else 'No length'}")
    print(f"5. Can slice: {hasattr(series, '__getitem__')}")
    
    if series:
        print(f"6. First item type: {type(series[0])}")
        if hasattr(series[0], 'get'):
            print(f"7. First item title: {series[0].get('title', 'No title')}")
    
    # Test slicing specifically
    try:
        print("\n🔪 Testing slicing...")
        start = 0
        end = min(2, len(series))
        slice_test = series[start:end]
        print(f"✅ Slicing works! Got {len(slice_test)} items")
    except Exception as e:
        print(f"❌ Slicing failed: {e}")
        print(f"   Series object: {series}")

if __name__ == "__main__":
    test_bazarr_debug()
