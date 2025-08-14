#!/usr/bin/env python3
"""
Test Plex Integration
"""

from config import config
from sync_engine import SyncEngine

def test_plex_integration():
    """Test the Plex integration setup"""
    print("🧪 TESTING PLEX INTEGRATION")
    print("=" * 50)
    
    # Check config
    plex_url = config.get("plex_url")
    plex_token = config.get("plex_token") 
    plex_enabled = config.get("plex_integration", True)
    
    print(f"📡 Plex URL: {plex_url}")
    print(f"🔑 Plex Token: {'Configured' if plex_token else 'Not configured'}")
    print(f"🎬 Plex Integration: {'Enabled' if plex_enabled else 'Disabled'}")
    
    # Test sync engine initialization
    print("\n🔧 Testing SyncEngine initialization...")
    try:
        sync_engine = SyncEngine()
        if sync_engine.plex_client:
            print("✅ Plex client initialized successfully")
            
            # Test connection
            if sync_engine.plex_client.test_connection():
                print("✅ Plex connection successful")
                
                # Show libraries
                libraries = sync_engine.plex_client.get_libraries()
                if libraries:
                    print(f"📚 Found {len(libraries)} libraries:")
                    for lib in libraries:
                        print(f"   • {lib['title']} ({lib['type']})")
            else:
                print("❌ Plex connection failed")
        else:
            print("⚠️ Plex client not initialized")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Test completed")

if __name__ == "__main__":
    test_plex_integration()
