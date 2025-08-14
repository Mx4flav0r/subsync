#!/usr/bin/env python3
"""
Test script to verify the slice error fix
"""

from bazarr import bazarr

def test_series_slicing():
    print("🧪 Testing Series Data Slicing")
    print("=" * 40)
    
    # Get series data
    series = bazarr.get_series()
    print(f"Series data type: {type(series)}")
    print(f"Series length: {len(series) if hasattr(series, '__len__') else 'No len attribute'}")
    
    if series:
        print(f"First item type: {type(series[0])}")
        print(f"First item keys: {list(series[0].keys()) if isinstance(series[0], dict) else 'Not a dict'}")
        
        # Test slicing (this was causing the error)
        try:
            page_size = 20
            start = 0
            end = min(start + page_size, len(series))
            page_series = series[start:end]
            print(f"✅ Slicing works! Got {len(page_series)} items")
            
            # Test first item access
            if page_series:
                first_item = page_series[0]
                title = first_item.get('title', 'Unknown')
                print(f"✅ First series title: {title}")
                
        except Exception as e:
            print(f"❌ Slicing error: {e}")
    else:
        print("❌ No series data found")

if __name__ == "__main__":
    test_series_slicing()
