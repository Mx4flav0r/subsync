#!/usr/bin/env python3
"""
Test the complete wanted items integration with Bazarr API
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_bazarr_wanted_api():
    """Test Bazarr wanted API integration"""
    print("🎯 Testing Bazarr wanted items API integration...")
    
    try:
        from bazarr_integration import BazarrIntegration
        from credential_manager import CredentialManager
        
        # Initialize credential manager and Bazarr integration
        cred_manager = CredentialManager()
        bazarr_client = BazarrIntegration(cred_manager)
        
        # Test connection first
        print("🔗 Testing Bazarr connection...")
        if not bazarr_client.test_connection():
            print("❌ Bazarr connection failed - check credentials and URL")
            return False
        
        print("✅ Bazarr connection successful")
        
        # Test wanted items methods
        print("\n🔍 Testing wanted items API...")
        
        # Get wanted movies
        wanted_movies = bazarr_client.get_wanted_movies()
        print(f"   Movies needing subtitles: {len(wanted_movies)}")
        
        # Get wanted series
        wanted_series = bazarr_client.get_wanted_series()
        print(f"   TV episodes needing subtitles: {len(wanted_series)}")
        
        # Get all wanted items
        all_wanted = bazarr_client.get_all_wanted_items()
        print(f"   Total items needing subtitles: {all_wanted['total']}")
        
        # Show sample wanted items
        if wanted_movies:
            print(f"\n📽️ Sample wanted movies:")
            for i, movie in enumerate(wanted_movies[:3]):
                title = movie.get('title', 'Unknown')
                print(f"     {i+1}. {title}")
        
        if wanted_series:
            print(f"\n📺 Sample wanted TV episodes:")
            for i, episode in enumerate(wanted_series[:3]):
                series = episode.get('series_title', 'Unknown Series')
                ep_title = episode.get('episode_title', 'Unknown Episode')
                print(f"     {i+1}. {series} - {ep_title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Bazarr wanted API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sync_engine_wanted_integration():
    """Test sync engine wanted items integration"""
    print("\n🔧 Testing sync engine wanted items integration...")
    
    try:
        from sync_engine import SyncEngine
        
        # Initialize sync engine
        sync_engine = SyncEngine()
        
        # Check if wanted items method exists
        if hasattr(sync_engine, 'process_wanted_items_with_translation'):
            print("✅ process_wanted_items_with_translation method found")
            
            # Check prerequisites
            if not sync_engine.use_pathmapper:
                print("⚠️ PathMapper not available")
                return False
                
            if not sync_engine.path_mapper.config:
                print("⚠️ Config not available")
                return False
                
            auto_trans = sync_engine.path_mapper.config.get('auto_translation', False)
            print(f"   Auto-translation enabled: {auto_trans}")
            
            if auto_trans and hasattr(sync_engine.path_mapper, 'bazarr_client'):
                print("✅ All prerequisites met for wanted items processing")
                return True
            else:
                print("⚠️ Some prerequisites not met")
                return False
        else:
            print("❌ process_wanted_items_with_translation method not found")
            return False
        
    except Exception as e:
        print(f"❌ Sync engine integration test failed: {e}")
        return False

def test_cli_wanted_menu():
    """Test CLI wanted menu integration"""
    print("\n📋 Testing CLI wanted menu integration...")
    
    try:
        from cli import SubtitleSyncCLI
        
        # Create CLI instance
        cli = SubtitleSyncCLI()
        
        # Check if wanted items menu method exists
        if hasattr(cli, '_wanted_items_menu'):
            print("✅ _wanted_items_menu method found in CLI")
            return True
        else:
            print("❌ _wanted_items_menu method not found in CLI")
            return False
        
    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running wanted items integration tests...\n")
    
    # Test Bazarr API
    bazarr_ok = test_bazarr_wanted_api()
    
    # Test sync engine integration
    sync_ok = test_sync_engine_wanted_integration()
    
    # Test CLI integration
    cli_ok = test_cli_wanted_menu()
    
    print(f"\n📊 Test Results:")
    print(f"   Bazarr API Integration: {'✅ PASS' if bazarr_ok else '❌ FAIL'}")
    print(f"   Sync Engine Integration: {'✅ PASS' if sync_ok else '❌ FAIL'}")
    print(f"   CLI Integration: {'✅ PASS' if cli_ok else '❌ FAIL'}")
    
    if bazarr_ok and sync_ok and cli_ok:
        print("\n🎉 All wanted items integration tests passed!")
        print("   Ready to automatically process items that need subtitles!")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
