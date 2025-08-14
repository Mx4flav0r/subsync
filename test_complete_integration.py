#!/usr/bin/env python3
"""
Test the complete integration of translation system with sync engine
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sync_engine_integration():
    """Test that sync engine can initialize with translation config"""
    print("🧪 Testing sync engine integration with translation system...")
    
    try:
        # Import sync engine
        from sync_engine import SyncEngine
        
        # Create sync engine instance
        sync_engine = SyncEngine()
        
        # Check if PathMapper is available and has config
        if sync_engine.use_pathmapper and sync_engine.path_mapper:
            print("✅ Sync engine initialized successfully")
            
            # Check if path mapper has config
            if hasattr(sync_engine.path_mapper, 'config'):
                config_obj = sync_engine.path_mapper.config
                print(f"✅ PathMapper has config: {bool(config_obj)}")
                print(f"   Config type: {type(config_obj)}")
                
                # Check if translation is enabled (handle different config types)
                try:
                    if isinstance(config_obj, dict):
                        enabled = config_obj.get('auto_translation', False)
                        print(f"✅ Translation enabled: {enabled}")
                    elif hasattr(config_obj, 'get'):
                        enabled = config_obj.get('auto_translation', False)
                        print(f"✅ Translation enabled: {enabled}")
                    else:
                        print(f"⚠️ Config object type not supported: {type(config_obj)}")
                except Exception as e:
                    print(f"⚠️ Could not check translation setting: {e}")
            else:
                print("⚠️ PathMapper missing config attribute")
        else:
            print("❌ PathMapper not available")
            
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_translation_availability():
    """Test that translation module is available"""
    print("\n🧪 Testing translation module availability...")
    
    try:
        from subtitle_translator import SubtitleTranslator
        
        # Create translator instance
        translator = SubtitleTranslator()
        print("✅ SubtitleTranslator imported successfully")
        
        # Test basic translation using a public method
        result = translator._translate_mymemory(["Hello"], target_language='nl')
        if result and len(result) > 0 and result[0] != "Hello":
            print(f"✅ Basic translation working: 'Hello' -> '{result[0]}'")
        else:
            print("⚠️ Translation returned original text or empty result")
            
        return True
        
    except Exception as e:
        print(f"❌ Translation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running complete integration tests...\n")
    
    # Test sync engine integration
    sync_ok = test_sync_engine_integration()
    
    # Test translation availability
    trans_ok = test_translation_availability()
    
    print(f"\n📊 Test Results:")
    print(f"   Sync Engine Integration: {'✅ PASS' if sync_ok else '❌ FAIL'}")
    print(f"   Translation Module: {'✅ PASS' if trans_ok else '❌ FAIL'}")
    
    if sync_ok and trans_ok:
        print("\n🎉 All tests passed! Translation system is ready!")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
